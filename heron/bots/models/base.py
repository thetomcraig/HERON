import random
from django.db import models


class Bot(models.Model):
    real_name = models.CharField(max_length=1000, default="PLACEHOLDER")
    first_name = models.CharField(max_length=1000, default="PLACEHOLDER")
    last_name = models.CharField(max_length=1000, default="PLACEHOLDER")
    username = models.CharField(max_length=1000, default="PLACEHOLDER")
    avatar = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)

    class Meta:
        abstract = True


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

    class Meta:
        abstract = True

    word1 = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    word2 = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    final_word = models.CharField(max_length=1000, default="PLACEHOLDER", null=True)
    beginning = models.BooleanField(default=False)
