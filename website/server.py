import json
import http
import asyncio
import datetime
import random
import websockets
import os
import sys

sys.path.append('..')

from card import Game

games = {}

async def send_msg(ws, player_name, down, rnd, event, state):
    msg = { 'player-name': player_name,
            'event': event,
            'is-down': down,
            'round': rnd,
            'state': state }
    try:
        await ws.send(json.dumps(msg))
    except websockets.exceptions.ConnectionClosedOK:
        print('uh')

async def handle_msg(game, msg, player_name):
    msg_split = msg.split()
    event = msg_split[0]
    if event == 'start-game':
        game.start_game()
        resp = 'game-started'
    elif event == 'take-throwcard':
        game.take_throwcard(player_name)
        resp = 'drew-card'
    elif event == 'draw-card':
        game.draw_card(player_name)
        resp = 'drew-card'
    elif event == 'discard':
        game.discard(msg_split[1], msg_split[2], player_name)
        game.finalize_tables(json.loads(' '.join(msg_split[3:])))
        resp = 'turn-started'
    elif event == 'validate-tables':
        print(' '.join(msg_split[1:]))
        tricks = json.loads(' '.join(msg_split[1:]))
        valid = game.validate_tables(tricks)
        print('valid: ' + str(valid))
        if valid:
            resp = 'tricks-valid'
        else:
            resp = 'tricks-invalid'

    return resp

async def run_server(websocket, path):
    _, game_name, player_name = path.split('/')
    if game_name not in games:
        games[game_name] = Game()

    game = games[game_name]
    game.add_player(websocket, player_name)

    for name, player in game.get_players().items():
        await send_msg(player.data, name, False, 1, 'players-changed', game.get_state(name))

    async for msg in websocket:
        print('recvd: ' + msg)
        resp = await handle_msg(game, msg, player_name)
        print('sending: ' + resp)
        for name, player in game.get_players().items():
            await send_msg(player.data, name, game.players[name].down,
                    game.get_round(), resp, game.get_state(name))

    print('Removing ' + str(player_name))
    game.remove_player(player_name)

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
        process_request=process_request)
print(type(start_server))

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
