import collections
import os

import pytest

from ..collector import (
    collect_audio_files,
    InvalidAudioDirectorException,
)

from .util import (
    FIXTURES_DIR,
    FAAC_FN,
    FLAC_FN,
    MP3_FN,
    VORBIS_FN,
    WAV_FN,

    mkaudiodir,
)


def test_basic_collector():
    with mkaudiodir(num_faac=5, other_ext_map={".jpg": 2, ".txt": 1}) as audio_dir:
        audio_files = collect_audio_files(audio_dir)
        assert len(audio_files) == 5
        for f in audio_files:
            assert f.path.endswith(".mp4")


def test_extension_case():
    with mkaudiodir(num_faac=5, other_ext_map={".MP4": 2}) as audio_dir:
        audio_files = collect_audio_files(audio_dir)
        assert len(audio_files) == 7

        for f in audio_files:
            assert f.path.endswith(".mp4") or f.path.endswith(".MP4")


def _assert_extensions(audio_files, **kwargs):
    """Expects kwargs to be ext=count (e.g. mp4=3)"""
    c = collections.defaultdict(int)
    for f in audio_files:
        # splitext()[1] gives extension starting with .
        c[os.path.splitext(f.path)[1][1:]] += 1
    assert c == kwargs


def test_multiple_audio_extensions():
    with mkaudiodir(num_faac=5, other_ext_map={".aac": 2}) as audio_dir:
        audio_files = collect_audio_files(audio_dir)
        assert len(audio_files) == 7
        _assert_extensions(audio_files, aac=2, mp4=5)


def test_heterogenous_dir():
    with mkaudiodir(num_faac=5, num_mp3=3) as audio_dir:
        with pytest.raises(InvalidAudioDirectorException):
            collect_audio_files(audio_dir, allow_heterogenous=False)

    with mkaudiodir(num_faac=5, num_mp3=3) as audio_dir:
        audio_files = collect_audio_files(audio_dir, allow_heterogenous=True)
        assert len(audio_files) == 8
        _assert_extensions(audio_files, mp4=5, mp3=3)


def test_empty_dir():
    with mkaudiodir(other_ext_map={".whatever": 2}) as audio_dir:
        with pytest.raises(InvalidAudioDirectorException):
            collect_audio_files(audio_dir)
