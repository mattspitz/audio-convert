from recordclass import recordclass

Tags = recordclass(
    "Tags",
    [
        "album_artist",
        "artist",
        "title",
        "album",
        "year",
        "track_no",
        "cd_no",
        "cd_tracks",
        "genre",
        "comment",
        "composer",
        "original_artist",
        "encoded_by",
    ],
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
    def encode(cls, fn_wav, output_fn):
        """Encodes the provided WAV file into the given output_fn"""
        raise NotImplementedError()

    @classmethod
    def decode(cls, fn, output_fn_wav):
        """Decodes the provided file into the given output_fn_wav"""
        raise NotImplementedError()


class MP3(BaseFormat):
    @classmethod
    def get_extension(cls):
        return "mp3"

    @classmethod
    def read_tags(cls, fn):
        pass
