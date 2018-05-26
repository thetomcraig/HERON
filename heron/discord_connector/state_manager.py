# Utilities for managing the state of a discord conversation


def create_names_to_ids_map(ids_to_names_dict):
    bot_names_to_ids = {}
    for k, v in ids_to_names_dict.iteritems():
        bot_names_to_ids[v] = k
    return bot_names_to_ids


def initialize_conversation_sate(ids_to_names_map={}, blacklist=[]):
    names_to_ids_map = create_names_to_ids_map(ids_to_names_map)
    state = {
        'messages': [],
        'next_speaker': '',
        'next_message': '',
        'bots_in_group_convo': [],
        'ids_to_names_map': ids_to_names_map,
        'names_to_ids_map': names_to_ids_map,
        'blacklist': blacklist,
    }
    return state


def add_bot_to_conversation_state(state, key, username):
    ids_to_names = state.get('ids_to_names_map')
    ids_to_names[key] = username
    names_to_ids = create_names_to_ids_map(ids_to_names)
    state.setdefault('ids_to_names_map', ids_to_names)
    state.setdefault('names_to_ids_map', names_to_ids)
    bots_in_group_convo = state.get('bots_in_group_convo')
    bots_in_group_convo.append(username)
    state.setdefault('bots_in_group_convo', bots_in_group_convo)

    return state
