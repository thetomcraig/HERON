import discord
import asyncio
import collections
import requests

client = discord.Client()
# Can instantiate more bots here
timeout = 1
all_messages = []
all_message_ids = []


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
    #r = requests.get('API_ENDPOINT')
    all_messages.extend(message.content)
    return 'test hi'




@client.event
async def on_message(message):
    """
    This function will loop, it sends a message,
    then gets called again when that message gets sent
    """
    # Do some corner case checking.. is this the first message?
    # Maybe look at all the previous messsages?
    response = get_response(message)
    # Sleep for a random amount of time, then send the message
    await asyncio.sleep(timeout)
    print('here')
    await client.send_message(message.channel, response)


client.run('NDEyMzA2MDg1Mjk1MjkyNDE4.DWIYvg.ZmgLGCkonDoc1Nu6q-WqkcxnROw')
