class Tags(dict):
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
        super(Tags, self).__init__()

        self.album_artist = album_artist
        self.artist = artist
        self.title = title
        self.album = album
        self.year = maybe_convert_int(year, fallback_on_failure=True)
        self.track_no = maybe_convert_int(track_no, fallback_on_failure=True)
        self.cd_no = maybe_convert_int(cd_no, fallback_on_failure=True)
        self.cd_tracks = maybe_convert_int(cd_tracks, fallback_on_failure=True)
        self.genre_id = maybe_convert_int(genre_id, fallback_on_failure=True)
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
        def get_slot(k):
            v = getattr(self, k)
            if isinstance(v, unicode):
                v = v.encode("ascii", "replace")
            if isinstance(v, basestring):
                return '"{}"'.format(v)
            return v

        return (
            "Tags("
            + ", ".join("{}={}".format(k, get_slot(k)) for k in self.__slots__)
            + ")"
        )


    def copy(self, **kwargs):
        """Make a copy of this object, optionally overriding any fields"""
        assert all(k in self.__slots__ for k in kwargs)

        new_vals = {
            # kwargs take precedence
            k: kwargs.get(k, getattr(self, k))
            for k in self.__slots__
        }
        return Tags(**new_vals)

    def to_dict(self):
        return {
            k: getattr(self, k)
            for k in self.__slots__
        }


def maybe_convert_int(v, fallback_on_failure=False):
    try:
        return int(v)
    except (TypeError, ValueError):
        if fallback_on_failure:
            return v
        raise


def vorbiscomment_to_tags(vorbiscomment_output):
    """Takes the line-by-line KEY=VALUE output from Vorbis-style comments (unicode) and converts it to a Tags() object"""
    assert isinstance(vorbiscomment_output, unicode)

    tags = {}
    for line in vorbiscomment_output.split("\n"):
        if line and "=" in line:
            key, value = line.split("=", 1)
            tags[key.lower()] = value

    artist = tags.get("artist")

    def get_int(k, fallback_on_failure=False):
        if k not in tags:
            return None
        return maybe_convert_int(tags[k], fallback_on_failure=fallback_on_failure)


    return Tags(
        artist=artist,
        album_artist=(
            tags.get("albumartist")
                or tags.get("album_artist")
                or tags.get("album-artist")
                or artist
        ),

        title=tags.get("title"),
        album=tags.get("album"),
        year=get_int("date", fallback_on_failure=True),

        track_no = get_int("tracknumber", fallback_on_failure=True),
        cd_no = get_int("discnumber", fallback_on_failure=True),
        cd_tracks = get_int("tracktotal", fallback_on_failure=True),

        genre_id=None,
        genre_name=tags.get("genre"),

        comment=tags.get("description"),
        composer=tags.get("composer"),
        original_artist=tags.get("performer"),

        encoded_by=(
            tags.get("encodedby")
            or tags.get("encoded-by")
        ),
    )
