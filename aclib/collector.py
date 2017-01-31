import collections
import os

from .audioformat import (
    faac,
    flac,
    mp3,
    vorbis,
    wav,
)

class InvalidAudioDirectorException(Exception):
    pass

class AudioFile(object):
    def __init__(self, audio_module, path):
        self.audio_module = audio_module
        self.path = path


    @property
    def ext(self):
        return os.path.splitext(self.path)[1].lower()


    def read_tags(self):
        return self.audio_module.read_tags(self.path)


    def write_tags(tags):
        if self.audio_module != mp3:
            raise NotImplementedError("Can only set tags for MP3s")
        return self.audio_module(self.path, tags)


    def decode(output_fn):
        self.audio_module.decode(self.path, output_fn)


    def __repr__(self):
        return "AudioFile({}, {})".format(self.audio_module.__name__, self.path)


def collect_audio_files(dir_fn):
    """Finds relevant AudioFiles in the given directory and returns them sorted by filename.

    Throws an Exception if a heterogenous collection of files is discovered."""
    modules_by_ext = {}
    for m in (faac, flac, mp3, vorbis, wav):
        for ext in m.EXTENSIONS:
            assert ext.startswith("."), "Extension {} in {} doesn't start with period.".format(ext, m)
            assert ext.lower() == ext, "Extension {} must be lowercase!".format(ext)
            assert ext not in modules_by_ext, "Extension {} defined in multiple modules: {} and {}.".format(ext, m, modules_by_ext[ext])
            modules_by_ext[ext] = m

    files_by_ext = collections.defaultdict(list)
    for fn in os.listdir(dir_fn):
        ext = os.path.splitext(fn)[1].lower()
        files_by_ext[ext].append(fn)

    files_by_audio_module = collections.defaultdict(list)
    for ext, files in files_by_ext.iteritems():
        if ext in modules_by_ext:
            module = modules_by_ext[ext]
            files_by_audio_module[module].extend(files)

    if not files_by_audio_module:
        raise InvalidAudioDirectorException(
            "No supported audio extensions found in {}. Valid extensions {}".format(
                dir_fn,
                sorted(modules_by_ext.keys()),
            )
        )

    if len(files_by_audio_module) > 1:
        raise InvalidAudioDirectorException(
            "Heterogenous audio types found in {}, where exactly one is allowed. Audio types found: {}".format(
                dir_fn,
                ", ".join(m.__name__ for m in files_by_audio_module.keys()),
            )
        )

    module, fns = files_by_audio_module.items()[0]
    return [
        AudioFile(module, os.path.join(dir_fn, path))
        for path in sorted(fns)
    ]
