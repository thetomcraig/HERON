from bots.models.twitter import TwitterBot, TwitterPost
from django.conf import settings

from bots.helpers.twitter_getters import (
    get_tweets_over_reply_threshold_and_analyze_text_understanding,
)


def list_all_emotion_twitter_bots():
    bot_data = {}
    for emotion in settings.WATSON_EMOTIONS:
        bot_name = emotion + "_bot"
        bot, _ = TwitterBot.objects.get_or_create(username=bot_name)
        tweets = TwitterPost.objects.filter(author=bot)
        bot_data[bot_name] = {"tweets": [x.content for x in tweets]}
    return bot_data


def get_emotion_tweets():
    bot_meta_data = {}
    for emotion in settings.WATSON_EMOTIONS:
        tweets = TwitterPost.objects.filter(emotion=emotion)
        bot_meta_data[emotion] = []
        for tweet in tweets:
            bot_meta_data[emotion].append(
                {"id": tweet.id, "emotion": emotion, "content": tweet.content}
            )

    return bot_meta_data


def add_new_tweets_to_emotion_bot(params):
    twitter_source_users = params.get("twitter_source_users")
    response_number = params.get("response_number")

    new_bot_tweets = {}
    for emotion in settings.WATSON_EMOTIONS:
        new_bot_tweets[emotion] = []
    threshold = 1
    scrape_mode = "single_reply"

    for username in twitter_source_users:
        print "getting responses for source user: %s" % username
        response_data = get_tweets_over_reply_threshold_and_analyze_text_understanding(
            username,
            scrape_mode,
            threshold=int(threshold),
            max_response_number=int(response_number),
        )
        for tweet_id, tweet_data in response_data.iteritems():
            replies = tweet_data["replies"]
            if replies:
                for reply_id, reply_content in replies.iteritems():
                    emotion = reply_content["overarching_emotion"]
                    if emotion in settings.WATSON_EMOTIONS:
                        content = reply_content["content"]
                        bot, _ = TwitterBot.objects.get_or_create(
                            username=emotion + "_bot"
                        )
                        bot.twitterpost_set.create(tweet_id=reply_id, content=content)
                        create_post_cache(content, bot.twitterpostcache_set)
                        new_bot_tweets[emotion].append(reply_content["content"])

    return new_bot_tweets
