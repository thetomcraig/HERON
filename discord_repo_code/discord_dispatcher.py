import asyncio
import random

import discord

client = discord.Client()

timeout = 5
all_messages = []


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def get_response(message):
    """
    Send the message to the backend
    The backend will generate a response and save it to the database, then return it
    """
    # r = requests.get('API_ENDPOINT')
    # Do some corner case checking.. is this the first message?
    #  counter = 0
    #  tmp = await client.send_message(message.channel, 'Calculating messages...')
    #  async for log in client.logs_from(message.channel, limit=100):
    #  if log.author == message.author:
    #  counter += 1
    # Maybe look at all the previous messsages?
    all_messages.extend(message.content)
    return 'test hi'


@client.event
async def on_message(message):
    """
    This function will loop, it sends a message,
    then gets called again when that message gets sent
    """
    tmp = await client.send_message(message.channel, 'Calculating messages...')

    response = get_response(message)

    await client.edit_message(tmp, response)

    # Sleep for a random amount of time, then send the message
    timeout = random.randrange(1, 10)
    await asyncio.sleep(timeout)
    print('here')
    await client.send_message(message.channel, response)

client.run('NDEyMzAzNDM2OTk1MTAwNjgy.DWIYng._QQ4-O3teZmuO42S92bDLiYi6mg')
