# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from . import state
from bots.helpers.twitter_bot_utils import add_message_to_group_convo
from bots.models.twitter import TwitterConversation, TwitterBot, TwitterPost
import random

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def message_received(request):
    body = json.loads(request.body)
    key = body.get('key')
    message = body.get('message')
    conversation_name = body.get('conversation_name')
    username = state.bot_ids_to_names[key]

    # First save the new message to the database
    add_message_to_group_convo(username, message, conversation_name)

    next_speaker, next_message = generate_next_speaker_and_message(conversation_name)

    state.speaker = next_speaker
    state.message = next_message
    return JsonResponse({'success': 'true',
                         'speaker': state.speaker,
                         'mesage': state.message})


def reply_query(request):
    return JsonResponse({'success': 'true', 'next_message': state.next_message, 'next_speaker': state.next_speaker})


def generate_next_speaker_and_message(conversation_name):
    """
    Given the conversatino name
    Get the conversation and all previous posts - there should be at least one
    """
    convo = TwitterConversation.objects.get(name=conversation_name)
    posts = convo.twitterconversationpost_set.order_by('index').all()
    next_speaker = posts.last().author.username
    next_message = 'yup'

    # If only one bot has spoken so far
    # Randomly choose a new one from the list of bots,
    # minus the one in question
    # If two have spoken, possibly choose a new one
    unique_speakers_so_far = set([x.author.username for x in posts])
    number_unique_speakers_so_far = len(unique_speakers_so_far)
    if number_unique_speakers_so_far == 1:
        next_speaker = random.choice(list(state.bots_in_group_convo - unique_speakers_so_far))
    if number_unique_speakers_so_far == 2:
        if random.randint(1, 2) == 1:
            next_speaker = random.choice(list(state.bots_in_group_convo - unique_speakers_so_far))
        else:
            next_speaker = posts[-2].author.username

    next_speaker_id = state.bot_names_to_ids[next_speaker]
    return next_speaker_id, next_message
