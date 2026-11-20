import math
import threading
import tkinter as tk
from tkinter import ttk

# Reuse the rate-fetching, caching and conversion code from the console version.
# Keep task5_currency_converter.py in the same folder as this file.
from task5_currency_converter import COMMON, convert, get_rates

# ---------- Look and feel ----------
BG = "#f4f6fb"
HEADER = "#4f46e5"
TEXT = "#1f2937"
MUTED = "#6b7280"
ACCENT, ACCENT_HOVER = "#4f46e5", "#4338ca"
GREEN, GREEN_HOVER = "#16a34a", "#15803d"
ORANGE = "#ea580c"
RED = "#dc2626"
GREY = "#9ca3af"
FONT = "Segoe UI"


# ---------- Helpers that don't touch the window ----------
def parse_amount(text):
    """Return (amount, error_message). error_message is None when the amount is valid."""
    text = text.strip().replace(",", "")
    if text == "":
        return None, "Please enter an amount."

    try:
        amount = float(text)
    except ValueError:
        return None, "Please enter a number (like 250 or 99.50)."

    if not math.isfinite(amount):
        return None, "Please enter a real number."
    if amount <= 0:
        return None, "The amount must be greater than zero."
    return amount, None


def ordered_codes(rates):
    """Popular currencies first, then everything else alphabetically."""
    popular = [code for code in COMMON if code in rates]
    others = sorted(code for code in rates if code not in popular)
    return popular + others


