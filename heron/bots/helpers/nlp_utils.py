"""
Utilities for NLP related analysis
"""
from django.conf import settings


def determine_tweet_emotion(keywords_data, entities_data):
    list_to_analyze = []
    if not len(entities_data):
        if not len(keywords_data):
            # Both lists empty
            return ""
        # Just entitity list empty; analyze the keywords_list
        list_to_analyze = keywords_data
    # Entity list non-empty, analyze it
    list_to_analyze = entities_data

    # To get the most prominent emotion, look for the one with the highest relevance
    # If there are several items with the same emotion, that emotion is
    # weighed higher
    emotion_to_counts = {item: 0 for item in settings.WATSON_EMOTIONS}
    for item in list_to_analyze:
        emotion_in_item = item["emotion"]
        emotion_to_counts[emotion_in_item] = emotion_to_counts[emotion_in_item] + 1

    for item in list_to_analyze:
        print item

    return
