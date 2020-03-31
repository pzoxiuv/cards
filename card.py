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

class TurnStage(Enum):
    NOT_STARTED = 'Game not started'
    DRAW_CARD = 'Draw card'
    DISCARD = 'Discard'

    def __str__(self):
        return self.value

class Card():
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

        if rank == Rank.TWO and suit in (Suit.HEARTS, Suit.DIAMONDS):
            self.score = 20
        elif rank in (Rank.JACK, Rank.QUEEN, Rank.KING):
            self.score = 10
        elif rank == Rank.ACE:
            self.score = 15
        else:
            self.score = rank.value

    def __str__(self) -> str:
        return '{} {}'.format(self.rank, self.suit)

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other) -> int:
        return self.score + other.score

class Deck():
    def __init__(self):
        self.draw_pile = list()
        self.discard_pile = list()

        for s in Suit:
            for r in Rank:
                self.draw_pile.append(Card(s, r))
                self.draw_pile.append(Card(s, r))
        assert len(self.draw_pile) == 104

        #shuffle(self.draw_pile)

    def draw(self) -> Card:
        return self.draw_pile.pop()

    def discard(self, c: Card) -> None:
        self.discard_pile.append(c)

    def draw_hand(self) -> List[Card]:
        return [self.draw() for x in range(0, 10)]

class Player():
    def __init__(self, data, name: str):
        self.hand = []
        self.data = data
        self.playing = True
        self.name = name
        self.score = 0
        self.down = False

        self.tricks = []

    def add_card(self, c: Card) -> None:
        self.hand.append(c)

    def show_hand(self) -> None:
        for i, c in enumerate(self.hand):
            print('{}: {}'.format(i, c))

    def get_hand(self) -> List[str]:
        return [{'rank': x.rank.to_json(), 'suit': x.suit.to_json()} for x in self.hand]
        #return [str(x) for x in self.hand]

    def score_hand(self) -> int:
        for c in self.hand:
            self.score += c.score

    def discard(self, rank, suit) -> Card:
        index = None
        for i, c in enumerate(self.hand):
            if c.rank.to_json() == rank and c.suit.to_json() == suit:
                index = i
        assert index != None
        return self.hand.pop(index)

