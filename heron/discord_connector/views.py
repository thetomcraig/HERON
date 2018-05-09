# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from . import state
from bots.helpers.twitter_bot_utils import add_to_group_convesation

from django.http import JsonResponse


# Create your views here.
def message_received(request):
    body = json.loads(request.body)
    key = body.get('key')
    message = body.get('message')

    username = state.bots_map[key]
    next_speaker, next_message = add_to_group_convesation(username, message, state.bots_in_group_convo)

    state.next_speaker = next_speaker
    state.next_message = next_message
    return JsonResponse({'success': 'true'})


def reply_query(request):
    return JsonResponse({'success': 'true', 'next_message': state.next_message, 'next_speaker': state.next_speaker})
