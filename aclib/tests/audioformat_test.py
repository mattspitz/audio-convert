import os

from ..audioformat import MP3

# http://doc.pytest.org/en/latest/tmpdir.html ?

FIXTURES_DIR = os.path.join(
    os.path.dirname(__name__),
    "fixtures",
)

WAV_FN = os.path.join(FIXTURES_DIR, "makeitso.wav")
MP3_FN = os.path.join(FIXTURES_DIR, "makeitso.mp3")

def test_mp3_read_tags():
    MP3.read_tags(MP3_FN)
