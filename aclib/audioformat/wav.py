import shutil

from .util import (
    Tags,
)

EXTENSIONS = [".wav"]

def read_tags(fn):
    return Tags()


def decode(fn, output_fn):
    shutil.copy(fn, output_fn)
