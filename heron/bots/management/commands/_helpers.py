def add_usernames_argument_to_parser(parser):
  parser.add_argument('usernames',
                      help='comma separated list of usernames to query with',
                      nargs='+',
                      type=str)
  return parser


def get_usernames_from_arguments(arguments):
  username_list = arguments.get('usernames')
  usernames = username_list[0].split(',')
  return usernames
