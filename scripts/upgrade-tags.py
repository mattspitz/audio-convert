import os
import sys

import eyed3

# Test unicode
# Skip "various artists"
# Skip non-MP3s

# Adding album artist

# blow up if we're missing...
    # CD disc number
    # year
    # artist
    # title
    # track num
    # all tracks

# save(version=ID3_V2_4, preserve_file_time=True)

def main():
    for d in sys.argv[1:]:
        process_dir(d)

def process_dir(d):
    if "Orchard Lounge" in d:
        return

    for fn in sorted(os.listdir(d)):
        path = os.path.join(d, fn)
        if not path.endswith("mp3"):
            continue

        f = eyed3.load(path)

        print f.tag.version, path
        VA = ("Various Artists" in d) or (f.tag.album_artist == "Various Artists")

        # validate
        assert f.tag.artist, path
        assert f.tag.title, path
        assert f.tag.album, path
        assert f.tag.best_release_date.year, path
        assert f.tag.track_num[0], "track_no {}".format(path)
        assert f.tag.track_num[1], "cd_tracks {}".format(path)
        assert f.tag.disc_num[0], "tpos {}".format(path)

        # add missing album artist?
        changed = (f.tag.version != eyed3.id3.ID3_V2_4)
        if not VA and not f.tag.album_artist:
            print "\tadding album artist"
            f.tag.album_artist = f.tag.artist
            changed = True

        if changed:
            raise
            f.tag.save(version=eyed3.id3.ID3_V2_4, preserve_file_time=True)
            print "\tsaved"
        else:
            print "\tunchanged!"

if __name__ =="__main__":
    main()
