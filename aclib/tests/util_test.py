import pytest

from .. import util

def test_get_trackfilename_representation():
    for disc_num, track_num, num_discs, num_tracks, expected in (
            (1, 1, 1, 12, "01"),
            (1, 1, 2, 12, "101"),
            (2, 1, 2, 12, "201"),
            (2, 11, 2, 12, "211"),
            (10, 5, 12, 12, "1005"),
            (1, None, 1, 1, "None"),

        ):
        assert util.get_track_filename_representation(disc_num, track_num, num_discs, num_tracks) == expected


    with pytest.raises(util.InvalidDiscTrackException):
        # disc_num > num_discs
        util.get_track_filename_representation(2, 1, 1, 10)

    with pytest.raises(util.InvalidDiscTrackException):
        # num_tracks >= 100
        util.get_track_filename_representation(1, 1, 1, 100)

    with pytest.raises(util.InvalidDiscTrackException):
        # track_num > num_tracks
        util.get_track_filename_representation(1, 11, 1, 10)
