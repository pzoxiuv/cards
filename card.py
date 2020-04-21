from itertools import cycle
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

class Player():
    def __init__(self, ws, name: str, theta: int):
        self.hand = []
        self.table = []
        self.ws = ws
        self.name = name
        self.theta = theta

    def add_card(self, c: Card) -> None:
        self.hand.append(c)

    def show_hand(self) -> None:
        for i, c in enumerate(self.hand):
            print('{}: {}'.format(i, c))

    def get_hand(self) -> List[str]:
        return [{'rank': x.rank.to_json(), 'suit': x.suit.to_json()} for x in self.hand]

"""
class Game():
    def __init__(self):
        self.deck = Deck(double=True)
        self.players = {}
        self.thetas = [0, 180, 60, 120, 240, 300]

    def add_player(self, data, name: str) -> None:
        if name in self.players:
            self.players[name].data = data
        else:
            cur_theta = len(self.players)
            player = Player(data, name, self.thetas[cur_theta])
            player.hand = self.deck.draw_hand()
            self.players[name] = player

    def get_names(self):
        ret = {}
        for name, p in self.players.items():
            ret[name] = p.theta
        return ret
"""
