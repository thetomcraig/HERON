from bots.helpers.twitter_utils import (add_to_twitter_conversation,
                                        clear_all_twitter_conversations,
                                        clear_twitter_conversation,
                                        create_markov_post, get_info,
                                        get_or_create_conversation_json,
                                        get_top_twitter_bots,
                                        get_tweet_replies, scrape)
from django.http import JsonResponse


def list_all_bots(limit=None):
    top = get_top_twitter_bots()
    return JsonResponse(top)


def get_bot_info(request, bot_id):
    info = get_info(bot_id)
    return JsonResponse(info)


def scrape_bot(request, bot_id):
    response_data = scrape(bot_id)
    return JsonResponse(response_data)


def get_replies_for_tweet(request, username, tweet_id):
    response_data = get_tweet_replies(username, tweet_id)
    return JsonResponse(response_data)


def create_post(request, bot_id):
    new_markov_post = create_markov_post(bot_id)
    return JsonResponse({'new post': new_markov_post})


def get_conversation(request, bot1_id, bot2_id):
    conversation_json = get_or_create_conversation_json(bot1_id, bot2_id)
    return JsonResponse(conversation_json)


def update_conversation(request, bot1_id, bot2_id):
    new_post_json = add_to_twitter_conversation(bot1_id, bot2_id)
    return JsonResponse(new_post_json)


def clear_conversation(request, bot1_id, bot2_id):
    clear_twitter_conversation(bot1_id, bot2_id)
    return JsonResponse({'success': 'true'})


def clear_all_conversations(request, bot_id):
    clear_all_twitter_conversations(bot_id)
    return JsonResponse({'success': 'true'})
