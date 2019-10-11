"""
Endpoints that are publicly available, mostly for debugging
"""
import json

from bots.helpers.twitter_bot_utils.emotion_utils import (
    list_all_emotion_twitter_bots,
    add_new_tweets_to_emotion_bot
)
from bots.helpers.twitter_bot_utils.crud_utils import (
    clear_twitter_bot,
    get_all_twitter_bots,
    get_twitter_bot_info,
    create_twitter_bots_for_top_users,
)
from bots.helpers.twitter_getters import (
    catalog_tweet_replies,
    get_tweet_replies,
    get_tweets_over_reply_threshold_and_analyze_text_understanding)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def create_top_bots(request, limit=None):
  success, all_bot_data = create_twitter_bots_for_top_users()
  return JsonResponse({'success': str(success), 'data': all_bot_data})


def get_all_bots(request, limit=None):
  success, all_bot_data = get_all_twitter_bots()
  return JsonResponse({'success': str(success), 'data': all_bot_data})


def get_bot(request, username):
  data = get_twitter_bot_info(username)
  return JsonResponse({'success': str(True), 'data': data})


def clear_bot_tweets(request, username):
  clear_twitter_bot(username)
  return JsonResponse({'success': 'true'})


def list_all_emotion_bots(limit=None):
  bots = list_all_emotion_twitter_bots()
  return JsonResponse(bots)


def get_replies_for_tweet(request, username, tweet_id):
  response_data = get_tweet_replies(username, tweet_id)
  return JsonResponse(response_data)


def get_tweets_over_threshold_and_analyze_text_understanding(request,
                                                             username, threshold, response_number, scrape_mode):
  response_data = get_tweets_over_reply_threshold_and_analyze_text_understanding(
      username,
      scrape_mode,
      threshold=int(threshold),
      max_response_number=int(response_number))

  catalog_tweet_replies(response_data)

  return JsonResponse(response_data)


def create_post(request, bot_id):
  new_markov_post = create_markov_post(bot_id)
  return JsonResponse({'new post': new_markov_post})


@csrf_exempt
def update_emotion_bot(request):
  """
  Input:
      request with:
          bot to attach replies to
          emotion that we will filter agains
          source list of twitter users who's replies we will analyze

  Get the replies and analysis for all the source twitter users sepcified
  Get all the replies that match the given emotion and attach them to the given bot


  """
  body = json.loads(request.body)
  new_tweets = add_new_tweets_to_emotion_bot(body)
  return JsonResponse({'new_tweets': new_tweets})
