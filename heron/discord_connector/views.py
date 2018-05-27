# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import json
from django.conf import settings
from .state_manager import initialize_conversation_sate, add_bot_to_conversation_state
from bots.helpers.twitter_bot_utils import add_message_to_group_convo
from bots.models.twitter import TwitterConversation, TwitterBot, TwitterPost
import random
from time import sleep

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def bot_online(request):
    body = json.loads(request.body.decode('utf-8'))
    key = body.get('key')
    username = body.get('username')
    conversation_name = body.get('conversation_name')
    # Get the global state for this convo, and add the bot
    state = settings.DISCORD_CONVERSATION_STATES.get(conversation_name, {})
    state = add_bot_to_conversation_state(state, key, username)
    settings.DISCORD_CONVERSATION_STATES.setdefault(conversation_name, state)
    print(state.get('bots_in_group_convo'))

    return JsonResponse({'success': True})


@csrf_exempt
def start_generator(_):
    conversation_name = settings.DISCORD_CONVERSATION_NAME
    state = settings.DISCORD_CONVERSATION_STATES.get(conversation_name, {})

    def termination_fn():
        return False

    run_generator(conversation_name, state, 2, termination_fn)

    return JsonResponse({'success': True})


def run_generator(conversation_name, state, delay, termination_fn):
    while (not termination_fn()):
        sleep(delay)
        print (state)
        print ('\n')

        next_speaker, next_message, convo, index = generate_next_speaker_and_message(state, conversation_name)
        if not next_speaker:
            continue
        bot = TwitterBot.objects.get(username=next_speaker)
        post = TwitterPost.objects.create(author=bot, content=next_message)
        convo.twitterconversationpost_set.create(index=index, author=bot, post=post)

        print(next_speaker)
        print(next_message)
        print ('\n')


def generate_next_speaker_and_message(state, conversation_name):
    print('conversation_name')
    print(conversation_name)
    convo = TwitterConversation.objects.get(name=conversation_name)

    next_speaker, index = generate_next_speaker(state, convo)
    next_message = generate_next_message(state, convo)

    return next_speaker, next_message, convo, index


def generate_next_speaker(state, convo):
    """
    Given the conversatino name
    Get the conversation and all previous posts - there should be at least one
    """
    posts = convo.twitterconversationpost_set.order_by('index').all()
    last_speaker = posts.last().author.username
    last_index = posts.last().index
    index = last_index + 1
    possible_next_speakers = copy.deepcopy(state.get('bots_in_group_convo'))
    if len(possible_next_speakers) < 2:
        print('not enough people conversation yet')
        return None, -1

    try:
        possible_next_speakers.remove(last_speaker)
    except Exception as e:
        print(e)
    next_speaker = possible_next_speakers[0]

    return next_speaker, index


def generate_next_message(state, convo):
    next_message = 'bot reply'
    return next_message
