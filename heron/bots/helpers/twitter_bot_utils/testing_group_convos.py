

def get_group_conversation_json(conversation_name):
    conversation = TwitterConversation.objects.get_or_create(name=conversation_name)[0]
    conversation_json = {}
    for conv_post in conversation.twitterconversationpost_set.all():
        conversation_json[conv_post.index] = {
            conv_post.post.author.username: conv_post.post.content
        }



def add_message_to_group_convo(bot_username, message, conversation_name):
    print (bot_username)
    print (message)
    print (conversation_name)
    conversation = TwitterConversation.objects.get_or_create(name=conversation_name)[0]
    bot = TwitterBot.objects.get_or_create(username=bot_username)[0]

    # Make sure this hasn't been added already
    sorted_conversation_posts = conversation.twitterconversationpost_set.order_by(
        "index"
    ).all()
    if len(sorted_conversation_posts):
        if sorted_conversation_posts.last().post.content == message:
            return message

    # This has not been added to the convo yet, so proceed
    post = TwitterPost.objects.create(tweet_id=-1, author=bot, content=message)

    index = conversation.twitterconversationpost_set.count()
    conversation_post = TwitterConversationPost.objects.create(
        author=bot, post=post, conversation=conversation, index=index
    )

    return conversation_post.post.content
