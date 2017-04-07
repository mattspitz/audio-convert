# -*- coding: utf8 -*-

import contextlib
import os
import shutil
import tempfile

from .util import (
    FAAC_FN,
    FLAC_FN,
    MP3_FN,
    VORBIS_FN,
    WAV_FN,
)

from ..audioformat import (
    faac,
    flac,
    mp3,
    vorbis,
    wav,
)
from ..audioformat.util import (
    Tags,
)

from ..util import (
    mktempdir,
)

FAAC_FIXTURE_TAGS = Tags(
    album_artist=u"Star Trek",
    artist=u"Jean-Luç Picard",
    title=u"Make It So",
    album=u"Sample Tracks",
    year=2016,
    track_no=4,
    cd_no=3,
    cd_tracks=22,
    genre_name=u"BritPop",
    comment=u"¡¡¡Comment!!!",
    composer=u"Composer!",
    encoded_by=u"Encoded By!",
)
FLAC_FIXTURE_TAGS = VORBIS_FIXTURE_TAGS = FAAC_FIXTURE_TAGS.copy(
    original_artist=u"Original Artist!",
)

MP3_FIXTURE_TAGS = VORBIS_FIXTURE_TAGS.copy(
    genre_id=132,
)

def _fixture_copy_gen(suffix, base_fn):
    @contextlib.contextmanager
    def f():
        with tempfile.NamedTemporaryFile(suffix=suffix) as f:
            shutil.copy2(base_fn, f.name)
            yield f.name
    return f

_mp3_copy_fn = _fixture_copy_gen(".mp3", MP3_FN)
_faac_copy_fn = _fixture_copy_gen(".mp4", FAAC_FN)
_flac_copy_fn = _fixture_copy_gen(".flac", FLAC_FN)
_vorbis_copy_fn = _fixture_copy_gen(".ogg", VORBIS_FN)


def test_mp3_encode():
    with mktempdir() as tmpdir:
        mp3.encode([WAV_FN], tmpdir)
        encoded_fn = os.path.join(tmpdir, "makeitso.mp3")
        assert os.path.getsize(encoded_fn) > 0
        assert mp3.read_tags(encoded_fn) is None

def test_mp3_read_tags():
    tags = mp3.read_tags(MP3_FN)
    assert tags == MP3_FIXTURE_TAGS


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
            genre_id=1,
            genre_name=u"Classic Rock",
            comment=u"Different comment!",
            composer=u"Different composer!",
            original_artist=u"Different Original Artist!",
            encoded_by=u"Different Encoded By!",
        )
        mp3.write_tags(fn, new_tags)

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
    def _validate(
        set_genre_id, set_genre_name,
        expected_genre_id, expected_genre_name
    ):
        with _mp3_copy_fn() as fn:
            mp3.write_tags(
                fn,
                Tags(
                    genre_id=set_genre_id,
                    genre_name=set_genre_name,
                ),
            )
            tags = mp3.read_tags(fn)
            assert tags.genre_id == expected_genre_id
            assert tags.genre_name == expected_genre_name

    # invalid genre_id
    _validate(99999999, None, None, None)

    # invalid genre_id, valid genre (fills in id)
    _validate(99999999, u"Rock", 17, u"Rock")

    # genre_id trumps genre_name
    _validate(17, u"BritPop", 17, u"Rock")

    # fall back on genre_name, anyway
    _validate(99999999, u"Whatever", None, u"Whatever")

    # only genre_name
    _validate(None, u"Whatever", None, u"Whatever")
    _validate(None, u"Rock", 17, u"Rock")


def test_faac_read_tags():
    tags = faac.read_tags(FAAC_FN)
    assert tags == FAAC_FIXTURE_TAGS


def test_flac_read_tags():
    tags = flac.read_tags(FLAC_FN)
    assert tags == FLAC_FIXTURE_TAGS


def test_vorbis_read_tags():
    tags = vorbis.read_tags(VORBIS_FN)
    assert tags == VORBIS_FIXTURE_TAGS


def test_wav_read_tags():
    tags = wav.read_tags(WAV_FN)
    # no tags for wav files
    assert tags == Tags()


def _gen_end_to_end(input_fn, read_tags, decode):
    def f():
        with mktempdir() as tmpdir:
            input_tags = read_tags(input_fn)

            wav_fn = os.path.join(tmpdir, "decoded.wav")
            decode(input_fn, wav_fn)
            assert os.path.getsize(wav_fn) > 0

            mp3.encode([wav_fn], tmpdir)

            mp3_fn = os.path.join(tmpdir, "decoded.mp3")
            mp3.write_tags(mp3_fn, input_tags)

            mp3_tags = mp3.read_tags(mp3_fn)

            if input_tags.genre_name:
                # we're smart enough to deduce genre just based on the name,
                # even if earlier formats didn't encode this information
                expected_tags = input_tags.copy(genre_id=132)
            else:
                expected_tags = input_tags

            assert mp3_tags == expected_tags
    return f


test_faac_end_to_end = _gen_end_to_end(FAAC_FN, faac.read_tags, faac.decode)
test_flac_end_to_end = _gen_end_to_end(FLAC_FN, flac.read_tags, flac.decode)
test_vorbis_end_to_end = _gen_end_to_end(VORBIS_FN, vorbis.read_tags, vorbis.decode)
test_wav_end_to_end = _gen_end_to_end(WAV_FN, wav.read_tags, wav.decode)
