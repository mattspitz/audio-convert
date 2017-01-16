import re

import eyed3
from recordclass import recordclass

Tags = recordclass(
    "Tags",
    [
        "album_artist",
        "artist",
        "title",
        "album",
        "year",
        "track_no",
        "cd_no",
        "cd_tracks",
        "genre_id",
        "genre_name",
        "comment",
        "composer",
        "original_artist",
        "encoded_by",
    ],
)

class BaseFormat(object):
    @classmethod
    def get_extension(cls):
        """Returns extension for this format (e.g. 'mp3')"""
        raise NotImplementedError()

    @classmethod
    def read_tags(cls, fn):
        """Returns Tags read from file"""
        raise NotImplementedError()

    @classmethod
    def write_tags(cls, fn, tags):
        """Writes given Tags to file"""
        raise NotImplementedError()

    @classmethod
    def encode(cls, fn_wav, output_fn):
        """Encodes the provided WAV file into the given output_fn"""
        raise NotImplementedError()

    @classmethod
    def decode(cls, fn, output_fn_wav):
        """Decodes the provided file into the given output_fn_wav"""
        raise NotImplementedError()


class MP3(BaseFormat):
    @classmethod
    def get_extension(cls):
        return "mp3"

    @classmethod
    def read_tags(cls, fn):
        audiofile = eyed3.load(fn)
        for f in dir(audiofile.tag):
            if not f.startswith("_"):
                pass#print f, getattr(audiofile.tag, f)
        if audiofile.tag.best_release_date:
            year = audiofile.tag.best_release_date.year
        else:
            year = None

        if audiofile.tag.track_num:
            track_no, cd_tracks = audiofile.tag.track_num
        else:
            track_no, cd_tracks = None, None

        if audiofile.tag.disc_num:
            tpos, _ = audiofile.tag.disc_num
        else:
            tpos = None

        if audiofile.tag.genre:
            genre_name, genre_id = audiofile.tag.genre.name, audiofile.tag.genre.id
        else:
            genre_name, genre_id = None, None

        extra_tags = {}
        for k in ("COMM", "TCOM", "TOPE", "TENC"):
            if k in audiofile.tag.frame_set:
                extra_tags[k] = audiofile.tag.frame_set.get(k)[0].text

        return Tags(
            album_artist=audiofile.tag.album_artist,
            artist=audiofile.tag.artist,
            title=audiofile.tag.title,
            album=audiofile.tag.album,
            year=year,
            track_no=track_no,
            cd_no=tpos,
            cd_tracks=cd_tracks,
            genre_id=genre_id,
            genre_name=genre_name,
            comment=extra_tags.get("COMM"),
            composer=extra_tags.get("TCOM"),
            original_artist=extra_tags.get("TOPE"),
            encoded_by=extra_tags.get("TENC"),
        )
