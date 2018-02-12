import discord
import asyncio
import collections

client = discord.Client()
timeout = 1
all_messages = collections.deque([])
all_message_ids = []



def get_response(message):
r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
    all_messages.extend(message)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    while True:
        await asyncio.sleep(timeout)
        response = get_response(message)
        await client.send_message(message.channel, response)

client.run('NDEyMzA2MDg1Mjk1MjkyNDE4.DWIYvg.ZmgLGCkonDoc1Nu6q-WqkcxnROw')
