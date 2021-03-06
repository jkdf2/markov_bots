from rw import RandomWriter
from rw import Tokenization
from configparser import ConfigParser
import praw
import tweepy

# Configurable bot behavior.
reddit_agent = "praw:generatenews:v1.0 (by nobody)"
subreddits = ["news", "worldnews", "upliftingnews"]
submissions_limit = 1000  # Number of submissions to train on per subreddit.
analysis_level = 12
tokenization_mode = Tokenization.character
char_limit = 140

# Authenticate with Twitter based on config.ini entries.
config = ConfigParser()
with open("config.ini") as cfgfile:
    config.read_file(cfgfile)
twitter_cfg = config["twitter"]
auth = tweepy.OAuthHandler(twitter_cfg["consumer_key"],
                           twitter_cfg["consumer_secret"])
auth.set_access_token(twitter_cfg["access_token"], twitter_cfg["access_secret"])
t = tweepy.API(auth)
print("Successfully authenticated with Twitter.")

# Access Reddit API
r = praw.Reddit(reddit_agent)

# Aggregate the titles for processing.
titles = ""
for subreddit in subreddits:
    hot = r.get_subreddit(subreddit).get_hot(limit=submissions_limit)
    for thread in hot:
        titles += thread.title + " "
print("Aggregated Reddit thread titles.")

# Train on the accumulated titles.
rw = RandomWriter(analysis_level, tokenization_mode)
rw.train_iterable(titles)
print("RandomWriter trained on thread titles.")

# Genate a tweet, which will always be unique based on the training.
tweet = ""
for _ in range(char_limit):
    tweet += next(rw.generate())
tweet += "."

# Partition and select the 3rd element, which will ensure we start with a
# complete word instead of just a few random characters.
tweet = tweet.partition(' ')[2]

# Capitalize the first letter, without changing the rest.
tweet = tweet[0].capitalize() + tweet[1:]

# Finally, submit the tweet.
tweet = t.update_status(tweet)
tweet_url = "https://twitter.com/{}/status/{}".format(t.me().id_str,
                                                      tweet.id_str)
print("{} just tweeted: {}\nSee Tweet at: {}".format(t.me().screen_name,
                                                     tweet.text, tweet_url))
