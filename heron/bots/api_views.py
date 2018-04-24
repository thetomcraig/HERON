"""
Endpoints that are publicly available, mostly for debugging
"""
import json

from bots.helpers.twitter_bot_utils import (add_new_tweets_to_emotion_bot,
                                            add_to_twitter_conversation,
                                            clear_all_twitter_conversations,
                                            clear_twitter_bot,
                                            clear_twitter_conversation,
                                            create_markov_post, get_info,
                                            get_or_create_conversation_json,
                                            get_top_twitter_bots,
                                            list_all_emotion_twitter_bots,
                                            scrape, update_top_twitter_bots)
from bots.helpers.twitter_getters import (catalog_tweet_replies,
                                          get_tweet_replies,
                                          get_tweets_over_reply_threshold_and_analyze_text_understanding)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def list_all_bots(limit=None):
    top = get_top_twitter_bots()
    return JsonResponse(top)


def get_bot_info(request, username):
    info = get_info(username)
    return JsonResponse(info)


def scrape_bot(request, username):
    response_data = scrape(username)
    return JsonResponse(response_data)


def scrape_bots(request):
    success = update_top_twitter_bots()
    return JsonResponse({'success': str(success)})


def clear_bot_tweets(request, username):
    clear_twitter_bot(username)
    return JsonResponse({'success': 'true'})


def list_all_emotion_bots(limit=None):
    bots = list_all_emotion_twitter_bots()
    return JsonResponse(bots)


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
    Given two conversation partners, make a new post for whomever is next
    """
    body = json.loads(request.body)
    author = body.get('author')
    partner = body.get('partner')
    post_number = body.get('post_number', 1)
    new_post_json = add_to_twitter_conversation(author, partner, post_number=post_number)
    return JsonResponse(new_post_json)


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


def clear_conversation(request, bot1_username, bot2_username):
    clear_twitter_conversation(bot1_username, bot2_username)
    return JsonResponse({'success': 'true'})


def clear_all_conversations(request, bot_id):
    clear_all_twitter_conversations(bot_id)
    return JsonResponse({'success': 'true'})
