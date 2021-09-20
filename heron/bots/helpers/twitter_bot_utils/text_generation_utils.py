import random
from bots.helpers.watson_utils import interpret_watson_keywords_and_entities
from bots.models.twitter import TwitterBot


def markov_chain(bot_id, previous_posts):
    """
    Caches are triplets of consecutive words from the source
    Beginning=True means the triplet was the beinning of a messaeg

    Starts with a random choice from the beginning caches
    Then makes random choices from the all_caches set, constructing a markov chain
    'randomness' value determined by totalling the number of words that were chosen randomly
    """
    bot = TwitterBot.objects.get(id=bot_id)
    beginning_caches = bot.twitterpostcache_set.filter(beginning=True)

    if not len(beginning_caches):
        print("Not enough data")
        return

    # Randomly choose one of the beginning caches to start with
    seed_index = random.randint(0, len(beginning_caches) - 1)
    seed_cache = beginning_caches[seed_index]
    # Start the chain
    new_markov_chain = [seed_cache.word1, seed_cache.word2]

    # Add words one by one to complete the markov chain
    all_caches = bot.twitterpostcache_set.all()
    next_cache = seed_cache
    while next_cache:
        new_markov_chain.append(next_cache.final_word)
        all_next_caches = all_caches.filter(
            word1=next_cache.word2, word2=next_cache.final_word
        )
        if len(all_next_caches):
            next_cache = random.choice(all_next_caches)
        else:
            all_next_caches = all_caches.filter(word1=next_cache.final_word)
            if len(all_next_caches):
                next_cache = random.choice(all_next_caches)
                new_markov_chain.append(next_cache.word2)
            else:
                next_cache = None

    return " ".join(new_markov_chain)


def markov_template_with_sentiment_replacement(bot_id, previous_posts):
    pass


def template_with_sentiment_replacement(bot_id, previous_posts):
    pass


#  def replace_temp_with_watson_shit():
    #  new_markov_template, _ = create_markov_chain_with_caches(
        #  bot, all_beginning_caches, all_caches
    #  )
    #  # Then, use Watson API to get the keywords and entities from this template
    #  _, markov_keywords, markov_entities = interpret_watson_keywords_and_entities(
        #  new_markov_template
    #  )
    #  # Then use Watson again to get the emotion/keywords/entities
    #  # of the last speaker to figure out what to say
    #  # Note this is the last speaker, NOT the user corresponding to "bot_id"
    #  # (maybe means adding a new user??)
    #  overarching_emotion, keywords, entities = interpret_watson_keywords_and_entities(
        #  previous_posts[-1]
    #  )

    #  # Now use all this data to try replacing words in the markov template
    #  # with words from the last speaker's post
    #  replacements = {}
    #  all_watson_data_from_last_post = dict(keywords, **entities)
    #  for keyword, data in all_watson_data_from_last_post.iteritems():
        #  emotion = data.get("emotion")
        #  for markov_keyword, markov_data in markov_keywords.iteritems():
            #  markov_emotion = markov_data.get("emotion")
            #  if emotion == markov_emotion:
                #  replacements[markov_keyword] = keyword

    #  # Now DO the replacements
    #  for phrase, replacement in replacements.iteritems():
        #  new_markov_template = new_markov_template.replace(phrase, replacement)

    #  # After the replacements are done, this should somewhat realish
    #  reply_text = new_markov_template
    #  return reply_text


#  def create_markov_post(bot_id):
    #  """
    #  Takes all the words from all the twitter
    #  posts on the twitterbot.
    #  Sticks them all into a giant
    #  list and gives this to the markov calc.
    #  Save this as a new twitterpostmarkov
    #  """
    #  bot = TwitterBot.objects.get(id=bot_id)

    #  all_beginning_caches = bot.twitterpostcache_set.filter(beginning=True)
    #  all_caches = bot.twitterpostcache_set.all()
    #  new_markov_post = bot.apply_markov_chains_inner(all_beginning_caches, all_caches)

    #  # Replace the tokens (twitter specific)
    #  replace_tokens(new_markov_post, settings.USER_TOKEN, bot.twittermention_set.all())
    #  replace_tokens(new_markov_post, settings.LINK_TOKEN, bot.twitterlink_set.all())
    #  replace_tokens(new_markov_post, settings.TAG_TOKEN, bot.twitterhashtag_set.all())

    #  randomness = new_markov_post[1]
    #  content = " ".join(new_markov_post[0])

    #  new_markov_post = bot.twitterpostmarkov_set.create(
        #  content=content, randomness=randomness
    #  )
    #  return new_markov_post.content


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
                print("Replaced " + token)

            except IndexError:
                print("failed to replace token:")
                print(word_list[word_index])

    return (word_list, word_list_and_randomness[1])


text_generation_utils_lookup = {
    # All functions will receive "previous posts"
    # which is the set of TwitterConversationPost objects ordered by index
    "markov_chain": markov_chain,
    "template_with_sentiment_replacement": template_with_sentiment_replacement,
}
