import pickle
import os
from nim_game import Nim
from nim_ai import NimAI

def train(n, model_path):
    player = NimAI()
    for i in range(n):
        game = Nim()
        last = {0: {"state": None, "action": None}, 1: {"state": None, "action": None}}

        while True:
            state = game.piles.copy()
            action = player.choose_action(game.piles)
            last[game.player]["state"] = state
            last[game.player]["action"] = action

            game.move(action)
            new_state = game.piles.copy()

            if game.winner is not None:
                player.update(state, action, new_state, -1)
                player.update(last[game.player]["state"], last[game.player]["action"], new_state, 1)
                break
            elif last[game.player]["state"] is not None:
                player.update(last[game.player]["state"], last[game.player]["action"], new_state, 0)

    # Save the trained model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(player, f)
    return player

def load_model(model_path):
    with open(model_path, 'rb') as f:
        return pickle.load(f)