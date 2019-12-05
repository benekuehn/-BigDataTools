import tweepy
import csv
from datetime import datetime

import re
import nltk
from nltk.tokenize import WordPunctTokenizer
from textblob import TextBlob

# Twitter API credentials
consumer_key = ""
consumer_secret = ""

# pass twitter credentials to tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

Collected_data = []

# name of twitter account
screen_name = ""

# number of tweets
tweets_max = 3000

# how many tweets per API request, default 200
tweets_per_call = 200

if tweets_max > tweets_per_call:
    print("More tweets then I can get per call")
    new_tweets = api.user_timeline(
        screen_name=screen_name, count=tweets_per_call, tweet_mode="extended")

elif tweets_max < tweets_per_call:
    print("Less tweets then I can get per call")
    tweets_per_call = tweets_max
    new_tweets = api.user_timeline(
        screen_name=screen_name, count=tweets_per_call, tweet_mode="extended")

Collected_data.extend(new_tweets)

oldest = Collected_data[-1].id - 1

tweets_collected = tweets_per_call
tweets_needed = tweets_max - tweets_collected

print("Still %s tweets to go" % tweets_needed)

while tweets_needed != 0:

    if tweets_needed < tweets_per_call:
        tweets_needed = tweets_per_call

    new_tweets = api.user_timeline(
        screen_name=screen_name, count=tweets_needed, max_id=oldest, tweet_mode="extended")

    # wait_on_rate_limit=True

    tweets_needed = tweets_needed - tweets_per_call

    print("Still %s tweets to go" % tweets_needed)

    Collected_data.extend(new_tweets)

    oldest = Collected_data[-1].id - 1


# print(Collected_data)

outtweets = [[tweet.id,
              tweet.user.screen_name,
              tweet.created_at,
              tweet.favorite_count,
              tweet.retweet_count,
              tweet.source,
              # tweet.full_text,
              # tweet.entities["user_mentions"], // Just in case to memorize how it works
              tweet.in_reply_to_user_id,
              # tweet.author.screen_name, // Just in case to memorize how it works
              ] for tweet in Collected_data if (datetime.now() - tweet.created_at).days > 1]  # Only processing tweets which are older then 1 day


i = 0
has_writer = False
for tweet in Collected_data:

    if (datetime.now() - tweet.created_at).days > 1:

        def clean_text(text):
            user_removed = re.sub(r'@[A-Za-z0-9]+', '', text)
            link_removed = re.sub('https?://[A-Za-z0-9./]+', '', user_removed)
            number_removed = re.sub('[^a-zA-Z]', ' ', link_removed)
            lower_case_tweet = number_removed.lower()
            tok = WordPunctTokenizer()
            words = tok.tokenize(lower_case_tweet)
            cleaned_text = (' '.join(words)).strip()
            return cleaned_text

        """
        # In order to use sentiment analysis, please uncomment this blog.
        # Further uncomment the headerrows polarity and subjectivity further down,
        # in the writer.writerow

        def get_text_sentiment(clean_text):
            # create TextBlob object of passed tweet text
            analysis = TextBlob(clean_text)
            # set sentiment
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
            return polarity, subjectivity

        """
        # sentiment analysis
        cleaned_text = clean_text(tweet.full_text)
        # polarity, subjectivity = get_text_sentiment(cleaned_text)
        # outtweets[i].append(polarity)
        # outtweets[i].append(subjectivity)

        # appends cleaned text, so without numbers, # etc, no need to clean it manually or in SAS
        outtweets[i].append(cleaned_text)

        if hasattr(tweet, "retweeted_status"):
            outtweets[i].append(1)
        else:
            outtweets[i].append(0)

        if tweet.is_quote_status == True:
            outtweets[i].append(1)
        else:
            outtweets[i].append(0)

        try:
            "url" in tweet.entities["urls"][0]
            outtweets[i].append(1)

        except IndexError:
            outtweets[i].append(0)

        if "media" in tweet.entities:
            if "media" in tweet.extended_entities:
                outtweets[i].append(1)
        else:
            outtweets[i].append(0)

        if "^" in tweet.full_text:
            writer = tweet.full_text.split("^", 1)[1]  # Splits Str at ^
            # Splits Str again after space to seperate only! two character abbreviation for writer
            writer = writer.split(" ", 1)[0]
            outtweets[i].append(writer)
            has_writer = True
        i += 1


# print(outtweets)

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")

file_name = "tweets_%s_%s.csv" % (screen_name, dt_string)

# helps to only include writer column in csv only when there is a writer like in my united case.
if has_writer == True:
    with open(file_name, "w",) as f:
        writer = csv.writer(f)
        writer.writerow(["tweet_id",
                         "username",
                         "created_at",
                         "favorite_count",
                         "retweet_count",
                         "source",
                         "in_reply_to_user_id",
                         # "polarity",
                         # "subjectivity",
                         "full_text",
                         "is_retweeted",
                         "is_quote_status",
                         "has_url",
                         "has_media",
                         "writer"]
                        )
        writer.writerows(outtweets)

    pass
else:
    with open(file_name, "w",) as f:
        writer = csv.writer(f)
        writer.writerow(["tweet_id",
                         "username",
                         "created_at",
                         "favorite_count",
                         "retweet_count",
                         "source",
                         "in_reply_to_user_id",
                         # "polarity",
                         # "subjectivity",
                         "full_text",
                         "is_retweeted",
                         "is_quote_status",
                         "has_url",
                         "has_media"]
                        )
        writer.writerows(outtweets)
    pass
