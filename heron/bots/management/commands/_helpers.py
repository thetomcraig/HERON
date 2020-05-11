def add_usernames_argument_to_parser(parser):
  parser.add_argument('usernames',
                      help='comma separated list of usernames to query with',
                      nargs='+',
                      type=str)
  return parser


def add_username_pairs_argument_to_parser(parser):
  parser.add_argument('pairs',
                      help='Comma separated list of pairings. Example: tom-john,john-amy,amy-tom',
                      nargs='+',
                      type=str)
  return parser


def get_usernames_from_arguments(arguments):
  username_list = arguments.get('usernames')
  usernames = username_list[0].split(',')
  return usernames


def get_username_pairs_from_arguments(arguments):
  username_list = arguments.get('pairs')
  username_pairings = username_list[0].split(',')
  username_pairs = [pair.split('-') for pair in username_pairings]
  return username_pairs
