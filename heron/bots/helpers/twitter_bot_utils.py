"""
Very general utilities for working with twitter bots, post, conversations
CRUD functions happen here
"""
import random
import HTMLParser
from collections import defaultdict

import nltk
from bots.helpers.twitter_api_interface import TwitterApiInterface
from bots.helpers.watson_utils import interpret_watson_keywords_and_entities
from bots.models.twitter import (TwitterBot, TwitterConversation,
                                 TwitterConversationPost, TwitterPost)
from django.conf import settings
from nltk.corpus import wordnet as wn
from nltk.corpus import webtext
from nltk.probability import FreqDist
from rake_nltk import Rake

from .utils import create_post_cache, replace_tokens

from bots.helpers.twitter_getters import get_tweets_over_reply_threshold_and_analyze_text_understanding


def get_top_twitter_users(limit=50):
    t = TwitterApiInterface(
        settings.TWEEPY_CONSUMER_KEY,
        settings.TWEEPY_CONSUMER_SECRET,
        settings.TWEEPY_ACCESS_TOKEN,
        settings.TWEEPY_ACCESS_TOKEN_SECRET)

    names_and_unames = t.scrape_top_users(limit)

    return names_and_unames


def get_top_twitter_bots(limit=50):
    # TODO Use order_by
    top_bots = TwitterBot.objects.all()
    if limit:
        top_bots = top_bots[:limit]
    bot_data = {x.id: {'first_name': x.first_name, 'username': x.username} for x in top_bots}
    return bot_data


def list_all_emotion_twitter_bots():
    bot_data = {}
    for emotion in settings.WATSON_EMOTIONS:
        bot_name = emotion + '_bot'
        bot, _ = TwitterBot.objects.get_or_create(username=bot_name)
        tweets = TwitterPost.objects.filter(author=bot)
        bot_data[bot_name] = {'tweets': [x.content for x in tweets]}
    return bot_data


def get_emotion_tweets():
    bot_meta_data = {}
    for emotion in settings.WATSON_EMOTIONS:
        tweets = TwitterPost.objects.filter(emotion=emotion)
        bot_meta_data[emotion] = []
        for tweet in tweets:
            bot_meta_data[emotion].append(
                {'id': tweet.id,
                 'emotion': emotion,
                 'content': tweet.content})

    return bot_meta_data


def update_top_twitter_bots():
    names_and_unames = get_top_twitter_users()

    for entry in names_and_unames:
        bot = None
        bot = TwitterBot.objects.get_or_create(username=entry['uname'])[0]

        bot.username = entry['uname']
        bot.real_name = entry['name']
        bot.avatar = entry['avatar']
        bot.save()

    return True


def scrape_top_twitter_bots():
    update_top_twitter_bots()

    all_twitter_bots = TwitterBot.objects.all()
    for bot in all_twitter_bots:
        scrape_twitter_bot(bot)


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

    response_data['new tweets'] = len(tweets)
    response_data['tweets'] = {}

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

        response_data['tweets'][idx] = str(tweet)

        h = HTMLParser.HTMLParser()
        tweet = h.unescape(tweet.decode('utf-8'))

        post = TwitterPost.objects.create(author=bot, content=tweet, tweet_id=tweet_id)

        create_post_cache(post.content, bot.twitterpostcache_set)
        idx += 1

    return response_data


def scrape(username):
    bot = TwitterBot.objects.get(username=username)
    scrape_response = scrape_twitter_bot(bot)
    data = {'success': True, 'new tweets': scrape_response['new tweets'], 'tweets':
            scrape_response['tweets']}
    return data


def clear_twitter_bot(username):
    bot = TwitterBot.objects.get(username=username)
    bot.twitterpost_set.all().delete()


def get_info(username):
    bot = TwitterBot.objects.get(username=username)
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


def find_word_frequency_for_user(username):
    words = FreqDist()

    bot = TwitterBot.objects.get(username=username)
    for post in bot.twitterpost_set.all():
        for word in nltk.tokenize.word_tokenize(post.content):
            words[word] += 1


def get_or_create_conversation(bot1_username, bot2_username):
    bot, _ = TwitterBot.objects.get_or_create(username=bot1_username)
    partner, _ = TwitterBot.objects.get_or_create(username=bot2_username)

    conversation = None
    try:
        conversation = TwitterConversation.objects.get(author=bot, partner=partner)
    except:
        try:
            conversation = TwitterConversation.objects.get(author=partner, partner=bot)
        except:
            pass
    if not conversation:
        conversation = TwitterConversation.objects.create(author=bot, partner=partner)
    return conversation


def get_or_create_conversation_json(bot1_username, bot2_username):
    conversation = get_or_create_conversation(bot1_username, bot2_username)[0]
    conversation_json = {'id': conversation.id,
                         'bot1': conversation.author.username,
                         'bot2': conversation.partner.username,
                         'posts': {}
                         }
    for idx, conv_post in enumerate(conversation.twitterconversationpost_set.all()):
        # TODO - do we need idx?
        # idx = None
        conversation_json['posts'][conv_post.index] = \
            {conv_post.author.username + ": ": conv_post.post.content}

    return conversation_json


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


def generate_response_with_key_phrases(key_phrases, author, partner):
    if not len(key_phrases):
        return 'first post'
    #  Will map key phrase to list of tweets that contain one of those phrases or a synonym
    #  Search for tweets that contain the given key phrase or a synonym
    #  Searh the author's tweets for something with that phrase
    key_phrase_match_map = defaultdict(list)
    for tweet in author.twitterpost_set.all():
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


