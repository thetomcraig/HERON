import HTMLParser
import logging
import random
from bots.models.twitter import TwitterPost, TwitterPostTemplate
from django.conf import settings


def process_new_tweets(bot, tweets):
    """
    Usually called with data from a Twitter API call
    """
    parser = HTMLParser.HTMLParser()

    logging.debug("Processing {} new tweets:".format(len(tweets)))
    for tweet_id, tweet in tweets.iteritems():
        logging.debug("Processing {}: {}".format(tweet_id, tweet))
        clean_tweet = parser.unescape(tweet.decode("utf-8"))
        is_retweet = tweet.startswith("RT")

        post = make_twitter_post(bot, tweet_id, clean_tweet, is_retweet)
        make_twitter_post_cache(bot, post.content, bot.twitterpostcache_set)

        template_post = make_twitter_post_template(bot, clean_tweet, is_retweet)
        make_twitter_post_cache(bot, template_post.content, bot.twitterposttemplatecache_set)

    return True


def make_twitter_post(bot, tweet_id, tweet, is_retweet):
    """
    First make a TwitterPost object with this tweet
    Then, tokenize, and make a Template object for it
    Also, make any auxilliary objects necessary
    """
    post = TwitterPost.objects.create(
        author=bot, content=tweet, tweet_id=tweet_id, retweet=is_retweet
    )
    logging.debug("Created TwitterPost: {}".format(tweet.encode("utf-8")))
    return post


def make_twitter_post_template(bot, tweet, is_retweet):
    words = tweet.split()
    tokenized_words = []
    for word in words:
        if word.startswith("@"):
            bot.twittermention_set.create(content=word[1:])
            word = settings.USER_TOKEN
        if word.startswith("http"):
            bot.twitterlink_set.create(content=word)
            word = settings.LINK_TOKEN
        if word.startswith("#"):
            bot.twitterhashtag_set.create(content=word[1:])
            word = settings.TAG_TOKEN
        tokenized_words.append(word)
    tokenized_tweet = " ".join(tokenized_words)

    template_post = TwitterPostTemplate.objects.create(
        author=bot, content=tokenized_tweet, retweet=is_retweet
    )

    logging.debug(
        "Tokenized tweet: {} => {}".format(
            tweet.encode("utf-8"), template_post.content.encode("utf-8")
        )
    )

    return template_post


def make_twitter_post_cache(words, cache_set):
    """
    Create the postcache item from the new post
    to be used to make the markov post
    For example:
        words = "The quick brown fox jumped"
    Will become:
        TwitterPostCache(The, quick, brown, beginning=True)
        TwitterPostCache(quick, brown, fox, beginning=False)
        TwitterPostCache(brown, fox, jumped, beginning=False)

    """
    word_list = words.split()
    for index in range(len(word_list) - 2):
        word1 = word_list[index]
        word2 = word_list[index + 1]
        final_word = word_list[index + 2]

        logging.debug("caching:")
        logging.debug(word1)
        logging.debug(word2)
        logging.debug("|")
        logging.debug("`--> " + final_word)

        beginning = False
        if index == 0:
            beginning = True

            cache_set.create(
                word1=word1, word2=word2, final_word=final_word, beginning=beginning
            )


def replace_tokens(word_list_and_randomness, token, model_set):
    """
    Takes a list of words and replaces tokens with the
    corresonding models linked to the user
    """
    word_list = word_list_and_randomness[0]
    for word_index in range(len(word_list)):
        if token in word_list[word_index]:
            seed_index = 0
            if len(model_set) > 1:
                seed_index = random.randint(0, len(model_set) - 1)
            try:
                word_list[word_index] = (model_set[seed_index]).content
                print "Replaced " + token

            except IndexError:
                print "failed to replace token:"
                print word_list[word_index]

    return (word_list, word_list_and_randomness[1])
