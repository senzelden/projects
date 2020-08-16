from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from indie_bands import indie_bands
import pandas as pd



# Set artists
ARTISTS = indie_bands

# Set a sampling dictionary for smote
SAMPLING_DICT = {
    0: 300,
    2: 300
}

# Set SMOTE dict for final model
FULL_SET_SAMPLING_DICT = {
        0: 400,
        2: 400
    }

# Set parameters for models
MODELS_PARAMS = {
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

# Input Elton John's "Can you feel the love tonight" for prediction
unseen_song = [
    """
    There's a calm surrender
    To the rush of day
    When the heat of a rolling wave
    Can be turned away
    An enchanted moment
    And it sees me through
    It's enough for this restless warrior
    Just to be with you
    And can you feel the love tonight?
    It is where we are
    It's enough for this wide-eyed wanderer
    That we've got this far
    And can you feel the love tonight? (Tonight)
    How it's laid to rest?
    It's enough to make kings and vagabonds
    Believe the very best
    There's a time for everyone
    If they only learn
    That the twisting kaleidoscope
    Moves us all in turn
    There's a rhyme and reason
    To the wild outdoors
    When the heart of this star-crossed voyager
    Beats in time with yours
    And can you feel the love tonight? (Tonight)
    It is where we are
    It's enough for this wide-eyed wanderer
    That we've got this far
    And can you feel the love tonight? (Tonight)
    How it's laid to rest?
    It's enough to make kings and vagabonds
    Believe the very best
    It's enough to make kings and vagabonds
    Believe the very best
    """
]


def vectors_and_df(complete_lyrics, indices):
    """creates vectors for songs and returns dataframe with songs as word vectors by all artists"""
    cv = TfidfVectorizer(stop_words="english")
    cv.fit(complete_lyrics)
    corpus_vecs = cv.transform(complete_lyrics)
    return pd.DataFrame(corpus_vecs.todense(), index=indices, columns=cv.get_feature_names()), cv


def smote(Xtrain, ytrain, model, sampling_dict):
    """upsamples underrepresented classes and returns fitted model"""
    sms = SMOTE(sampling_strategy=sampling_dict, random_state=42)
    Xtrain_sms, ytrain_sms = sms.fit_resample(Xtrain, ytrain)
    model.fit(Xtrain_sms, ytrain_sms)
    return model


def train_models(Xtrain, Xtest, ytrain, ytest, models_params, smote_dict={}):
    """trains models with and without SMOTE on corpus and returns dataframe with scores"""
    scores = {}
    for model in models_params:
        if model == "LogisticRegression":
            m = LogisticRegression(**models_params[model])
        elif model == "RandomForestClassifier":
            m = RandomForestClassifier(**models_params[model])
        elif model == "MultinomialNB":
            m = MultinomialNB(**models_params[model])

        to_smote_m = m
        m.fit(Xtrain, ytrain)
        score_train = m.score(Xtrain, ytrain)
        score_test = m.score(Xtest, ytest)
        smote_model = smote(Xtrain, ytrain, to_smote_m, smote_dict)
        smote_score_train = smote_model.score(Xtrain, ytrain)
        smote_score_test = smote_model.score(Xtest, ytest)

        scores[f"{model}"] = {
            "params": models_params[model],
            "train score": score_train,
            "smote train score": smote_score_train,
            "test score": score_test,
            "smote test score": smote_score_test,
        }
    return pd.DataFrame(scores).T


def predict_artist(song, model, cv, artists):
    """predicts artist of song based on artists in corpus"""
    # transform song into vector matrix
    new_song_vecs = cv.transform(song)
    ynew = new_song_vecs.todense()

    print(f"This classifier predicts the song to be written by:\n")
    for i, artist in enumerate(artists):
        print(f"{artist}: {round(model.predict_proba(ynew)[0][i] * 100, 1)}%.")
    song_pred = model.predict(ynew)[0]
    confidence = model.predict_proba(ynew).max()
    if confidence > 0.9:
        confidence_word = "definitely"
    elif confidence > 0.7:
        confidence_word = "probably"
    else:
        confidence_word = "maybe"
    print(f"\nThis song is {confidence_word} by {artists[song_pred]}!")


def main():
    # Load dataframe from csv
    df = pd.read_csv('songs.csv', sep=';', index_col=0)
    # Store vectors in dataframe, keep cv for later prediction
    df_vectors, cv = vectors_and_df(df[0], df.index)
    # Define features and target column
    X, y = df_vectors, df_vectors.index
    # Split the data into train and test set
    Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size=0.2)
    df_scores = train_models(Xtrain, Xtest, ytrain, ytest, MODELS_PARAMS, SAMPLING_DICT)
    print(df_scores)
    # Train on most promising model
    model = "MultinomialNB"
    m = MultinomialNB(**MODELS_PARAMS[model])
    m = smote(X, y, m, FULL_SET_SAMPLING_DICT)
    m.score(X, y)
    # Make prediction
    predict_artist(unseen_song, m, cv, ARTISTS)


if __name__ == "__main__":
    main()
