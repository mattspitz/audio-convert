from . import (
    faac,
    flac,
    mp3,
    vorbis,
)

# map of extensions to the audio format modules
FMT_BY_EXT = {}
for module in (faac, flac, mp3, vorbis):
    for ext in module.EXTENSIONS:
        if ext in FMT_BY_EXT:
            raise Exception(
                "Duplicate extension found among audio formats: {} found in {} and {}".format(
                    ext,
                    module.__name__,
                    FMT_BY_EXT[ext].__name__,
                ))
        FMT_BY_EXT[ext] = module
