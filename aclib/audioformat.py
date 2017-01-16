import re
import subprocess

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
        output = subprocess.check_output([
            "id3v2",
            "--list-rfc822",
            fn,
        ])

        tags = {}
        for line in output.strip().split("\n"):
            key, val = line.split(": ", 1)
            tags[key] = val

        if "TYER" in tags:
            try:
                year = int(tags["TYER"])
            except ValueError:
                year = tags["TYER"]
        else:
            year = None

        if "TRCK" in tags:
            trck = tags["TRCK"]
            if "/" in trck:
                track_no, cd_tracks = map(int, trck.split("/"))
            else:
                track_no = int(trck)
        else:
            track_no, cd_tracks = None, None

        if "TPOS" in tags:
            tpos = int(tags["TPOS"])
        else:
            tpos = None

        if "TCON" in tags:
            match = re.match(r"(?P<genre_name>.*) \((?P<genre_id>\d+)\)", tags["TCON"])
            genre_name = match.group("genre_name")
            genre_id = int(match.group("genre_id"))
        else:
            genre_name, genre_id = None, None

        if "COMM" in tags:
            # format is like '()[]: Comment'
            comment = tags["COMM"].split(": ", 1)[1]
        else:
            comment = None

        return Tags(
            album_artist=tags.get("TPE2"),
            artist=tags.get("TPE1"),
            title=tags.get("TIT2"),
            album=tags.get("TALB"),
            year=year,
            track_no=track_no,
            cd_no=tpos,
            cd_tracks=cd_tracks,
            genre_id=genre_id,
            genre_name=genre_name,
            comment=comment,
            composer=tags.get("TCOM"),
            original_artist=tags.get("TOPE"),
            encoded_by=tags.get("TENC"),
        )
