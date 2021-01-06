# adapted from: https://github.com/siangooding/cwi_2018/blob/master/Algorithm%20Application.ipynb


from sklearn.naive_bayes import GaussianNB
import scipy.stats as stats
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
import string
import numpy as np

# import feature frames

import pandas as pd

x = 'Wikipedia'

wikipedia_test_data = pd.read_pickle('pickled-dataframes/'+x+'_test_data')
wikipedia_training_data = pd.read_pickle(
    'pickled-dataframes/'+x+'_training_data')
wikipedia_test_data.name = x
wikipedia_training_data.name = x

x = 'News'

news_test_data = pd.read_pickle('pickled-dataframes/'+x+'_test_data')
news_training_data = pd.read_pickle('pickled-dataframes/'+x+'_training_data')
news_test_data.name = 'News'
news_training_data.name = 'News'

x = 'WikiNews'

wiki_test_data = pd.read_pickle('pickled-dataframes/'+x+'_test_data')
wiki_training_data = pd.read_pickle('pickled-dataframes/'+x+'_training_data')
wiki_test_data.name = x
wiki_training_data.name = x
lexicon = pd.read_table('lexicon', delim_whitespace=True,
                        names=('phrase', 'score'))
lexicon['phrase'] = lexicon['phrase'].apply(lambda x: str(x).lower())


class TextSelector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a single column from the data frame to perform additional transformations on
    Use on text columns in the data
    """

    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[self.key]


class NumberSelector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a single column from the data frame to perform additional transformations on
    Use on numeric columns in the data
    """

    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[[self.key]]


first_fixation = Pipeline([
    ('selector', NumberSelector(key='IA_FIRST_FIXATION_DURATION')),
    ('standard', StandardScaler())
])

words = Pipeline([
    ('selector', TextSelector(key='phrase')),
    ('vect', CountVectorizer())
])

word_length = Pipeline([
    ('selector', NumberSelector(key='length')),
    ('standard', StandardScaler())
])

dep_num = Pipeline([
    ('selector', NumberSelector(key='dep num')),
    ('standard', StandardScaler())
])


tag = Pipeline([
    ('selector', TextSelector(key='pos')),
    ('vect', CountVectorizer())
])

synonyms = Pipeline([
    ('selector', NumberSelector(key='synonyms')),
    ('standard', StandardScaler())
])

hypernyms = Pipeline([
    ('selector', NumberSelector(key='hypernyms')),
    ('standard', StandardScaler())
])

hyponyms = Pipeline([
    ('selector', NumberSelector(key='hyponyms')),
    ('standard', StandardScaler())
])

syllables = Pipeline([
    ('selector', NumberSelector(key='syllables')),
    ('standard', StandardScaler())
])

simple_wiki = Pipeline([
    ('selector', NumberSelector(key='simple_wiki')),
    ('standard', StandardScaler())
])

ogden = Pipeline([
    ('selector', NumberSelector(key='ogden')),
    ('standard', StandardScaler())
])
origin = Pipeline([
    ('selector', TextSelector(key='origin')),
    ('vect', CountVectorizer())
])

frequency = Pipeline([
    ('selector', NumberSelector(key='google frequency')),
    ('standard', StandardScaler())
])

subimdb = Pipeline([
    ('selector', NumberSelector(key='sub_imdb')),
    ('standard', StandardScaler())
])

n_gram_freq = Pipeline([
    ('selector', NumberSelector(key='ngram freq')),
    ('standard', StandardScaler())
])

# cald = Pipeline([
#                 ('selector', NumberSelector(key='cald')),
#                 ('standard', StandardScaler())
#                 ])


aoa = Pipeline([
    ('selector', NumberSelector(key='aoa')),
    ('standard', StandardScaler())
])
conc = Pipeline([
                ('selector', NumberSelector(key='conc')),
                ('standard', StandardScaler())
                ])
fam = Pipeline([
    ('selector', NumberSelector(key='fam')),
    ('standard', StandardScaler())
])
img = Pipeline([
    ('selector', NumberSelector(key='img')),
    ('standard', StandardScaler())
])
phon = Pipeline([
                ('selector', NumberSelector(key='phon')),
                ('standard', StandardScaler())
                ])

score = Pipeline([
    ('selector', NumberSelector(key='score')),
    ('standard', StandardScaler())
])


global feats
feats = FeatureUnion([  # ('ff',first_fixation),
    ('words', words),
    ('word_length', word_length),
    ('Tag', tag),
    ('dep_num', dep_num),
    ('hypernyms', hypernyms),
    ('hyponyms', hyponyms),
    ('synonyms', synonyms),
    ('Syllables', syllables),
    ('ogden', ogden),
    ('simple_wiki', simple_wiki),
    #('origin', origin),
    ('freq', frequency),
    ('subimdb', subimdb),
    # ('n_gram_freq',n_gram_freq),
    # ('cald', cald),
    ('aoa', aoa),
    ('conc', conc),
    ('fam', fam),
    ('img', img),
    ('phon', phon),
    ('score', score)
])

frames = [news_training_data, wikipedia_training_data, wiki_training_data]
total_training = pd.concat(frames)

frames = [wikipedia_test_data, wiki_test_data, news_test_data]
total_test = pd.concat(frames)

total_training = pd.merge(total_training, lexicon, on='phrase', how='left')
total_training.fillna(0.0, inplace=True)

total_test = pd.merge(total_test, lexicon, on='phrase', how='left')
total_test.fillna(0.0, inplace=True)

training_data = total_training
train_targets = training_data['complex_binary'].values

feature_processing = Pipeline([('feats', feats)])
feature_processing.fit_transform(training_data)

model = AdaBoostClassifier(n_estimators=5000, random_state=67)
pipeline = Pipeline([
    ('features', feats),
    ('classifier', model),
])

pipeline.fit(training_data, train_targets)


global model_stats
model_stats = pd.DataFrame(
    columns=['Data', 'Classifier', 'Precision', 'Recall', 'F-Score'])


def apply_algorithm(array):

    i = 0
    for x in array:

        test_data = x
        test_targets = test_data['complex_binary'].values

        test_predictions = pipeline.predict(test_data)

        accuracy = accuracy_score(test_targets, test_predictions)
        precision = precision_score(test_targets, test_predictions)
        recall = recall_score(test_targets, test_predictions)
        F_Score = f1_score(test_targets, test_predictions)

        model_stats.loc[len(model_stats)] = [i, (str(model))[
            :60], precision, recall, F_Score]
        # baseline_accuracies(test_targets)


apply_algorithm([total_test])  # with lexicon
model_stats


apply_algorithm([total_test])  # without lexicon
model_stats