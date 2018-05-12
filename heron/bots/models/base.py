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
            All of the beginning caches for a bot
            All of the caches for a user
        Output:
            New text message made with markov chains using the input
            Float of how random the chain is

        Caches are triplets of consecutive words from the source
        Beginning=True means the triplet was the bginning of a messaeg

        Starts with a random choice from the beginning caches
        makes random choices from the all_caches set, constructing a markov chain
        'randomness' value determined by totalling the number of words that were chosen randomly
        """
        new_markov_chain = []
        randomness = -0.0

        if not beginning_caches:
            print "Not enough data, skipping"
            return ('', randomness)

        seed_index = 0
        if len(beginning_caches) != 0:
            seed_index = random.randint(0, len(beginning_caches) - 1)
        seed_cache = beginning_caches[seed_index]

        w0 = seed_cache.word1
        w1 = seed_cache.word2
        w2 = seed_cache.final_word
        new_markov_chain.append(w0)
        new_markov_chain.append(w1)

        # percentage, calculated by the number of random
        # choices made to create the markov post
        randomness = 0
        while True:
            try:
                new_markov_chain.append(w2)
                all_next_caches = all_caches.filter(word1=w1, word2=w2)
                next_cache_index = random.randint(0, len(all_next_caches) - 1)
                next_cache = all_next_caches[next_cache_index]
                w1 = next_cache.word2
                w2 = next_cache.final_word

                if len(all_next_caches) > 1:
                    randomness = randomness + 1

            except Exception as e:
                print e
                print "Done"
                break

        # Determind random level, and save the post
        randomness = 1.0 - float(randomness) / len(new_markov_chain)
        # Done making the post

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
    the markov posts uses these
    """
    class Meta:
        abstract = True

    word1 = models.CharField(max_length=1000, default='PLACEHOLDER', null=True)
    word2 = models.CharField(max_length=1000, default='PLACEHOLDER', null=True)
    final_word = models.CharField(max_length=1000, default='PLACEHOLDER', null=True)
    beginning = models.BooleanField(default=False)
