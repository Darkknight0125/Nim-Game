# main.py
import os
from train import train
from ui import NimUI

if __name__ == "__main__":
    models = {
        "easy": ("models/easy_ai.pkl", 1000),
        "medium": ("models/medium_ai.pkl", 10000),
        "hard": ("models/hard_ai.pkl", 100000)
    }

    print("Checking for pre-trained models...")
    for difficulty, (path, n_games) in models.items():
        if not os.path.exists(path):
            print(f"Training {difficulty} AI model with {n_games} games...")
            train(n_games, path)
            print(f"{difficulty.capitalize()} model saved to {path}")

    print("Starting game...")
    ui = NimUI()
    ui.run()