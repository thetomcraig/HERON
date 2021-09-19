"""
Very general utilities for working with twitter bots
TwitterBots created and updated mostly using the Tweepy API, via TwitterApiInterface
"""
from bots.helpers.twitter_api_interface import TwitterApiInterface
from bots.helpers.twitter_bot_utils.crud_utils import get_twitter_bot
from bots.helpers.twitter_bot_utils.twitter_post_creation_utils import process_new_tweets
from bots.models.twitter import TwitterBot
from django.conf import settings
import logging

logger = logging.getLogger("django")


def scrape_twitter_bot(bot):
    """
    Scrape the given user with tweepy
    Clean up all of their tweets and process them
    """
    response_data = {"success": False}

    t = TwitterApiInterface(
        settings.TWEEPY_CONSUMER_KEY,
        settings.TWEEPY_CONSUMER_SECRET,
        settings.TWEEPY_ACCESS_TOKEN,
        settings.TWEEPY_ACCESS_TOKEN_SECRET,
    )

    tweets = t.get_tweets_from_user(bot.username, 100)
    num_tweets = len(tweets)

    response_data["num_new_tweets"] = num_tweets
    response_data["new_tweets"] = {idx: tweet for (idx, tweet) in enumerate(tweets.values())}

    process_new_tweets(bot, tweets)
    logger.debug("Processed {} new tweets".format(num_tweets))

    response_data["success"] = True

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
    bot = get_twitter_bot(username)
    if not bot:
        return {
            "success": False,
            "msg": 'No bot found with username: "{}"'.format(username),
        }

    scrape_response = scrape_twitter_bot(bot)

    scrape_successful = scrape_response.get("success")
    if not scrape_successful:
        return {
            "success": False,
            "msg": 'Scraping failed for username: "{}"'.format(username),
        }

    return {
        "success": True,
        "new tweets": scrape_response["new_tweets"],
        "num_new_tweets": scrape_response["num_new_tweets"],
    }
