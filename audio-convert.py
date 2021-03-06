#!/usr/bin/python

import argparse
import errno
import itertools
import operator
import os
import shutil
import subprocess
import tempfile

import pycolor
import tabulate
import yaml

from aclib import (
    audioformat,
    collector,
    util,
)

PROCESSED_DIR = "processed"
UTF8_TYPE = lambda s: unicode(s, "utf8")
TAG_OVERRIDES = {
        "album_artist": {"type": UTF8_TYPE, "strip_from_singles": False},
        "album": {"type": UTF8_TYPE, "strip_from_singles": False},
        "year": {"type": UTF8_TYPE, "strip_from_singles": False},
        "genre_name": {"type": UTF8_TYPE, "strip_from_singles": True},
        "comment": {"type": UTF8_TYPE, "strip_from_singles": True},
        "composer": {"type": UTF8_TYPE, "strip_from_singles": True},
        "original_artist": {"type": UTF8_TYPE, "strip_from_singles": True},
        "encoded_by": {"type": UTF8_TYPE, "strip_from_singles": True},
}

# courtesy of http://stackoverflow.com/questions/2890146/how-to-force-pyyaml-to-load-strings-as-unicode-objects
def construct_yaml_str(self, node):
    # Override the default string handling function to return unicode objects always
    return self.construct_scalar(node)
yaml.Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Standardize your audio encoding and tagging!",
    )

    # force these tags (optional)
    override_group = parser.add_argument_group("tag_overrides", "ID3 tag overrides")
    for k, cfg in TAG_OVERRIDES.iteritems():
        override_group.add_argument("--" + k, type=cfg["type"])

    parser.add_argument(
        "--output_dir",
        default=".",
    )

    parser.add_argument(
        "--singles",
        action="store_true",
        help="If specified, the single directory passed to 'audio_dirs' represents a list of singles to be tagged as Various Artists and stripped of most metadata.",
    )

    parser.add_argument(
        "audio_dirs",
        metavar="AUDIO_DIR",
        nargs="+",
        help="Directories of audio to process non-recursively. Multiple directories will be interpreted as multiple discs and will be tagged CD=1,2,3,...",
    )

    args = parser.parse_args()
    assert os.path.exists(args.output_dir)
    assert not (args.singles and len(args.audio_dirs) > 1), "Only process one singles directory at a time."
    return args


class PendingDisc(object):
    def __init__(self, pending_audio_files, output_dir):
        needs_conversion = [
            paf.needs_conversion()
            for paf in pending_audio_files
        ]
        if any(needs_conversion):
            assert all(needs_conversion)

        dirname = {
            os.path.dirname(paf.current_filename)
            for paf in pending_audio_files
        }
        assert len(dirname) == 1

        self.dirname = dirname.pop()
        self.pending_audio_files = pending_audio_files
        self.output_dir = output_dir

    def process_disc(self):
        # copy to mp3_tmpdir, reencoding if necessary
        with util.mktempdir() as mp3_tmpdir:
            if any(paf.needs_conversion() for paf in self.pending_audio_files):
                with util.mktempdir() as wav_tmpdir:
                    for idx, paf in enumerate(self.pending_audio_files, 1):
                        paf.decode(os.path.join(wav_tmpdir, "{:03d}.wav".format(idx)))

                    audioformat.mp3.encode([
                            paf.decoded_fn
                            for paf in self.pending_audio_files
                        ],
                        mp3_tmpdir,
                    )
                    for paf in self.pending_audio_files:
                        assert paf.decoded_fn.endswith(".wav")
                        encoded_fn = os.path.join(
                            mp3_tmpdir,
                            os.path.splitext(os.path.basename(paf.decoded_fn))[0] + ".mp3",
                        )
                        paf.mark_encoded_fn(encoded_fn)
            else:
                for paf in self.pending_audio_files:
                    new_fn = os.path.join(
                        mp3_tmpdir,
                        os.path.basename(paf.current_filename),
                    )
                    assert not os.path.exists(new_fn)
                    shutil.copy(paf.current_filename, new_fn)
                    paf.mark_encoded_fn(new_fn)

            # write tags
            for paf in self.pending_audio_files:
                paf.write_tags()

            # create output directory and rename
            dirs = set(paf.new_directory for paf in self.pending_audio_files)
            assert len(dirs) == 1

            output_dir = dirs.pop()
            try:
                os.makedirs(output_dir)
            except OSError as exc:  # Python >2.5
                if exc.errno == errno.EEXIST and os.path.isdir(output_dir):
                    pass
                else:
                    raise

            for paf in self.pending_audio_files:
                paf.rename()

            processed_dir = os.path.join(self.output_dir, PROCESSED_DIR)
            if not os.path.exists(processed_dir):
                os.mkdir(processed_dir)
            shutil.move(self.dirname, processed_dir)


