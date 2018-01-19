from datetime import datetime, timedelta
from dateutil import parser
from io import BytesIO
from logdna import LogDNAHandler
from pack_creation import Pack

import asyncio
import boto3
import discord
import logging
import json
import sys
import traceback

client = discord.Client()

def can_pull(user, draw_time, last_draw, use_cache):
    if use_cache:
        return not(draw_time - timedelta(hours=20) <= last_opened_cache[user] <= draw_time)
    else:
        return not(draw_time - timedelta(hours=20) <= last_draw <= draw_time)

def next_pull_message(draw_time, last_pull_time):
    next_pull = last_pull_time + timedelta(days=1)
    hours = int((next_pull - draw_time).seconds / 60 / 60)
    minutes = int((next_pull - draw_time).seconds / 60 % 60)
    return "Slow down! It hasn't been 20 hours since your last pack opening! Try again in " + str(hours) + " hour(s) " + str(minutes) + " minutes."


@client.event
async def on_ready():
    info = {
        'id': client.user.id,
        'username': client.user.name,
        'time': str(datetime.now())
    }
    log.info('Logged in', { 'meta': info })


@client.event
async def on_message(message):
    split_message = message.content.split(" ", 1)
    if split_message[0] == ".pack":
        if len(split_message) > 1 and split_message[1] in packs.keys():
            draw = False

            # Get current time
            draw_time = datetime.now()

            # Check cache first to see if a draw is available
            if message.author.id in last_opened_cache:
                if can_pull(message.author.id, draw_time, None, True):
                    draw = True
                else:
                    draw = False
                    await client.send_message(message.channel, next_pull_message(draw_time, last_opened_cache[message.author.id]))

            try:
                # Get user info
                dynamodb = boto3.resource("dynamodb", region_name = "us-west-1", endpoint_url = endpoint_url)
                table = dynamodb.Table(users_table)
                response = table.get_item(
                    Key={
                        "user_id": message.author.id
                    }
                )

                # Check if user already exists in database
                if "Item" in response.keys():
                    # If user not in cache, check to see if they can pull
                    if message.author.id not in last_opened_cache:
                        last_pack_opened = parser.parse(response["Item"]["last_pack_opened"])
                        last_opened_cache[message.author.id] = last_pack_opened

                        if not can_pull(message.author.id, draw_time, last_pack_opened, False):
                            await client.send_message(message.channel, next_pull_message(draw_time, last_pack_opened))
                            draw = False
                        else:
                            draw = True
                else:
                    draw = True

                if draw:
                    pack = Pack(packs[split_message[1]]["table"])

                    fd = BytesIO()
                    pack.image.save(fd, "png")
                    fd.seek(0)

                    if "Item" in response.keys():
                        # User already exists in database
                        user_cards = response["Item"]["cards"]
                    else:
                        # User does not exist in database
                        user_cards = []

                    for card in pack.cards:
                        ndx = 0
                        found = False
                        while ndx < len(user_cards) and not found:
                            found = (card["id"] == user_cards[ndx]["id"] and card["rarity"] == user_cards[ndx]["rarity"] and card["set"] == user_cards[ndx]["set"])
                            if not found:
                                ndx += 1

                        if found:
                            user_cards[ndx]["quantity"] += 1
                        else:
                            new_card = {}
                            new_card["set"] = card["set"]
                            new_card["rarity"] = card["rarity"]
                            new_card["id"] = card["id"]
                            new_card["quantity"] = 1
                            user_cards.append(new_card)

                    table.put_item(
                        Item={
                            "user_id": message.author.id,
                            "last_pack_opened": str(draw_time),
                            "cards": user_cards,
                            "username": str(message.author),
                            "username_searchable": str(message.author).lower()
                        }
                    )

                    last_opened_cache[message.author.id] = draw_time

                    obtained_embed = discord.Embed(color=0x0054a6)
                    for ndx in range(0, len(pack.card_names)):
                        split_name = pack.card_names[ndx].split(' ', 1)
                        obtained_embed.add_field(name=split_name[0], value=split_name[1], inline=False)

                    await client.send_message(message.channel, str(message.author).split('#')[0] + " obtained:", embed=obtained_embed)
                    await client.send_file(message.channel, fd, filename="pack.png")
            except Exception as e:
                meta = {
                    'message': str(e),
                    'stacktrace': traceback.format_exc()
                }

                log.info('Unable to obtain pack', { 'level': 'Error', 'meta': meta })
                await client.send_message(message.channel, "Something went wrong getting your pack D:")
        elif len(split_message) > 1:
            await client.send_message(message.channel, "The pack ``" + split_message[1] + "`` doesn't exist.")
        else:
            await client.send_message(message.channel, "Please specify the name of a pack to open.")
    elif split_message[0] == ".help":
        # Get the pack names alphabetically
        packs_keys = sorted(packs.keys())

        embed = discord.Embed(title="Available Packs", description="Packs currently available", color=0x0054a6)
        for k in packs_keys:
            embed.add_field(name=k, value=packs[k]["name"], inline=False)
        await client.send_message(message.author, embed=embed)


token = ''
key = ''
endpoint_url = ''
users_table = ''
config_json = {}
packs = {}
last_opened_cache = {}

try:
    if len(sys.argv) != 3:
        print('USAGE: bot.py path/to/config pack/to/packs')
        exit()
    config = open(sys.argv[1])
    config_json = json.load(config)
    token = config_json['token']
    key = config_json['ingestion_key']
    endpoint_url = config_json['dynamodb_endpoint']
    users_table = config_json['users_table']

    packs_file = open(sys.argv[2])
    packs = json.load(packs_file)
except Exception as e:
    print(e)
    exit()


# Set up logging to LogDNA
log = logging.getLogger('logdna')
log.setLevel(logging.INFO)
options = {
    'app': 'Discord Gacha',
    'hostname': config_json['hostname'],
    'index_meta': True
}
handler = LogDNAHandler(key, options)
log.addHandler(handler)

# Also log to stdout
log.addHandler(logging.StreamHandler())

# Log Discord errors too
discord_log = logging.getLogger('discord')
discord_log.setLevel(logging.ERROR)
discord_log.addHandler(handler)

client.run(token)
