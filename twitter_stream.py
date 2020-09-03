import pymongo as py
import tweepy as tw
import re

'''A reference of steps for Twitter extraction process has been taken from a DataQuest blog. But the program has not 
been copied. Reference Link: https://www.dataquest.io/blog/streaming-data-python/'''

# variables that contain my user credentials to access the Twitter API
consumer_key = 'LGJPU01uuK4NIqYgr4aoVvahZ'
consumer_secret = 'Y0RWWR11J9IB1qcbYNkUxFdi5x2VHW1OuS2Ls9Shd7X2qGvofJ'
access_token = '302138681-q41ccKrd6fEaHRjsgnSTHzJKvtQQ3f9vPd20Vyyb'
access_token_secret = 'AC0vbT5aVvvJlPNyZC0cUzaZw3Bwfl58atCT658TVaKBF'

# setting up tweepy to authenticate with Twitter
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# create API object to pull data from Twitter
api = tw.API(auth)

# setup db and collection for MongoDB
client = py.MongoClient('mongodb://127.0.0.1:27017/')
db = client['Asgmt3']
collection = db['twitter_stream']
x = []

# search keywords
search_terms = ['Canada', 'University', 'Dalhousie University', 'Halifax', 'Canada Education']
max_tweets = 3000


# clean emoji logic, regex from https://programmersought.com/article/15261349366/
def clean_emoji(string):
    if string is not None:
        pattern = re.compile("\["
                             u"\U0001F600-\U0001F64F"  # emoticons
                             u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                             u"\U0001F680-\U0001F6FF"  # transport & map symbols
                             u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                             u"\U00002702-\U000027B0"
                            u"\U000024C2-\U0001F251"
                             "\]+", flags=re.UNICODE)
        return pattern.sub(r'', string)


# Creating a StreamListener
class StreamListener(tw.StreamListener):

    """
    logic to stop collecting tweets, Reference: https://stackoverflow.com/questions/38297150/twitter-streaming-stop-collecting-data
    """

    def __init__(self, api=None):
        print ("Streaming Tweets...")
        super(StreamListener, self).__init__()
        # initializes the counter
        self.count = 0

    def on_status(self, status):
        tweetDetail = {'description': status.user.description, 'twitter_handle': status.user.screen_name,
                       'tweet_date': status.created_at.strftime("%d-%b-%Y"),
                       'location': status.user.location, 'name': status.user.name,
                       'following': status.user.friends_count,
                       'tweet': status.text, 'retweets': status.retweet_count, 'followers': status.user.followers_count}

        # prints status text. Also count the mentions and clean tweets.
        self.count += 1
        if self.count <= max_tweets:
            clean_emoji(tweetDetail['tweet'])
            clean_emoji(tweetDetail['description'])
            clean_emoji(tweetDetail['location'])
            clean_emoji(tweetDetail['name'])
            if tweetDetail['tweet'] is not None:
                tweetDetail['tweet'] = re.sub(r'[^a-zA-Z0-9\s\.]+', '', tweetDetail['tweet'])
                tweetDetail['tweet'] = re.sub(r'http\S+', '', tweetDetail['tweet'], flags=re.MULTILINE)
            if tweetDetail['description'] is not None:
                tweetDetail['description'] = re.sub(r'http\S+', '', tweetDetail['description'], flags=re.MULTILINE)
                tweetDetail['description'] = re.sub(r'[^a-zA-Z0-9\s\.]+', '', tweetDetail['description'])
            if tweetDetail['location'] is not None:
                tweetDetail['location'] = re.sub(r'http\S+', '', tweetDetail['location'], flags=re.MULTILINE)
                tweetDetail['location'] = re.sub(r'[^a-zA-Z0-9\s\.]+', '', tweetDetail['location'])
            if tweetDetail['name'] is not None:
                tweetDetail['name'] = re.sub(r'[^a-zA-Z0-9\s\.]+', '', tweetDetail['name'])
                tweetDetail['name'] = re.sub(r'http\S+', '', tweetDetail['name'], flags=re.MULTILINE)
            x.append(tweetDetail)
            return True
        else:
            print("Fetched", self.count - 1, "tweets")
            return False

    def on_error(self, status_code):
        # returning False in on_error disconnects the stream
        if status_code == 420:
            return False
    # returning non-False reconnects the stream, with backoff.


# creating a stream
stream_listener = StreamListener()
stream = tw.Stream(auth=api.auth, listener=stream_listener)
# starting a stream
stream.filter(track=['Canada', 'University', 'Dalhousie University', 'Halifax', 'Canada Education'])
# sending data to mongoDB
collection.insert_many(x)
print('data stored successfully in MongoDB')