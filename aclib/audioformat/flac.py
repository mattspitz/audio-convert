import subprocess

from .util import (
    vorbiscomment_to_tags,
)

def read_tags(fn):
    output = subprocess.check_output([
        "metaflac",
        "--no-utf8-convert",
        "--export-tags-to=-",
        fn,
    ]).decode("utf8")

    return vorbiscomment_to_tags(output)


def decode(fn, output_fn):
    subprocess.check_call([
        "flac",
        "-d", fn,
        "-o", output_fn,
    ])
