import json
import http
import asyncio
import datetime
import random
import websockets
import os
import sys

sys.path.append('..')

#from card import Game
from card import Deck

games = {}
#lobby = []

class Player():
    def __init__(self, name, ws):
        self.name = name
        self.ws = ws
        self.hand = []

class Game():
    def __init__(self):
        self.deck = Deck(double=True)
        self.player_list = {}

    def add_player(self, ws, name):
        self.player_list[name] = Player(name, ws)

    @property
    def players(self):
        return list(self.player_list.keys())

    def player_ws(self, name):
        return self.player_list[name].ws

    def player_hand(self, name):
        return self.player_list[name].hand

    def set_ws(self, name, ws):
        self.player_list[name].ws = ws

    def set_hand(self, name, hand):
        for c in hand:
            c['rank'] = int(c['rank'])
        self.player_list[name].hand = hand
        print(self.player_list[name].hand)

async def send_msg(ws, msg):
    try:
        await ws.send(json.dumps(msg))
    except websockets.exceptions.ConnectionClosedOK:
        print('uh')

async def handle_msg(game, msg, player_name):
    msg_split = msg.split()
    event = msg_split[0]
    resp_data = {}
    if event == 'update':
        resp = 'update'
        data = json.loads(' '.join(msg_split[1:]))
        resp_data = data['updatedCards']
        game.set_hand(player_name, data['playerCards'])
    elif event == 'draw-card':
        resp = 'card-added'
        c = game.deck.draw()
        resp_data = {'card': c.to_json()}

    return {'msg': resp, 'data': resp_data}

async def add_player(game, ws, name):
    game.add_player(ws, name)
    hand = []
    for _ in range(0, 10):
        c = game.deck.draw()
        hand.append(c.to_json())
        print(c)
        msg = {'msg': 'card-added', 'data': {'card': c.to_json()}, 'name':
                name, 'names': game.players}
        await send_msg(ws, msg)
    game.set_hand(name, hand)

"""
async notify_lobby():
    remove = []
    msg = {'games': list(games.keys())}
    for ws in lobby:
        try:
            await ws.send(json.dumps(msg))
        except websockets.exceptions.ConnectionClosedOK:
            remove.append(ws)
    lobby = [x for x in lobby if x not in remove]
"""

async def run_server(websocket, path):
    """
    if path == 'lobby':
        lobby.append(websocket)
        msg = {'games': list(games.keys())}
        send_msg(websocket, msg)
    """

    _, game_name, player_name = path.split('/')
    if game_name not in games:
        games[game_name] = Game()
    game = games[game_name]

    if player_name not in game.players:
        await add_player(game, websocket, player_name)
        for name in game.players:
            resp = {'msg': 'player-added', 'names': game.players, 'name':
                    name}
            await send_msg(game.player_ws(name), resp)
    else:
        game.set_ws(player_name, websocket)
        print(game.player_hand(player_name))
        for c in game.player_hand(player_name):
            print(c)
            msg = {'msg': 'card-added', 'data': {'card': c}, 'name':
                    player_name, 'names': game.players}
            await send_msg(websocket, msg)

    async for msg in websocket:
        print('recvd from ' + player_name + ': ' + msg)
        resp = await handle_msg(game, msg, player_name)
        if resp is None:
            continue
        print('sending: ' + json.dumps(resp))
        print()
        # update messages go to all players
        if resp['msg'] == 'update':
            for name in game.players:
                if name == player_name:
                    continue
                resp['name'] = name
                print('sending to ' + name)
                await send_msg(game.player_ws(name), resp)
        # card added just goes to whoever got the card
        elif resp['msg'] == 'card-added':
            await send_msg(game.player_ws(player_name), resp)

async def process_request(path, req_headers):
    print(path)
    print(req_headers)
    headers = []
    if path[0] == '/':
        path = path[1:]
    if os.path.exists(path):
        with open(path, 'rb') as f:
            c = f.read()
        if path.endswith('html'):
            headers.append(('Content-Type', 'text/html; charset=utf-8'))
        elif path.endswith('css'):
            headers.append(('Content-Type', 'text/css; charset=utf-8'))
        elif path.endswith('svg'):
            headers.append(('Content-Type', 'image/svg+xml'))
        elif path.endswith('js'):
            headers.append(('Content-Type', 'text/javascript; charset=utf-8'))
        print(headers)
        return http.HTTPStatus.OK, headers, c

start_server = websockets.serve(run_server, "127.0.0.1", 5678,
#start_server = websockets.serve(run_server, "0.0.0.0", 80,
        process_request=process_request)
print(type(start_server))

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
