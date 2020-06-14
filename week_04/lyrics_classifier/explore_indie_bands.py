import pandas as pd
import sys
import random
import os
import urllib.parse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


def artist_lyrics(df, artist):
    rows = df[df.index == artist]
    return rows["SONGS"], rows.index


def create_song(df, response2, response3):
    complete_lyrics, indices = artist_lyrics(df, response2)
    vector_df, cv = vectors_and_df(complete_lyrics, indices)
    words = vector_df.columns.values.tolist()
    weights = vector_df.mean(axis=0).values.tolist()
    return join_random_words(words, weights, n_words=int(response3))


def create_song_list(artists):
    """loads song texts from files and stores lyrics and artist in a dictionary"""
    songs_dict = {}
    for i, artist in enumerate(artists):
        directory = f"lyrics/{artist.lower().replace(' ', '-')}-lyrics"
        allfiles = os.listdir(directory)
        songs = []
        for song in allfiles:
            clean_song = urllib.parse.unquote_plus(song[:-4])
            songs.append(clean_song)
        songs.sort()
        songs_dict[artist] = songs
    return songs_dict


def get_df_slice(df, list_of_bands):
    df_list = []
    for band in list_of_bands:
        band_df = df.filter(like=band, axis=0)
        df_list.append(band_df)
    return pd.concat(df_list)


def join_random_words(words, weights, n_words=20):
    song = []
    for i in range(n_words):
        word = random.choices(words, weights=weights)  # weighted probabilites (unnormalized)
        song += word
    return ' '.join(song)


def merge_dfs(first_df, second_df):
    # merge and set band names as index
    df2 = pd.merge(first_df, second_df, how="left", left_on=first_df.index, right_on=second_df.index)
    df2 = df2.rename({"band_names": "BAND NAMES", "lyrics": "SONGS"}, axis=1)
    del df2["key_0"]
    df2.set_index("BAND NAMES", inplace=True)
    df2.set_index(df2.index.str.title(), inplace=True)
    # drop rows without lyrics
    return df2[df2.isna() == False]


def most_songs(df, amount=10):
    return df.groupby("BAND NAMES").count().sort_values(by="SONGS", ascending=False).head(amount)


def number_of_songs(df, artist):
    return int(df[df.index == artist.title()].count())


def predict_artist(df, n_artists=20):
    predict_df = get_df_slice(df, most_songs(df, n_artists).index.tolist())
    vector_df, cv = vectors_and_df(predict_df["SONGS"], predict_df.index)
    # Define features and target column
    X = vector_df
    y = vector_df.index
    model = "MultinomialNB"
    models_params = {
        "MultinomialNB": {"alpha": 0.005},
        "RandomForestClassifier": {
            "n_estimators": 500,
            "max_depth": 200,
            "max_features": "auto",
            "n_jobs": -1,
            "random_state": 1,
        },
        "LogisticRegression": {"C": 1e6},
    }
    m = MultinomialNB(**models_params[model])
    m.fit(X, y)
    song_lyrics = input("Insert text of song to be predicted: \n")
    print_prediction([song_lyrics], most_songs(df, n_artists).index.tolist(), cv, m)


def print_prediction(song_lyrics, list_of_bands, cv, m):
    """predicts artist of song based on artists in corpus"""
    # transform song into vector matrix
    new_song_vecs = cv.transform(song_lyrics)
    ynew = new_song_vecs.todense()
    # print results
    print(f"This classifier predicts the song to be written by:\n")
    artists_df = pd.DataFrame(m.predict_proba(ynew)[0], list_of_bands)
    artists_df = (artists_df.sort_values(by=0, ascending=False) * 100).round(1)
    artists_df = artists_df.rename(columns={0: "PREDICTION"})
    print(artists_df.head(10))
    confidence = m.predict_proba(ynew).max()
    if confidence > 0.9:
        confidence_word = "definitely"
    elif confidence > 0.7:
        confidence_word = "probably"
    else:
        confidence_word = "maybe"
    print(f"\nThis song is {confidence_word} by {artists_df.index.tolist()[0]}!")


def print_this(element):
    """prints elements for command line"""
    if element == "new_line":
        print("\n")
    elif element == "dash_line":
        print("----------------------------------------------------")
    elif element == "intro":
        print_this("new_line")
        print_this("dash_line")
        print("Indie Rock Classifier")
        print_this("dash_line")
        print_this("new_line")
        print("This program explores a data set of lyrics by 558 indie rock bands with a total amount of 16875 songs.")


def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def vectors_and_df(complete_lyrics, indices):
    """creates vectors for songs and returns dataframe with songs as word vectors by all artists"""
    cv = TfidfVectorizer()
    cv.fit(complete_lyrics)
    corpus_vecs = cv.transform(complete_lyrics)
    return pd.DataFrame(corpus_vecs.todense(), index=indices, columns=cv.get_feature_names()), cv


def main():
    exit = "No"
    # load data sets
    lyrics = pd.read_csv('songs_cleaned.csv', sep=';', index_col=0)
    bands = pd.read_csv("band_map.csv", index_col=0)
    df_bands = merge_dfs(lyrics, bands)
    artists = df_bands.index.unique().str.title().tolist()
    titles = create_song_list(artists)
    print_this("intro")
    while exit == "No":
        print_this("new_line")
        print("What do you want to do?")
        print_this("new_line")
        print("1) See list of bands by number of songs in data set")
        print("2) Look up band")
        print("3) Predict indie rock band")
        print("4) Exit")
        response = input("")
        if response == "1":
            print(most_songs(df_bands))
            response = input("To see more Bands, indicate number: ")
            try:
                print(most_songs(df_bands, int(response)))
            except ValueError:
                while not isint(response):
                    response = input("Please write a number (10, 50, 100..): ")
                print(most_songs(df_bands, int(response)))
        elif response == "2":
            band_exit = "no"
            while band_exit == "no":
                print("What do you want to do?")
                print("1) Look up list of songs")
                print("2) Get a randomly created song")
                print("3) Go back to main")
                response = input()
                if response == "1":
                    response2 = input("What band are you looking for?: ")
                    response2 = response2.title()
                    if response2 in artists:
                        print(f"There are {number_of_songs(df_bands,response2)} songs by {response2} in the data set.")
                        print("List of all songs: ")
                        print(f"{titles[response2]}")
                    else:
                        print(f"{response2} is not in this data set. Try: {most_songs(df_bands).index.tolist()}")
                    print_this("new_line")
                elif response == "2":
                    response2 = input("By what band shall the random song be inspired by?: ")
                    response2 = response2.title()
                    if response2 in artists:
                        response3 = ""
                        while not isint(response3):
                            response3 = input("How many words for the song?: ")
                        song = create_song(df_bands, response2, response3)
                        print(f"Random {response2} song goes like this: ")
                        print(f"{song}")
                        print_this("new_line")
                    else:
                        print("That band is not in the database.")
                elif response == "3":
                    band_exit = "yes"
                else:
                    pass
        elif response == "3":
            predict_artist(df_bands, 25)
        elif response == "4":
            sys.exit(0)
        else:
            pass


if __name__ == "__main__":
    main()