class PendingAudioFile(object):
    def __init__(self, audio_file, tag_overrides, num_total_discs, is_singles, output_dir):
        self.audio_file = audio_file
        self.tag_overrides = tag_overrides
        self.num_total_discs = num_total_discs
        self.is_singles = is_singles
        self.output_dir = output_dir

        self._current_tags = None
        self._current_tags_memoized = False

        # set if decoded
        self._decoded_fn = None
        # marked externally if encoded
        self._encoded_fn = None

    @property
    def current_tags(self):
        if not self._current_tags_memoized:
            self._current_tags = self.audio_file.read_tags()
            self._current_tags_memoized = True
        return self._current_tags

    @property
    def proposed_tags(self):
        proposed_tags = self.current_tags.copy(**self.tag_overrides)

        # null-out empty-stringed tags
        proposed_tags.genre_id = proposed_tags.genre_id or None
        proposed_tags.genre_name = proposed_tags.genre_name or None

        proposed_tags.comment = proposed_tags.comment or None
        proposed_tags.composer = proposed_tags.composer or None
        proposed_tags.original_artist = proposed_tags.original_artist or None
        proposed_tags.encoded_by = proposed_tags.encoded_by or None

        return proposed_tags

    @property
    def current_filename(self):
        return self.audio_file.path

    @property
    def new_filename(self):
        new_tags = self.proposed_tags

        track_num = util.get_track_filename_representation(
            new_tags.cd_no, new_tags.track_no,
            self.num_total_discs, new_tags.cd_tracks,
        )

        if self.is_singles:
            return os.path.join(
                self.output_dir,
                u"Various Artists".encode("utf8"),
                u"{artist} - {title}.mp3".format(artist=new_tags.artist, title=new_tags.title).replace("/", "-").encode("utf8"),
            ).encode("utf8")

        return os.path.join(
            self.output_dir,
            u"{album_artist}".format(album_artist=new_tags.album_artist).replace("/", "-").encode("utf8"),
            u"{year} - {album}".format(year=new_tags.year, album=new_tags.album).replace("/", "-").encode("utf8"),
            u"{track_num} {title}.mp3".format(track_num=track_num, title=new_tags.title).replace("/", "-").encode("utf8"),
        )

    @property
    def new_directory(self):
        return os.path.dirname(self.new_filename)

    def needs_conversion(self):
        return self.audio_file.ext != ".mp3"

    def decode(self, output_fn):
        assert not self._decoded_fn
        self.audio_file.decode(output_fn)
        self._decoded_fn = output_fn

    @property
    def decoded_fn(self):
        assert self._decoded_fn
        return self._decoded_fn

    def mark_encoded_fn(self, encoded_fn):
        assert not self._encoded_fn
        assert os.path.exists(encoded_fn)
        self._encoded_fn = encoded_fn

    def write_tags(self):
        assert self._encoded_fn
        assert self._encoded_fn.endswith(".mp3")

        new_tags = self.proposed_tags
        assert new_tags.album_artist
        assert new_tags.year
        assert new_tags.album
        assert new_tags.title
        assert new_tags.cd_no
        assert new_tags.track_no or self.is_singles
        assert self.num_total_discs or self.is_singles
        assert new_tags.cd_tracks or self.is_singles

        return audioformat.mp3.write_tags(self._encoded_fn, self.proposed_tags)

    def rename(self):
        assert self._encoded_fn
        assert os.path.exists(self._encoded_fn)
        assert not os.path.exists(self.new_filename)
        shutil.move(self._encoded_fn, self.new_filename)

    def __repr__(self):
        return "PendingAudioFile({}, {}, {})".format(self.audio_file, self.tag_overrides, self.new_filename)


def get_tag_overrides(args):
    # blah, hacky
    overrides = {
        k: getattr(args, k)
        for k in TAG_OVERRIDES
        if getattr(args, k) is not None
    }
    if ("album_artist" in overrides
            and overrides["album_artist"] != "Various Artists"):
        overrides["artist"] = overrides["album_artist"]
    return overrides


