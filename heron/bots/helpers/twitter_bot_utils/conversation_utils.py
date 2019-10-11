import random
from collections import defaultdict

from bots.helpers.watson_utils import interpret_watson_keywords_and_entities
from bots.models.twitter import (TwitterBot, TwitterConversation,
                                 TwitterConversationPost, TwitterPost)
from django.conf import settings
from nltk.corpus import wordnet as wn
from nltk.corpus import webtext
from rake_nltk import Rake
import nltk
from nltk.probability import FreqDist

from .twitter_post_utils import create_post_cache, replace_tokens


def get_or_create_conversation(bot1_username, bot2_username):
  bot, _ = TwitterBot.objects.get_or_create(username=bot1_username)
  partner, _ = TwitterBot.objects.get_or_create(username=bot2_username)

  conversation = None
  try:
    conversation = TwitterConversation.objects.get(author=bot, partner=partner)
  except:
    pass
  try:
    conversation = TwitterConversation.objects.get(author=partner, partner=bot)
  except:
    pass
  if not conversation:
    conversation = TwitterConversation.objects.create(author=bot, partner=partner)
  return conversation


def get_group_conversation_json(conversation_name):
  conversation = TwitterConversation.objects.get_or_create(name=conversation_name)[0]
  conversation_json = {}
  for conv_post in conversation.twitterconversationpost_set.all():
    conversation_json[conv_post.index] = {conv_post.post.author.username: conv_post.post.content}

  return {conversation_name: conversation_json}


def get_next_speaker_and_last_speaker(conversation_posts, author, partner):
  """
  Input:
      All the current posts in a 2 speaker conversation
      The two speakers
  Output:
      Based on the given list of posts, return who speaks next and who spoke last
  """
  last_speaker = author
  next_speaker = partner

  last_post = conversation_posts.last()
  if last_post:
    if last_post.author == next_speaker:
      last_speaker = partner
      next_speaker = author

  return next_speaker, last_speaker


def clear_twitter_conversation(bot1_username, bot2_username, conversation=None):
  if not conversation:
    conversation = get_or_create_conversation(bot1_username, bot2_username)

  for convo_post in conversation.twitterconversationpost_set.all():
    convo_post.post.delete()
    convo_post.delete()
  conversation.delete()
  return True


def clear_all_twitter_conversations(bot_id):
  bot = TwitterBot.objects.get(id=bot_id)
  conversations = TwitterConversation.objects.filter(author=bot)
  for c in conversations:
    clear_twitter_conversation(c)


def generate_new_conversation_post_text(bot_id, previous_posts):
  """
  If there are previous posts, then analyze the last one with the watson API
  Use that data, and all the previous posts to construct a new one for the speaker
  """
  bot = TwitterBot.objects.get(id=bot_id)

  reply_text = ''
  all_beginning_caches = bot.twitterpostcache_set.filter(beginning=True)
  all_caches = bot.twitterpostcache_set.all()
  # Get The template represents how this user talks; it's a randomized list of strings
  new_markov_template, _ = bot.apply_markov_chains_inner(all_beginning_caches, all_caches)
  print new_markov_template
  # Then, use Watson API to get the keywords and entities from this template
  _, markov_keywords, markov_entities = interpret_watson_keywords_and_entities(new_markov_template)
  # Then use Watson again to get the emotion/keywords/entities of the last speaker to figure out what to say
  # Note this is the last speaker, NOT the user corresponding to "bot_id"
  # (maybe means adding a new user??)
  overarching_emotion, keywords, entities = interpret_watson_keywords_and_entities(previous_posts[-1])

  # Now use all this data to try replacing words in the markov template with words from the last speaker's post
  replacements = {}
  all_watson_data_from_last_post = dict(keywords, **entities)
  for keyword, data in all_watson_data_from_last_post.iteritems():
    emotion = data.get('emotion')
    for markov_keyword, markov_data in markov_keywords.iteritems():
      markov_emotion = markov_data.get('emotion')
      if emotion == markov_emotion:
        replacements[markov_keyword] = keyword

  # Now DO the replacements
  for phrase, replacement in replacements.iteritems():
    new_markov_template = new_markov_template.replace(phrase, replacement)

  # After the replacements are done, this should somewhat realish
  reply_text = new_markov_template
  return reply_text


def add_single_post_to_twitter_conversation(conversation_id, index, next_speaker):
  """
  Given a conversation ID, grab all the posts in the conversation and sort them
  Then generate the text of a new post
  Then make a ne post
  """
  conversation = TwitterConversation.objects.get(id=conversation_id)
  sorted_conversation_posts = conversation.twitterconversationpost_set.order_by('index').all()
  previous_posts = [x.post.content for x in sorted_conversation_posts]

  # If the conversation has no posts, don't bother doing anything fancy
  # To kick things off, choose a random post from the user
  reply_text = ''
  if len(previous_posts) == 0:
    post_set = next_speaker.twitterpost_set.all()
    # Should always have at least ONE
    if post_set.count():
      random_post = random.choice(next_speaker.twitterpost_set.all())
      reply_text = random_post.content
  # Otherwise, the conversation is not empty
  # So make new text for repoly post
  else:
    reply_text = generate_new_conversation_post_text(next_speaker.id, previous_posts)

  new_post = next_speaker.twitterpost_set.create(tweet_id=-1, content=reply_text)
  create_post_cache(reply_text, next_speaker.twitterpostcache_set)

  new_convo_post = TwitterConversationPost.objects.create(
      post=new_post,
      conversation=conversation,
      author=next_speaker,
      index=index
  )
  return new_convo_post


