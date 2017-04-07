import contextlib
import os
import shutil
import tempfile

from ..util import (
    mktempdir,
)

FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
)

FAAC_FN = os.path.join(FIXTURES_DIR, "makeitso.mp4")
FLAC_FN = os.path.join(FIXTURES_DIR, "makeitso.flac")
MP3_FN = os.path.join(FIXTURES_DIR, "makeitso.mp3")
VORBIS_FN = os.path.join(FIXTURES_DIR, "makeitso.ogg")

WAV_FN = os.path.join(FIXTURES_DIR, "makeitso.wav")

@contextlib.contextmanager
def mkaudiodir(num_faac=0, num_flac=0, num_mp3=0, num_vorbis=0, num_wav=0, other_ext_map=None):
    with mktempdir() as tmpdir:
        for count, fn, ext in (
            (num_faac, FAAC_FN, ".mp4"),
            (num_flac, FLAC_FN, ".flac"),
            (num_mp3, MP3_FN, ".mp3"),
            (num_vorbis, VORBIS_FN, ".ogg"),
            (num_wav, WAV_FN, ".wav"),
        ):
            for i in xrange(count):
                shutil.copy(fn, os.path.join(tmpdir, "{:03d}{}".format(i, ext)))

        if other_ext_map:
            for ext, count in other_ext_map.iteritems():
                for i in xrange(count):
                    # create empty file
                    path =  os.path.join(tmpdir, "{:03d}-other{}".format(i, ext))
                    assert not os.path.exists(path)
                    open(path, "w").close()
        yield tmpdir