def get_pending_discs(audio_dirs, global_tag_overrides, output_dir, is_singles):
    pending_discs = []
    for disc_num, d in enumerate(audio_dirs, 1):
        audio_files = collector.collect_audio_files(d, allow_heterogenous=is_singles)
        disc_overrides = dict(global_tag_overrides)
        if is_singles:
            disc_overrides["album_artist"] = u"Various Artists"
            disc_overrides["album"] = u"Singles"
            disc_overrides["year"] = 2019
            disc_overrides["cd_no"] = 1
            disc_overrides["cd_tracks"] = None
            disc_overrides["genre_id"] = None
            for k, cfg in TAG_OVERRIDES.iteritems():
                if cfg["strip_from_singles"]:
                    disc_overrides[k] = ""
        else:
            disc_overrides["cd_no"] = disc_num
            disc_overrides["cd_tracks"] = len(audio_files)

        pending_audio_files = []

        for track_num, audio_file in enumerate(sorted(audio_files, key=operator.attrgetter("path")), 1):
            overrides = dict(disc_overrides)
            overrides["track_no"] = None if is_singles else track_num

            pending_audio_files.append(
                PendingAudioFile(
                    audio_file,
                    overrides,
                    len(audio_dirs),
                    is_singles,
                    output_dir,
            ))
        pending_discs.append(PendingDisc(pending_audio_files, output_dir))

    return pending_discs


def print_pending_discs(pending_discs):
    def get_update_str(new_val, old_val):
        if new_val == old_val:
            return old_val

        new_colored_unicode = pycolor.color_string(
            # make sure it goes in as a plain string
            new_val.encode("utf8") if isinstance(new_val, unicode) else str(new_val),
            attribute="bold",
            fg_color="green",
        ).decode("utf8")

        # upgrade old_val to unicode only if it's a plain string
        old_unicode = old_val.decode("utf8") if isinstance(old_val, str) else old_val

        # neither arg may be a plain string...
        return u"{} ({})".format(new_colored_unicode, old_unicode)

    def print_2_column_table(cells):
        table = list(itertools.izip_longest(cells[0:(len(cells)/2)], cells[(len(cells)/2):], fillvalue=""))
        print tabulate.tabulate(table, tablefmt="plain")

    for disc in pending_discs:
        for af in disc.pending_audio_files:
            print get_update_str(af.new_filename, af.current_filename)
            cells = []
            for slot in audioformat.util.Tags.__slots__:
                cells.append(u"{}: {}".format(
                    slot,
                    get_update_str(getattr(af.proposed_tags, slot), getattr(af.current_tags, slot)),
                ))
            print_2_column_table(cells)


def update_pending_discs(initial_pending_discs, output_dir, is_singles):
    print_pending_discs(initial_pending_discs)

    print
    print "Ready to edit? Skip by entering 'n'. Ctrl+C to exit."
    maybe_no = raw_input()
    if maybe_no == 'n':
        return initial_pending_discs

    paf_by_filename = {}
    with tempfile.NamedTemporaryFile() as tmpfile:
        display_yaml = []
        for disc in initial_pending_discs:
            paf_yaml = []
            for paf in disc.pending_audio_files:
                # save the filename as unicode! it gets saved as unicode in the yaml and otherwise we can't pop it later #facepalm
                paf_by_filename[paf.current_filename.decode("utf8")] = paf

                paf_yaml.append({
                    "filename": paf.current_filename,
                    "proposed_tags": paf.proposed_tags.to_dict(),
                })

            display_yaml.append({
                "audio_files": paf_yaml,
            })

        yaml.safe_dump(display_yaml, tmpfile, default_flow_style=False, allow_unicode=True)
        tmpfile.flush()

        editor = os.environ.get("EDITOR", "vim")
        subprocess.call([editor, tmpfile.name])

        tmpfile.seek(0)
        loaded_yaml = yaml.safe_load(tmpfile)

    pending_discs = []
    for disc in loaded_yaml:
        pending_audio_files = []
        for paf in disc["audio_files"]:
            cached_af = paf_by_filename.pop(paf.pop("filename"))
            pending_audio_files.append(
                PendingAudioFile(
                    cached_af.audio_file,
                    paf.pop("proposed_tags"),
                    cached_af.num_total_discs,
                    is_singles,
                    output_dir,
                ),
            )
        pending_discs.append(
            PendingDisc(pending_audio_files, output_dir),
        )
    assert len(paf_by_filename) == 0, "Expected to find all filenames!"

    print_pending_discs(pending_discs)

    print
    print "Look good? Press Enter. Ctrl+C to exit."
    raw_input()

    return pending_discs


def main():
    args = parse_args()

    initial_pending_discs = get_pending_discs(args.audio_dirs, get_tag_overrides(args), args.output_dir, args.singles)
    pending_discs = update_pending_discs(initial_pending_discs, args.output_dir, args.singles)

    for disc in pending_discs:
        disc.process_disc()


if __name__ == "__main__":
    main()
