import os
from fuzzywuzzy import fuzz


"""The strategy is to first remove files with brute method
 and then get remaining duplicates with fuzzywuzzy. This works
 reasonably well with song titles."""

ARTISTS = ["France Gall"]


# brute method
def remove_compare_beginning(directory):
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


# fine-grained method
def remove_fuzzywuzzy(directory):
    """removes duplicate files from artist directory, set ratio threshold according to problem"""
    allfiles = os.listdir(directory)
    allfiles.sort()
    allfiles.sort(key=len)
    single_files = [""]
    removed_files = []
    for file in allfiles:
        for single_file in single_files:
            ratio = fuzz.ratio(file[:-4].lower(), single_file[:-4].lower())
            partial_ratio = fuzz.partial_ratio(file[:-4].lower(), single_file[:-4].lower())
            token_sort_ratio = fuzz.token_sort_ratio(file[:-4].lower(), single_file[:-4].lower())
            token_set_ratio = fuzz.token_set_ratio(file[:-4].lower(), single_file[:-4].lower())
            # Token Set Ratio seems to be the best method to check similarity for this problem
            # if ratio > 80 sufficient for english titles
            if token_set_ratio >= 86:  # 86 works best for France Gall
                print(file, single_file)
                print("Ratio: ", ratio)
                print("Partial Ratio: ", partial_ratio)
                print("Token Sort Ratio: ", token_sort_ratio)
                print("Token Set Ratio: ", token_set_ratio)
                removed_files.append(file)
                os.remove(directory + "/" + file)
                break
        single_files.append(file)
    return removed_files

def main():
    for artist in ARTISTS:
        # make sure empty spaces in artist's name ar filled with dash:
        artist = artist.replace(" ", "-")
        remove_compare_beginning(f"{artist.lower()}-lyrics")
        remove_fuzzywuzzy(f"{artist.lower()}-lyrics")


if __name__ == "__main__":
    main()