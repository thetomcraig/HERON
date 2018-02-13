import discord
import asyncio
import collections

angry_bot = discord.Client()
# Can instantiate more bots here
timeout = 1
all_messages = collections.deque([])
all_message_ids = []


def get_response(message):
    """
    Send the message to the backend
    The backend will generate a response and save it to the database, then return it
    """
    r = requests.get('API_ENDPOINT')
    all_messages.extend(message)


def send_response(channel, bot, response):
    """
    Send the response to the discord channel
    """
   await bot.send_message(channel, response)


@angry_bot.event
async def on_ready():
    print('Logged in as')
    print(angry_bot.user.name)
    print(angry_bot.user.id)
    print('------')


@angry_bot.event
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
    send_tesponse(message.channel, bot, response)



angry_bot.run('NDEyMzA2MDg1Mjk1MjkyNDE4.DWIYvg.ZmgLGCkonDoc1Nu6q-WqkcxnROw')
