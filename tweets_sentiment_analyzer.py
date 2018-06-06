import getTweets_and_clean as tweets
from textblob import TextBlob
from elasticsearch import Elasticsearch
from elasticsearch import helpers


def sentiment_tweet(text):
    result = TextBlob(text).sentiment
    if result.polarity == 0:
        sentiment = "netural"
    elif result.polarity > 0:
        sentiment = "possitive"
    else:
        sentiment = "negative"
    return sentiment, round(result.polarity, 2)


def analysis_tweets(df):
    scores = list()
    sentiments = list()
    for index, row in df.iterrows():
        sentiment, score = sentiment_tweet(row['text'])
        scores.append(score)
        sentiments.append(sentiment)

    df['sentiment'] = sentiments
    df['score'] = scores
    return df


def import_data_ES_server(es_server, df):
    i = 0
    actions = []
    for index, row in df.iterrows():
        record = {
            "_index": "tweet_data",
            "_type": "_doc",
            "_source": {
                "id": row['id'],
                "user": row['user'],
                "created_at": row['created_at'],
                "text": row['text'],
                "sentiment": row['sentiment'],
                "score": row['score']
            }
        }
        actions.append(record.copy())
        i += 1
        if i == 100:
            helpers.bulk(es_server, actions)
            actions = []
            i = 0
            print("Send: 100 records")


tweet_df = ''
if __name__ == '__main__':
    es = Elasticsearch(['http://35.183.6.252:9200/'])

    #  get and clean tweets
    print("Start getting data from twitter...")
    tweet_df = tweets.get_query_result()

    print("The raw data saved in raw_tweets.csv")
    print("Start analysis data twitter...")

    tweet_df = analysis_tweets(tweet_df)

    print("the analysed data saved in sentimental_tweets.csv")
    tweet_df.to_csv("sentimental_tweets.csv", index=False)

    print("import data to Elastic Search...")
    import_data_ES_server(es, tweet_df)
