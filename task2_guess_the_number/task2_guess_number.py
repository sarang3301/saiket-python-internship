import random

LEVELS = {
    "1": {"name": "Easy", "low": 1, "high": 50, "max_attempts": 8},
    "2": {"name": "Medium", "low": 1, "high": 100, "max_attempts": 10},
    "3": {"name": "Hard", "low": 1, "high": 200, "max_attempts": 9},
}


def choose_level():
    """Show the difficulty menu until the player picks a valid level."""
    print("\nChoose a difficulty:")
    for key, level in LEVELS.items():
        print(f"  {key}. {level['name']:<7} (number {level['low']}-{level['high']}, "
              f"{level['max_attempts']} attempts)")

    while True:
        choice = input("Your choice (1-3): ").strip()
        if choice in LEVELS:
            return LEVELS[choice]
        print("Please type 1, 2 or 3.")


def get_guess(prompt, low, high):
    """Keep asking until the player enters a whole number inside the range."""
    while True:
        answer = input(prompt).strip()

        try:
            guess = int(answer)
        except ValueError:
            print("Please enter a whole number (like 42).")
            continue

        if guess < low or guess > high:
            print(f"Please guess a number between {low} and {high}.")
            continue

        return guess


def play_round(level):
    """Play one game. Return the attempts used if won, or None if lost."""
    low = level["low"]
    high = level["high"]
    max_attempts = level["max_attempts"]
    secret_number = random.randint(low, high)
    # print(secret_number)   # remove the # to cheat while testing

    print(f"\nI'm thinking of a number between {low} and {high}.")
    print(f"You have {max_attempts} attempts. Good luck!\n")

    for attempt in range(1, max_attempts + 1):
        guess = get_guess(f"Attempt {attempt}/{max_attempts} - your guess: ", low, high)

        if guess == secret_number:
            word = "attempt" if attempt == 1 else "attempts"
            print(f"\nCorrect! You got it in {attempt} {word}.")
            return attempt

        if guess < secret_number:
            print("Too low! Try a higher number.")
        else:
            print("Too high! Try a lower number.")

        left = max_attempts - attempt
        if left > 0:
            print(f"({left} left)\n")

    print(f"\nOut of attempts! The number was {secret_number}.")
    return None


def ask_play_again():
    while True:
        answer = input("\nPlay again? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.")


def main():
    best_scores = {}   # best (lowest) attempts for each difficulty

    print("=== GUESS THE NUMBER ===")
    print("I pick a secret number. You guess it. I tell you higher or lower.")

    while True:
        level = choose_level()
        attempts_used = play_round(level)

        if attempts_used is not None:
            name = level["name"]
            best = best_scores.get(name)
            if best is None or attempts_used < best:
                best_scores[name] = attempts_used
                print(f"New best score on {name}: {attempts_used}!")
            else:
                print(f"Your best score on {name} is still {best}.")

        if not ask_play_again():
            break

    print("\nThanks for playing! Goodbye.")


if __name__ == "__main__":
    main()