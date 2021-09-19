from django.db import models
import logging


class Bot(models.Model):
    class Meta:
        abstract = True

    real_name = models.CharField(max_length=1000, default="PLACEHOLDER")
    first_name = models.CharField(max_length=1000, default="PLACEHOLDER")
    last_name = models.CharField(max_length=1000, default="PLACEHOLDER")
    username = models.CharField(max_length=1000, default="PLACEHOLDER")
    avatar = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)


class Word(models.Model):
    class Meta:
        abstract = True

    content = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)

    def __str__(self):
        return self.content

    @classmethod
    def create(cls, content):
        word = cls(content)
        logging.debug("Created: \n{}".format(str(word)))
        return cls


class Sentence(models.Model):
    class Meta:
        abstract = True

    content = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    happiness = models.FloatField(default=0)

    def sentiment_analyze(self):
        self.happiness = 5

    def __str__(self):
        return self.content


class MarkovChain(models.Model):
    class Meta:
        abstract = True

    content = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    randomness = models.FloatField(default=0.0)

    def __str__(self):
        return (
            " author: "
            + str(self.author)
            + "\n"
            + " content: "
            + self.content.encode("utf-8")
            + "\n"
            + " randomness "
            + str(self.randomness)
            + "\n"
        )


class SentenceCache(models.Model):
    """
    Used to cache words from the original posts
    to be used to make the markov post

    For example:
        words = "The quick brown fox jumped"
    Will become:
        SentenceCache(The, quick, brown, beginning=True)
        SentenceCache(quick, brown, fox, beginning=False)
        SentenceCache(brown, fox, jumped, beginning=False)
    """
    word1 = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    word2 = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    final_word = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    beginning = models.BooleanField(default=False)

    def __str__(self):
        beginning_string = "   "
        if self.beginning_string:
            beginning_string = "b: "
        return "{} {}: ({}, {})".format(
            beginning_string, self.word1, self.word2, self.final_word
        )

    @classmethod
    def create(cls, beginning, word1, word2, final_word):
        cache = cls(
            beginning=beginning, word1=word1, word2=word2, final_word=final_word
        )
        logging.debug("Created: \n{}".format(str(cls)))
        return cache
