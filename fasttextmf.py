import re  # library for regular expression operations
# import string  # for string operations
# import time
import os

import fasttext
# import numpy as np
import pandas as pd
import spacy
import spacy.cli
from metaflow import FlowSpec, step
# from nltk.stem import PorterStemmer
# from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
from text_preprocessing import (
    # check_spelling,
    expand_contraction,
    normalize_unicode,
    preprocess_text,
    remove_number,
    remove_punctuation,
    remove_special_character,
    remove_stopword,
    to_lower,
)

import logging

def clean_data(text_pro, load_spacy_model):
    text_pro = re.sub("<[^>]*>", " ", text_pro)
    emoticons = re.findall("(?::|;|=)(?:-)?(?:\)|\(|D|P)", text_pro)
    doc = load_spacy_model(text_pro)
    # text = " ".join([token.lemma_ for token in doc])
    preprocess_functions = [
        to_lower,
        remove_special_character,
        remove_number,
        normalize_unicode,
        remove_punctuation,
        expand_contraction,
        remove_stopword,
    ]
    preprocessed_text = preprocess_text(text_pro, preprocess_functions)
    # preprocessed_text = [porter.stem(word.strip()) for word in preprocessed_text.split() if (len(word)>1)]
    if emoticons:
        return preprocessed_text + " " + "".join(emoticons)
    else:
        return preprocessed_text

def add_label(df):
    rows = []
    for row in df.iterrows():
        if row[1][1] == "negative":
            text = "__label__NEGATIVE "
        else:
            text = "__label__POSITIVE "
        row[1][0] = text + row[1][0]
        rows.append(row[1][0])
    df = pd.DataFrame({"text": rows})
    return df


class HelloFlow(FlowSpec):

    logging.basicConfig(format="%(levelname)s: %(message)s")
    logger = logging.getLogger("mylogger")
    logger.setLevel("WARNING")

    @step
    def start(self):

        print("Metaflow is starting.")
        self.next(self.load_data)

    @step
    def load_data(self):

        self.df = pd.read_csv("data/fasttext/movie_data.csv")
        print(self.df.shape)

        print("INFO: data loaded")
        self.next(self.clean_data)

    @step
    def clean_data(self):

        spacy.cli.download("en_core_web_sm")
        load_spacy_model = spacy.load("en_core_web_sm", disable=["parser", "ner"])

        print(self.df.loc[0, 'review'])

        # processing each review into a list of stemmed tokens
        self.df["review_processed"] = self.df["review"].apply(
            lambda x: clean_data(x, load_spacy_model)
        )
        self.df.to_csv("data/fasttext/clean_movie_data.csv", index=False)

        print("INFO: data cleaned and saved")
        self.next(self.transform_data)

    @step
    def transform_data(self):

        # self.df = pd.read_csv("data/fasttext/clean_movie_data.csv")
        print(self.df.shape)

        X = self.df['review_processed']
        y = self.df['sentiment']

        # train/test split is 80/20, with the same number of positive
        # and negative reviews in both subsets (stratified)

        X_train, self.X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify = y)
        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=42, stratify = y_train)

        X_train = pd.concat([X_train, y_train], axis=1).reset_index(drop=True)
        X_val = pd.concat([X_val, y_val], axis=1).reset_index(drop=True)
        self.X_test = pd.concat([self.X_test, y_test], axis=1).reset_index(drop=True)

        print(X_train.shape)
        print(X_val.shape)
        print(self.X_test.shape)

        df_train = X_train.copy()
        df_val = X_val.copy()
        df_test= self.X_test.copy()

        self.df_train = add_label(df_train)
        self.df_val = add_label(df_val)
        self.df_test = add_label(df_test)


        print("INFO: data transformed")
        self.next(self.save_data)

    @step
    def save_data(self):

        self.df_train.to_csv(
            "data/fasttext/train.csv", header=None, index=False, columns=["text"]
        )

        self.df_val.to_csv(
            "data/fasttext/val.csv", header=None, index=False, columns=["text"]
        )
        
        self.df_test.to_csv(
            "data/fasttext/test.csv", header=None, index=False, columns=["text"]
        )

        print("INFO: data saved")
        self.next(self.training_model)

    @step
    def training_model(self):

        print("INFO: starting training...")

        model = fasttext.train_supervised(
            input="data/fasttext/train.csv",
            autotuneValidationFile="data/fasttext/val.csv",
            autotuneDuration=300 * 1,
        )

        model.save_model("models/fasttext_model.bin")

        print(model.labels)

        print("INFO: model trained and saved")
        self.next(self.evaluate_model)

    @step
    def evaluate_model(self):

        model = fasttext.load_model("models/fasttext_model.bin")
        results = model.test("data/fasttext/test.csv")
        print(results)

        print(f"Test Samples: {results[0]} Precision : {results[1]*100:2.4f}")

        self.X_test['prediction'] = 'negative'

        for i in range(self.X_test.shape[0]):
            value = (
                'negative'
                if model.predict(self.X_test.loc[i, "review_processed"])[0][0]
                == "__label__NEGATIVE"
                else 'positive'
            )
            self.X_test.loc[i, "prediction"] = value

        print(self.X_test.loc[0,"prediction"])
        print(self.X_test.loc[0,"sentiment"])

        # provera accuracy
        print(f'''Accuracy:  {(self.X_test["prediction"] == self.X_test["sentiment"]).sum() / self.X_test.shape[0] * 100}''')

        print("INFO: model evaluated")
        self.next(self.end)

    @step
    def end(self):

        print("Metaflow is all done.")


if __name__ == "__main__":

    HelloFlow()