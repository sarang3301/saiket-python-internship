import json
import os
import tkinter as tk
from tkinter import messagebox

# ---------- Settings ----------
FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks_gui.json")

BG = "#f4f6fb"
HEADER = "#4f46e5"
HEADER_TEXT = "#ffffff"
TEXT = "#1f2937"
MUTED = "#9ca3af"
SELECT = "#e0e7ff"
GREEN, GREEN_HOVER = "#16a34a", "#15803d"
RED, RED_HOVER = "#dc2626", "#b91c1c"
ACCENT, ACCENT_HOVER = "#4f46e5", "#4338ca"
FONT = "Segoe UI"

tasks = []


# ---------- Saving and loading ----------
def save_tasks():
    try:
        with open(FILENAME, "w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4)
    except OSError as error:
        messagebox.showerror("Save error", f"Could not save tasks:\n{error}")


def load_tasks():
    try:
        with open(FILENAME, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        messagebox.showwarning("Damaged file", "Task file is damaged. Starting with an empty list.")
        return []

    # Keep only well-formed tasks
    return [
        {"description": str(t["description"]), "done": bool(t["done"])}
        for t in data
        if isinstance(t, dict) and "description" in t and "done" in t
    ]


# ---------- Task actions ----------
def refresh_list(select=None):
    """Redraw the list box from the tasks list."""
    task_listbox.delete(0, tk.END)
    for i, task in enumerate(tasks):
        mark = "✔" if task["done"] else "○"
        task_listbox.insert(tk.END, f"  {mark}   {task['description']}")
        if task["done"]:
            task_listbox.itemconfig(i, fg=MUTED)

    if select is not None and 0 <= select < len(tasks):
        task_listbox.selection_set(select)

    done_count = sum(1 for t in tasks if t["done"])
    counter_label.config(text=f"{done_count} of {len(tasks)} tasks completed")


def add_task(event=None):
    description = task_entry.get().strip()
    if description == "":
        messagebox.showwarning("Empty task", "Please type a task first.")
        return

    tasks.append({"description": description, "done": False})
    task_entry.delete(0, tk.END)
    save_tasks()
    refresh_list()


def get_selected_index():
    selection = task_listbox.curselection()
    if not selection:
        messagebox.showinfo("No selection", "Click a task in the list first.")
        return None
    return selection[0]


def toggle_done(event=None):
    index = get_selected_index()
    if index is None:
        return

    tasks[index]["done"] = not tasks[index]["done"]
    save_tasks()
    refresh_list(select=index)


def delete_task():
    index = get_selected_index()
    if index is None:
        return

    if messagebox.askyesno("Delete task", f"Delete \"{tasks[index]['description']}\"?"):
        tasks.pop(index)
        save_tasks()
        refresh_list()


# ---------- Helper to build nice buttons ----------
def make_button(parent, text, color, hover, command, width=12):
    button = tk.Button(
        parent, text=text, command=command, width=width,
        bg=color, fg="white", activebackground=hover, activeforeground="white",
        font=(FONT, 10, "bold"), relief="flat", bd=0, cursor="hand2", pady=6,
    )
    button.bind("<Enter>", lambda e: button.config(bg=hover))
    button.bind("<Leave>", lambda e: button.config(bg=color))
    return button


# ---------- Window ----------
root = tk.Tk()
root.title("To-Do List")
root.geometry("460x600")
root.minsize(380, 480)
root.configure(bg=BG)

# Header
header = tk.Frame(root, bg=HEADER)
header.pack(fill="x")

tk.Label(header, text="My To-Do List", bg=HEADER, fg=HEADER_TEXT,
         font=(FONT, 20, "bold")).pack(pady=(18, 2))
counter_label = tk.Label(header, text="", bg=HEADER, fg="#c7d2fe", font=(FONT, 10))
counter_label.pack(pady=(0, 16))

# Entry row
entry_frame = tk.Frame(root, bg=BG)
entry_frame.pack(fill="x", padx=20, pady=(18, 8))

task_entry = tk.Entry(
    entry_frame, font=(FONT, 12), relief="flat", bg="white", fg=TEXT,
    insertbackground=TEXT, highlightthickness=1,
    highlightbackground="#d1d5db", highlightcolor=ACCENT,
)
task_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
task_entry.bind("<Return>", add_task)

make_button(entry_frame, "+ Add", ACCENT, ACCENT_HOVER, add_task, width=8).pack(side="left")

# List with scrollbar
list_frame = tk.Frame(root, bg=BG)
list_frame.pack(fill="both", expand=True, padx=20, pady=8)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

task_listbox = tk.Listbox(
    list_frame, font=(FONT, 12), bg="white", fg=TEXT, relief="flat",
    highlightthickness=1, highlightbackground="#d1d5db", highlightcolor="#d1d5db",
    selectbackground=SELECT, selectforeground=TEXT, activestyle="none",
    yscrollcommand=scrollbar.set,
)
task_listbox.pack(side="left", fill="both", expand=True)
scrollbar.config(command=task_listbox.yview)
task_listbox.bind("<Double-Button-1>", toggle_done)

# Buttons
button_frame = tk.Frame(root, bg=BG)
button_frame.pack(pady=(8, 6))

make_button(button_frame, "✔  Done / Undo", GREEN, GREEN_HOVER, toggle_done, width=16).pack(side="left", padx=6)
make_button(button_frame, "🗑  Delete", RED, RED_HOVER, delete_task, width=12).pack(side="left", padx=6)

tk.Label(root, text="Tip: double-click a task to mark it done",
         bg=BG, fg=MUTED, font=(FONT, 9)).pack(pady=(0, 12))

# ---------- Start ----------
tasks = load_tasks()
refresh_list()
task_entry.focus()
root.mainloop()