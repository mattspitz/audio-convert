import os

from ..audioformat import (
    MP3,
    Tags,
)

# http://doc.pytest.org/en/latest/tmpdir.html ?

FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
)

WAV_FN = os.path.join(FIXTURES_DIR, "makeitso.wav")
MP3_FN = os.path.join(FIXTURES_DIR, "makeitso.mp3")

def test_mp3_read_tags():
    tags = MP3.read_tags(MP3_FN)

    expected_tags = Tags(
        album_artist="Star Trek",
        artist="Jean-Luc Picard",
        title="Make It So",
        album="Sample Tracks",
        year=2016,
        track_no=4,
        cd_no=3,
        cd_tracks=22,
        genre_id=132,
        genre_name="Britpop",
        comment="Comment!",
        composer="Composer!",
        original_artist="Original Artist!",
        encoded_by="Encoded By!",
    )

    assert tags == expected_tags
