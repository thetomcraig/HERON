from django.core.management.base import BaseCommand
from bots.helpers.twitter_bot_utils.conversation_utils import get_full_conversation_as_json
from bots.management.commands._helpers import get_username_pairs_from_arguments, add_username_pairs_argument_to_parser

NUM_NEW_POSTS = 10


class Command(BaseCommand):
  help = 'Take in a list of pairs of usernames. Update the conversation beween each pair'

  def add_arguments(self, parser):
    add_username_pairs_argument_to_parser(parser)

  def handle(self, *args, **options):
    verbosity = options.get('verbosity')
    # Make the input arguments into a list of lists; each list inside the big list has length==2
    # For example: [['tom', 'john'] , ['john','amy']]
    username_pairs = get_username_pairs_from_arguments(options)
    for username_1, username_2 in username_pairs:
      print('Querying for conversation: "{} <-> {}"'.format(username_1, username_2))
      conversation_json = get_full_conversation_as_json(username_1, username_2)
      # `conversation_json` will always exist at this point
      print('Success')
      if verbosity == 1:
        # To make things less annoying, remove the post data and just show the NUMBER of posts
        conversation_json['posts'] = len(conversation_json['posts'])
      print(conversation_json)
