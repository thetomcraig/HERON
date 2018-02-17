import random


def clear_set(set_to_clear):
    [x.delete() for x in set_to_clear]


def create_post_cache(words, cache_set):
    """
    Create the postcache item from the new post
    to be used to make the markov post
    """
    print words
    word_list = words.split()
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
