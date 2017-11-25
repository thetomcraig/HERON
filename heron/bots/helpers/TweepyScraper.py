#streamer class for realtime feedback of a tweets using a given topic

from bs4 import BeautifulSoup
import mechanize 
import tweepy
import json
import re

class TweepyScraper: 

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        '''Setup, using credentials from Twitter'''
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        
        self.api = tweepy.API(self.auth)
        
    #Top 100 users
    def scrape_top_users(self,limit):
        people_dict = []
        browser = mechanize.Browser()
        ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0 (compatible;)'
        browser.addheaders = [('User-Agent', ua), ('Accept', '*/*')]

        url = 'http://twittercounter.com/pages/100'
        browser.open(url)

        html = browser.response().read().decode('utf-8', 'ignore')
        raw = BeautifulSoup(html, "html.parser")
    
        def has_class_and_data_pos(tag):
            return tag.has_attr('class') and tag.has_attr('data-pos')
        people = raw.find_all(has_class_and_data_pos)
        print raw
        for person in people:
            name = person.find(class_='name').text
            uname = person.find(class_='uname').text.replace('@', '')
            avatar = person.find('img')['src']
            people_dict.append({'name': name, 'uname': uname, 'avatar': avatar})
            
            if len(people_dict) >= limit:
                return people_dict
        return people_dict
        
    def get_tweets_from_user(self, screen_name, limit):
        alltweets = []    
        outtweets = []

        new_tweets = self.api.user_timeline(screen_name=screen_name, count=limit)
        alltweets.extend(new_tweets)
        outtweets = [tweet.text.encode("utf-8") for tweet in alltweets]

        return outtweets
         
    def findTrends(self):
        #This will be a one element dict
        trends = self.api.trends_place(1)
        #Extract the actual trends
        data = trends[0] 
        #These are all JSON objects
        #with a name element
        parsedTrends = data['trends']
        #Taking out just the names
        names = [trend['name'] for trend in parsedTrends]
        #Finally, fixing the encoding
        for i in range (len(names)):
            names[i] = names[i].encode('ascii', 'ignore')        
        return names
    
    # Searches for tweets that use a given tag
    def search(self, tag):
        results = self.api.search(q=tag)
        for i in range (len(results)):
            results[i] = (results[i]).text.encode('ascii', 'ignore')
        return results
        
    def stream(self, tag):
        '''Setting up the streamer'''
        l = StdOutListener()
        # There are different kinds of streams: public stream, user stream, multi-user streams
        # In this example follow tag
        # For more details refer to https://dev.twitter.com/docs/streaming-apis
        stream = tweepy.Stream(self.auth, l)
        stream.filter(track=[tag])
    
        
# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):
        def on_data(self, data):
                # Twitter returns data in JSON format - we need to decode it first
                decoded = json.loads(data)
                # Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
                print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
                print ''
                return True

        def on_error(self, status):
                print status
