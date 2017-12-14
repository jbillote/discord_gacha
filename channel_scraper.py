from datetime import datetime
from logdna import LogDNAHandler

import asyncio
import boto3
import discord
import logging
import json
import sys

client = discord.Client()


@client.event
async def on_ready():
    info = {
        'id': client.user.id,
        'username': client.user.name,
        'time': str(datetime.now())
    }
    log.info('Logged in', {'meta': info})

    text_channel = client.get_channel(channel)
    logs = client.logs_from(text_channel, 1000)
    cards = []
    async for message in logs:
        for attachment in message.attachments:
            url = attachment['proxy_url']
            name = attachment['filename'].split('.', 1)[0].replace('_', ' ')

            card = {
                'image': url,
                'name': name
            }
            cards.append(card)

    dynamodb = boto3.resource("dynamodb", region_name="us-west-1",
                              endpoint_url="https://dynamodb.us-west-1.amazonaws.com")
    table = dynamodb.Table(table_name)
    table.put_item(
        Item={
            'rarity': rarity,
            'cards': cards
        }
    )
    print('Done')
    info = {
        'table_name': table_name,
        'rarity': rarity,
        'channel': channel
    }
    log.info('Added cards to database', {'meta': info})


try:
    if len(sys.argv) != 5:
        print('USAGE: channel_scraper.py path/to/config channel_id set rarity')
        exit()
    config = open(sys.argv[1])
    config_json = json.load(config)
    token = config_json['token']
    key = config_json['ingestion_key']

    # Set up logging
    log = logging.getLogger('logdna')
    log.setLevel(logging.INFO)
    options = {
        'app': 'Discord Gacha Channel Scraper',
        'hostname': 'Local Dev'
    }
    options['index_meta'] = True
    handler = LogDNAHandler(key, options)
    log.addHandler(handler)

    channel = str(sys.argv[2])
    table_name = str(sys.argv[3])
    rarity = str(sys.argv[4])

    client.run(token)
except Exception as e:
    print(e)
