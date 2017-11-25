from nltk import (
    FreqDist,
    NaiveBayesClassifier,
    classify,
)
import random


def clear_set(set_to_clear):
    [x.delete() for x in set_to_clear]


def create_post_cache(post, cache_set):
    """
    Create the postcache item from the new post
    to be used to make the markov post
    """
    word_list = post.content.split()
    for index in range(len(word_list) - 2):
        word1 = word_list[index]
        word2 = word_list[index + 1]
        final_word = word_list[index + 2]

        print "caching:"
        print word1
        print word2
        print "|"
        print "`--> " + final_word

        beginning = False
        if (index == 0):
            beginning = True

        cache_set.create(word1=word1, word2=word2, final_word=final_word, beginning=beginning)


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


class Classifier():
    def __init__(self):
        all_sentences =[]
        classifier = None

    def trim_sentences(self, sentences):
        cut_sentences = []
        for sentence in sentences:
            cut_sentence = []
            for word in sentence.lower().split(' '):
                if len(word) >= 3:
                    cut_sentence.append(word)
            cut_sentences.append(cut_sentence)
        return cut_sentences

    def get_words_from_tagged_sentences(self, tagged_sentences):
        all_words = []
        for (words, sentiment) in tagged_sentences:
            for word in words:
                all_words.append(word)
        return all_words

    def get_word_features(self, words):
        word_list = FreqDist(words)
        word_features = word_list.keys()
        return word_features

    def extract_features(self, word_list):
        words = set(word_list)
        features = {}
        for word in self.word_features:
            features['contains(%s)' % word] = (word in words)
        return features

    def train(self, training_set):
        """
        training_set should be a dict
        {
            pos: [list of strings]
            neg: [list of strings]
        }
        """
        trimmed_pos = self.trim_sentences(training_set['pos'])
        tagged_pos = [(x, 'positive') for x in trimmed_pos]
        trimmed_neg = self.trim_sentences(training_set['neg'])
        tagged_neg = [(x, 'negative') for x in trimmed_neg]
        all_sentences = tagged_pos + tagged_neg

        all_words = self.get_words_from_tagged_sentences(all_sentences)
        self.word_features = self.get_word_features(all_words)
        training_set = classify.apply_features(self.extract_features, all_sentences)
        self.classifier = NaiveBayesClassifier.train(training_set)

    def classify(self, test_tweet): 
        if not self.classifier:
            print('train first!')
            return

        # print classifier.show_most_informative_features(20)
        return self.classifier.classify(self.extract_features(test_tweet.split()))

