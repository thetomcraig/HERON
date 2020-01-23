from django.core.management.base import BaseCommand
from bots.helpers.twitter_bot_utils.crud_utils import get_twitter_bot, get_twitter_bot_info
from bots.management.commands._helpers import add_usernames_argument_to_parser, get_usernames_from_arguments


class Command(BaseCommand):
  help = 'Get bots for the given usernames'

  def add_arguments(self, parser):
    add_usernames_argument_to_parser(parser)
    return parser

  def handle(self, *args, **options):
    usernames = get_usernames_from_arguments(options)
    verbosity = options.get('verbosity')

    for username in usernames:
      print('Querying for bot with username: "{}"'.format(username))
      bot = get_twitter_bot(username)
      if bot:
        print('Success')
        if verbosity >= 2:
          include_posts = verbosity >= 3
          bot_data = get_twitter_bot_info(username, include_posts=include_posts)
          print(bot_data)
      else:
        print('Failure')
