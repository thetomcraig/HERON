from django.core.management.base import BaseCommand
from bots.helpers.twitter_bot_utils.conversation_utils import add_posts_to_twitter_conversation
from bots.management.commands._helpers import get_username_pairs_from_arguments, add_username_pairs_argument_to_parser


class Command(BaseCommand):
  help = 'Take in a list of pairs of usernames. Update the conversation beween each pair'

  def add_arguments(self, parser):
    add_username_pairs_argument_to_parser(parser)
    parser.add_argument('--number_of_posts',
                        '-n',
                        nargs=1,
                        type=int)

  def handle(self, *args, **options):
    number_of_posts = options.get('number_of_posts')[0]
    username_pairs = get_username_pairs_from_arguments(options)
    for username_1, username_2 in username_pairs:
      print('Updating Conversation: "{}-{}"'.format(username_1, username_2))
      # To debug, print out this line
      add_posts_to_twitter_conversation(username_1, username_2, number_of_posts)
      print('Done')
