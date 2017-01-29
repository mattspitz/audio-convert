#!/usr/bin/python

import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Standardize your audio encoding and tagging!",
    )

    # force these tags (optional)
    parser.add_argument("--artist")
    parser.add_argument("--album_artist")
    parser.add_argument("--album")
    parser.add_argument("--year")
    parser.add_argument("--genre_name")
    parser.add_argument("--comment")
    parser.add_argument("--composer")
    parser.add_argument("--original_artist")
    parser.add_argument("--encoded_by")

    parser.add_argument(
        "audio_dirs",
        metavar="AUDIO_DIR",
        nargs="+",
        help="Directories of audio to process non-recursively. Multiple directories will be interpreted as multiple discs and will be tagged CD=1,2,3,...",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # input: one or more directories (multiple directories -> multiple discs)

    # find all the non-MP3s; blow up if we have a heterogenous set of recognized filenames (FLAC and MP3, etc)

    # pull the tags and print them out (with pending changes, if necessary); user should hit enter to confirm (rerun to force tags)
    # infer #tracks and cd_number

    # if necessary, decode and convert files to MP3 (into a separate directory, <dir>/converted)

    # reapply tags (upgrade to ID3v2.4 regardless)

    # rename? maybe as a separate command...

    # Later...
        # - allow manual edits for in-place changes of track names, VA-discs, etc
        # - concurrency
        # - color output (colorama?)

if __name__ == "__main__":
    main()
