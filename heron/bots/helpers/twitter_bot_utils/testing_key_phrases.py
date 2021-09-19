

def generate_response_with_key_phrases(key_phrases, bot_1, bot_2):
    if not len(key_phrases):
        return "first post"
    #  Will map key phrase to list of tweets that contain one of those phrases or a synonym
    #  Search for tweets that contain the given key phrase or a synonym
    #  Searh the bot_1's tweets for something with that phrase
    key_phrase_match_map = defaultdict(list)
    for tweet in bot_1.twitterpost_set.all():
        for phrase in key_phrases:
            if phrase in tweet.content:
                key_phrase_match_map[phrase].append(tweet.content)
            for synset in wn.synsets(phrase):
                for lemma in synset.lemmas():
                    if lemma.name() in tweet.content:
                        key_phrase_match_map[lemma.name()].append(tweet.content)

    for k, v in key_phrase_match_map.iteritems():
        print "KEY"
        print k
        print "V"
        print v

    return "STUB"



def get_key_phrases(conversation):
    last_post = conversation.last()
    r = Rake()
    phrases = []
    content = last_post.post.content
    if content:
        r.extract_keywords_from_text(content)
        # TODO Filter further
        phrases = r.get_ranked_phrases()

    return phrases



