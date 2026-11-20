import json

FILENAME = "tasks.json"
tasks = []


def show_menu():
    print("\n--- TO-DO LIST ---")
    print("1. View tasks")
    print("2. Add task")
    print("3. Mark task as done")
    print("4. Delete task")
    print("5. Exit")



def save_tasks():
    try:
        with open(FILENAME, "w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4)
    except OSError as error:
        print(f"Could not save tasks: {error}")


def load_tasks():
    try:
        with open(FILENAME, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Task file is damaged. Starting with an empty list.")
        return []

    

def view_tasks():
    if not tasks:
        print("\nNo tasks yet. Add one!")
        return

    print("\nYour tasks:")
    for number, task in enumerate(tasks, start=1):
        status = "✔" if task["done"] else " "
        print(f"{number}. [{status}] {task['title']}")


def add_task():
    title = input("Enter the task: ").strip()

    if title == "":
        print("Task cannot be empty.")
        return

    tasks.append({"title": title, "done": False})
    print(f"Added: {title}")
    save_tasks()


def ask_task_number():
    """Ask for a task number. Return the list index, or None if invalid."""
    if not tasks:
        print("\nNo tasks yet.")
        return None

    view_tasks()
    answer = input("Enter task number: ").strip()

    if not answer.isdigit():
        print("Please enter a number.")
        return None

    number = int(answer)

    if number < 1 or number > len(tasks):
        print(f"Choose a number between 1 and {len(tasks)}.")
        return None

    return number - 1


def mark_done():
    index = ask_task_number()
    if index is None:
        return

    tasks[index]["done"] = True
    print(f"Marked as done: {tasks[index]['title']}")
    save_tasks()


def delete_task():
    index = ask_task_number()
    if index is None:
        return

    removed = tasks.pop(index)
    print(f"Deleted: {removed['title']}")
    save_tasks()

tasks = load_tasks()

while True:
    show_menu()
    choice = input("Choose an option (1-5): ")

    if choice == "1":
        view_tasks()
    elif choice == "2":
        add_task()
    elif choice == "3":
        mark_done()
    elif choice == "4":
        delete_task()
    elif choice == "5":
        print("Goodbye!")
        break
    else:
        print("Invalid choice, try again.")