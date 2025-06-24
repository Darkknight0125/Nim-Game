import tkinter as tk
from tkinter import messagebox
import time
from nim_game import Nim
from nim_ai import NimAI

class NimUI:
    def __init__(self, ai):
        self.ai = ai
        self.game = Nim()
        self.human_player = None
        self.root = tk.Tk()
        self.root.title("Nim Game")
        self.root.geometry("400x600")
        self.root.configure(bg="#f0f0f0")
        self.selected_pile = tk.IntVar(value=-1)
        self.count = tk.IntVar(value=1)
        self.status_label = tk.Label(self.root, text="Choose who goes first:", font=("Arial", 14), bg="#f0f0f0")
        self.status_label.pack(pady=10)

        self.start_frame = tk.Frame(self.root, bg="#f0f0f0")
        tk.Button(self.start_frame, text="Human First", command=lambda: self.start_game(0),
                  bg="#4CAF50", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.start_frame, text="AI First", command=lambda: self.start_game(1),
                  bg="#4CAF50", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.start_frame.pack(pady=10)

        self.piles_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.piles_frame.pack(pady=10)
        self.pile_buttons = []

        self.move_frame = tk.Frame(self.root, bg="#f0f0f0")
        tk.Label(self.move_frame, text="Items to remove:", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        tk.Entry(self.move_frame, textvariable=self.count, width=5, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.move_frame, text="Make Move", command=self.human_move,
                  bg="#2196F3", fg="white", font=("Arial", 12)).pack(pady=5)
        self.move_frame.pack(pady=10)

        tk.Button(self.root, text="Reset Game", command=self.reset_game,
                  bg="#f44336", fg="white", font=("Arial", 12)).pack(pady=10)

    def update_piles(self):
        for widget in self.piles_frame.winfo_children():
            widget.destroy()
        self.pile_buttons = []
        for i, pile in enumerate(self.game.piles):
            btn = tk.Radiobutton(
                self.piles_frame, text=f"Pile {i}: {pile} {'●' * pile}", variable=self.selected_pile, value=i,
                font=("Arial", 12), bg="#e0e0e0", indicatoron=0, selectcolor="#bbdefb", width=20
            )
            btn.pack(pady=5)
            self.pile_buttons.append(btn)

    def start_game(self, human_player):
        self.human_player = human_player
        self.start_frame.pack_forget()
        self.update_piles()
        self.status_label.config(text="Your turn" if self.game.player == human_player else "AI's turn")
        if self.game.player != human_player:
            self.root.after(1000, self.ai_move)

    def ai_move(self):
        if self.game.winner is not None:
            return
        action = self.ai.choose_action(self.game.piles, epsilon=False)
        self.game.move(action)
        self.update_piles()
        self.status_label.config(text="Your turn")
        self.check_winner()
        if self.game.winner is None and self.game.player != self.human_player:
            self.root.after(1000, self.ai_move)

    def human_move(self):
        if self.game.winner is not None or self.game.player != self.human_player:
            return
        pile = self.selected_pile.get()
        count = self.count.get()
        if pile == -1 or (pile, count) not in Nim.available_actions(self.game.piles):
            messagebox.showerror("Error", "Invalid move")
            return
        self.game.move((pile, count))
        self.update_piles()
        self.status_label.config(text="AI's turn")
        self.check_winner()
        if self.game.winner is None:
            self.root.after(1000, self.ai_move)

    def check_winner(self):
        if self.game.winner is not None:
            winner = "Human" if self.game.winner == self.human_player else "AI"
            self.status_label.config(text=f"Game Over! Winner: {winner}")
            messagebox.showinfo("Game Over", f"Winner is {winner}")

    def reset_game(self):
        self.game = Nim()
        self.human_player = None
        self.selected_pile.set(-1)
        self.count.set(1)
        self.status_label.config(text="Choose who goes first:")
        self.start_frame.pack()
        for widget in self.piles_frame.winfo_children():
            widget.destroy()
        self.pile_buttons = []

    def run(self):
        self.root.mainloop()