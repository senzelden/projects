import os


ARTISTS = ["Sonic-Youth", "Pavement", "Barbra-Streisand", "Peaches"]


def remove_duplicate_files(directory):
    """removes duplicate files from artist directory, not completely safe"""
    allfiles = os.listdir(directory)
    allfiles.sort()
    allfiles.sort(key=len)
    single_files = []
    removed_files = []
    for file in allfiles:
        for single_file in single_files:
            # a bit dangerous: if a track with the name "a" existed, every track starting with "a" would be deleted
            if file.lower().startswith(single_file[:-4].lower()):
                print(file, single_file)
                removed_files.append(file)
                os.remove(directory + "/" + file)
                break
        single_files.append(file)
    return removed_files

def main():
    for artist in ARTISTS:
        remove_duplicate_files(f"{artist.lower()}-lyrics")


if __name__ == "__main__":
    main()