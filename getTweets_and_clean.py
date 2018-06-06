import tweepy
import json
import csv
import re
import pandas as pd

consumer_key = "GG1MmGFXWbVEvjAz5thB5EQDs"
consumer_secret = "NG0nsSsy0Iu29RKVr2z3hSiL4HcwcHievXfE8Qw4r6x77AdPd0"
access_key = "1002349562093363200-O5m7LI30kIMuruS9U2tCs06zza2711"
access_secret = "i0o8KPVxU6pIRcrmzW60vmpJ1CbS6oib9IXDt28tgpqXP"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


def get_profile(screen_name):
    try:
        # https://dev.twitter.com/rest/reference/get/users/show describes get_user
        user_profile = api.get_user(screen_name)
    except tweepy.error.TweepError as e:
        user_profile = json.loads(e.response.text)
    return user_profile


def get_trends(location_id):
    try:
        # https://developer.twitter.com/en/docs/trends/trends-forlocation/api-reference/get-trends-place.html
        trends = api.trends_place(location_id)
    except tweepy.error.TweepError as e:
        trends = json.loads(e.response.text)
    return trends


def get_tweets(query):
    try:
        tweets = api.search(query)

    except tweepy.error.TweepError as e:
        tweets = [json.loads(e.response.text)]
    return tweets

def get_query_result(query="black panther -filter:retweets"):
    with open('raw_tweets.csv', 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['id', 'user', 'created_at', 'text'])
        col = ['id', 'user', 'created_at', 'text']
        tweet_list = list()
        tw = tweepy.Cursor(api.search, q=query, lang='en', count=100).items()
        i = 0
        for tweet in tw:
            text = tweet.text
            text = str(text.encode('utf8'))
            text = text.replace("#", ' ')
            text = text.replace('\n', ' ')
            # remove bad unicode
            text = re.sub('[^(\x20-\x7F)]+', ' ', text)
            # remove @ssdfsdf
            text = re.sub(r'@[\w]+', " ", text)
            # remove &lt;
            text = re.sub(r'&[\w]+;', " ", text)
            # remove https
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', " ", text)
            text = text.strip()

            writer.writerow([tweet.id_str, tweet.user.screen_name, tweet.created_at, text])
            tweet_list.append([tweet.id_str, tweet.user.screen_name, tweet.created_at, text])
            i = i + 1
            if i == 1000:
                break
        return pd.DataFrame(columns=col, data=tweet_list)
