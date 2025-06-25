# ui.py
import tkinter as tk
from tkinter import messagebox, ttk
from nim_game import Nim
from train import load_model
import random
import os

class NimUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nim Game")
        self.root.geometry("600x700")
        self.root.configure(bg="#2c3e50")
        self.models = {
            "Easy": "models/easy_ai.pkl",
            "Medium": "models/medium_ai.pkl",
            "Hard": "models/hard_ai.pkl"
        }
        self.ai = None
        self.game = None
        self.human_player = None
        self.selected_pile = tk.IntVar(value=-1)
        self.count = tk.IntVar(value=1)
        self.difficulty = tk.StringVar(value="Medium")
        self.num_piles = tk.IntVar(value=4)
        self.move_history = []

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=10)
        self.style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1")
        self.style.configure("TCombobox", font=("Helvetica", 12))
        self.style.configure("TEntry", font=("Helvetica", 12))

        # Header
        self.header_label = ttk.Label(self.root, text="Nim Game", font=("Helvetica", 24, "bold"), foreground="#ecf0f1")
        self.header_label.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(self.root, text="Configure game and start", font=("Helvetica", 14), foreground="#f1c40f")
        self.status_label.pack(pady=5)

        # Configuration frame
        self.config_frame = ttk.Frame(self.root)
        ttk.Label(self.config_frame, text="Number of Piles (1-20):", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        ttk.Entry(self.config_frame, textvariable=self.num_piles, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(self.config_frame, text="Difficulty:", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        ttk.Combobox(self.config_frame, textvariable=self.difficulty, values=["Easy", "Medium", "Hard"],
                     state="readonly", width=10).pack(side=tk.LEFT, padx=5)
        self.config_frame.pack(pady=10)

        # Start buttons
        self.start_frame = ttk.Frame(self.root)
        self.create_button(self.start_frame, "Human First", lambda: self.start_game(0)).pack(side=tk.LEFT, padx=5)
        self.create_button(self.start_frame, "AI First", lambda: self.start_game(1)).pack(side=tk.LEFT, padx=5)
        self.start_frame.pack(pady=10)

        # Piles canvas with scrollbar
        self.piles_frame = ttk.Frame(self.root)
        self.piles_canvas = tk.Canvas(self.piles_frame, bg="#34495e", width=500, height=300, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.piles_frame, orient="vertical", command=self.piles_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.piles_canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.piles_canvas.configure(scrollregion=self.piles_canvas.bbox("all"))
        )
        self.piles_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.piles_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.piles_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.piles_frame.pack(pady=10, fill="both", expand=True)
        self.pile_buttons = []

        # Move input
        self.move_frame = ttk.Frame(self.root)
        ttk.Label(self.move_frame, text="Items to remove:", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        ttk.Entry(self.move_frame, textvariable=self.count, width=5).pack(side=tk.LEFT, padx=5)
        self.create_button(self.move_frame, "Make Move", self.human_move).pack(side=tk.LEFT, padx=5)
        self.move_frame.pack(pady=10)

        # History log
        self.history_label = ttk.Label(self.root, text="MoveUnchecked history:", font=("Helvetica", 12))
        self.history_label.pack(pady=5)
        self.history_text = tk.Text(self.root, height=5, width=50, font=("Helvetica", 10), bg="#ecf0f1", fg="#2c3e50")
        self.history_text.pack(pady=5)
        self.history_text.config(state="disabled")

        # Reset button
        self.create_button(self.root, "Reset Game", self.reset_game).pack(pady=10)

    def create_button(self, parent, text, command):
        btn = ttk.Button(parent, text=text, command=command)
        btn.bind("<Enter>", lambda e: btn.configure(style="Hover.TButton"))
        btn.bind("<Leave>", lambda e: btn.configure(style="TButton"))
        self.style.configure("Hover.TButton", background="#3498db", foreground="#ffffff")
        return btn

    def update_piles(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.pile_buttons = []
        canvas_height = max(300, len(self.game.piles) * 50 + 20)
        self.piles_canvas.configure(height=canvas_height)
        for i, pile in enumerate(self.game.piles):
            frame = ttk.Frame(self.scrollable_frame)
            label = ttk.Label(frame, text=f"Pile {i}:", font=("Helvetica", 12), width=8)
            label.pack(side=tk.LEFT, padx=5)
            canvas = tk.Canvas(frame, bg="#34495e", height=30, width=300, highlightthickness=0)
            for j in range(pile):
                x = 10 + j * 30
                y = 15
                oval = canvas.create_oval(x-10, y-10, x+10, y+10, fill="#e74c3c", tags=f"pile_{i}")
                canvas.tag_bind(f"pile_{i}", "<Button-1>", lambda e, idx=i: self.select_pile(idx))
            canvas.pack(side=tk.LEFT)
            frame.pack(pady=5, anchor="w")
            self.pile_buttons.append(canvas)

    def select_pile(self, pile):
        self.selected_pile.set(pile)
        for widget in self.scrollable_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, tk.Canvas):
                    child.delete("highlight")
        frame = self.scrollable_frame.winfo_children()[pile]
        canvas = frame.winfo_children()[1]
        canvas.create_rectangle(0, 0, 80, 30, outline="#f1c40f", width=2, tags="highlight")

    def start_game(self, human_player):
        num_piles = self.num_piles.get()
        if not (1 <= num_piles <= 20):
            messagebox.showerror("Error", "Number of piles must be between 1 and 20")
            return
        if not os.path.exists(self.models[self.difficulty.get()]):
            messagebox.showerror("Error", f"Model for {self.difficulty.get()} difficulty not found. Please train models first.")
            return
        self.ai = load_model(self.models[self.difficulty.get()])
        initial_piles = [random.randint(1, 10) for _ in range(num_piles)]
        self.game = Nim(initial_piles)
        self.human_player = human_player
        self.config_frame.pack_forget()
        self.start_frame.pack_forget()
        self.update_piles()
        self.status_label.config(text="Your turn" if self.game.player == human_player else "AI's turn", foreground="#2ecc71")
        if self.game.player != human_player:
            self.root.after(1000, self.ai_move)

    def ai_move(self):
        if self.game.winner is not None:
            return
        action = self.ai.choose_action(self.game.piles, epsilon=False)
        pile, count = action
        self.game.move(action)
        self.update_piles()
        self.log_move(f"AI removed {count} from pile {pile}")
        self.status_label.config(text="Your turn", foreground="#2ecc71")
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
        self.log_move(f"Human removed {count} from pile {pile}")
        self.status_label.config(text="AI's turn", foreground="#e74c3c")
        self.check_winner()
        if self.game.winner is None:
            self.root.after(1000, self.ai_move)

    def log_move(self, move):
        self.move_history.append(move)
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        for m in self.move_history[-5:]:
            self.history_text.insert(tk.END, m + "\n")
        self.history_text.config(state="disabled")

    def check_winner(self):
        if self.game.winner is not None:
            winner = "Human" if self.game.winner == self.human_player else "AI"
            self.status_label.config(text=f"Game Over! Winner: {winner}", foreground="#e74c3c")
            messagebox.showinfo("Game Over", f"Winner is {winner}")

    def reset_game(self):
        self.game = None
        self.human_player = None
        self.ai = None
        self.selected_pile.set(-1)
        self.count.set(1)
        self.num_piles.set(4)
        self.move_history = []
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state="disabled")
        self.status_label.config(text="Configure game and start", foreground="#f1c40f")
        self.config_frame.pack()
        self.start_frame.pack()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.pile_buttons = []

    def run(self):
        self.root.mainloop()