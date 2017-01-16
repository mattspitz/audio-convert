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
        album_artist=u"Star Trek",
        artist=u"Jean-Luc Picard",
        title=u"Make It So",
        album=u"Sample Tracks",
        year=2016,
        track_no=4,
        cd_no=3,
        cd_tracks=22,
        genre_id=132,
        genre_name=u"BritPop",
        comment=u"Comment!",
        composer=u"Composer!",
        original_artist=u"Original Artist!",
        encoded_by=u"Encoded By!",
    )

    assert tags == expected_tags
