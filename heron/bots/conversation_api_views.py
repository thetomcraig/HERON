"""
Endpoints that are publicly available, mostly for debugging
"""
import json

from bots.helpers.twitter_bot_utils.conversation_utils import (
    add_posts_to_twitter_conversation,
    clear_all_twitter_conversations,
    clear_twitter_conversation,
    get_full_conversation_as_json,
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def get_conversation(request, bot1_username, bot2_username):
    conversation_json = get_full_conversation_as_json(bot1_username, bot2_username)
    return JsonResponse(conversation_json)


def update_conversation(request, bot1_username, bot2_username, post_number):
    """
  Given two conversation partners, make a new post for whomever is next
  """
    add_posts_to_twitter_conversation(
        bot1_username, bot2_username, post_number=int(post_number)
    )

    return get_conversation(request, bot1_username, bot2_username)


def clear_conversation(request, bot1_username, bot2_username):
    clear_twitter_conversation(bot1_username, bot2_username)
    return JsonResponse({"success": "true"})


def clear_all_conversations(request, bot_id):
    clear_all_twitter_conversations(bot_id)
    return JsonResponse({"success": "true"})


#  @csrf_exempt
#  def get_group_conversation(request):
    #  body = json.loads(request.body)
    #  conversation_name = body.get("conversation_name")
    #  json_data = get_group_conversation_json(conversation_name)
    #  return JsonResponse(json_data)


#  @csrf_exempt
#  def update_group_conversation(request):
    #  body = json.loads(request.body.decode("utf-8"))
    #  username = body.get("username")
    #  message = body.get("message")
    #  conversation_name = body.get("conversation_name")
    #  content = add_message_to_group_convo(username, message, conversation_name)
    #  return JsonResponse({"success": "true", "content": content})
