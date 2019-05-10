import subprocess
import sys

import eyed3

from .util import (
    Tags,
)

EXTENSIONS = [".mp3"]

LAME_OPTS = [
    "-m", "auto",
    "-h",
    "--vbr-new",
    "-b", "256",
    "-B", "320",
    "--replaygain-accurate",
    "--preset", "extreme",
]


def encode(wav_fns, output_dir):
    """Encodes the provided WAV files into the given output directory"""
    assert all(fn.endswith(".wav") for fn in wav_fns)
    subprocess.check_call(
        ["lame"]
        + LAME_OPTS
        + [ "--nogaptags",
            "--nogapout", output_dir,
            "--nogap", ]
        + wav_fns,
    )


def read_tags(fn):
    f = eyed3.load(unicode(fn, sys.getfilesystemencoding()))
    if f.tag is None:
        return None

    if f.tag.getBestDate():
        year = f.tag.getBestDate().year
    else:
        year = None

    if f.tag.track_num:
        track_no, cd_tracks = f.tag.track_num
    else:
        track_no, cd_tracks = None, None

    if f.tag.disc_num:
        tpos, _ = f.tag.disc_num
    else:
        tpos = None

    if f.tag.genre:
        genre_name, genre_id = f.tag.genre.name, f.tag.genre.id
    else:
        genre_name, genre_id = None, None

    extra_tags = {}
    for k in ("COMM", "TCOM", "TOPE", "TENC"):
        if k in f.tag.frame_set:
            extra_tags[k] = f.tag.frame_set.get(k)[0].text

    return Tags(
        album_artist=f.tag.album_artist,
        artist=f.tag.artist,
        title=f.tag.title,
        album=f.tag.album,
        year=year,
        track_no=track_no,
        cd_no=tpos,
        cd_tracks=cd_tracks,
        genre_id=genre_id,
        genre_name=genre_name,
        comment=extra_tags.get("COMM") or None,
        composer=extra_tags.get("TCOM") or None,
        original_artist=extra_tags.get("TOPE") or None,
        encoded_by=extra_tags.get("TENC") or None,
    )


def write_tags(fn, tags):
    """ Writes the tags provided, augmenting what already exists.

    Each value is only updated if it's not None. Empty strings clear fields."""
    f = eyed3.load(unicode(fn, sys.getfilesystemencoding()))
    if not f.tag:
        f.initTag(version=eyed3.id3.ID3_V2_4)

    if tags.album_artist is not None:
        f.tag.album_artist = tags.album_artist

    if tags.artist is not None:
        f.tag.artist = tags.artist

    if tags.title is not None:
        f.tag.title = tags.title

    if tags.album is not None:
        f.tag.album = tags.album

    if tags.year is not None:
        f.tag.original_release_date = tags.year

    if tags.cd_no is not None:
        _, num_discs = f.tag.disc_num
        f.tag.disc_num = (tags.cd_no, num_discs)

    if tags.track_no is not None:
        _, cd_tracks = f.tag.track_num
        f.tag.track_num = (tags.track_no, cd_tracks)

    if tags.cd_tracks is not None:
        track_no, _ = f.tag.track_num
        f.tag.track_num = (track_no, tags.cd_tracks)

    if (tags.genre_id is not None
            or tags.genre_name is not None):
        class MyGenreMap(eyed3.id3.GenreMap):
            def __missing__(self, key):
                # otherwise, need to catch KeyError for missing genre ids/names
                return None

        genre_map = MyGenreMap()
        def _get_genre():
            # genre_id trumps genre_name, if present
            if tags.genre_id is not None:
                genre = genre_map[tags.genre_id]
                if genre:
                    return genre

            # try to guess genre just from the name
            if tags.genre_name is not None:
                genre = genre_map[tags.genre_name]
                if genre:
                    return genre

            # fall back on just the name
            if tags.genre_name:
                return eyed3.id3.Genre(name=tags.genre_name)
            return None

        f.tag.genre = _get_genre()

    if tags.comment is not None:
        for c in f.tag.comments:
            f.tag.comments.remove(c.description, c.lang)

        if tags.comment: # empty string clears it
            f.tag.comments.set(tags.comment)

    if tags.composer is not None:
        f.tag.frame_set.setTextFrame("TCOM", tags.composer)

    if tags.original_artist is not None:
        f.tag.frame_set.setTextFrame("TOPE", tags.original_artist)

    if tags.encoded_by is not None:
        f.tag.frame_set.setTextFrame("TENC", tags.encoded_by)

    f.tag.save(version=eyed3.id3.ID3_V2_4, preserve_file_time=True)
