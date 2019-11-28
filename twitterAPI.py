import tweepy
import csv
from datetime import datetime

# Twitter API credentials
consumer_key = ""
consumer_secret = ""

# pass twitter credentials to tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

Collected_data = []

#name of twitter account
screen_name = ""

#number of tweets
tweets_max = 3000

#how many tweets per API request, default 200
tweets_per_call = 200

if tweets_max > tweets_per_call:
    new_tweets = api.user_timeline(
        screen_name=screen_name, count=tweets_per_call, tweet_mode="extended")

elif tweets_max < tweets_per_call:
    tweets_per_call = tweets_max
    new_tweets = api.user_timeline(
        screen_name=screen_name, count=tweets_per_call, tweet_mode="extended")

Collected_data.extend(new_tweets)

oldest = Collected_data[-1].id - 1

tweets_collected = tweets_per_call
tweets_needed = tweets_max - tweets_collected

while tweets_needed != 0:

    if tweets_needed < tweets_per_call:
        tweets_needed = tweets_per_call

    new_tweets = api.user_timeline(
        screen_name=screen_name, count=tweets_needed, max_id=oldest, tweet_mode="extended")

    tweets_needed = tweets_needed - tweets_per_call

    print(tweets_collected)

    Collected_data.extend(new_tweets)

    oldest = Collected_data[-1].id - 1

outtweets = [[tweet.id,
              tweet.user.screen_name,
              tweet.created_at,
              tweet.favorite_count,
              tweet.retweet_count,
              tweet.retweeted,
              tweet.source,
              tweet.text,
              hash(tweet.in_reply_to_screen_name) % (10 ** 8)
             ] for tweet in Collected_data]

i = 0

for tweet in Collected_data:
    if "media" in tweet.entities:
        if "media" in tweet.extended_entities:
            outtweets[i].append(tweet.extended_entities["media"][0]["type"])

    i += 1

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")

file_name = "tweets_%s_%s.csv" % (screen_name, dt_string)

with open(file_name, "w",) as f:
    writer = csv.writer(f)
    writer.writerow(["tweet_id",
                     "username",
                     "created_at",
                     "favorites",
                     "retweets",
                     "retweeted",
                     "source",
                     "text",
                     "in_reply_to_screen_name",
                     "media_type"])
    writer.writerows(outtweets)

pass
