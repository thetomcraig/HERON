"""
Wrapper around the watson develop cloud API
Formats responses in a form that can be consumed by the twitter bots
"""
import json

import requests
from django.conf import settings
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import (EntitiesOptions,
                                                                      Features,
                                                                      KeywordsOptions)


def interpret_watson_keywords_and_entities(text):
    """
    Input:
        text to be analyzed
    Output:
        Emotion for the entire text message
        keyword dict of the form:
            {'word or phrase':
                {'emotion': associated emotion, 'relevance': revelance number, 'sentiment': associated sentimanet),
            {'word or phrase':
                {'emotion': associated emotion, 'relevance': revelance number, 'sentiment': associated sentimanet),
             ...
            }
        entity dict of the form
            {'word or phrase':
                {'emotion': associated emotion, 'relevance': revelance number, 'sentiment': associated sentimanet),
            {'word or phrase':
                {'emotion': associated emotion, 'relevance': revelance number, 'sentiment': associated sentimanet),
             ...
            }
        where the sentiment is either 'positive' or 'negative'
    """
    # All the information back from the API
    emotion_dict = watson_analyze_text_understanding(text)
    # Final lists that will hold the text objects and their metadata
    keywords_dict = {}
    entities_dict = {}
    # Most prevalent emotion from the entire API response
    overarching_emotion = ''

    keywords = emotion_dict.get('keywords', [])
    for k in keywords:
        text, emotion, relevance, sentiment = interpret_watson_data(k)
        keywords_dict[text] = {'emotion': emotion, 'relevance': relevance, 'sentiment': sentiment}
    entities = emotion_dict.get('entities', [])
    for e in entities:
        text, emotion, relevance, sentiment = interpret_watson_data(e)
        entities_dict[text] = {'emotion': emotion, 'relevance': relevance, 'sentiment': sentiment}

    overarching_emotion = get_overarching_emotion(keywords_dict, entities_dict)

    return overarching_emotion, keywords_dict, entities_dict


def interpret_watson_data(data_dict):
    """
    Input:
        dict of info returned from the watson API call
    Output:
        the original text
        the emotion most strongly associated
        the probability number for that emotion
        the main sentiment found for the text (either 'positive' or 'negative')
    """
    main_emotion = ''
    highest_emotion_relevance = 0
    text = data_dict['text']
    emotion_dict = data_dict.get('emotion', {})

    for emotion in settings.WATSON_EMOTIONS:
        if emotion_dict.get(emotion, 0) > highest_emotion_relevance:
            main_emotion = emotion
            highest_emotion_relevance = emotion_dict[emotion]

    main_sentiment = data_dict.get('sentiment').get('label')

    return text, main_emotion, highest_emotion_relevance, main_sentiment


def get_overarching_emotion(keywords_dict, entities_dict):
    """
    Input:
        Dictionaries with all the keywords and entities with their metadata
        keywords_dict:
        entities_dict:
            { text: {'emotion': emotion,
                     'relevance': relevance,
                     'sentiment': sentiment}
            }

    Output:
        The most prominent emotion in all the data given
    """
    overarching_emotion = ''

    empty_entries = {'positive': 0, 'negative': 0, 'neutral': 0}
    emotion_matrix = {}
    for emotion in settings.WATSON_EMOTIONS:
        emotion_matrix[emotion] = 0

    for key, data in keywords_dict.iteritems():
        # We add 1 to account for entries with a 0 value;
        # This way they're still accounted for
        emotion = data['emotion']
        if emotion == '':
            empty_entries[data['sentiment']] = empty_entries[data['sentiment']] + data['relevance'] + 1
        else:
            emotion_matrix[emotion] = emotion_matrix[emotion] + data['relevance'] + 1

    # Return the emotoin with the highes calculated sum
    max_emotion_count = 0
    for emotion, total in emotion_matrix.iteritems():
        if total > max_emotion_count:
            overarching_emotion = emotion

    return overarching_emotion


def watson_analyze_text_understanding(text):
    """
    Input:
        text to be analyzed
    Output:
        response from the watson API

    Taken from the watson API docs.
    """
    natural_language_understanding = NaturalLanguageUnderstandingV1(username=settings.WATSON_UNDERSTANDING_USERNAME,
                                                                    password=settings.WATSON_UNDERSTANDING_PASSWORD,
                                                                    version='2017-02-27')

    response = {}
    try:
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(
                entities=EntitiesOptions(
                    emotion=True,
                    sentiment=True,
                    limit=2),
                keywords=KeywordsOptions(
                    emotion=True,
                    sentiment=True,
                    limit=2)))
    except Exception as e:
        print e
        print 'Proceeding without the watson data'

    return response


def watson_analyze_text_emotion(data):
    """
    Input:
        text to be analyzed
    Output:
        response from the watson API
    """
    username = settings.WATSON_TONE_USERNAME
    password = settings.WATSON_TONE_PASSWORD
    url = 'https://gateway.watsonplatform.net/tone-analyzer/api/v3/tone?version=2017-09-21&text='

    headers = {"content-type": "text/plain"}
    response = requests.post(url, auth=(username, password), headers=headers, data=data.encode('utf8'))
    response_json = json.loads(response)

    tone_dict = response_json['document_tone']['tones']
    readable_dict = {x['tone_name']: x['score'] for x in tone_dict}
    return readable_dict
