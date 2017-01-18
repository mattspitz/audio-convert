class Tags(object):
    __slots__ = [
        "album_artist",
        "artist",
        "title",
        "album",
        "year",
        "track_no",
        "cd_no",
        "cd_tracks",
        "genre_id",
        "genre_name",
        "comment",
        "composer",
        "original_artist",
        "encoded_by",
    ]

    def __init__(
        self,
        album_artist=None,
        artist=None,
        title=None,
        album=None,
        year=None,
        track_no=None,
        cd_no=None,
        cd_tracks=None,
        genre_id=None,
        genre_name=None,
        comment=None,
        composer=None,
        original_artist=None,
        encoded_by=None,
    ):
        self.album_artist = album_artist
        self.artist = artist
        self.title = title
        self.album = album
        self.year = year
        self.track_no = track_no
        self.cd_no = cd_no
        self.cd_tracks = cd_tracks
        self.genre_id = genre_id
        self.genre_name = genre_name
        self.comment = comment
        self.composer = composer
        self.original_artist = original_artist
        self.encoded_by = encoded_by

    def __eq__(self, other):
        for k in self.__slots__:
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def __repr__(self):
        return (
            "Tags("
            + ", ".join("{}={}".format(k, getattr(self, k)) for k in self.__slots__)
            + ")"
        )


class BaseFormat(object):
    @classmethod
    def get_extension(cls):
        """Returns extension for this format (e.g. 'mp3')"""
        raise NotImplementedError()

    @classmethod
    def read_tags(cls, fn):
        """Returns Tags read from file"""
        raise NotImplementedError()

    @classmethod
    def write_tags(cls, fn, tags):
        """Writes given Tags to file"""
        raise NotImplementedError()

    @classmethod
    def decode(cls, fn, output_fn_wav):
        """Decodes the provided file into the given output_fn_wav"""
        raise NotImplementedError()