def add_posts_to_twitter_conversation(bot1_username, bot2_username, post_number=1):
  """
  First we sort the conversation query dict by index
  Then, repeatedly:
    Get the index for the new post
    Get the next speaker
    Generate the new ConversationPost object
  """
  conversation = get_or_create_conversation(bot1_username, bot2_username)
  sorted_conversation_posts = conversation.twitterconversationpost_set.order_by('index').all()

  index = 0
  if len(sorted_conversation_posts):
    index = sorted_conversation_posts.last().index + 1

  next_speaker, last_speaker = get_next_speaker_and_last_speaker(sorted_conversation_posts,
                                                                 conversation.author,
                                                                 conversation.partner)
  for _ in range(post_number):
    add_single_post_to_twitter_conversation(conversation.id, index, next_speaker)

    # Switch the speakers
    last_speaker, next_speaker = next_speaker, last_speaker
    index += 1
  return True

# ALL TESTING BELOW THIS


def get_key_phrases(conversation):
  last_post = conversation.last()
  r = Rake()
  phrases = []
  content = last_post.post.content
  if content:
    r.extract_keywords_from_text(content)
    # TODO Filter further
    phrases = r.get_ranked_phrases()

  return phrases


def generate_response_with_key_phrases(key_phrases, bot_1, bot_2):
  if not len(key_phrases):
    return 'first post'
  #  Will map key phrase to list of tweets that contain one of those phrases or a synonym
  #  Search for tweets that contain the given key phrase or a synonym
  #  Searh the bot_1's tweets for something with that phrase
  key_phrase_match_map = defaultdict(list)
  for tweet in bot_1.twitterpost_set.all():
    for phrase in key_phrases:
      if phrase in tweet.content:
        key_phrase_match_map[phrase].append(tweet.content)
      for synset in wn.synsets(phrase):
        for lemma in synset.lemmas():
          if lemma.name() in tweet.content:
            key_phrase_match_map[lemma.name()].append(tweet.content)

  for k, v in key_phrase_match_map.iteritems():
    print 'KEY'
    print k
    print 'V'
    print v

  return 'STUB'


def get_web_text_response(conversation_posts):
  """
  Use nltk's webtext to get a response then twitter-fy it
  """
  firefox_raw = webtext.raw(u'overheard.txt')
  print type(firefox_raw)
  print firefox_raw
  print firefox_raw[:100]
  return 'STUB'


def add_message_to_group_convo(bot_username, message, conversation_name):
  print(bot_username)
  print(message)
  print(conversation_name)
  conversation = TwitterConversation.objects.get_or_create(name=conversation_name)[0]
  bot = TwitterBot.objects.get_or_create(username=bot_username)[0]

  # Make sure this hasn't been added already
  sorted_conversation_posts = conversation.twitterconversationpost_set.order_by('index').all()
  if len(sorted_conversation_posts):
    if sorted_conversation_posts.last().post.content == message:
      return message

  # This has not been added to the convo yet, so proceed
  post = TwitterPost.objects.create(tweet_id=-1, author=bot, content=message)

  index = conversation.twitterconversationpost_set.count()
  conversation_post = TwitterConversationPost.objects.create(
      author=bot, post=post, conversation=conversation, index=index)

  return conversation_post.post.content


def create_markov_post(bot_id):
  """
  Takes all the words from all the twitter
  posts on the twitterbot.
  Sticks them all into a giant
  list and gives this to the markov calc.
  Save this as a new twitterpostmarkov
  """
  bot = TwitterBot.objects.get(id=bot_id)

  all_beginning_caches = bot.twitterpostcache_set.filter(beginning=True)
  all_caches = bot.twitterpostcache_set.all()
  new_markov_post = bot.apply_markov_chains_inner(all_beginning_caches, all_caches)

  # Replace the tokens (twitter specific)
  replace_tokens(new_markov_post, settings.USER_TOKEN,
                 bot.twittermention_set.all())
  replace_tokens(new_markov_post, settings.LINK_TOKEN,
                 bot.twitterlink_set.all())
  replace_tokens(new_markov_post, settings.TAG_TOKEN,
                 bot.twitterhashtag_set.all())

  randomness = new_markov_post[1]
  content = " ".join(new_markov_post[0])

  new_markov_post = bot.twitterpostmarkov_set.create(content=content, randomness=randomness)
  return new_markov_post.content


def find_word_frequency_for_user(username):
  words = FreqDist()

  bot = TwitterBot.objects.get(username=username)
  for post in bot.twitterpost_set.all():
    for word in nltk.tokenize.word_tokenize(post.content):
      words[word] += 1
