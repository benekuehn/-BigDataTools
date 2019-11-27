import time
import pandas as pd

import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Put in location of chrome driver https://chromedriver.chromium.org
browser = webdriver.Chrome("")

# Put in URL of account you want to scrape
browser.get("https://twitter.com/elonmusk")
time.sleep(1)

elem = browser.find_element_by_tag_name("body")

no_of_pagedowns = 2

while no_of_pagedowns:
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)
    no_of_pagedowns -= 1

post_elems = browser.find_elements_by_class_name("has-cards")

pd_list = []

for item in post_elems:
    item_dict = {}

    # Handle
    handle = item.find_elements_by_class_name("u-dir")

    # handle_text = ''
    if len(handle) > 0:
        handle_text = handle[0].text
    item_dict['handle'] = handle_text

    # ID
    ID = item.find_elements_by_class_name("show-popup-with-id")
    ID_text = ''
    if len(ID) > 0:
        ID_text = ID[0].text
    item_dict['screen_name'] = ID_text

    # Time
    time_ = item.find_elements_by_class_name("js-short-timestamp")
    time_text = ''
    if len(time_) > 0:
        time_text = time_[0].text
    item_dict['time'] = time_text

    # Text
    text_ = item.find_elements_by_class_name("tweet-text")
    text_text = ''
    if len(text_) > 0:
        text_text = text_[0].text
    item_dict['content'] = text_text

    # NO of replies
    replies = item.find_elements_by_class_name("js-actionReply")
    replies_text = 0
    if len(replies) > 0:
        temp = replies[0].find_elements_by_class_name(
            "ProfileTweet-actionCountForPresentation")
        if len(temp) > 0:
            replies_text = temp[0].text
            if "K" in replies_text:
                replies_text = replies_text[:-1]
                replies_text = int(float(replies_text) * 1000)
    item_dict['replies'] = replies_text

    # NO of retweets
    retweets = item.find_elements_by_class_name("js-actionRetweet")
    retweets_text = 0
    if len(retweets) > 0:
        temp = retweets[0].find_elements_by_class_name(
            "ProfileTweet-actionCountForPresentation")
        if len(temp) > 0:
            retweets_text = temp[0].text
            if "K" in retweets_text:
                retweets_text = retweets_text[:-1]
                retweets_text = int(float(retweets_text) * 1000)
    item_dict['retweets'] = retweets_text

    # NO of favourites
    favourites = item.find_elements_by_class_name("js-actionFavorite")
    favourites_text = 0
    if len(favourites) > 0:
        temp = favourites[0].find_elements_by_class_name(
            "ProfileTweet-actionCountForPresentation")
        if len(temp) > 0:
            favourites_text = temp[0].text
            if "K" in favourites_text:
                favourites_text = favourites_text[:-1]
                favourites_text = int(float(favourites_text) * 1000)
    item_dict['favourites'] = favourites_text

    # photo
    image = item.find_elements_by_class_name("js-adaptive-photo img")
    image_text = False
    if len(image) > 0:
        image_text = True
    item_dict['images'] = image_text

    # video
    video = item.find_elements_by_class_name("PlayableMedia-player")
    video_text = False
    if len(video) > 0:
        video_text = True
    item_dict['videos'] = video_text

    # embedded link
    embedded_link = item.find_elements_by_class_name(
        "card-type-summary_large_image")
    embedded_link_text = False
    if len(embedded_link) > 0:
        embedded_link_text = True
    item_dict['embedded_link'] = embedded_link_text

    # pinned_tweet
    pinned = item.find_elements_by_class_name("js-pinned-text")
    pinned_text = False
    if len(pinned) > 0:
        pinned_text = True
    item_dict['pinned'] = pinned_text

    # retweeting
    retweeting = item.find_elements_by_class_name("js-retweet-text")
    retweeting_text = False
    if len(retweeting) > 0:
        retweeing_text = True
    item_dict['retweeting'] = retweeting_text

    item_pd = pd.DataFrame(item_dict, index=[0])

    pd_list.append(item_pd)


data = pd.concat(pd_list)
data.to_csv('twitter_test.csv')
