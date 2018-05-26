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
    print(state)

    return JsonResponse({'success': True})


@csrf_exempt
def start_generator(_):
    conversation_name = 'general'
    state = settings.DISCORD_CONVERSATION_STATES.get(conversation_name, {})

    generate = True
    delay = 5

    while (generate):
        sleep(delay)
        state = settings.DISCORD_CONVERSATION_STATES.get(conversation_name, {})
        print (state)
        print ('\n')
        next_speaker_id, next_message = generate_next_speaker_and_message(state, conversation_name)
        print(next_speaker_id)
        print(next_message)
        print ('\n')
        print ('\n')

    return JsonResponse({'success': True})


def generate_next_speaker_and_message(state, conversation_name):
    convo = TwitterConversation.objects.get(name=conversation_name)
    posts = convo.twitterconversationpost_set.order_by('index').all()
    last_speaker = posts.last().author.username
    last_index = posts.last().index
    index = last_index+1

    next_speaker = generate_next_speaker(state, last_speaker)

    next_message = 'bot reply'

    bot = TwitterBot.objects.get(username=next_speaker)
    post = TwitterPost.objects.create(author=bot, content=next_message)
    convo.twitterconversationpost_set.create(index=index, author=bot)

    order_by('index').all()

    return next_speaker_id, next_message


def generate_next_speaker(state, last_speaker):
    """
    Given the conversatino name
    Get the conversation and all previous posts - there should be at least one
    """
    print('last_speaker')
    print(last_speaker)
    possible_next_speakers = copy.deepcopy(state.get('bots_in_group_convo'))
    if len(possible_next_speakers) < 2:
        print('not enough people conversation yet')
        return -1

    print('possible_next_speakers')
    print(possible_next_speakers)
    try:
        possible_next_speakers.remove(last_speaker)
    except:
        pass
    next_speaker = possible_next_speakers[0]

    print('next_speaker')
    print(next_speaker)
    return next_speaker
