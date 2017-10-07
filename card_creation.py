from enum import Enum
from PIL import Image


class Rarity(Enum):
    """
    Enum used to define constants for different card rarities.
    """
    R = 0,
    SR = 1,
    UR = 2


class Card:
    """
    Represents a card that can be obtained in a `Pack`.

    Attributes:
        image (:obj:`Image`): Completed card image
    """
    def __init__(self, character, rarity):
        foreground = None

        if rarity == Rarity.R:
            foreground = Image.open("./card_borders/r.png")
            background = Image.new("RGBA", character.size, (255, 214, 242))
            background.paste(character, (0, 0), character)
        if rarity == Rarity.SR:
            foreground = Image.open("./card_borders/sr.png")
            background = Image.new("RGBA", character.size, (215, 247, 250))
            background.paste(character, (0, 0), character)
        if rarity == Rarity.UR:
            foreground = Image.open("./card_borders/ur.png")
            background = character

        self.image = Image.new("RGBA", foreground.size)

        self.image.paste(background, (10, 10), None)
        self.image.paste(foreground, (0, 0), foreground)
