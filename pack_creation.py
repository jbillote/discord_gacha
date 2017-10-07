from card_creation import Card
from card_creation import Rarity

import boto3
import requests

from io import BytesIO
from random import randint
from PIL import Image


class Pack:
    def __init__(self, table_name):
        cards = []
        self.card_names = []
        self.cards = []
        curCard = {}
        dynamodb = boto3.resource("dynamodb", region_name = "us-west-1", endpoint_url = "https://dynamodb.us-west-1.amazonaws.com")
        table = dynamodb.Table(table_name)
        for i in range(0, 5):
            roll = randint(1, 100)
            rarity_field = ""
            rarity = None
            if roll <= 82:
                rarity_field = "R"
                rarity = Rarity.R
            elif roll <= 97 and roll >= 83:
                rarity_field = "SR"
                rarity = Rarity.SR
            else:
                rarity_field = "UR"
                rarity = Rarity.UR

            response = table.get_item(
                Key={
                    "rarity": rarity_field
                }
            )
            ndx = randint(0, len(response["Item"]["cards"]))
            card = response["Item"]["cards"][ndx]
            resp = requests.get(card["image"])
            self.card_names.append(rarity_field + " " + card["name"])
            curCard["set"] = table_name
            curCard["name"] = card["name"]
            curCard["rarity"] = rarity_field
            curCard["id"] = ndx
            self.cards.append(curCard.copy())
            cards.append(Card(Image.open(BytesIO(resp.content)), rarity))

        cards[0].image = cards[0].image.rotate(50, 0, 1)
        cards[1].image = cards[1].image.rotate(25, 0, 1)
        cards[3].image = cards[3].image.rotate(-25, 0, 1)
        cards[4].image = cards[4].image.rotate(-50, 0, 1)

        self.image = Image.new("RGBA", (1500, 662))
        for offset in range(0, 2):
            left = cards[0 + offset].image
            right = cards[4 - offset].image
            self.image.paste(left, (int(450 + offset * 150 - left.size[0] / 2), int(662 / 2 - left.size[1] / 2)), left)
            self.image.paste(right, (int(1050 - offset * 150 - right.size[0] / 2), int(662 / 2 - right.size[1] / 2)), right)
        self.image.paste(cards[2].image, (int(750 - cards[2].image.size[0] / 2), int(662 / 2 - cards[2].image.size[1] / 2)), cards[2].image)
