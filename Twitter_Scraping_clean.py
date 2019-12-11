import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

now = datetime.now()

# Using Selenium
browser = webdriver.Chrome(
    "/Users/benediktkuehn/Documents/Development/Python/Twitter/TwitterScraping/chromedriver")

# Put in URL of account you want to scrape
browser.get("https://twitter.com/united")
time.sleep(1.5)

elem = browser.find_element_by_tag_name("body")

no_of_pagedowns = 10

while no_of_pagedowns:
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)
    no_of_pagedowns -= 1

html = BeautifulSoup(browser.page_source, 'html.parser')
timeline = html.select("#timeline li.stream-item")


outtweets = []


for tweet in timeline:
    tweet_id = tweet["data-item-id"]
    username = tweet.find("span", {"class": 'username'}).text
    full_text = tweet.select('p.tweet-text')[0].get_text()

    created_at = datetime.fromtimestamp(int(tweet.find(
        "span", {"class": "_timestamp"}).attrs["data-time"]))
    favorite_count = int(tweet.find(
        "span", {"class": "ProfileTweet-action--favorite"}).find(
        "span", {"class": "ProfileTweet-actionCount"}).attrs["data-tweet-stat-count"])
    retweet_count = int(tweet.find(
        "span", {"class": "ProfileTweet-action--retweet"}).find(
        "span", {"class": "ProfileTweet-actionCount"}).attrs["data-tweet-stat-count"])
    replies_count = int(tweet.find(
        "span", {"class": "ProfileTweet-action--reply"}).find(
        "span", {"class": "ProfileTweet-actionCount"}).attrs["data-tweet-stat-count"])

    has_url = 0
    try:
        if tweet.find("div", {"class": "card-type-summary_large_image"}):
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
                          created_at,
                          favorite_count,
                          retweet_count,
                          replies_count,
                          has_url,
                          has_image,
                          has_video,
                          has_media])


dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")

file_name = "tweets_scraped_united_%s.csv" % (dt_string)

with open(file_name, "w",) as f:
    writer = csv.writer(f)
    writer.writerow(["tweet_id",
                     "username",
                     "full_text",
                     "created_at",
                     "favorite_count",
                     "retweet_count",
                     "replies_count",
                     "has_url",
                     "has_image",
                     "has_video",
                     "has_media"]
                    )
    writer.writerows(outtweets)
