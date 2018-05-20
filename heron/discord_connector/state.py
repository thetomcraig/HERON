messages = []
next_speaker = ''
next_message = ''

bots_in_group_convo = ['angry_bot', 'trump_bot']

bot_ids_to_names = {
    '412303436995100682': 'trump_bot',
    '412306085295292418': 'angry_bot',
}
bot_names_to_ids = {}
for k, v in bot_ids_to_names.iteritems():
    bot_names_to_ids[v] = k

BLACK_LIST = ['sad_bot', 'thetomcraig']
