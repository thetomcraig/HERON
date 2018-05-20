# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import json
from . import state
from bots.helpers.twitter_bot_utils import add_message_to_group_convo
from bots.models.twitter import TwitterConversation, TwitterBot, TwitterPost
import random

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def message_received(request):
    print('received call')
    body = json.loads(request.body.decode('utf-8'))
    username = body.get('name')
    message = body.get('message')
    conversation_name = body.get('conversation_name')

    # First save the new message to the database
    add_message_to_group_convo(username, message, conversation_name)

    repliers_key, next_message = generate_next_speaker_and_message(conversation_name)

    state.message = next_message

    reply = state.message
    return JsonResponse({'key': repliers_key,
                         'reply': reply})


def reply_query(request):
    return JsonResponse({'success': 'true', 'next_message': state.next_message, 'next_speaker': state.next_speaker})


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
