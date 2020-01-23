"""
Utilities for working with REAL Twitter data and the bot objects

You will see both the phrase "person" and "bot" in this file,
  as data comes in from REAL people, and is processed and shunted into the bots
"""
from bots.helpers.twitter_api_interface import TwitterApiInterface
from bots.models.twitter import TwitterBot
from django.conf import settings


def get_twitter_bot(username):
  if not username:
    return None

  # If the @ symbol was included, strip it
  if username[0] == '@':
    username = username[1:]

  # Retrieve the bot object safely
  try:
    bot = TwitterBot.objects.get(username=username)
    return bot
  except TwitterBot.DoesNotExist:
    return None


def get_all_twitter_bots():
  # TODO, change the return signature
  all_bots = TwitterBot.objects.all()
  bot_data = {x.id: get_twitter_bot_info(x.username) for x in all_bots}
  return True, bot_data


def create_or_update_bot(username, name, avatar):
  bot = TwitterBot.objects.get_or_create(username=username)[0]
  bot.username = username
  bot.real_name = name
  bot.avatar = avatar
  bot.save()
  # Done, format return dict
  return bot


def start_tweepy_interface():
  tweepy_interface = TwitterApiInterface(
      settings.TWEEPY_CONSUMER_KEY,
      settings.TWEEPY_CONSUMER_SECRET,
      settings.TWEEPY_ACCESS_TOKEN,
      settings.TWEEPY_ACCESS_TOKEN_SECRET)
  # Could throw friendly errors here if this fails
  return tweepy_interface


def create_twitter_bot_from_person(username):
  # Authorize and set up Tweepy
  t = start_tweepy_interface()
  # Use Tweepy to get data
  person_dict = t.find_user(username)
  # Post process
  name = person_dict.get('name')
  if not name:
    return False, {}

  name = person_dict.get('name')
  avatar = person_dict.get('avatar')
  bot = create_or_update_bot(username, name, avatar)
  return bot


def create_twitter_bots_for_top_users():
  # Change name from "user" to "person"
  """
  Using the Twitter API interface, find the 100 most popular users
  For each one, create/update a Twitterbot object
  """
  # Authorize and set up Tweepy
  t = start_tweepy_interface()
  # Use Tweepy to get data
  people_dict = t.find_top_users()
  # Post process
  updated_bots = []
  for entry in people_dict:
    bot = create_or_update_bot(entry.get('username'), entry.get('name'), entry.get('avatar'))
    bot.save()
    updated_bots.append(bot)

  all_twitter_bot_data = {x.id: get_twitter_bot_info(x.username) for x in updated_bots}
  return True, all_twitter_bot_data


def clear_twitter_bot(username):
  bot = get_twitter_bot(username)
  if not bot:
    return False
  bot.twitterpost_set.all().delete()
  return True


def get_twitter_bot_info(username):
  bot = get_twitter_bot(username)
  real_posts = {x.id: x.content for x in bot.twitterpost_set.all()}
  fake_posts = {x.id: x.content for x in bot.twitterpostmarkov_set.all()}
  bot_data = {
      'real_name': bot.real_name,
      'first_name': bot.first_name,
      'last_name': bot.last_name,
      'username': bot.username,
      'avatar': bot.avatar,
      'real posts': real_posts,
      'fake posts': fake_posts,
  }
  return bot_data


def get_bot_attributes(username):
  classifier_metrics = {
      'mention_percentage': -1,
      'retweet_percentage': -1,
      'link_percentage': -1,
      'hash_percentage': -1,
      'verbosity': -1,
  }
  bot = TwitterBot.objects.get(username=username)
  real_posts = bot.twitterpost_set.filter()

  mention_tweets = 0
  retweet_tweets = 0
  link_tweets = 0
  hash_tweets = 0
  total_word_number = 0
  for post in real_posts:
    mention_tweets += 1 if settings.USER_TOKEN in post.content else 0
    retweet_tweets += 1 if 'RT' in post.content else 0
    link_tweets += 1 if settings.LINK_TOKEN in post.content else 0
    hash_tweets += 1 if settings.TAG_TOKEN in post.content else 0
    total_word_number += len(post.content.split(' '))

  total_posts_len = 1.0
  if len(real_posts) > 0:
    total_posts_len = float(len(real_posts))

  classifier_metrics['mention_percentage'] = mention_tweets / total_posts_len
  classifier_metrics['retweet_percentage'] = retweet_tweets / total_posts_len
  classifier_metrics['link_percentage'] = link_tweets / total_posts_len
  classifier_metrics['hash_percentage'] = hash_tweets / total_posts_len
  classifier_metrics['verbosity'] = total_word_number / 144 * total_posts_len
  return classifier_metrics
