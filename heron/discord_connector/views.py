# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import json
from django.conf import settings
import random
from bots.helpers.watson_utils import interpret_watson_keywords_and_entities
from .state_manager import initialize_conversation_sate, add_bot_to_conversation_state

# from bots.helpers.twitter_bot_utils import add_message_to_group_convo
from bots.models.twitter import TwitterConversation, TwitterBot, TwitterPost

#  from bots.helpers.utils import create_post_cache, replace_tokens

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def bot_online(request):
    """
    Called when a bot logs in on Discord.
    The Bot's information is saved in the conversation's state
    Using the passed in conversaion name,
    the conversation in the current state is updated to include the bot
    """
    body = json.loads(request.body.decode("utf-8"))
    key = body.get("key")
    username = body.get("username")
    conversation_name = body.get("conversation_name")
    # Get the global state for this convo, and add the bot
    state = settings.DISCORD_CONVERSATION_STATES.get(conversation_name, {})
    state = add_bot_to_conversation_state(state, key, username)
    settings.DISCORD_CONVERSATION_STATES.setdefault(conversation_name, state)

    return JsonResponse({"success": True})


@csrf_exempt
def get_message(request):
    """
    Called by a Discord bot when they need a new message
    We run the generator and generate a new message and a new speaker to send it
    """
    body = json.loads(request.body.decode("utf-8"))
    username = body.get("username")
    conversation_name = body.get("conversation_name")

    next_speaker, message = run_generator(conversation_name)

    if not (next_speaker and message):
        return JsonResponse({"success": True, "should_send": False, "message": None})

    should_send = username == next_speaker
    return JsonResponse(
        {"success": True, "should_send": should_send, "message": message}
    )


def run_generator(conversation_name):
    """
    Input:
        conversation_name: name of conversation to analyze
    Output:
        username of next speaker, message for that speaker to send next
    """
    state = settings.DISCORD_CONVERSATION_STATES.get(conversation_name, {})

    (
        next_speaker_username,
        next_message,
        convo,
        index,
    ) = generate_next_speaker_and_message(state, conversation_name)
    if not next_speaker_username:
        return None, None

    bot = TwitterBot.objects.get(username=next_speaker_username)
    post = TwitterPost.objects.create(author=bot, content=next_message)
    convo.twitterconversationpost_set.create(index=index, author=bot, post=post)

    return next_speaker_username, next_message


def generate_next_speaker_and_message(state, conversation_name):
    """
    Input:
        state: The entire state of the conversation
        conversation_name: The name of the conversation
    """
    convo = TwitterConversation.objects.get(name=conversation_name)
    posts = convo.twitterconversationpost_set.order_by("index").all()

    next_speaker_username = generate_next_speaker(state, posts)
    next_message, index = generate_next_message(
        state, convo, next_speaker_username, posts
    )

    return next_speaker_username, next_message, convo, index


def generate_next_speaker(state, posts):
    """
    Get the conversation and all previous posts - there should be at least one
    Last speaker was author of that post
    Determine new speaker
    """
    last_post = posts.last()
    last_speaker = last_post.author.username
    possible_next_speakers = copy.deepcopy(state.get("bots_in_group_convo"))
    if len(possible_next_speakers) < 2:
        print("not enough people conversation yet")
        return None, -1

    # Replace with random stuff. for debugging just doing the other user
    try:
        possible_next_speakers.remove(last_speaker)
    except Exception as e:
        print(e)
    next_speaker_username = possible_next_speakers[0]

    return next_speaker_username


def generate_next_message(state, convo, next_speaker_username, posts):
    """
    Look at convo
        Iterate through the conversation
        Find recent sentiment and key terms/subjects

    Generate new message
        Make markov message from next_speaker
        TODO - Need some other rules here for iterating on speech patterns
            Basically need things to be more AI/Machine Learning esque
        Keyword replacement

    """
    next_message = "None made"
    next_index = -1
    previous_messages = []
    try:
        last_post = posts.last()
        next_index = last_post.index + 1
        previous_messages.append(last_post.post.content)
    except Exception:
        print("No last post!")
        print("List of posts passed in with len: {}".format(len(posts)))

    # Number of previous messages to look at/analyze
    # Start at 1 because we already recorded the last one
    lookback = 4
    counter = 1
    reversed_posts = reversed(posts)
    try:
        while counter < lookback:
            previous_messages.append(reversed_posts[counter])
            counter += 1
    except IndexError:
        print("Index Error; number of posts less than lookback range")
    finally:
        print("gathered {} previous posts".format(counter))

    # Found the last couple of messages, now look at the bot
    bot = TwitterBot.objects.get(username=next_speaker_username)
    all_beginning_caches = bot.twitterpostcache_set.filter(beginning=True)
    all_caches = bot.twitterpostcache_set.all()
    # The template represents how this bot talks,
    # We will alter this text based on the previous conversation posts
    new_markov_template, randomness = bot.apply_markov_chains_inner(
        all_beginning_caches, all_caches
    )
    _, markov_keywords, markov_entities = interpret_watson_keywords_and_entities(
        new_markov_template
    )

    # TODO this should turn into a loop of some sort
    last_message = reversed_posts[0]
    # Use the emotion of the last speaker to figure out what to say, maybe means adding a new user??
    overarching_emotion, keywords, entities = interpret_watson_keywords_and_entities(
        last_message
    )

    # Look at the keywords in the previous post and see if they can be injected into the new markov post
    replacements = {}
    for keyword, data in keywords.iteritems():
        emotion = data.get("emotion")
        for markov_keyword, markov_data in markov_keywords.iteritems():
            markov_emotion = markov_data.get("emotion")
            if emotion == markov_emotion:
                replacements[markov_keyword] = keyword

    for entity, data in entities.iteritems():
        emotion = data.get("emotion")
        for markov_keyword, markov_data in markov_keywords.iteritems():
            markov_emotion = markov_data.get("emotion")
            if emotion == markov_emotion:
                if markov_keyword not in replacements.keys():
                    replacements[markov_keyword] = entity

    for phrase, replacement in replacements.iteritems():
        new_markov_template = new_markov_template.replace(phrase, replacement)

    next_message = new_markov_template
    create_post_cache(next_message, bot.twitterpostcache_set)
    return next_message, next_index
