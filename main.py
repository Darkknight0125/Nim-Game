from train import train
from ui import NimUI

if __name__ == "__main__":
    print("Training AI...")
    ai = train(1000)  # Reduced training games for faster startup; increase for better AI
    print("Training complete!")
    ui = NimUI(ai)
    ui.run()