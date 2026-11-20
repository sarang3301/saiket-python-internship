DEFAULT_FILE = "sample.txt"


# ---------- File helpers with error handling ----------
def read_file(filename):
    """Return the file's text, or None if it could not be read."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f'Error: "{filename}" was not found. Check the name and folder.')
    except IsADirectoryError:
        print(f'Error: "{filename}" is a folder, not a file.')
    except PermissionError:
        print(f'Error: no permission to read "{filename}".')
    except UnicodeDecodeError:
        print(f'Error: "{filename}" is not a plain text file.')
    except OSError as error:
        print(f'Error: could not read "{filename}": {error}')
    return None


def write_file(filename, text):
    """Save text to the file. Return True on success, False on failure."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(text)
        return True
    except PermissionError:
        print(f'Error: no permission to write to "{filename}". Is it read-only?')
    except OSError as error:
        print(f'Error: could not save "{filename}": {error}')
    return False


# ---------- Menu actions ----------
def view_file(filename):
    content = read_file(filename)
    if content is None:
        return

    if content.strip() == "":
        print("The file is empty.")
        return

    print(f"\n--- {filename} ---")
    print(content)
    print("-" * (len(filename) + 8))
    print(f"Characters: {len(content)}   Lines: {len(content.splitlines())}")


def find_word(filename):
    content = read_file(filename)
    if content is None:
        return

    if content.strip() == "":
        print("The file is empty, so there is nothing to search.")
        return

    word = input("Enter a word to find: ").strip()
    if word == "":
        print("Please enter a word.")
        return

    count = content.count(word)
    if count == 0:
        print(f'"{word}" was not found.')
        return

    print(f'"{word}" appears {count} time(s).')
    print("\nFound on these lines:")
    for number, line in enumerate(content.splitlines(), start=1):
        if word in line:
            print(f"  Line {number}: {line}")


def replace_word(filename):
    content = read_file(filename)
    if content is None:
        return

    if content.strip() == "":
        print("The file is empty, so there is nothing to replace.")
        return

    old_word = input("Word to replace: ").strip()
    if old_word == "":
        print("The word to replace cannot be empty.")
        return

    count = content.count(old_word)
    if count == 0:
        print(f'"{old_word}" was not found. Nothing changed.')
        return

    new_word = input("Replace with: ").strip()
    new_content = content.replace(old_word, new_word)

    if write_file(filename, new_content):
        print(f'Replaced {count} occurrence(s) of "{old_word}" with "{new_word}".')
        print("File saved.")


def choose_file(current):
    name = input(f"File name (press Enter to keep '{current}'): ").strip()
    return name if name else current


# ---------- Main menu ----------
def show_menu(filename):
    print("\n=== FILE FIND & REPLACE ===")
    print(f"Current file: {filename}")
    print("1. View file")
    print("2. Find a word")
    print("3. Replace a word")
    print("4. Change file")
    print("5. Exit")


def main():
    filename = DEFAULT_FILE

    while True:
        show_menu(filename)
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            view_file(filename)
        elif choice == "2":
            find_word(filename)
        elif choice == "3":
            replace_word(filename)
        elif choice == "4":
            filename = choose_file(filename)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()