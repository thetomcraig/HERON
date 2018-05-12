messages = []
next_speaker = ''
next_message = ''
bots_in_group_convo = set(['angry_bot', 'joy_bot', 'sad_bot'])
bot_ids_to_names = {
    'NDEyMzAzNDM2OTk1MTAwNjgy.DWIYng._QQ4-O3teZmuO42S92bDLiYi6mg': 'angry_bot',
    'NDEyMzA2MDg1Mjk1MjkyNDE4.DWIYvg.ZmgLGCkonDoc1Nu6q-WqkcxnROw': 'joy_bot',
    'fake': 'sad_bot',
}
bot_names_to_ids = {}
for k, v in bot_ids_to_names.iteritems():
    bot_names_to_ids[v] = k