def generate_new_conversation_post_text(speaker_id, is_new_conversation, previous_posts):
    """
    Input:
        Id of the bot who is going to speak
        Boolean - is this conversation brand new
        Sorted list of plain text posts of the entire conversation
    Output:
        A new post for the next speaker

    If this is a new conversation, then there are no posts, so return a pseudo random post
    If there are previous posts, then analyze the last one with the watson API
    Use that data, and all the previous posts to construct a new one for the speaker
    """
    bot = TwitterBot.objects.get(id=speaker_id)
    if is_new_conversation:
        # Choose a random post from the user
        post_set = bot.twitterpost_set.all()
        if post_set.count():
            random_tweet = random.choice(bot.twitterpost_set.all())
            reply = random_tweet.content
            # Make sure it's not a reply??
            return reply
        else:
            return None

    reply = ''
    all_beginning_caches = bot.twitterpostcache_set.filter(beginning=True)
    all_caches = bot.twitterpostcache_set.all()
    # The template represents how this user talks,
    # We will alter this text based on the previous conversation posts
    new_markov_template, randomness = bot.apply_markov_chains_inner(all_beginning_caches, all_caches)
    _, markov_keywords, markov_entities = interpret_watson_keywords_and_entities(new_markov_template)

    # Use the emotion of the last speaker to figure out what to say, maybe means adding a new user??
    overarching_emotion, keywords, entities = interpret_watson_keywords_and_entities(previous_posts[-1])

    # Look at the keywords in the previous post and see if they can be injected into the new markov post
    replacements = {}
    for keyword, data in keywords.iteritems():
        emotion = data.get('emotion')
        for markov_keyword, markov_data in markov_keywords.iteritems():
            markov_emotion = markov_data.get('emotion')
            if emotion == markov_emotion:
                replacements[markov_keyword] = keyword

    for entity, data in entities.iteritems():
        emotion = data.get('emotion')
        for markov_keyword, markov_data in markov_keywords.iteritems():
            markov_emotion = markov_data.get('emotion')
            if emotion == markov_emotion:
                if markov_keyword not in replacements.keys():
                    replacements[markov_keyword] = entity

    for phrase, replacement in replacements.iteritems():
        new_markov_template = new_markov_template.replace(phrase, replacement)

    reply = new_markov_template
    create_post_cache(reply, bot.twitterpostcache_set)
    return reply


def add_to_twitter_conversation(bot_username, partner_username, post_number=1):
    """
    Input:
        Username of first speaker
        Username of second speaker
        The Number of posts to make
    Output:
        JSON corresponding to a new post in the conversation between these two

    First we sort the conversation query dict
    Then we determind if it is brand new, and who speaks next
    Then we generate the text for the new post and create a django object for it
    Then we return JSON corresponding to that new object
    """
    conversation = get_or_create_conversation(bot_username, partner_username)
    sorted_conversation_posts = conversation.twitterconversationpost_set.order_by('index').all()

    last_post = sorted_conversation_posts.last()
    index = 0
    new_conversation = True
    if last_post:
        index = last_post.index + 1
        new_conversation = False

    next_speaker, last_speaker = get_next_speaker_and_last_speaker(sorted_conversation_posts,
                                                                   conversation.author,
                                                                   conversation.partner)

    new_posts_json = {}
    for i in range(post_number):
        previous_tweets = [x.post.content for x in sorted_conversation_posts]
        # This does the logic of creating the content
        reply = generate_new_conversation_post_text(next_speaker.id, new_conversation, previous_tweets)
        if not reply:
            reply = generate_new_conversation_post_text(last_speaker.id, new_conversation, previous_tweets)

        new_post = next_speaker.twitterpost_set.create(tweet_id=-1, content=reply)

        new_convo_post = TwitterConversationPost.objects.create(
            post=new_post,
            conversation=conversation,
            author=next_speaker,
            index=index
        )
        new_post_json = {'author': new_convo_post.author.username,
                         'index': new_convo_post.index,
                         'conversation': new_convo_post.conversation.id,
                         'content': new_convo_post.post.content}
        new_posts_json[i] = new_post_json

        # Switch the speakers
        last_speaker, next_speaker = next_speaker, last_speaker
        index += 1
    return new_posts_json


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


def add_new_tweets_to_emotion_bot(params):

    twitter_source_users = params.get('twitter_source_users')
    response_number = params.get('response_number')

    new_bot_tweets = {}
    for emotion in settings.WATSON_EMOTIONS:
        new_bot_tweets[emotion] = []
    threshold = 1
    scrape_mode = 'single_reply'

    for username in twitter_source_users:
        print 'getting responses for source user: %s' % username
        response_data = get_tweets_over_reply_threshold_and_analyze_text_understanding(
            username, scrape_mode, threshold=int(threshold), max_response_number=int(response_number))
        for tweet_id, tweet_data in response_data.iteritems():
            replies = tweet_data['replies']
            if replies:
                for reply_id, reply_content in replies.iteritems():
                    emotion = reply_content['overarching_emotion']
                    if emotion in settings.WATSON_EMOTIONS:
                        content = reply_content['content']
                        bot, _ = TwitterBot.objects.get_or_create(username=emotion + '_bot')
                        bot.twitterpost_set.create(tweet_id=reply_id, content=content)
                        create_post_cache(content, bot.twitterpostcache_set)
                        new_bot_tweets[emotion].append(reply_content['content'])

    return new_bot_tweets


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
