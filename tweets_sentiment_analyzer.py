import getTweets_and_clean as tweets
from elasticsearch import Elasticsearch
import sentiment_classifier as classifier
from elasticsearch import helpers


def analysis_tweets(df):
    df = classifier.analiys_tweets(df)
    return df


def import_data_ES_server(es_server, df):
    i = 0
    actions = []
    for index, row in df.iterrows():
        record = {
            "_index": "tweet_db",
            "_type": "_doc",
            "_source": {
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
    es = Elasticsearch(['http://ec2-52-91-233-44.compute-1.amazonaws.com:9200/'])

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
