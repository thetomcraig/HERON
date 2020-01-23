"""
Endpoints that are publicly available, mostly for debugging
"""
from django.http import JsonResponse
from bots.helpers.twitter_bot_utils.scraping_utils import (
    scrape,
    scrape_all_twitter_bots,
)


def scrape_bot(request, username):
    response_data = scrape(username)
    return JsonResponse(response_data)


def scrape_all_bots(request):
    """
  'people_dict' contains all the data for the updates TwitterBots
  """
    success, people_dict = scrape_all_twitter_bots()
    return JsonResponse({"success": str(success), "data": str(people_dict)})
