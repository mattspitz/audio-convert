import os
import sys

import eyed3

# Ensure that we set "recording date", not "original release date" as the year.
# Plex for whatever reason goes for the former, and we've been setting the latter

def update_year(fn):
    if not fn.endswith("mp3"):
        return

    f = eyed3.load(os.path.abspath(fn))

    recording_date = f.tag.recording_date

    rgad = f.tag.frame_set["RGAD"]

    if not recording_date:
        raise Exception("uh oh")
    if f.tag.release_date and not f.tag.original_release_date and not rgad:
        return

    f.tag.original_release_date = None
    f.tag.release_date = recording_date
    f.tag.frame_set.pop("RGAD", "")

    print fn
    raise # don't actually run this
    f.tag.save(preserve_file_time=True)

def main():
    for fn in sys.argv[1:]:
        update_year(fn)

if __name__ == "__main__":
    main()