class Game():
    def __init__(self):
        self.deck = Deck()
        self.players = {}
        self.player_order = None
        self.cur_player = None

        self.started = False
        self.can_take_throwcard = False

        self.round = 1;
        self.reqs = [{'threes': 2, 'fours': 0, 'empty': 1},
                     {'threes': 1, 'fours': 1, 'empty': 1},
                     {'threes': 0, 'fours': 2, 'empty': 1},
                     {'threes': 3, 'fours': 0, 'empty': 0},
                     {'threes': 2, 'fours': 1, 'empty': 0},
                     {'threes': 1, 'fours': 2, 'empty': 0},
                     {'threes': 0, 'fours': 3, 'empty': 0}]

        self.turn_stage = TurnStage.NOT_STARTED

    def start_game(self) -> None:
        self.started = True
        self.turn_stage = TurnStage.DRAW_CARD
        self.player_order = cycle(list(self.players.keys()))
        self.cur_player = next(self.player_order)

    def add_player(self, data, name: str) -> None:
        if name in self.players:
            self.players[name].data = data
            self.players[name].playing = True
        else:
            player = Player(data, name)
            player.hand = self.deck.draw_hand()
            self.players[name] = player

    def remove_player(self, name) -> None:
        self.players[name].playing = False

    def draw_card(self, name) -> None:
        if self.turn_stage != TurnStage.DRAW_CARD:
            print('WARNING wrong turn stage')
            return
        elif name != self.cur_player:
            print('WARNING wrong player')
            return

        self.players[name].add_card(self.deck.draw())
        self.can_take_throwcard = False
        self.turn_stage = TurnStage.DISCARD

    def take_throwcard(self, name) -> None:
        if self.turn_stage != TurnStage.DRAW_CARD:
            print('WARNING wrong turn stage')
            return
        elif name != self.cur_player:
            print('WARNING wrong player')
            return
        assert self.turn_stage == TurnStage.DRAW_CARD
        assert self.can_take_throwcard

        self.players[name].add_card(self.deck.discard_pile.pop())
        self.can_take_throwcard = False
        self.turn_stage = TurnStage.DISCARD

    def validate_tricks(self, tricks) -> bool:
        def is_redtwo(c):
            return int(c['rank']) == 2 and c['suit'] in ('diamonds', 'hearts')

        def is_empty(trick):
            print('is empty? ' + str(len(trick) == 0))
            return len(trick) == 0

        def is_three(trick):
            num = None
            for c in trick:
                if is_redtwo(c):
                    continue
                n = int(c['rank'])
                if num is None:
                    num = n
                elif n != num:
                    print('is_three returning false ' + str(num) + ' ' + str(n))
                    return False
            return len(trick) >= 3

        def same_suit(trick):
            suit = None
            for c in trick:
                if is_redtwo(c):
                    continue
                if suit is None:
                    suit = c['suit']
                elif c['suit'] != suit:
                    print('same_suit returning false ' + suit + ' ' + c['suit'])
                    return False
            return True

        def is_four(trick):
            if not same_suit(trick):
                print('not same suit')
                return False
            if len(trick) < 4:
                print('less than 4')
                return False
            order = sorted(trick, key=lambda x: x['x'])
            prev = None
            prev = int(order[0]['rank'])
            print(order)
            for c in order[1:]:
                if prev is None:
                    if not is_redtwo(c):
                        prev = int(c['rank'])
                    continue
                if is_redtwo(c):
                    prev = prev + 1
                    continue
                if int(c['rank']) != prev+1:
                    print('wrong order')
                    return False
                prev = int(c['rank'])
            return True

        def check_res(req, res):
            return req['threes'] == res['threes'] and req['fours'] == res['fours'] and req['empty'] == res['empty']

        res = {'fours': 0, 'threes': 0, 'empty': 0}
        for t in tricks:
            print('trick: ')
            print(t)
            if is_empty(t):
                res['empty'] += 1
                print('was empty')
            elif is_three(t):
                res['threes'] += 1
                print('was three')
            elif is_four(t):
                res['fours'] += 1
                print('was four')
            else:
                print('other')
                return False

        if res['empty'] == 3:
            return True
        print(self.reqs[self.round])
        print(res)
        ret = check_res(self.reqs[self.round], res)
        print('ret: ' + str(ret))
        return ret

    def validate_tables(self, tricks) -> bool:
        all_valid = True
        for name, t in tricks.items():
            print('validating tricks for ' + name)
            if not self.validate_tricks(t):
                all_valid = False
                self.players[name].down = False
        return all_valid

    # called after discard
    def finalize_tables(self, tricks) -> None:
        if len(tricks) == 0:
            return
        for name, t in tricks.items():
            print('finalize tables for ' + name)
            assert self.validate_tricks(t)
            self.players[name].tricks = [sorted(x, key=lambda y: y['x']) for x in t]
            if len([x for x in t if len(x) > 0]) > 0:
                self.players[name].down = True
            else:
                self.players[name].down = False
            print(self.players[name].tricks)

    def discard(self, rank, suit, name) -> None:
        assert name == self.cur_player
        assert self.turn_stage == TurnStage.DISCARD

        self.deck.discard_pile.append(self.players[name].discard(int(rank),
            suit.strip()))
        self.can_take_throwcard = True

        if len(self.players[name].hand) == 0:
            self.end_round()
 
        self.cur_player = next(self.player_order)
        self.turn_stage = TurnStage.DRAW_CARD

    def end_round(self) -> None:
        self.round += 1
        for p in self.players.values():
            p.score_hand()
            for _ in range(0, len(p.hand)):
                self.deck.discard_pile.append(p.hand.pop())
            assert len(p.hand) == 0
            p.hand = self.deck.draw_hand()
            p.tricks = []
            p.down = False

    def get_players(self) -> Dict[str, Player]:
        return {k: v for k,v in self.players.items() if v.playing}

    def get_state(self, name):
        state = {'players': list(self.get_players().keys()),
                'cards-remaining': len(self.deck.draw_pile),
                'hand': self.players[name].get_hand(),
                'turn-stage': str(self.turn_stage),
                'can-take-throwcard': self.can_take_throwcard,
                'tricks': {n: self.players[n].tricks for n in
                    self.players.keys()}}
        if len(self.deck.discard_pile) > 0:
            state['throw-card'] = {'suit':
                    self.deck.discard_pile[-1].suit.to_json(),
                    'rank': self.deck.discard_pile[-1].rank.to_json()}
        else:
            state['throw-card'] = 'None'

        if not self.started:
            state['cur-player'] = 'Game not started'
        else:
            state['cur-player'] = self.cur_player
        return state

    def get_round(self):
        round_text = ['Two threes', 'Three and a four', 'Two fours', 'Three threes', 'Two threes and a four', 'Two fours and a three', 'Three fours']
        return round_text[self.round]
