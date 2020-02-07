# at artandlogic.com modles for comment storing)
from django.db import models

import base


class TwitterBot(base.Bot):
    def __str__(self):
        return self.username


class TwitterPost(base.Sentence):
    author = models.ForeignKey(TwitterBot, default=None, null=True)
    emotion = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    tweet_id = models.IntegerField(null=True)
    retweet = models.BooleanField(default=False)


class TwitterPostCache(base.SentenceCache):
    author = models.ForeignKey(TwitterBot, default=None, null=True)


class TwitterPostMarkov(base.MarkovChain):
    author = models.ForeignKey(TwitterBot, default=None)


class TwitterLink(models.Model):
    author = models.ForeignKey(TwitterBot)
    content = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)

    def __str__(self):
        return self.content


class TwitterHashtag(models.Model):
    author = models.ForeignKey(TwitterBot)
    content = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)

    def __str__(self):
        return self.content


class TwitterMention(models.Model):
    author = models.ForeignKey(TwitterBot)
    content = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)

    def __str__(self):
        return self.content


class TwitterConversation(models.Model):
    name = models.CharField(max_length=1000, default="PLACEHOLDER")
    author = models.ForeignKey(TwitterBot, related_name="author", null=True)
    partner = models.ForeignKey(TwitterBot, null=True)


class TwitterConversationPost(models.Model):
    conversation = models.ForeignKey(TwitterConversation)
    post = models.ForeignKey(TwitterPost)
    author = models.ForeignKey(TwitterBot)
    index = models.IntegerField()
