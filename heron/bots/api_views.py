"""
Endpoints that are publicly available, mostly for debugging
"""
import json
from django.http import JsonResponse

from bots.helpers.twitter_bot_utils import (add_to_twitter_conversation,
                                            clear_all_twitter_conversations,
                                            clear_twitter_conversation,
                                            create_markov_post, get_info,
                                            get_or_create_conversation_json,
                                            get_top_twitter_bots,
                                            scrape,
                                            get_emotion_bots)
from bots.helpers.twitter_getters import (get_tweet_replies,
                                          get_tweets_over_reply_threshold_and_analyze_text_understanding,
                                          catalog_tweet_replies)
from django.views.decorators.csrf import csrf_exempt


def list_all_emotion_bots(request):
    top = get_emotion_bots()
    return JsonResponse(top)


def list_all_bots(limit=None):
    top = get_top_twitter_bots()
    return JsonResponse(top)


def get_bot_info(request, bot_id):
    info = get_info(bot_id)
    return JsonResponse(info)


def scrape_bot(request, username):
    response_data = scrape(username)
    return JsonResponse(response_data)


def get_replies_for_tweet(request, username, tweet_id):
    response_data = get_tweet_replies(username, tweet_id)
    return JsonResponse(response_data)


def get_tweets_over_threshold_and_analyze_text_understanding(request, username, threshold, response_number, scrape_mode):
    response_data = get_tweets_over_reply_threshold_and_analyze_text_understanding(
        username, scrape_mode, threshold=int(threshold), max_response_number=int(response_number))

    catalog_tweet_replies(response_data)

    return JsonResponse(response_data)


def create_post(request, bot_id):
    new_markov_post = create_markov_post(bot_id)
    return JsonResponse({'new post': new_markov_post})


def get_conversation(request, bot1_username, bot2_username):
    conversation_json = get_or_create_conversation_json(bot1_username, bot2_username)
    return JsonResponse(conversation_json)


@csrf_exempt
def update_conversation(request):
    """
    """
    print (request.body)
    print type(request.body)
    body = json.loads(request.body)
    author = body.get('author')
    partner = body.get('partner')
    new_post_json = add_to_twitter_conversation(author, partner)
    # response_data = get_response_to_message(message, author, partner)
    return JsonResponse(new_post_json)


def clear_conversation(request, bot1_username, bot2_username):
    clear_twitter_conversation(bot1_username, bot2_username)
    return JsonResponse({'success': 'true'})


def clear_all_conversations(request, bot_id):
    clear_all_twitter_conversations(bot_id)
    return JsonResponse({'success': 'true'})
