# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import json
from django.conf import settings
from .state_manager import initialize_conversation_sate, add_bot_to_conversation_state
from bots.helpers.twitter_bot_utils import add_message_to_group_convo
from bots.models.twitter import TwitterConversation, TwitterBot, TwitterPost

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def bot_online(request):
    """
    Called when a bot logs in on Discord.
    The Bot's information is saved in the conversation's state
    Using the passed in conversaion name,
    the conversation in the current state is updated to include the bot
    """
    body = json.loads(request.body.decode('utf-8'))
    key = body.get('key')
    username = body.get('username')
    conversation_name = body.get('conversation_name')
    # Get the global state for this convo, and add the bot
    state = settings.DISCORD_CONVERSATION_STATES.get(conversation_name, {})
    state = add_bot_to_conversation_state(state, key, username)
    settings.DISCORD_CONVERSATION_STATES.setdefault(conversation_name, state)

    return JsonResponse({'success': True})


@csrf_exempt
def get_message(request):
    """
    Called by a Discord bot when they need a new message
    We run the generator and generate a new message and a new speaker to send it
    """
    body = json.loads(request.body.decode('utf-8'))
    username = body.get('username')
    conversation_name = body.get('conversation_name')

    next_speaker, message = run_generator(conversation_name)

    if not (next_speaker and message):
        return JsonResponse({'success': True, 'should_send': False, 'message': None})

    should_send = username == next_speaker
    return JsonResponse({'success': True, 'should_send': should_send, 'message': message})


def run_generator(conversation_name):
    """
    Input:
        conversation_name: name of conversation to analyze
    Output:
        username of next speaker, message for that speaker to send next
    """
    state = settings.DISCORD_CONVERSATION_STATES.get(conversation_name, {})

    next_speaker, next_message, convo, index = generate_next_speaker_and_message(state, conversation_name)
    if not next_speaker:
        return None, None

    bot = TwitterBot.objects.get(username=next_speaker)
    post = TwitterPost.objects.create(author=bot, content=next_message)
    convo.twitterconversationpost_set.create(index=index, author=bot, post=post)

    return next_speaker, next_message


def generate_next_speaker_and_message(state, conversation_name):
    """
    Input:
        state: The entire state of the conversation
        conversation_name: The name of the conversation
    """
    convo = TwitterConversation.objects.get(name=conversation_name)

    next_speaker, index = generate_next_speaker(state, convo)
    next_message = generate_next_message(state, convo)

    return next_speaker, next_message, convo, index


def generate_next_speaker(state, convo):
    """
    Get the conversation and all previous posts - there should be at least one
    Last speaker was author of that post
    Generate new index for new post, and determine new speaker
    """
    posts = convo.twitterconversationpost_set.order_by('index').all()
    last_speaker = posts.last().author.username
    last_index = posts.last().index
    index = last_index + 1
    possible_next_speakers = copy.deepcopy(state.get('bots_in_group_convo'))
    if len(possible_next_speakers) < 2:
        print('not enough people conversation yet')
        return None, -1

    # Replace with random stuff. for debugging just doing the other user
    try:
        possible_next_speakers.remove(last_speaker)
    except Exception as e:
        print(e)
    next_speaker = possible_next_speakers[0]

    return next_speaker, index


def generate_next_message(state, convo):
    next_message = 'bot reply'
    print(state)
    return next_message
