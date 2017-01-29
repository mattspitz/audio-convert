import subprocess

from .util import (
    vorbiscomment_to_tags,
)

EXTENSIONS = [".ogg", ".oga"]

def read_tags(fn):
    output = subprocess.check_output([
        "vorbiscomment",
        "-l",
        fn,
    ]).decode("utf8")

    return vorbiscomment_to_tags(output)


def decode(fn, output_fn):
    subprocess.check_call([
        "oggdec",
        "-o", output_fn,
        fn,
    ])
