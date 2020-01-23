from django.core.management.base import BaseCommand
from bots.helpers.twitter_bot_utils.scraping_utils import scrape


class Command(BaseCommand):
  help = 'Updates the bot'

  def add_arguments(self, parser):
    parser.add_argument('usernames',
                        help='comma separated list of usernames to scrape',
                        nargs='+',
                        type=str)

  def handle(self, *args, **options):
    username_list = options.get('usernames')
    usernames = username_list[0].split(',')

    for username in usernames:
      print('Scraping "{}"'.format(username))
      # Print this to debug:
      scrape(username)
      print("Done")
