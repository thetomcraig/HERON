from django.core.management.base import BaseCommand
from bots.helpers.twitter_bot_utils.conversation_utils import add_posts_to_twitter_conversation

NUM_NEW_POSTS = 10


class Command(BaseCommand):
  help = 'Take in a list of pairs of usernames. Update the conversation beween each pair'

  def add_arguments(self, parser):
    parser.add_argument('pairs',
                        help='Comma separated list of pairings. Example: tom-john,john-amy,amy-tom',
                        nargs='+',
                        type=str)

  def handle(self, *args, **options):
    username_list = options.get('pairs')
    username_pairs = username_list[0].split(',')
    for pair in username_pairs:
      username_1, username_2 = pair.split('-')
      print('Updating Conversation: "{}-{}"'.format(username_1, username_2))
      # To debug, print out this line
      add_posts_to_twitter_conversation(username_1, username_2, NUM_NEW_POSTS)
      print('Done')
