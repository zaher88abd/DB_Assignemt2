import nltk
from nltk.corpus import sentiwordnet as swn
import numpy as np


def analiys_tweets(df):
    nltk.download('sentiwordnet')
    nltk.download('wordnet')
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    # nltk.download('stopwords')
    # stop_words = list(get_stop_words('en'))  # About 900 stopwords
    # nltk_words = list(stopwords.words('english'))

    scores = list()
    sentiments = list()
    df = df[df['text'].notnull()]
    for index, row in df.iterrows():
        text = row['text']
        text = text.split()
        text = ' '.join(text)
        text_tokens = nltk.word_tokenize(text)
        tagged_text = nltk.pos_tag(text_tokens)
        token_count = pos_score = neg_score = obj_score = 0
        for word, tag in tagged_text:
            ss_set = None
            if 'NN' in tag and len(list(swn.senti_synsets(word, 'n'))) >= 1:
                ss_set = list(swn.senti_synsets(word, 'n'))[0]
            elif 'VB' in tag and len(list(swn.senti_synsets(word, 'v'))) >= 1:
                ss_set = list(swn.senti_synsets(word, 'v'))[0]
            elif 'JJ' in tag and len(list(swn.senti_synsets(word, 'a'))) >= 1:
                ss_set = list(swn.senti_synsets(word, 'a'))[0]
            elif 'RB' in tag and len(list(swn.senti_synsets(word, 'r'))) >= 1:
                ss_set = list(swn.senti_synsets(word, 'r'))[0]
            if ss_set:
                pos_score += ss_set.pos_score()
                neg_score += ss_set.neg_score()
                obj_score += ss_set.obj_score()
            token_count += 1

        norm_obj_score = round(float(obj_score) / token_count, 2)
        norm_pos_score = round(float(pos_score) / token_count, 2)
        norm_neg_score = round(float(neg_score) / token_count, 2)

        scores_arr = np.array([norm_obj_score, norm_pos_score, norm_neg_score])
        final_score = 0
        sentiment = ''
        if scores_arr.argmax() == 0:
            final_score = scores_arr[0]
            sentiment = 'natural'
        elif scores_arr.argmax() == 1:
            final_score = scores_arr[1]
            sentiment = 'positive'
        else:
            final_score = scores_arr[2]
            sentiment = 'negative'

        scores.append(final_score)
        sentiments.append(sentiment)

    df['score'] = scores
    df['sentiment'] = sentiments

    return df
# https: // github.com / dipanjanS / text - analytics -
# with-python / blob / master / Chapter - 7 / sentiment_analysis_unsupervised_lexical.py
# https: // stackoverflow.com / questions / 5486337 / how - to - remove - stop - words - using - nltk - or -python
