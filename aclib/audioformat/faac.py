import re
import subprocess

from .util import (
    maybe_convert_int,
    Tags,
)

EXTENSIONS = [".m4a", ".mp4", ".aac"]

def read_tags(fn):
    output = subprocess.check_output([
        "faad",
        "--info",
        fn,
    ], stderr=subprocess.STDOUT).decode("utf8", "ignore")

    tags = {}
    for line in output.split("\n"):
        match = re.match(r"(?P<key>\w+): (?P<val>.+)", line)
        if match:
            tags[match.group("key")] = match.group("val")

    artist = tags.get("artist")

    def get_int(k, fallback_on_failure=False):
        if k not in tags:
            return None
        return maybe_convert_int(tags[k], fallback_on_failure=fallback_on_failure)

    return Tags(
        artist=artist,
        album_artist=(
            tags.get("album_artist")
                or artist
        ),

        title=tags.get("title"),
        album=tags.get("album"),
        year=get_int("date", fallback_on_failure=True),

        track_no=get_int("track"),
        cd_no=get_int("disc"),
        cd_tracks=get_int("totaltracks"),

        genre_id=None,
        genre_name=tags.get("genre"),

        comment=tags.get("comment"),
        composer=tags.get("writer"),
        original_artist=None,

        encoded_by=tags.get("tool"),
    )


def decode(fn, output_fn):
    subprocess.check_call([
        "faad",
        "-o", output_fn,
        fn,
    ])
