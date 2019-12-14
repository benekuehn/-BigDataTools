import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime

import re
import nltk
from nltk.tokenize import WordPunctTokenizer
from textblob import TextBlob

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
outtweets = []

username = "united"
amount_of_tweets = 15000  # minimum

file_name = "tweets_scraped_%s_%s.csv" % (username, dt_string)


# Text Cleaning
# by https://github.com/dzakyputra/sentweetbot/blob/master/main.py

def clean_text(text):
    user_removed = re.sub(r'@[A-Za-z0-9]+', '', text)
    link_removed = re.sub('https?://[A-Za-z0-9./]+', '', user_removed)
    number_removed = re.sub('[^a-zA-Z]', ' ', link_removed)
    lower_case_tweet = number_removed.lower()
    tok = WordPunctTokenizer()
    words = tok.tokenize(lower_case_tweet)
    cleaned_text = (' '.join(words)).strip()
    return cleaned_text


# Sentiment Analysis

def get_text_sentiment(clean_text):
    analysis = TextBlob(clean_text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    return polarity, subjectivity


# Safe scraped tweets to list of lists -> outtweets

def create_outtweets(timeline, source):
    for tweet in timeline:
        tweet_id = tweet["data-item-id"]
        username = tweet.find("span", {"class": 'username'}).text[1:]
        full_text = clean_text(tweet.select('p.tweet-text')[0].get_text())
        sentiment_value = get_text_sentiment(full_text)

        if sentiment_value[0] > 0:
            polarity = "positve"
        elif sentiment_value[0] < 0:
            polarity = "negative"
        else:
            polarity = "neutral"

        if sentiment_value[1] > 0.5:
            subjectivity = "subjective"
        else:
            subjectivity = "objective"

        created_at = datetime.fromtimestamp(int(tweet.find(
            "span", {"class": "_timestamp"}).attrs["data-time"]))
        favorite_count = int(tweet.find(
            "span", {"class": "ProfileTweet-action--favorite"}).find(
            "span", {"class": "ProfileTweet-actionCount"}).attrs["data-tweet-stat-count"])
        retweet_count = int(tweet.find(
            "span", {"class": "ProfileTweet-action--retweet"}).find(
            "span", {"class": "ProfileTweet-actionCount"}).attrs["data-tweet-stat-count"])

        has_url = 0
        try:
            if tweet.find("div", {"class": "card-type-summary_large_image"}):
                has_url = 1
            elif tweet.find("span", {"class": "js-display-url"}):
                has_url = 1
            elif tweet.find("div", {"data-card2-name": "promo_website"}):
                has_url = 1
        except:
            pass

        has_image = 0
        try:
            if tweet.find("div", {"class": "AdaptiveMedia-photoContainer"}):
                has_image = 1
        except:
            pass

        has_video = 0
        try:
            if tweet.find("div", {"class": "AdaptiveMedia-video"}):
                has_video = 1
        except:
            pass

        if has_image or has_video:
            has_media = 1
        else:
            has_media = 0

        # print(has_url)

        if (now - created_at).days > 1:

            outtweets.append([tweet_id,
                              username,
                              full_text,
                              sentiment_value[0],
                              polarity,
                              sentiment_value[1],
                              subjectivity,
                              created_at,
                              favorite_count,
                              retweet_count,
                              has_url,
                              has_image,
                              has_video,
                              has_media,
                              source])
    return outtweets


# Save to CSV
# 1) create header row
# 2) Write each list entry of outtweets as row

def save_csv():
    saved_file_name = file_name
    with open(saved_file_name, "w",) as f:
        writer = csv.writer(f)
        writer.writerow(["tweet_id",
                         "username",
                         "full_text",
                         "polarity_value",
                         "polarity",
                         "subjectivity_value",
                         "subjectivity",
                         "created_at",
                         "favorite_count",
                         "retweet_count",
                         "has_url",
                         "has_image",
                         "has_video",
                         "has_media",
                         "tweet_source"]
                        )
        writer.writerows(outtweets)
    return saved_file_name


# Scraping class with two options:
# 1) Scrape users timeline
# 2) Use Advanced Search

class scrape:

    browser = webdriver.Chrome(
        "/Users/benediktkuehn/Documents/Development/Python/Twitter/TwitterScraping/chromedriver")

    def user_timeline(self, username, no_of_pagedowns):

        url = "https://twitter.com/%s" % (username)

        self.browser.get(url)
        elem = self.browser.find_element_by_tag_name("body")

        while no_of_pagedowns:
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            no_of_pagedowns -= 1

        html = BeautifulSoup(self.browser.page_source, 'html.parser')
        timeline = html.select("#timeline li.stream-item")
        outtweets = create_outtweets(timeline, "User Timeline")
        save_csv()

    def user_advanced_search(self, username, amount_of_tweets, last_tweet_date=str(now.date())):

        outtweets = []

        while amount_of_tweets > len(outtweets):

            try:
                with open(saved_file_name, "r") as f:
                    reader = csv.reader(f)
                    reader.next()
                    outtweets = list(reader)
            except:
                pass

            url = "https://twitter.com/search?f=tweets&vertical=default&q=%28from%3A" + \
                (username) + "%29%20until%3A" + \
                last_tweet_date + "%20-filter%3Areplies"

            self.browser.get(url)
            elem = self.browser.find_element_by_tag_name("body")

            no_of_pagedowns = 2
            while no_of_pagedowns:
                elem.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)
                no_of_pagedowns -= 1

            html = BeautifulSoup(self.browser.page_source, 'html.parser')
            timeline = html.select("#timeline li.stream-item")
            outtweets = create_outtweets(
                timeline, "Advanced Search")

            last_tweet_index = len(outtweets) - 1

            last_tweet_date = str(outtweets[last_tweet_index][7].date())
            # print(last_tweet_date)

            saved_file_name = save_csv()
        return outtweets


# Main part of program, just calls one of the two functions of scrape class

outtweets = scrape(
).user_advanced_search(username, amount_of_tweets)
