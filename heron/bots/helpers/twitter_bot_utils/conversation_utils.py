import random

from bots.helpers.twitter_bot_utils.text_generation_utils import (
    text_generation_utils_lookup,
)
from bots.models.twitter import (
    TwitterBot,
    TwitterConversation,
    TwitterConversationPost,
)
from django.conf import settings


def get_or_create_conversation(bot1_username, bot2_username):
    bot, _ = TwitterBot.objects.get_or_create(username=bot1_username)
    partner, _ = TwitterBot.objects.get_or_create(username=bot2_username)

    conversation = None
    try:
        conversation = TwitterConversation.objects.get(author=bot, partner=partner)
    except:
        pass
    try:
        conversation = TwitterConversation.objects.get(author=partner, partner=bot)
    except:
        pass
    if not conversation:
        conversation = TwitterConversation.objects.create(author=bot, partner=partner)
    return conversation


def get_full_conversation_as_json(bot1_username, bot2_username):
    conversation = get_or_create_conversation(bot1_username, bot2_username)
    conversation_json = {
        "id": conversation.id,
        "bot1": conversation.author.username,
        "bot2": conversation.partner.username,
        "posts": {},
    }
    for _, conv_post in enumerate(conversation.twitterconversationpost_set.all()):
        conversation_json["posts"][conv_post.index] = {
            conv_post.author.username + ": ": conv_post.post.content
        }
    return conversation_json


def get_next_speaker_and_last_speaker(conversation_posts, author, partner):
    """
    Input:
        All the current posts in a 2 speaker conversation
        The two speakers
    Output:
        Based on the given list of posts, return who speaks next and who spoke last
    """
    last_speaker = author
    next_speaker = partner

    last_post = conversation_posts.last()
    if last_post:
        if last_post.author == next_speaker:
            last_speaker = partner
            next_speaker = author

    return next_speaker, last_speaker


def clear_twitter_conversation(bot1_username, bot2_username, conversation=None):
    if not conversation:
        conversation = get_or_create_conversation(bot1_username, bot2_username)

    for convo_post in conversation.twitterconversationpost_set.all():
        convo_post.post.delete()
        convo_post.delete()
    conversation.delete()
    return True


def clear_all_twitter_conversations(bot_id):
    bot = TwitterBot.objects.get(id=bot_id)
    conversations = TwitterConversation.objects.filter(author=bot)
    for c in conversations:
        clear_twitter_conversation(c)


def generate_new_conversation_post_text(bot_id, previous_posts):
    """
    This is where you can tweak the function used to generate new text
    """
    alg = settings.TEXT_GENERATION_FUNCTION
    text_generation_function = text_generation_utils_lookup.get(alg)
    new_text = text_generation_function(bot_id, previous_posts)
    return new_text


def add_single_post_to_twitter_conversation(conversation_id, index, next_speaker):
    """
    Given a conversation ID, grab all the posts in the conversation and sort them
    Then generate the text of a new post
    Then make a new post object
    """
    conversation = TwitterConversation.objects.get(id=conversation_id)
    previous_posts = conversation.twitterconversationpost_set.order_by(
        "index"
    ).all()

    # If the conversation has no posts, don't bother doing anything fancy
    # To kick things off, choose a random post from the user
    reply_text = ""
    if len(previous_posts) == 0:
        post_set = next_speaker.twitterpost_set.all()
        # Should always have at least ONE
        if post_set.count():
            random_post = random.choice(next_speaker.twitterpost_set.all())
            reply_text = random_post.content
    # Otherwise, the conversation is not empty
    # So make new text for reply post
    else:
        reply_text = generate_new_conversation_post_text(
            next_speaker.id, previous_posts
        )

    new_post = next_speaker.twitterpost_set.create(tweet_id=-1, content=reply_text)
    # TODO, fix
    #create_post_cache(reply_text, next_speaker.twitterpostcache_set)

    new_convo_post = TwitterConversationPost.objects.create(
        post=new_post, conversation=conversation, author=next_speaker, index=index
    )
    return new_convo_post


def add_posts_to_twitter_conversation(bot1_username, bot2_username, post_number=1):
    """
    First we sort the conversation query dict by index
    Then, repeatedly:
        Get the index for the new post
        Get the next speaker
        Generate the new ConversationPost object
    """
    newly_created_posts = []

    conversation = get_or_create_conversation(bot1_username, bot2_username)
    sorted_conversation_posts = conversation.twitterconversationpost_set.order_by(
        "index"
    ).all()

    index = 0
    if len(sorted_conversation_posts):
        index = sorted_conversation_posts.last().index + 1

    next_speaker, last_speaker = get_next_speaker_and_last_speaker(
        sorted_conversation_posts, conversation.author, conversation.partner
    )
    for _ in range(post_number):
        new_post = add_single_post_to_twitter_conversation(
            conversation.id, index, next_speaker
        )
        newly_created_posts.append(new_post)

        # Switch the speakers
        last_speaker, next_speaker = next_speaker, last_speaker
        index += 1
    return newly_created_posts
