import HTMLParser
import json
from collections import defaultdict

import mechanize
import nltk
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from nltk.corpus import wordnet as wn
from nltk.corpus import webtext
from nltk.probability import FreqDist
from rake_nltk import Rake

from bots.helpers.TweepyScraper import TweepyScraper
from bots.models.twitter import (TwitterBot, TwitterConversation,
                                 TwitterConversationPost, TwitterPost)

from .utils import create_post_cache, replace_tokens


def get_top_twitter_users(limit=50):
    t = TweepyScraper(
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


def scrape(username):
    bot = TwitterBot.objects.get(username=username)
    scrape_response = scrape_twitter_bot(bot)
    print scrape_response
    data = {'success': True, 'new tweets': scrape_response['new tweets'], 'tweets':
            scrape_response['tweets']}
    return data


def get_info(bot_id):
    bot = TwitterBot.objects.get(id=bot_id)
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

    t = TweepyScraper(
        settings.TWEEPY_CONSUMER_KEY,
        settings.TWEEPY_CONSUMER_SECRET,
        settings.TWEEPY_ACCESS_TOKEN,
        settings.TWEEPY_ACCESS_TOKEN_SECRET)

    tweets = t.get_tweets_from_user(bot.username, 100)

    response_data['new tweets'] = len(tweets)
    response_data['tweets'] = {}

    for idx, tweet_data in enumerate(tweets):
        tweet = tweet_data[0]
        tweet_id = tweet_data[1]
        words = tweet.split()
        for word in words:
            if "@" in word:
                bot.twittermention_set.create(content=word)
            if "http" in word:
                bot.twitterlink_set.create(content=word)
            if "#" in word:
                bot.twitterhashtag_set.create(content=word)

        response_data['tweets'][idx] = str(tweet_data)

        h = HTMLParser.HTMLParser()
        tweet = h.unescape(tweet.decode('utf-8'))

        post = TwitterPost.objects.create(author=bot, content=tweet, tweet_id=tweet_id)

        create_post_cache(post, bot.twitterpostcache_set)

    return response_data


def get_or_create_conversation(bot1_id, bot2_id):
    bot = TwitterBot.objects.get(id=bot1_id)
    partner = TwitterBot.objects.get(id=bot2_id)

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


def get_or_create_conversation_json(bot1_id, bot2_id):
    conversation = get_or_create_conversation(bot1_id, bot2_id)
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


def clear_twitter_conversation(bot1_id, bot2_id, conversation=None):
    if not conversation:
        conversation = get_or_create_conversation(bot1_id, bot2_id)

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


def get_next_speaker_and_last_speaker(conversation_posts, author, partner):
    """
    Figure out the order of speech
    Start by guessing, that the author spoke last
    If there are more than 0 posts and in it was actually the parter who spoke last,
    swith our assignments
    """
    last_speaker = author
    next_speaker = partner

    last_post = conversation_posts.last()
    if last_post:
        if last_post.author == next_speaker:
            last_speaker = partner
            next_speaker = author

    return next_speaker, last_speaker


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


def generate_new_conversation_post_text(conversation):
    """
    Query set of the conversation posts in the current conversation, sorted chronologically
    """
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

    if new_conversation:
        key_phrases = []
    else:
        key_phrases = get_key_phrases(sorted_conversation_posts)
    # reply = generate_response_with_key_phrases(key_phrases, next_speaker, last_speaker)
    reply = get_web_text_response(sorted_conversation_posts)

    return index, next_speaker, reply


def get_tweets_over_reply_threshold_and_analyze_text_emotion(username, scrape_mode='recurse', threshold=1):
    tweets = get_tweets_over_reply_threshold(username, scrape_mode, threshold)
    for tweet_id, tweet_data in tweets.iteritems():
        text = tweet_data['content']
        emotion_dict = watson_analyze_text_emotion(text)
        emotion, probability = emotion_dict.iteritems().next()
        tweet_data.update({'emotion': emotion})
        tweets[tweet_id] = tweet_data
    return tweets


def get_tweets_over_reply_threshold_and_analyze_text_understanding(username, scrape_mode='recurse', threshold=1):
    tweets = get_tweets_over_reply_threshold(username, scrape_mode, threshold)
    for tweet_id, tweet_data in tweets.iteritems():
        text = tweet_data['content']
        emotion_dict = watson_analyze_text_uderstanding(text)
        emotion, probability = emotion_dict.iteritems().next()
        tweet_data.update({'emotion': emotion})
        tweets[tweet_id] = tweet_data
    return tweets


def get_tweets_over_reply_threshold(username, scrape_mode='recurse', threshold=1):
    if scrape_mode == 'recurse':
        reply_function = recursively_get_replies
    elif scrape_mode == 'highest_reply_number':
        reply_function = highest_reply_number
    elif scrape_mode == 'single_reply':
        reply_function = single_reply
    elif scrape_mode == 'first_responder':
        reply_function = first_responder
    else:
        reply_function = None
    print('method: %s' % str(reply_function))

    length_limiter = 5

    bot = TwitterBot.objects.get(username=username)
    browser = mechanize.Browser()
    ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0 (compatible;)'
    browser.addheaders = [('User-Agent', ua), ('Accept', '*/*')]

    tweets_over_threshold = {}
    # Get viable top level tweets, that have reply count over the threshold
    print "looping on the bot's tweets"
    for tweet in bot.twitterpost_set.all()[:length_limiter]:
        reply_data = get_tweet_replies(browser, username, tweet.tweet_id)
        num_replies = len(reply_data)
        if num_replies >= threshold:
            print('lots of replies; recursing')
            tweets_over_threshold[tweet.tweet_id] = \
                {'content': tweet.content, 'replies': reply_function(browser, username, tweet.tweet_id)}
            return tweets_over_threshold
    # Recursive find replies to get the entire thread for each tweet
    return tweets_over_threshold


def highest_reply_number(browser, username, tweet_id):
    print('getting replies for %s' % tweet_id)
    all_responses = get_tweet_replies(browser, username, tweet_id)
    highest_reply_number = 0
    tweet_with_highest_reply_number = None
    if len(all_responses) > 0:
        for reply_id, response_data in all_responses.iteritems():
            reply_number = get_tweet_replies(browser, response_data['author'], reply_id)
            print('reply number for reply %d is: %d' % (int(reply_id), reply_number))
            if reply_number == 0:
                return {}
            if reply_number > highest_reply_number:
                highest_reply_number = reply_number
                tweet_with_highest_reply_number = response_data
        return {'author': tweet_with_highest_reply_number['author'],
                'content': tweet_with_highest_reply_number['content'],
                'reply': highest_reply_number(browser, tweet_with_highest_reply_number['author'], reply_id)}


def single_reply(browser, username, tweet_id):
    replies = {}
    all_responses = get_tweet_replies(browser, username, tweet_id)
    if len(all_responses) > 0:
        for reply_id, response_data in all_responses.iteritems():
            replies[reply_id] = {'author': response_data['author'], 'content': response_data['content'], 'replies':
                                 recursively_get_replies(browser, username, reply_id)}
    return replies


def first_responder(browser, username, tweet_id):
    replies = {}
    all_responses = get_tweet_replies(browser, username, tweet_id)
    if len(all_responses) > 0:
        reply_id, response_data = all_responses.iteritems().next()
        replies[reply_id] = {'author': response_data['author'], 'content': response_data['content'], 'replies':
                             first_responder(browser, username, reply_id)}
    return replies


def recursively_get_replies(browser, username, tweet_id):
    replies = {}
    all_responses = get_tweet_replies(browser, username, tweet_id)

    if len(all_responses) > 0:
        for reply_id, response_data in all_responses.iteritems():
            replies[reply_id] = {'author': response_data['author'], 'content': response_data['content'], 'replies':
                                 recursively_get_replies(browser, username, reply_id)}
    return replies


def get_tweet_replies(browser, username, tweet_id):
    url = 'https://twitter.com/{0}/status/{1}'.format(username, tweet_id)
    browser.open(url)
    html = browser.response().read().decode('utf-8', 'ignore')
    raw = BeautifulSoup(html, "html.parser")
    replies_div = raw.find('div', class_='replies-to')
    replies = replies_div.find_all('div', class_='ThreadedConversation-tweet')

    # If there are no replies, stop
    if not replies:
        return {}

    all_tweets = []
    for reply in replies:
        tweets = reply.find_all('div', class_='tweet')
        all_tweets.extend(tweets)

    all_responses = {}
    for tweet in all_tweets:
        content = tweet.find_all('div', class_='content')[0]
        inner_content = content.find_all('div', class_='js-tweet-text-container')[0]
        text = inner_content.find('p')

        screen_name = tweet['data-screen-name']
        tweet_id = tweet['data-tweet-id']
        all_responses[tweet_id] = {'author': screen_name, 'content': text.text}

    return all_responses


def add_to_twitter_conversation(bot_username, partner_username):
    conversation = get_or_create_conversation(bot_username, partner_username)

    new_index, new_author, new_content = generate_new_conversation_post_text(conversation)
    new_post = new_author.twitterpost_set.create(content=new_content)

    new_convo_post = TwitterConversationPost.objects.create(
        post=new_post,
        conversation=conversation,
        author=new_author,
        index=new_index
    )
    new_post_json = {'author': new_convo_post.author.username,
                     'index': new_convo_post.index,
                     'conversation': new_convo_post.conversation.id,
                     'content': new_convo_post.post.content}
    return new_post_json


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


def watson_analyze_text_uderstanding(text):
    username = settings.WATSON_UNDERSTANDING_USERNAME
    password = settings.WATSON_UNDERSTANDING_PASSWORD
    url = 'https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2017-02-27'

    features = {
        "entities": {
            "emotion": True,
            "sentiment": True,
            "limit": 2
        },
        "keywords": {
            "emotion": True,
            "sentiment": True,
            "limit": 2
        }
    }
    data = {'parameters': {'text': text, 'features': features}}
    headers = {"content-type": "text/plain"}
    response = requests.post(url, auth=(username, password), headers=headers, data=json.dumps(data))

    print response
    print response.content


def watson_analyze_text_emotion(data):
    username = settings.WATSON_TONE_USERNAME
    password = settings.WATSON_TONE_PASSWORD
    url = 'https://gateway.watsonplatform.net/tone-analyzer/api/v3/tone?version=2017-09-21&text='

    headers = {"content-type": "text/plain"}
    response = requests.post(url, auth=(username, password), headers=headers, data=data.encode('utf8'))
    response_json = json.loads(response)

    tone_dict = response_json['document_tone']['tones']
    readable_dict = {x['tone_name']: x['score'] for x in tone_dict}
    return readable_dict