def make_button(parent, text, color, hover, command, width=12, size=11):
    button = tk.Button(
        parent, text=text, command=command, width=width,
        bg=color, fg="white", activebackground=hover, activeforeground="white",
        disabledforeground="white",
        font=(FONT, size, "bold"), relief="flat", bd=0, cursor="hand2", pady=7,
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


# ---------- The window ----------
def main():
    root = tk.Tk()
    root.title("Currency Converter")
    root.geometry("480x640")
    root.minsize(420, 600)
    root.configure(bg=BG)
    root.option_add("*TCombobox*Listbox.font", (FONT, 11))   # bigger dropdown lists

    state = {"rates": None}

    # Header
    header = tk.Frame(root, bg=HEADER)
    header.pack(fill="x")
    tk.Label(header, text="Currency Converter", bg=HEADER, fg="white",
             font=(FONT, 22, "bold")).pack(pady=(18, 2))
    status_label = tk.Label(header, text="Loading exchange rates...", bg=HEADER,
                            fg="#c7d2fe", font=(FONT, 10), wraplength=420)
    status_label.pack(pady=(0, 16))

    # Amount
    tk.Label(root, text="Amount", bg=BG, fg=MUTED, font=(FONT, 10)).pack(anchor="w", padx=30, pady=(20, 0))
    amount_entry = tk.Entry(
        root, font=(FONT, 20), relief="flat", bg="white", fg=TEXT,
        insertbackground=TEXT, highlightthickness=2,
        highlightbackground="#d1d5db", highlightcolor=ACCENT,
    )
    amount_entry.pack(fill="x", padx=30, pady=(4, 12), ipady=6)
    amount_entry.insert(0, "1")

    # From  <swap>  To
    row = tk.Frame(root, bg=BG)
    row.pack(fill="x", padx=30, pady=4)
    row.columnconfigure(0, weight=1)
    row.columnconfigure(2, weight=1)

    from_frame = tk.Frame(row, bg=BG)
    from_frame.grid(row=0, column=0, sticky="ew")
    tk.Label(from_frame, text="From", bg=BG, fg=MUTED, font=(FONT, 10)).pack(anchor="w")
    from_box = ttk.Combobox(from_frame, state="readonly", font=(FONT, 13), width=8)
    from_box.pack(fill="x", ipady=4)

    to_frame = tk.Frame(row, bg=BG)
    to_frame.grid(row=0, column=2, sticky="ew")
    tk.Label(to_frame, text="To", bg=BG, fg=MUTED, font=(FONT, 10)).pack(anchor="w")
    to_box = ttk.Combobox(to_frame, state="readonly", font=(FONT, 13), width=8)
    to_box.pack(fill="x", ipady=4)

    # Result card
    card = tk.Frame(root, bg="white", highlightthickness=1, highlightbackground="#d1d5db")
    card.pack(fill="x", padx=30, pady=(18, 8))
    result_label = tk.Label(card, text="", bg="white", fg=ACCENT,
                            font=(FONT, 18, "bold"), wraplength=380, height=2)
    result_label.pack(padx=12, pady=(14, 2))
    rate_label = tk.Label(card, text="", bg="white", fg=MUTED, font=(FONT, 11))
    rate_label.pack(padx=12, pady=(0, 14))

    # ---- actions ----
    def show_result(message, rate_text="", color=ACCENT):
        result_label.config(text=message, fg=color)
        rate_label.config(text=rate_text)

    def do_convert(event=None):
        if state["rates"] is None:
            show_result("Exchange rates are not loaded yet.", color=ORANGE)
            return

        amount, error = parse_amount(amount_entry.get())
        if error:
            show_result(error, color=ORANGE)
            return

        from_code = from_box.get()
        to_code = to_box.get()
        result = convert(state["rates"], amount, from_code, to_code)
        one_unit = convert(state["rates"], 1, from_code, to_code)

        show_result(f"{amount:,.2f} {from_code} = {result:,.2f} {to_code}",
                    f"1 {from_code} = {one_unit:,.4f} {to_code}")

    def swap():
        first, second = from_box.get(), to_box.get()
        from_box.set(second)
        to_box.set(first)
        if state["rates"] is not None:
            do_convert()

    convert_button = make_button(root, "Convert", ACCENT, ACCENT_HOVER, do_convert, width=20, size=12)
    convert_button.pack(pady=(10, 4))

    # The swap button sits between the two dropdowns
    swap_button = make_button(row, "⇄", GREEN, GREEN_HOVER, swap, width=3, size=12)
    swap_button.grid(row=0, column=1, padx=10, pady=(18, 0))

    retry_button = make_button(root, "Retry", ORANGE, "#c2410c", lambda: start_loading(), width=12)

    tk.Label(root, text="Rates by Exchange Rate API (exchangerate-api.com)",
             bg=BG, fg=MUTED, font=(FONT, 9)).pack(side="bottom", pady=(0, 12))
    updated_label = tk.Label(root, text="", bg=BG, fg=MUTED, font=(FONT, 9))
    updated_label.pack(side="bottom")

    # ---- loading the rates without freezing the window ----
    def finish_loading(data):
        if data is None:
            state["rates"] = None
            status_label.config(text="No exchange rates available")
            show_result("Could not load exchange rates. Check your internet connection, then press Retry.",
                        color=RED)
            retry_button.pack(pady=4)
            return

        state["rates"] = data["rates"]
        codes = ordered_codes(data["rates"])
        from_box.config(values=codes)
        to_box.config(values=codes)
        if from_box.get() not in codes:
            from_box.set("USD" if "USD" in codes else codes[0])
        if to_box.get() not in codes:
            to_box.set("INR" if "INR" in codes else codes[-1])

        status_label.config(text=data["note"])
        updated_label.config(text=f"Provider last updated: {data['last_update']}")
        convert_button.config(state="normal", bg=ACCENT)
        do_convert()

    def start_loading():
        status_label.config(text="Loading exchange rates...")
        show_result("Loading...", color=MUTED)
        convert_button.config(state="disabled", bg=GREY)
        retry_button.pack_forget()

        box = {}

        def worker():
            box["data"] = get_rates()   # this may take a few seconds

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        def check():
            if thread.is_alive():
                root.after(100, check)   # not done yet: look again in 0.1 s
            else:
                finish_loading(box.get("data"))

        root.after(100, check)

    # ---- events ----
    amount_entry.bind("<Return>", do_convert)
    from_box.bind("<<ComboboxSelected>>", do_convert)
    to_box.bind("<<ComboboxSelected>>", do_convert)

    amount_entry.focus()
    start_loading()
    root.mainloop()


if __name__ == "__main__":
    main()