#  import os
#  from django.conf import settings
#  import django

#  os.environ['DJANGO_SETTINGS_MODULE'] = 'heron.settings'
#  settings.configure(DEBUG=True)
#  django.setup()

from bots.models.twitter import TwitterBot
from bots.helpers.twitter_bot_utils.scraping_utils import scrape
from bots.helpers.twitter_bot_utils.conversation_utils import add_posts_to_twitter_conversation

NUM_NEW_POSTS = 1

username_whitelist = [
    '@realDonaldTrump',
    '@taylorswift13',
    '@justinbieber',
    '@BarackObama',
]

# Scarape all of them
for username in username_whitelist:
  data = scrape(username)
  print(data)

# Loop over all pairings
for username_1 in username_whitelist:
  for username_2 in username_whitelist:
    # Skip; no conversation between one person and themselves
    if username_1 == username_2:
      continue

    new_posts = add_posts_to_twitter_conversation(username_1, username_2, NUM_NEW_POSTS)
