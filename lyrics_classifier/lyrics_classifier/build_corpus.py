import os
import spacy
import pandas as pd


# Set artists you want to train on
ARTISTS = [
    "Peaches",
    "Barbra Streisand",
    "Britney Spears",
]


# helper function for corpus creation
def clean_my_song(song, model):
    # parse the song through the spacy model
    tokenised_song = model(song)
    clean_song = ""
    # loop through words, drop stop words
    for word in tokenised_song:
        if not word.is_stop:
            clean_song += word.lemma_ + " "
    # return the lemmatized version to the call
    return clean_song.strip()


def create_lyrics_corpus(artists, lang_model):
    """loads song texts from files and stores lyrics and artist index in seperate lists"""
    complete_lyrics = []
    indices = []
    for i, artist in enumerate(artists):
        directory = f"lyrics/{artist.lower().replace(' ', '-')}-lyrics"
        allfiles = os.listdir(directory)
        all_lyrics = []
        for file in allfiles:
            with open(directory + "/" + file, "r", encoding="utf-8") as f:
                song_lyrics = f.read()
                all_lyrics.append(clean_my_song(song_lyrics, lang_model))
        indices += [i] * len(all_lyrics)
        print(artist, len(all_lyrics))
        complete_lyrics += all_lyrics
    return complete_lyrics, indices


def main():
    # Load language model for cleaning
    lang_model = spacy.load("en_core_web_md")
    # Store lists into variables, print out number of songs by artist
    complete_lyrics, indices = create_lyrics_corpus(ARTISTS, lang_model)
    df = pd.DataFrame(data=complete_lyrics, index=indices)
    df.to_csv('songs.csv', sep=';')


if __name__ == "__main__":
    main()
