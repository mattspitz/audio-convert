import contextlib
import shutil
import tempfile

class InvalidDiscTrackException(Exception):
    # thrown when an invalid disc/track combination is fed to get_track_filename_representation
    pass

def get_track_filename_representation(disc_num, track_num, num_discs, num_tracks):
    if num_tracks >= 100:
        raise InvalidDiscTrackException("Can't parse more than 99 tracks. Got {}.".format(num_tracks))

    if track_num > num_tracks:
        raise InvalidDiscTrackException("Track number ({}) greater than total number of track ({})!".format(track_num, num_tracks))

    if disc_num > num_discs:
        raise InvalidDiscTrackException("Disc number ({}) greater than total number of discs ({})!".format(disc_num, num_discs))

    if num_discs >= 10:
        return "{:02d}{:02d}".format(disc_num, track_num)
    elif num_discs > 1:
        return "{:d}{:02d}".format(disc_num, track_num)
    else:
        return "{:02d}".format(track_num)

@contextlib.contextmanager
def mktempdir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


