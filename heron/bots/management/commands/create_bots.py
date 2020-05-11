from django.core.management.base import BaseCommand
from bots.management.commands._helpers import add_usernames_argument_to_parser, get_usernames_from_arguments
from bots.helpers.twitter_bot_utils.crud_utils import get_twitter_bot, create_twitter_bot_from_person


class Command(BaseCommand):
  help = 'Add bots for the given usernames'

  def add_arguments(self, parser):
    add_usernames_argument_to_parser(parser)

  def handle(self, *args, **options):
    usernames = get_usernames_from_arguments(options)

    for username in usernames:
      print('Querying for bot with username: "{}"'.format(username))
      bot = get_twitter_bot(username)
      if bot:
        print('Failure - already exists')
      else:
        print('Creating new bot...')
        create_twitter_bot_from_person(username)
        print('Success')
