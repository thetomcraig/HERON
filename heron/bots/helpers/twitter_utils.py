import HTMLParser
import nltk
from nltk.corpus import wordnet as wn
from nltk.probability import FreqDist
from rake_nltk import Rake

from django.conf import settings

from bots.models.twitter import TwitterPost, TwitterBot, TwitterConversation, TwitterConversationPost
from bots.helpers.TweepyScraper import TweepyScraper

from .utils import (
    replace_tokens,
    create_post_cache,
)


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


def scrape(bot_id):
    bot = TwitterBot.objects.get(id=bot_id)
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

    for idx, tweet in enumerate(tweets):
        words = tweet.split()
        for word in words:
            if "@" in word:
                bot.twittermention_set.create(content=word)
            if "http" in word:
                bot.twitterlink_set.create(content=word)
            if "#" in word:
                bot.twitterhashtag_set.create(content=word)

        response_data['tweets'][idx] = tweet

        h = HTMLParser.HTMLParser()
        tweet = h.unescape(tweet.decode('utf-8'))

        post = TwitterPost.objects.create(author=bot, content=tweet)

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


def get_next_speaker_and_partner(conversation):
    last_post = conversation.last()
    partner = last_post.author

    bot1 = last_post.conversation.author
    bot2 = last_post.conversation.partner
    if bot1 == partner:
        next_speaker = bot2
    else:
        next_speaker = bot1

    return next_speaker, partner


def get_key_phrases(conversation):
    last_post = conversation.last()
    r = Rake()
    r.extract_keywords_from_text(last_post.post.content)
    # TODO Filter further
    phrases = r.get_ranked_phrases()
    return phrases


def generate_response_with_key_phrases(key_phrases, author, partner):
    for tweet in author.twitterpost_set.all():
        for phrase in key_phrases:
            if phrase in tweet.content:
                print phrase
                print tweet.content
                print 'success'
            for synset in wn.synsets(phrase):
                for lemma in synset.lemmas():
                    if lemma.name() in tweet.content:
                        print lemma.name()
                        print tweet.content
    # Search for tweets that contain the given key phrase or a synonym
    # Searh the author's tweets for something with that phrase

    # Search responess (containing '@') and replace that mention with the partner
    # Use the response as a template for the new response
    return 'STUB'


def generate_new_conversation_post_text(current_conversation):
    """
    Query set of the conversation posts in the current conversation, sorted chronologically
    """
    index = current_conversation.last().index
    next_speaker, partner = get_next_speaker_and_partner(current_conversation)
    key_phrases = get_key_phrases(current_conversation)
    reply = generate_response_with_key_phrases(key_phrases, next_speaker, partner)

    return index, next_speaker, reply


def add_to_twitter_conversation(bot_username, partner_username):
    conversation = get_or_create_conversation(bot_username, partner_username)
    sorted_conversation = conversation.twitterconversationpost_set.order_by('index').all()

    new_index, new_author, new_content = generate_new_conversation_post_text(sorted_conversation)
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
