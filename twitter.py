from datetime import datetime, timedelta
import tweepy as tw



def getTweets(hashtag, consumer_key, consumer_secret, token_key, token_secret):
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(token_key, token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    hashtag = '#' + hashtag + ' -filter:retweets'
    date_since = datetime.now()-timedelta(days=30)
    date_since = date_since.strftime('%Y') + '-' + date_since.strftime('%m') + '-' + date_since.strftime('%d')
    tweets = tw.Cursor(api.search, q=hashtag, lang="en", since=date_since).items(5)
    return [tweet.text for tweet in tweets]
