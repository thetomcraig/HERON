import random
from django.db import models


class Bot(models.Model):
  real_name = models.CharField(max_length=1000, default='PLACEHOLDER')
  first_name = models.CharField(max_length=1000, default='PLACEHOLDER')
  last_name = models.CharField(max_length=1000, default='PLACEHOLDER')
  username = models.CharField(max_length=1000, default='PLACEHOLDER')
  avatar = models.CharField(max_length=1000, default='PLACEHOLDER', null=True)

  class Meta:
    abstract = True

  def apply_markov_chains_inner(self, beginning_caches, all_caches):
    """
    Input:
        All of the beginning caches for a user
        All of the caches for a user
    Output:
        New message made with markov chains using the input
        Float of how random the message is

    Caches are triplets of consecutive words from the source
    Beginning=True means the triplet was the beinning of a messaeg

    Starts with a random choice from the beginning caches
    Then makes random choices from the all_caches set, constructing a markov chain
    'randomness' value determined by totalling the number of words that were chosen randomly
    """
    new_markov_chain = []
    randomness = 0.0

    if not len(beginning_caches):
      print "Not enough data, skipping"
      return ('', randomness)

    # Randomly choose one of the beginning caches to start with
    seed_index = random.randint(0, len(beginning_caches) - 1)
    seed_cache = beginning_caches[seed_index]

    new_markov_chain.append(seed_cache.word1)
    new_markov_chain.append(seed_cache.word2)

    # Add words one by one to complete the markov chain
    # If we don't have enough data to make an actual markov chain, fall back on an actual post
    next_cache = seed_cache
    while next_cache:
      new_markov_chain.append(next_cache.final_word)
      all_next_caches = all_caches.filter(word1=next_cache.word2, word2=next_cache.final_word)
      if len(all_next_caches):
        next_cache = random.choice(all_next_caches)
      else:
        all_next_caches = all_caches.filter(word1=next_cache.final_word)
        if len(all_next_caches):
          next_cache = random.choice(all_next_caches)
          new_markov_chain.append(next_cache.word2)
        else:
          next_cache = None

    print "made: "
    print new_markov_chain, randomness

    return (' '.join(new_markov_chain), randomness)


class Sentence(models.Model):

  class Meta:
    abstract = True

  content = models.CharField(max_length=1000, default='PLACEHOLDER', null=True)
  happiness = models.FloatField(default=0)

  def sentiment_analyze(self):
    self.happiness = 5

  def __str__(self):
    return self.content


class MarkovChain(models.Model):

  class Meta:
    abstract = True

  content = models.CharField(max_length=1000, default='PLACEHOLDER', null=True)
  randomness = models.FloatField(default=0.0)

  def __str__(self):
    return ' author: ' + str(self.author) + '\n' + \
        ' content: ' + self.content.encode('utf-8') + '\n' + \
        ' randomness ' + str(self.randomness) + '\n'


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

  word1 = models.CharField(max_length=1000, default='PLACEHOLDER', null=True)
  word2 = models.CharField(max_length=1000, default='PLACEHOLDER', null=True)
  final_word = models.CharField(
      max_length=1000,
      default='PLACEHOLDER',
      null=True)
  beginning = models.BooleanField(default=False)
