"""
Utilities for getting tweets on a more granular level
Functions can control the way in which reply chains are parsed,
and return tweets and replys that march specific critera
"""
import mechanize
from bots.models.twitter import TwitterBot
from bs4 import BeautifulSoup
import watson_utils


def get_tweet_replies(browser, username, tweet_id):
    url = 'https://twitter.com/{0}/status/{1}'.format(username, tweet_id)
    browser.open(url)
    html = browser.response().read().decode('utf-8', 'ignore')
    raw = BeautifulSoup(html, "html.parser")
    replies_div = raw.find('div', class_='replies-to')
    replies = replies_div.find_all('div', class_='ThreadedConversation-tweet')

    # If there are no replies, stop
    if not replies:
        return {}

    all_tweets = []
    for reply in replies:
        tweets = reply.find_all('div', class_='tweet')
        all_tweets.extend(tweets)

    all_responses = {}
    for tweet in all_tweets:
        content = tweet.find_all('div', class_='content')[0]
        inner_content = content.find_all('div', class_='js-tweet-text-container')[0]
        text = inner_content.find('p')

        screen_name = tweet['data-screen-name']
        tweet_id = tweet['data-tweet-id']
        all_responses[tweet_id] = {'author': screen_name, 'content': text.text}

    return all_responses


def recursively_get_replies(browser, username, tweet_id, max_iterations=None):
    print 'calling recursively_get_replies with {}'.format(tweet_id)
    replies = {}
    all_responses = get_tweet_replies(browser, username, tweet_id)
    print 'got responses: {}'.format(all_responses)

    iterations = 0
    if not len(all_responses):
        return replies

    for reply_id, response_data in all_responses.iteritems():
        if max_iterations:
            if iterations > max_iterations:
                return replies

        print 'initiate call for {}'.format(reply_id)
        replies[reply_id] = {'author': response_data['author'], 'content': response_data['content'], 'replies':
                             recursively_get_replies(browser, username, reply_id)}
        iterations = iterations + 1

    return replies


def get_tweets_over_reply_threshold_and_analyze_text_emotion(username, scrape_mode='recurse', threshold=1):
    tweets = get_tweets_over_reply_threshold(username, scrape_mode, threshold)
    for tweet_id, tweet_data in tweets.iteritems():
        text = tweet_data['content']
        emotion_dict = watson_utils.watson_analyze_text_emotion(text)
        emotion, probability = emotion_dict.iteritems().next()
        tweet_data.update({'emotion': emotion})
        tweets[tweet_id] = tweet_data
    return tweets


def get_tweets_over_reply_threshold_and_analyze_text_understanding(username, scrape_mode='recurse', threshold=1):
    tweets = get_tweets_over_reply_threshold(username, scrape_mode, threshold)
    for tweet_id, tweet_data in tweets.iteritems():
        text = tweet_data['content']
        keywords_list, entities_list = watson_utils.interpret_watson_keywords_and_entities(text)

        tweet_data.update({'keyword_data': keywords_list})
        tweet_data.update({'entities_data': entities_list})
        tweets[tweet_id] = tweet_data
    return tweets


def get_tweets_over_reply_threshold(username, scrape_mode='all', threshold=1):
    if scrape_mode == 'all':
        reply_function = recursively_get_replies
    elif scrape_mode == 'single_reply':
        reply_function = single_reply
    elif scrape_mode == 'first_responder':
        reply_function = first_responder
    else:
        reply_function = None
    print('method: %s' % str(reply_function))

    length_limiter = 5

    bot = TwitterBot.objects.get(username=username)
    browser = mechanize.Browser()
    ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0 (compatible;)'
    browser.addheaders = [('User-Agent', ua), ('Accept', '*/*')]

    tweets_over_threshold = {}
    # Get viable top level tweets, that have reply count over the threshold
    print "looping on the bot's tweets"
    for tweet in bot.twitterpost_set.all()[:length_limiter]:
        reply_data = get_tweet_replies(browser, username, tweet.tweet_id)
        num_replies = len(reply_data)
        if num_replies >= threshold:
            print('lots of replies; recursing')
            tweets_over_threshold[tweet.tweet_id] = \
                {'content': tweet.content, 'replies': reply_function(browser, username, tweet.tweet_id)}
            return tweets_over_threshold
    # Recursive find replies to get the entire thread for each tweet
    return tweets_over_threshold


def single_reply(browser, username, tweet_id):
    replies = {}
    all_responses = get_tweet_replies(browser, username, tweet_id)

    if len(all_responses) == 0:
        return replies

    reply_id = all_responses.keys()[0]
    response_data = all_responses[reply_id]

    replies[reply_id] = {'author': response_data['author'], 'content': response_data['content'], 'replies': {}}
    keywords_list, entities_list = watson_utils.interpret_watson_keywords_and_entities(response_data['content'])
    replies[reply_id].update({'keyword_data': keywords_list})
    replies[reply_id].update({'entities_data': entities_list})

    return replies


def first_responder(browser, username, tweet_id):
    print 'calling first_responder with {}'.format(tweet_id)
    replies = {}
    all_responses = get_tweet_replies(browser, username, tweet_id)
    if len(all_responses) > 0:
        reply_id, response_data = all_responses.iteritems().next()

        replies[reply_id] = {'author': response_data['author'], 'content': response_data['content'], 'replies':
                             first_responder(browser, username, reply_id)}

        keywords_list, entities_list = watson_utils.interpret_watson_keywords_and_entities(response_data['content'])
        replies[reply_id].update({'keyword_data': keywords_list})
        replies[reply_id].update({'entities_data': entities_list})

    return replies
