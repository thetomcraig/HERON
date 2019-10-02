"""
Utilities for getting data directly from twitter
Uses Tweepy for getting tweets and trends
Uses mechanize+BeautifulSoup to get reply chains and top users
"""
import mechanize
import tweepy
from bs4 import BeautifulSoup


class TwitterApiInterface:

  def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
    """
    Setup, using credentials from Twitter
    """
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.access_token = access_token
    self.access_token_secret = access_token_secret

    self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
    self.auth.set_access_token(self.access_token, self.access_token_secret)

    self.api = tweepy.API(self.auth)

  def scrape_top_users(self, limit):
    people_dict = []
    browser = mechanize.Browser()
    ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0 (compatible;)'
    browser.addheaders = [('User-Agent', ua), ('Accept', '*/*')]
    browser.set_handle_robots(False)

    url = 'https://friendorfollow.com/twitter/most-followers/'
    browser.open(url)

    html = browser.response().read().decode('utf-8', 'ignore')
    raw = BeautifulSoup(html, "html.parser")
    browser.close()

    people_dict = []
    people_divs = raw.findAll("div", {"class": "text-holder"})
    for person in people_divs:
      uname = person.find(class_="mail").next_element.text
      name = ''.join(person.contents[1].text.split('.')[1::]).strip()
      avatar = person.parent.find('img').attrs.get('src')
      people_dict.append({'name': name, 'uname': uname, 'avatar': avatar})

    return people_dict

  def get_tweets_from_user(self, username, limit):
    alltweets = self.api.user_timeline(screen_name=username, count=limit)
    full_length_tweets = {}
    for tweet in alltweets:
      full_length_tweet = self.api.get_status(tweet.id, tweet_mode='extended')._json['full_text']
      full_length_tweets[tweet.id] = full_length_tweet.encode("utf-8")

    return full_length_tweets

  def findTrends(self):
    # This will be a one element dict
    trends = self.api.trends_place(1)
    # Extract the actual trends
    data = trends[0]
    # These are all JSON objects
    # with a name element
    parsedTrends = data['trends']
    # Taking out just the names
    names = [trend['name'] for trend in parsedTrends]
    # Finally, fixing the encoding
    for i in range(len(names)):
      names[i] = names[i].encode('ascii', 'ignore')
    return names

  # Searches for tweets that use a given tag
  def search(self, tag):
    results = self.api.search(q=tag)
    for i in range(len(results)):
      results[i] = (results[i]).text.encode('ascii', 'ignore')
    return results
