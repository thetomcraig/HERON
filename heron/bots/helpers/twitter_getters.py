"""
Utilities for getting tweets on a more granular level
Functions can control the way in which reply chains are parsed,
and return tweets and replys that march specific critera
"""
import mechanize
from bots.models.twitter import TwitterBot, TwitterPost
from bs4 import BeautifulSoup
import watson_utils


def get_tweet_replies(username, tweet_id):
    """
    Input:
        twitter username
        tweet id
    Output:
        replies to that tweet
    """
    browser = mechanize.Browser()
    ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0 (compatible;)'
    browser.addheaders = [('User-Agent', ua), ('Accept', '*/*')]

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

    # Need to remove duplicates here, same tweets show up with the same id...
    # WAIT, this seems to actually be legitimate... should it be deduped
    return all_responses


def get_all_replies(username, tweet_id, max_iterations=None):
    """
    Input:
        twitter username
        tweet id
        number of maximum iterations before stopping
    Output:
        dictionary like this:
            { reply id: { author: '<name>',
                          content: '<text of the reply>',
                          replies: { <dictionary like this one> }
                        }
            }
    """
    print 'calling get_all_replies with {}'.format(tweet_id)
    replies = {}
    all_responses = get_tweet_replies(username, tweet_id)
    print 'got responses: {}'.format(all_responses)

    if len(all_responses) == 0:
        return replies

    iterations = 0
    for reply_id, response_data in all_responses.iteritems():
        if max_iterations:
            if iterations > max_iterations:
                return replies

        print 'initiate call for {}'.format(reply_id)
        replies[reply_id] = {'author': response_data['author'], 'content': response_data['content'], 'replies':
                             get_all_replies(username, reply_id)}
        iterations = iterations + 1

    return replies


def single_reply(username, tweet_id):
    """
    Input:
        twitter username
        tweet id
    Output:
        dictionary like this:
            { reply id: { author: '<name>',
                          content: '<text of the reply>',
                          replies: {}
                        }
            }
    """
    replies = {}
    all_responses = get_tweet_replies(username, tweet_id)
    print 'all responses'
    print all_responses

    if len(all_responses) == 0:
        return replies

    # Just take the first response
    reply_id = all_responses.keys()[0]
    response_data = all_responses[reply_id]

    replies[reply_id] = {'author': response_data['author'], 'content': response_data['content'], 'replies': {}}

    overarching_emotion, keywords_list, entities_list = watson_utils.interpret_watson_keywords_and_entities(response_data[
                                                                                                            'content'])
    replies[reply_id].update({'keyword_data': keywords_list})
    replies[reply_id].update({'entities_data': entities_list})
    replies[reply_id].update({'overarching_emotion': overarching_emotion})

    return replies


def get_tweets_over_reply_threshold_and_analyze_text_understanding(username, scrape_mode='all', threshold=1,
                                                                   max_response_number=5):
    """
    Input:
        twitter username
        scrape mode (how many and what type of replies to return)
        reply threshold (retrieve tweets with more replies than this number)
    Output:
        tweets and their replies, scraped according to the scrape method
        each reply will have NLP analytics attached from the watson API
    """
    # Decide what function we want to scrape with
    if scrape_mode == 'all':
        reply_function = get_all_replies
    elif scrape_mode == 'single_reply':
        reply_function = single_reply
    else:
        reply_function = None

    bot, _ = TwitterBot.objects.get_or_create(username=username)

    tweets_over_threshold = {}
    # Get viable top level tweets
    # Get replies to that tweet
    # Put the tweet and its replies into the dict if the reply number is over the threshold
    # Call the recursive scrape function on each reply to get its replies
    for tweet in bot.twitterpost_set.all():
        reply_data = get_tweet_replies(username, tweet.tweet_id)
        num_replies = len(reply_data)
        if num_replies >= threshold:
            print('lots of replies; analyzing')
            overarching_emotion, keywords_list, entities_list = watson_utils.interpret_watson_keywords_and_entities(
                tweet.content)
            tweets_over_threshold[tweet.tweet_id] = {'keyword_data': keywords_list,
                                                     'entities_data': entities_list,
                                                     'content': tweet.content,
                                                     'overarching_emotion': overarching_emotion}
            print('recursing')
            tweets_over_threshold[tweet.tweet_id].update({'replies': reply_function(username, tweet.tweet_id)})

            if len(tweets_over_threshold.keys()) >= max_response_number:
                return tweets_over_threshold
    # Recursive find replies to get the entire thread for each tweet
    return tweets_over_threshold


def catalog_tweet_replies(tweets_over_threshold):
    """
    Given a user, grab their tweets
    Assign the replies to the corresponding linked bots

    The response from the getter function looks like:
    tweets_dictionary = {
        tweet_id : {'author': author,
                    'keyword_data': keywords_list,
                    'entities_data': entities_list,
                    'content': tweet.content,
                    'overarching_emotion': overarching_emotion,
                    'replies': <Dictionary that matches this one>
                   }
    }

    Grab all of the twitter bots that correspond to the emotions the watson API returns
    """
    for tweetid, tweet_data in tweets_over_threshold.iteritems():
        for reply_id, reply_data in tweet_data['replies'].iteritems():
            overarching_emotion = reply_data['overarching_emotion']
            reply_username = reply_data['author']
            reply_author = TwitterBot.objects.get_or_create(username=reply_username)[0]
            TwitterPost.objects.create(tweet_id=reply_id,
                                       author=reply_author,
                                       content=reply_data['content'],
                                       emotion=overarching_emotion)

    # With this done; logic to group together the tweets with the same emotions and do markov chains
