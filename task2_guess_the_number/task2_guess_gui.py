import random
import tkinter as tk

# ---------- Settings ----------
LOW = 1
HIGH = 100
MAX_ATTEMPTS = 10

BG = "#f4f6fb"
HEADER = "#4f46e5"
TEXT = "#1f2937"
MUTED = "#6b7280"
GREEN, GREEN_HOVER = "#16a34a", "#15803d"
BLUE = "#2563eb"
ORANGE = "#ea580c"
RED = "#dc2626"
ACCENT, ACCENT_HOVER = "#4f46e5", "#4338ca"
GREY = "#9ca3af"
FONT = "Segoe UI"

# All the game's changing data lives in one dictionary
game = {"secret": 0, "attempts": 0, "over": False, "history": []}


# ---------- Game logic ----------
def new_game():
    game["secret"] = random.randint(LOW, HIGH)
    game["attempts"] = 0
    game["over"] = False
    game["history"] = []
    # print(game["secret"])   # remove the # to cheat while testing

    guess_entry.config(state="normal")
    guess_entry.delete(0, tk.END)
    guess_button.config(state="normal", bg=ACCENT)
    show_feedback("Make your first guess!", MUTED)
    update_labels()
    guess_entry.focus()


def update_labels():
    attempts_label.config(text=f"Attempts: {game['attempts']} / {MAX_ATTEMPTS}")
    history_label.config(text="  ".join(game["history"]) if game["history"] else "No guesses yet")


def show_feedback(message, color):
    feedback_label.config(text=message, fg=color)


def end_game():
    game["over"] = True
    guess_entry.config(state="disabled")
    guess_button.config(state="disabled", bg=GREY)


def check_guess(event=None):
    if game["over"]:
        return

    text = guess_entry.get().strip()

    try:
        guess = int(text)
    except ValueError:
        show_feedback("Please enter a whole number.", ORANGE)
        return

    if guess < LOW or guess > HIGH:
        show_feedback(f"Pick a number between {LOW} and {HIGH}.", ORANGE)
        return

    game["attempts"] += 1
    guess_entry.delete(0, tk.END)

    if guess == game["secret"]:
        word = "attempt" if game["attempts"] == 1 else "attempts"
        game["history"].append(f"{guess} ✔")
        show_feedback(f"🎉 Correct! You got it in {game['attempts']} {word}.", GREEN)
        end_game()
    else:
        if guess < game["secret"]:
            game["history"].append(f"{guess} ↑")
            show_feedback("Too low! Go higher ↑", BLUE)
        else:
            game["history"].append(f"{guess} ↓")
            show_feedback("Too high! Go lower ↓", ORANGE)

        if game["attempts"] >= MAX_ATTEMPTS:
            show_feedback(f"Out of attempts! The number was {game['secret']}.", RED)
            end_game()

    update_labels()


# ---------- Helper to build nice buttons ----------
def make_button(parent, text, color, hover, command, width=12):
    button = tk.Button(
        parent, text=text, command=command, width=width,
        bg=color, fg="white", activebackground=hover, activeforeground="white",
        disabledforeground="white",
        font=(FONT, 11, "bold"), relief="flat", bd=0, cursor="hand2", pady=7,
    )

    def on_enter(event):
        if str(button["state"]) == "normal":
            button.config(bg=hover)

    def on_leave(event):
        if str(button["state"]) == "normal":
            button.config(bg=color)

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    return button


# ---------- Window ----------
root = tk.Tk()
root.title("Guess the Number")
root.geometry("460x560")
root.minsize(400, 520)
root.configure(bg=BG)

# Header
header = tk.Frame(root, bg=HEADER)
header.pack(fill="x")
tk.Label(header, text="Guess the Number", bg=HEADER, fg="white",
         font=(FONT, 22, "bold")).pack(pady=(18, 2))
tk.Label(header, text=f"I'm thinking of a number between {LOW} and {HIGH}",
         bg=HEADER, fg="#c7d2fe", font=(FONT, 10)).pack(pady=(0, 16))

# Attempts counter
attempts_label = tk.Label(root, text="", bg=BG, fg=TEXT, font=(FONT, 12, "bold"))
attempts_label.pack(pady=(20, 6))

# Guess entry
guess_entry = tk.Entry(
    root, font=(FONT, 24), justify="center", width=8, relief="flat",
    bg="white", fg=TEXT, insertbackground=TEXT, highlightthickness=2,
    highlightbackground="#d1d5db", highlightcolor=ACCENT,
    disabledbackground="#e5e7eb", disabledforeground=MUTED,
)
guess_entry.pack(pady=8, ipady=6)
guess_entry.bind("<Return>", check_guess)

guess_button = make_button(root, "Guess", ACCENT, ACCENT_HOVER, check_guess, width=16)
guess_button.pack(pady=8)

# Feedback message
feedback_label = tk.Label(root, text="", bg=BG, font=(FONT, 14, "bold"),
                          wraplength=400, height=2)
feedback_label.pack(pady=(14, 6))

# Guess history
tk.Label(root, text="Your guesses", bg=BG, fg=MUTED, font=(FONT, 9)).pack(pady=(8, 0))
history_label = tk.Label(root, text="", bg=BG, fg=TEXT, font=(FONT, 11), wraplength=400)
history_label.pack(pady=(2, 10))

# New game button
make_button(root, "New Game", GREEN, GREEN_HOVER, new_game, width=16).pack(pady=10)

# ---------- Start ----------
new_game()
root.mainloop()