#!/usr/bin/python

import argparse
import operator
import os

import pycolor

from aclib import (
    audioformat,
    collector,
    util,
)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Standardize your audio encoding and tagging!",
    )

    # force these tags (optional)
    override_group = parser.add_argument_group("tag_overrides", "ID3 tag overrides (optional)")
    override_group.add_argument("--artist")
    override_group.add_argument("--album_artist")
    override_group.add_argument("--album")
    override_group.add_argument("--year")
    override_group.add_argument("--genre_name")
    override_group.add_argument("--comment")
    override_group.add_argument("--composer")
    override_group.add_argument("--original_artist")
    override_group.add_argument("--encoded_by")

    parser.add_argument(
        "audio_dirs",
        metavar="AUDIO_DIR",
        nargs="+",
        help="Directories of audio to process non-recursively. Multiple directories will be interpreted as multiple discs and will be tagged CD=1,2,3,...",
    )

    return parser.parse_args()


class PendingAudioFile(object):
    def __init__(self, audio_file, tag_overrides, num_total_discs):
        self.audio_file = audio_file
        self.tag_overrides = tag_overrides
        self.num_total_discs = num_total_discs

        self._current_tags = None
        self._current_tags_memoized = False


    @property
    def current_tags(self):
        if not self._current_tags_memoized:
            self._current_tags = self.audio_file.read_tags()
            self._current_tags_memoized = True
        return self._current_tags


    @property
    def proposed_tags(self):
        return self.current_tags.copy(**self.tag_overrides)


    @property
    def new_filename(self):
        new_tags = self.proposed_tags

        track_num = util.get_track_filename_representation(
            new_tags.cd_no, new_tags.track_no,
            self.num_total_discs, new_tags.cd_tracks,
        )

        return os.path.join(
            "{album_artist}".format(album_artist=new_tags.album_artist),
            "{year} - {album}".format(year=new_tags.year, album=new_tags.album),
            "{track_num} {title}.mp3".format(track_num=track_num, title=new_tags.title),
        )


    def needs_conversion(self):
        return self.audio_file.ext != ".mp3"


    def write_tags(self):
        return self.audio_file.write_tags(self.proposed_tags)


    def __repr__(self):
        return "PendingAudioFile({}, {}, {})".format(self.audio_file, self.tag_overrides, self.new_filename)


def get_tag_overrides(args):
    # blah, hacky
    return {
        k: v
        for k, v in vars(args).iteritems()
        if k not in ("audio_dirs") and v is not None
    }


def get_pending_audio_files(audio_dirs, global_tag_overrides):
    pending_audio_files = []
    for disc_num, d in enumerate(audio_dirs, 1):
        audio_files = collector.collect_audio_files(d)
        disc_overrides = dict(global_tag_overrides)
        disc_overrides["cd_no"] = disc_num
        disc_overrides["cd_tracks"] = len(audio_files)

        for track_num, audio_file in enumerate(sorted(audio_files, key=operator.attrgetter("path")), 1):
            overrides = dict(disc_overrides)
            overrides["track_no"] = track_num

            pending_audio_files.append(
                PendingAudioFile(
                    audio_file,
                    overrides,
                    len(audio_dirs),
            ))

    return pending_audio_files


def print_pending_audio_files(pending_audio_files):
    def get_update_str(new_val, old_val):
        if new_val == old_val:
            return old_val
        return "{} ({})".format(
            pycolor.color_string(unicode(new_val), attribute="bold", fg_color="green"),
            old_val,
        )

    # TODO: drop this into `less`; when the user quits, ask to confirm

    for af in pending_audio_files:
        print get_update_str(af.new_filename, af.audio_file.path)
        for slot in audioformat.util.Tags.__slots__:
            print "\t{}: {}".format(
                slot,
                get_update_str(getattr(af.proposed_tags, slot), getattr(af.current_tags, slot)),
            )


def main():
    args = parse_args()

    pending_audio_files = get_pending_audio_files(args.audio_dirs, get_tag_overrides(args))
    print_pending_audio_files(pending_audio_files)

    # print the differences (enter to confirm, Ctrl+C to exit out)

    # convert
    # encode

    # rename

    # find all the non-MP3s; blow up if we have a heterogenous set of recognized filenames (FLAC and MP3, etc)

    # pull the tags and print them out (with pending changes, if necessary); user should hit enter to confirm (rerun to force tags)
    # infer #tracks and cd_number

    # if necessary, decode and convert files to MP3 (into a separate directory, <dir>/converted)

    # rename? maybe as a separate command...

    # Later...
        # - allow manual edits for in-place changes of track names, VA-discs, etc
        # - concurrency
        # - color output (colorama?)

if __name__ == "__main__":
    main()
