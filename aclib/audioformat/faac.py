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
    print output
    for line in output.split("\n"):
        match = re.match(r"(?P<key>.+?)(?:\s+)?:(?:\s+)?(?P<val>.+)", line)
        if match:
            tags[match.group("key")] = match.group("val")
    print tags

    artist = tags.get("Artist")

    def get_int(k, fallback_on_failure=False):
        if k not in tags:
            return None
        return maybe_convert_int(tags[k], fallback_on_failure=fallback_on_failure)

    track_no, cd_tracks = None, None
    if isinstance(tags.get("Track"), basestring):
        track_no, cd_tracks = map(int, tags.get("Track").split("/"))

    cd_no = None
    if isinstance(tags.get("Disc#"), basestring):
        cd_no, _ = map(int, tags.get("Disc#").split("/"))

    return Tags(
        artist=artist,
        album_artist=(
            tags.get("Album Artist")
                or artist
        ),

        title=tags.get("Tille"),
        album=tags.get("Album"),
        year=get_int("Date", fallback_on_failure=True),

        track_no=track_no,
        cd_no=cd_no,
        cd_tracks=cd_tracks,

        genre_id=None,
        genre_name=tags.get("'gen'"),

        comment=tags.get("Comment"),
        composer=tags.get("Composer"),
        original_artist=None,

        encoded_by=tags.get("Encoder"),
    )


def decode(fn, output_fn):
    subprocess.check_call([
        "faad",
        "-o", output_fn,
        fn,
    ])
