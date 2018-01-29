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
        keyword list of the form:
            [('word or phrase', 'associated emotion', 'sentiment'),
             ('word or phrase', 'associated emotion', 'sentiment'),
             ...
            ]
        entity list of the form
            [('word or phrase', 'associated emotion', 'sentiment'),
             ('word or phrase', 'associated emotion', 'sentiment'),
             ...
            ]
        where the sentiment is either 'positive' or 'negative'
    """
    emotion_dict = watson_analyze_text_understanding(text)
    keywords_list = []
    entities_list = []

    keywords = emotion_dict.get('keywords', [])
    for k in keywords:
        text, emotion, relevance, sentiment = interpret_watson_data(k)
        keywords_list.append((text, emotion, relevance, sentiment))
    entities = emotion_dict.get('entities', [])
    for e in entities:
        text, emotion, relevance, sentiment = interpret_watson_data(k)
        entities_list.append((text, emotion, relevance, sentiment))

    return keywords_list, entities_list


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
    highest_emotion_number = 0
    text = data_dict['text']
    emotion_dict = data_dict.get('emotion', {})

    for emotion in ['anger', u'joy', u'sadness', u'fear', u'disgust']:
        if emotion_dict.get(emotion, 0) > highest_emotion_number:
            main_emotion = emotion
            highest_emotion_number = emotion_dict[emotion]

    main_sentiment = data_dict.get('sentiment').get('label')

    return text, main_emotion, highest_emotion_number, main_sentiment


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
