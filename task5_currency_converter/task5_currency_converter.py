import json
import math
import os
import time
from datetime import datetime

import requests

URL = "https://open.er-api.com/v6/latest/USD"
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rates_cache.json")
CACHE_HOURS = 6   # rates only change once a day, so reusing them is fine
COMMON = ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF", "CNY", "AED", "SGD"]


# ---------- Getting the exchange rates ----------
def clean_rates(raw):
    """Keep only rates that are real, positive numbers (protects against bad data)."""
    good = {}
    if not isinstance(raw, dict):
        return good
    for code, value in raw.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if math.isfinite(value) and value > 0:
            good[str(code)] = float(value)
    return good


def fetch_rates_from_api():
    """Download fresh rates. Return (rates, last_update_text), or None if anything fails."""
    try:
        response = requests.get(URL, timeout=10)
    except requests.exceptions.Timeout:
        print("Network problem: the rate service took too long to respond.")
        return None
    except requests.exceptions.ConnectionError:
        print("Network problem: could not connect. Check your internet connection.")
        return None
    except requests.exceptions.RequestException as error:
        print(f"Network problem: {error}")
        return None

    if response.status_code == 429:
        print("The rate service says we asked too many times. Try again in about 20 minutes.")
        return None
    if not response.ok:
        print(f"The rate service returned an error (HTTP {response.status_code}).")
        return None

    try:
        data = response.json()
    except ValueError:
        print("The rate service sent a reply we could not read.")
        return None

    if not isinstance(data, dict) or data.get("result") != "success":
        reason = data.get("error-type", "unknown") if isinstance(data, dict) else "unknown"
        print(f"The rate service reported an error: {reason}")
        return None

    rates = clean_rates(data.get("rates"))
    if "USD" not in rates or len(rates) < 2:
        print("The rate service sent incomplete data.")
        return None

    return rates, str(data.get("time_last_update_utc", "unknown"))


def load_cache():
    """Return the saved cache as a dictionary, or None if there is no usable cache."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            cache = json.load(file)
        rates = clean_rates(cache["rates"])
        if "USD" not in rates:
            return None
        return {"rates": rates, "saved_at": float(cache["saved_at"]),
                "last_update": str(cache.get("last_update", "unknown"))}
    except (OSError, ValueError, KeyError, TypeError):
        return None   # missing, damaged or unreadable: treat as "no cache"


def save_cache(rates, last_update):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as file:
            json.dump({"saved_at": time.time(), "last_update": last_update, "rates": rates}, file)
    except OSError:
        pass   # failing to save is not worth stopping the program for


def get_rates():
    """Return a dictionary with the rates and where they came from, or None."""
    cache = load_cache()
    age_hours = (time.time() - cache["saved_at"]) / 3600 if cache else None

    # 1. A recent saved copy is good enough (and kinder to the API)
    if cache and age_hours < CACHE_HOURS:
        return {"rates": cache["rates"], "last_update": cache["last_update"],
                "note": f"Using saved rates ({age_hours:.1f} hours old)."}

    # 2. Otherwise ask the API for fresh rates
    fresh = fetch_rates_from_api()
    if fresh:
        rates, last_update = fresh
        save_cache(rates, last_update)
        return {"rates": rates, "last_update": last_update, "note": "Fresh rates downloaded."}

    # 3. API failed: fall back to an old saved copy if we have one
    if cache:
        saved = datetime.fromtimestamp(cache["saved_at"]).strftime("%d %b %Y %H:%M")
        return {"rates": cache["rates"], "last_update": cache["last_update"],
                "note": f"OFFLINE MODE: using older saved rates from {saved}. They may be out of date."}

    return None


# ---------- Converting ----------
def convert(rates, amount, from_code, to_code):
    """Convert an amount between two currencies using USD as the middle step."""
    amount_in_usd = amount / rates[from_code]
    return amount_in_usd * rates[to_code]


# ---------- User input ----------
def show_currencies(rates):
    codes = sorted(rates)
    print(f"\nAll {len(codes)} supported currency codes:")
    for start in range(0, len(codes), 10):
        print("  " + "  ".join(codes[start:start + 10]))
    print()


def ask_currency(prompt, rates):
    """Keep asking until the user enters a supported currency code."""
    while True:
        code = input(prompt).strip().upper()

        if code == "":
            print("Please enter a currency code (like USD).")
        elif code == "LIST":
            show_currencies(rates)
        elif code in rates:
            return code
        else:
            print(f'"{code}" is not a supported currency. Type LIST to see all codes.')


def ask_amount():
    """Keep asking until the user enters a valid positive amount."""
    while True:
        text = input("Amount: ").strip().replace(",", "")

        try:
            amount = float(text)
        except ValueError:
            print("Please enter a number (like 250 or 99.50).")
            continue

        if not math.isfinite(amount):
            print("Please enter a real number.")
        elif amount <= 0:
            print("The amount must be greater than zero.")
        else:
            return amount


def ask_yes_no(question):
    while True:
        answer = input(f"{question} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.")


# ---------- Main program ----------
def main():
    print("=== CURRENCY CONVERTER ===")

    data = get_rates()
    if data is None:
        print("\nSorry, no exchange rates are available and there is no saved copy.")
        print("Please check your internet connection and try again.")
        return

    rates = data["rates"]
    print(data["note"])
    print(f"Rates last updated by provider: {data['last_update']}")
    print("Popular codes: " + ", ".join(code for code in COMMON if code in rates))
    print("Type LIST at a currency prompt to see every supported code.\n")

    while True:
        from_code = ask_currency("Convert FROM (e.g. USD): ", rates)
        to_code = ask_currency("Convert TO   (e.g. INR): ", rates)
        amount = ask_amount()

        result = convert(rates, amount, from_code, to_code)
        one_unit = convert(rates, 1, from_code, to_code)

        print("\n" + "-" * 44)
        print(f"  {amount:,.2f} {from_code} = {result:,.2f} {to_code}")
        print(f"  (1 {from_code} = {one_unit:,.4f} {to_code})")
        print("-" * 44)
        print("Rates by Exchange Rate API (exchangerate-api.com)\n")

        if not ask_yes_no("Convert another amount?"):
            break

    print("\nGoodbye!")


if __name__ == "__main__":
    main()