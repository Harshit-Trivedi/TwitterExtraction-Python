import pymongo as py
import tweepy as tw
import re

'''A reference of steps for Twitter extraction process has been taken from a Medium blog. But the program has not 
been copied. Reference Link: https://medium.com/@adamichelllle/exploring-twitter-api-and-data-using-tweepy-pandas-and
-matplotlib-part-1-2ac07fcc4717 '''

# variables that contain my user credentials to access the Twitter API
consumer_key = 'LGJPU01uuK4NIqYgr4aoVvahZ'
consumer_secret = 'Y0RWWR11J9IB1qcbYNkUxFdi5x2VHW1OuS2Ls9Shd7X2qGvofJ'
access_token = '302138681-q41ccKrd6fEaHRjsgnSTHzJKvtQQ3f9vPd20Vyyb'
access_token_secret = 'AC0vbT5aVvvJlPNyZC0cUzaZw3Bwfl58atCT658TVaKBF'

# set up tweepy to authenticate with Twitter
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# create API object to pull data from Twitter
api = tw.API(auth, wait_on_rate_limit=True)

# setup db and collection for MongoDB
client = py.MongoClient('mongodb://127.0.0.1:27017/')
db = client['Asgmt3']
collection = db['twitter']
file = open("output.txt", "a+")

# search keywords
search_terms = ['Canada', 'University', 'Dalhousie University', 'Halifax', 'Canada Education']
cleaned_data = []  # empty list to which cleaned tweet data will be stored

# clean emoji logic, regex from https://programmersought.com/article/15261349366/
def clean_emoji(string):
    pattern = re.compile("\["
                         u"\U0001F600-\U0001F64F"  # emoticons
                         u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                         u"\U0001F680-\U0001F6FF"  # transport & map symbols
                         u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                         u"\U00002702-\U000027B0"
                         u"\U000024C2-\U0001F251"
                         "\]+", flags=re.UNICODE)
    return pattern.sub(r'', string)


def search_tweets(search_term):
    data = []  # empty list to which tweet_details obj will be added
    counter = 0  # counter to keep track of each iteration

    for tweet in tw.Cursor(api.search, q='\"{}\"'.format(search_term), count=100, lang='en',
                           tweet_mode='extended').items():
        tweet_details = {'name': tweet.user.name, 'twitter_handle': tweet.user.screen_name, 'tweet': tweet.full_text,
                         'retweets': tweet.retweet_count, 'source': tweet.source, 'location': tweet.user.location,
                         'tweet_date': tweet.created_at.strftime("%d-%b-%Y"), 'followers': tweet.user.followers_count,
                         'following': tweet.user.friends_count}
        data.append(tweet_details)
        counter += 1
        # ensuring that loop will stop after 1000 iterations
        if counter == 1000:
            break
        else:
            pass

        # cleaning emoticons
        clean_emoji(tweet_details['tweet'])
        clean_emoji(tweet_details['name'])
        clean_emoji(tweet_details['location'])

        # removing special characters & URLs
        # special characters regex reference: https://www.webdeveloper.com/d/199621-need-a-regex-to-exclude-all-but-a-za-z0-9s
        # URl cleaning regex reference: https://stackoverflow.com/questions/11331982/how-to-remove-any-url-within-a-string-in-python
        tweet_details['name'] = re.sub(r'[^a-zA-Z0-9\s\.]+', '', tweet_details['name'])
        tweet_details['name'] = re.sub(r'http\S+', '', tweet_details['name'], flags=re.MULTILINE)
        tweet_details['tweet'] = re.sub(r'[^a-zA-Z0-9\s\.]+', '', tweet_details['tweet'])
        tweet_details['tweet'] = re.sub(r'http\S+', '', tweet_details['tweet'], flags=re.MULTILINE)

        # writing data to "output.txt", that will be used later during frequency count
        file.write(tweet_details['tweet'])
        print("fetching tweets...")
        cleaned_data.append(tweet_details)

# begin mainscript execution
if __name__ == "__main__":
    print('Searching for tweets...')
    for search_term in search_terms:
        search_tweets(search_term)
    print('cleaning finished!')

# sending data to mongoDB
collection.insert_many(cleaned_data)
print('data stored successfully in MongoDB')
file.close()
