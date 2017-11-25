from django.http import JsonResponse

from bots.helpers.twitter_utils import (
    get_top_twitter_bots,
    get_info,
    scrape,
    create_markov_post,
    get_or_create_conversation_json,
    add_to_twitter_conversation,
)


def list_all_bots(limit=None):
    top = get_top_twitter_bots()
    return JsonResponse(top)


def get_bot_info(request, bot_id):
    info = get_info(bot_id)
    return JsonResponse(info)


def scrape_bot(request, bot_id):
    response_data = scrape(bot_id)
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
    return JsonResponse({'success': 'stub'})


def clear_all_conversations(request, bot_id):
    return JsonResponse({'success': 'stub'})
