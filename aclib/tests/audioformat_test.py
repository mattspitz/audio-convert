import contextlib
import os
import shutil
import tempfile

from ..audioformat import (
    mp3,
    Tags,
)

# http://doc.pytest.org/en/latest/tmpdir.html ?

FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
)

MP3_BASENAME = "makeitso.mp3"

WAV_FN = os.path.join(FIXTURES_DIR, "makeitso.wav")
MP3_FN = os.path.join(FIXTURES_DIR, MP3_BASENAME)

FIXTURE_TAGS = Tags(
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

@contextlib.contextmanager
def _mp3_copy_fn():
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        shutil.copy2(MP3_FN, f.name)
        yield f.name

@contextlib.contextmanager
def _tmpdir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)

def test_mp3_encode():
    with _tmpdir() as tmpdir:
        mp3.encode([WAV_FN], tmpdir)
        mp3_fn = os.path.join(tmpdir, MP3_BASENAME)
        assert os.path.getsize(mp3_fn) > 0
        assert mp3.read_tags(mp3_fn) is None

def test_mp3_read_tags():
    tags = mp3.read_tags(MP3_FN)
    assert tags == FIXTURE_TAGS


def test_mp3_write_tags():
    """Ensures that we can edit all fields"""
    with _mp3_copy_fn() as fn:
        new_tags = Tags(
            album_artist=u"Different Star Trek",
            artist=u"Different Jean-Luc Picard",
            title=u"Different Make It So",
            album=u"Different Sample Tracks",
            year=2022,
            track_no=2,
            cd_no=2,
            cd_tracks=45,
            #genre_id=1,
            #genre_name=u"Classic Rock",
            comment=u"Different comment!",
            composer=u"Different composer!",
            original_artist=u"Different Original Artist!",
            encoded_by=u"Different Encoded By!",
        )

        mp3.write_tags(fn, new_tags)

        # TODO remove this genre hack when it's supported
        new_tags.genre_id = 132
        new_tags.genre_name = "BritPop"

        tags = mp3.read_tags(fn)
        assert tags == new_tags


def test_mp3_augment():
    """Ensures that we can clear tags and only update some in place"""
    with _mp3_copy_fn() as fn:
        new_tags = Tags(
            album_artist=u"hello",
            artist=u"", # clears the tag
            track_no=555,
            encoded_by=u"puppy dogs",
        )
        mp3.write_tags(fn, new_tags)
        tags = mp3.read_tags(fn)

        assert tags.album_artist == "hello"
        assert tags.artist is None
        # unchanged
        assert tags.title == u"Make It So"

        # only changing one of track_no/cd_tracks
        assert tags.track_no == 555
        assert tags.cd_tracks == 22

        # modifying the extra frameset
        assert tags.original_artist == u"Original Artist!"
        assert tags.encoded_by == u"puppy dogs"


def test_mp3_track_cd():
    with _mp3_copy_fn() as fn:
        # modify both track_no and cd_tracks
        new_tags = Tags(
            track_no=555,
            cd_tracks=600,
            cd_no=14,
        )
        mp3.write_tags(fn, new_tags)
        tags = mp3.read_tags(fn)
        assert tags.track_no == 555
        assert tags.cd_tracks == 600
        assert tags.cd_no == 14


def test_mp3_genre():
    """Ensures that we properly validate genres"""
    # TODO
    pass
