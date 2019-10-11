from bots.models.twitter import TwitterBot
from bots.helpers.twitter_bot_utils.scraping_utils import scrape
from bots.helpers.twitter_bot_utils.conversation_utils import get_or_create_conversation, add_to_twitter_conversation


username_whitelist = [
    '@realDonaldTrump',
    '@taylorswift13',
    '@justinbieber',
    '@BarackObama',
]

# Scarape all of them
for username in username_whitelist:
  scrape(username)
  bot = TwitterBot.objects.get_one(username=username)

for username_1 in username_whitelist:
  for username_2 in username_whitelist:
    # Skip; no conversation between one person and themselves
    if username_1 == username_2:
      continue
    conversation = get_or_create_conversation(username_1, username_2)
    add_to_twitter_conversation(
    


