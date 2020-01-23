from django.core.management.base import BaseCommand
from bots.helpers.twitter_bot_utils.scraping_utils import scrape
from bots.management.commands._helpers import add_usernames_argument_to_parser, get_usernames_from_arguments


class Command(BaseCommand):
  help = 'Updates the bot'

  def add_arguments(self, parser):
    add_usernames_argument_to_parser(parser)

  def handle(self, *args, **options):
    usernames = get_usernames_from_arguments(options)

    for username in usernames:
      print('Scraping "{}"'.format(username))
      response = scrape(username)
      if response.get('success'):
        print('Success')
      else:
        print('Failure', response.get('msg'))
