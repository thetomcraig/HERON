# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import json
from django.conf import settings
from .state_manager import initialize_conversation_sate, add_bot_to_conversation_state
from bots.helpers.twitter_bot_utils import add_message_to_group_convo
from bots.models.twitter import TwitterConversation, TwitterBot, TwitterPost
import random

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
    print (state)

    return JsonResponse({'success': True})


def generate_next_speaker_and_message(conversation_name):
    next_speaker_id = generate_next_speaker(conversation_name)
    next_message = 'bot reply'
    return next_speaker_id, next_message


def generate_next_speaker(conversation_name):
    """
    Given the conversatino name
    Get the conversation and all previous posts - there should be at least one
    """
    convo = TwitterConversation.objects.get(name=conversation_name)
    posts = convo.twitterconversationpost_set.order_by('index').all()
    last_speaker = posts.last().author.username
    print('last_speaker')
    print(last_speaker)
    possible_next_speakers = copy.deepcopy(state.bots_in_group_convo)
    print('possible_next_speakers')
    print(possible_next_speakers)
    try:
        possible_next_speakers.remove(last_speaker)
    except:
        pass
    next_speaker = possible_next_speakers[0]

    print('next_speaker')
    print(next_speaker)
    state.speaker = next_speaker
    next_speaker_id = state.bot_names_to_ids[next_speaker]
    return next_speaker_id
