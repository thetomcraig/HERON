import HTMLParser
import logging
from bots.models.twitter import (
    TwitterPost,
    TwitterLink,
    TwitterHashtag,
    TwitterMention,
    TwitterPostCache,
)
from django.conf import settings

logger = logging.getLogger("django")


def process_new_tweets(bot, tweets):
    """
    Usually called with data from a Twitter API call
    """
    parser = HTMLParser.HTMLParser()

    logger.debug("Processing {} new tweets:".format(len(tweets)))
    for tweet_id, tweet in tweets.iteritems():
        logger.debug("Processing {}: {}".format(tweet_id, tweet))
        clean_tweet = parser.unescape(tweet.decode("utf-8"))
        is_retweet = tweet.startswith("RT")

        (template_text, caches, template_caches, links, hashtags, mentions,) = parse_tweet(
            clean_tweet
        )

        TwitterPost.objects.create(
            author=bot,
            content=tweet,
            tweet_id=tweet_id,
            template=template_text,
            retweet=is_retweet,
        )

        for idx, (cache_words, template_cache_words) in enumerate(zip(caches, template_caches)):
            if idx == 0:
                beginning = True
            else:
                beginning = False
            TwitterPostCache.create_with_tuples(bot, beginning, cache_words, template_cache_words)

        for link in links:
            TwitterLink.create(author=bot, content=link)
        for tag in hashtags:
            TwitterHashtag.create(author=bot, content=tag)
        for mention in mentions:
            TwitterMention.create(author=bot, content=mention)

    return True


def parse_tweet(text):
    template_text = []
    caches = []
    template_caches = []
    links = []
    hashtags = []
    mentions = []

    words = text.split()

    # If it's a retweet, remove the first two words,
    # which will be "RT" and the name of the tweeter
    if len(words) >= 3:
        if words[0] == "RT":
            words = words[2:]

    num_words = len(words)
    for idx, word in enumerate(words):
        template_word = word
        if word.startswith("http"):
            links.append(word)
            template_word = settings.LINK_TOKEN
        elif word.startswith("#"):
            hashtags.append(word[1:])
            template_word = settings.LINK_TOKEN
        elif word.startswith("@"):
            mentions.append(word[1:])
            template_word = settings.USER_TOKEN

        template_text.append(template_word)

        if idx < num_words - 2:
            caches.append((word, words[idx + 1], words[idx + 2]))

    for idx, word in enumerate(template_text):
        if idx < num_words - 2:
            template_caches.append((word, template_text[idx + 1], template_text[idx + 2]))

    logger.debug(
        "\n".join(
            [
                "Parsed into:",
                "template_text: {}",
                "caches: {}",
                "template_caches: {}",
                "links: {}",
                "hashtags: {}",
                "mentions: {}",
            ]
        ).format(template_text, caches, template_caches, links, hashtags, mentions)
    )
    return " ".join(template_text), caches, template_caches, links, hashtags, mentions


#  def make_twitter_post(bot, tweet_id, tweet, template, is_retweet):
#  post = TwitterPost.objects.create(
#  author=bot,
#  content=tweet,
#  tweet_id=tweet_id,
#  template=template,
#  retweet=is_retweet,
#  )
#  logger.debug("Created TwitterPost: {}".format(tweet.encode("utf-8")))
#  return post
