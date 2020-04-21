from typing import List, Dict
from random import shuffle
from enum import Enum

class Suit(Enum):
    SPADES = '\u2660'
    CLUBS = '\u2663'
    HEARTS = '\u2665'
    DIAMONDS = '\u2666'

    def __str__(self):
        return self.value

    def to_json(self):
        return self.name.lower()

class Rank(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

    def __str__(self):
        return self.name[0] + self.name.lower()[1:]

    def to_json(self):
        return self.value - 1

class Card():
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def to_json(self):
        return {'suit': self.suit.to_json(),
                'rank': self.rank.to_json()}

    def __str__(self) -> str:
        return '{} {}'.format(self.rank, self.suit)

    def __repr__(self) -> str:
        return self.__str__()

class Deck():
    def __init__(self, double=False):
        self.draw_pile = list()
        self.discard_pile = list()

        for s in Suit:
            for r in Rank:
                self.draw_pile.append(Card(s, r))
                if double:
                    self.draw_pile.append(Card(s, r))

        shuffle(self.draw_pile)

    def draw(self) -> Card:
        return self.draw_pile.pop()

    def draw_hand(self, n=10) -> List[Card]:
        return [self.draw() for x in range(0, n)]
