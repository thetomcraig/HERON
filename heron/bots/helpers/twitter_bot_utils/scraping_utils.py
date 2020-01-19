"""
Very general utilities for working with twitter bots
TwitterBots created and updated mostly using the Tweepy API, via TwitterApiInterface
"""
from .twitter_post_utils import create_post_cache
import HTMLParser
from bots.helpers.twitter_api_interface import TwitterApiInterface
from bots.models.twitter import TwitterBot, TwitterPost
from django.conf import settings


def scrape_twitter_bot(bot):
  """
  Scrape the given user with tweepy
  take all of their tweets and
  turn them into TwitterPost objects
  strip out uncommon words (links, hashtags, users)
  and save them seperately in instances, then
  replace with dummy words.
  """
  response_data = {}

  t = TwitterApiInterface(
      settings.TWEEPY_CONSUMER_KEY,
      settings.TWEEPY_CONSUMER_SECRET,
      settings.TWEEPY_ACCESS_TOKEN,
      settings.TWEEPY_ACCESS_TOKEN_SECRET)

  tweets = t.get_tweets_from_user(bot.username, 100)

  response_data['num_new_tweets'] = len(tweets)
  response_data['new_tweets'] = {}

  idx = 0
  for tweet_id, tweet in tweets.iteritems():

    words = tweet.split()
    for word in words:
      if "@" in word:
        bot.twittermention_set.create(content=word)
      if "http" in word:
        bot.twitterlink_set.create(content=word)
      if "#" in word:
        bot.twitterhashtag_set.create(content=word)

    response_data['new_tweets'][idx] = str(tweet)

    h = HTMLParser.HTMLParser()
    tweet = h.unescape(tweet.decode('utf-8'))

    post = TwitterPost.objects.create(author=bot, content=tweet, tweet_id=tweet_id)

    create_post_cache(post.content, bot.twitterpostcache_set)
    idx += 1

  return response_data


def scrape_all_twitter_bots():
  """
  WARNING this can cause rate limit-related errors
  """
  all_twitter_bots = TwitterBot.objects.all()

  response_data = {}
  for bot in all_twitter_bots:
    bot_data = scrape_twitter_bot(bot)
    response_data[bot.id] = bot_data

  return response_data


def scrape(username):
  bot = TwitterBot.objects.get(username=username)
  scrape_response = scrape_twitter_bot(bot)
  data = {'success': True, 'new tweets': scrape_response['new_tweets'], 'num_new_tweets':
          scrape_response['num_new_tweets']}
  return data
