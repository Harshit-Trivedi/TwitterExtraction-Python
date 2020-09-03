# Overview

For Twitter data extraction, I have used Python to access twitter data. For this I imported the tweepy package. To access the Twitter API, I used my consumer key, 
consumer secret key, access token key & access token secret key. For searching tweets related to the target keywords, I have used the .Cursor() method. While when 
streaming tweets, I have used the StreamListener class to implement my logic. Along with tweets and retweets, I have also extracted meta data about name, twitter handle, 
retweet count, tweet source (android,iOS or desktop), location, date, followers count & following count. 

## Target Keywords

“Canada”, “University”, “Dalhousie University”, “Halifax”, “Canada Education”.

## File description

The python script files named twitter_search.py and twitter_stream.py have the code for searching and streaming tweets respectively.

Files named twitter_search_cleaned.json and twitter_stream_cleaned.json are the output JSON data files for searching and streaming tweets respectively.

## Data Cleaning

For all the Twitter data, I have removed emoticons, symbols, pictographs, transport/map symbols, flags(iOS), special characters & URLs. For removing the special 
characters and URLs, I have used regex substitution. For cleaning all the emojis, symbols, etc. I have created a separate custom function named “clean_emoji”. 
This function also performs a regex operation to substitute and clean data. The above approach is used for both searching and streaming data.
