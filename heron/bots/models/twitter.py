# at artandlogic.com modles for comment storing)
import logging
from django.db import models

import base


logger = logging.getLogger("django")


class TwitterBot(base.Bot):
    def __str__(self):
        return self.username


class TwitterPost(base.Sentence):
    """
    This is a real tweet, recorded exactly
    If the "tweet_id" is -1, then it's not real
    """

    author = models.ForeignKey(TwitterBot, default=None, null=True)
    template = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    emotion = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    tweet_id = models.IntegerField(null=True)
    retweet = models.BooleanField(default=False)


class TwitterPostCache(models.Model):
    cache = models.ForeignKey(base.SentenceCache, related_name="cache", default=None, null=True)
    template_cache = models.ForeignKey(
        base.SentenceCache, related_name="template_cache", default=None, null=True
    )
    author = models.ForeignKey(TwitterBot, default=None, null=True)
    beginning = models.BooleanField(default=False)

    def __str__(self):
        beginning_string = "   "
        if self.beginning_string:
            beginning_string = "b: "
        return "{}, author: {}\n   cache: {}\n    template_cache: {}".format(
            beginning_string, self.author, str(self.cache), str(self.template_cache)
        )

    @classmethod
    def create_with_tuples(cls, bot, beginning, cache_tuple, template_tuple):
        cache = base.SentenceCache(beginning=beginning, *cache_tuple)
        template_cache = base.SentenceCache(beginning=beginning, *template_tuple)
        twitter_post_cache = cls(
            author=bot, beginning=beginning, cache=cache, template_cache=template_cache
        )
        logger.debug("Created: \n{}".format(cls.__str__()))
        return twitter_post_cache


class TwitterPostMarkov(base.MarkovChain):
    author = models.ForeignKey(TwitterBot, default=None)


class TwitterLink(base.Word):
    author = models.ForeignKey(TwitterBot)


class TwitterHashtag(base.Word):
    author = models.ForeignKey(TwitterBot)


class TwitterMention(base.Word):
    author = models.ForeignKey(TwitterBot)


class TwitterConversation(models.Model):
    name = models.CharField(max_length=1000, default="PLACEHOLDER")
    author = models.ForeignKey(TwitterBot, related_name="author", null=True)
    partner = models.ForeignKey(TwitterBot, null=True)


class TwitterConversationPost(models.Model):
    conversation = models.ForeignKey(TwitterConversation)
    post = models.ForeignKey(TwitterPost)
    author = models.ForeignKey(TwitterBot)
    index = models.IntegerField()
