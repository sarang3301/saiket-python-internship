from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

OUTPUT_FILE = "scraped_results.txt"

# Polite identification, like a normal browser would send
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InternshipNewsScraper/1.0; learning project)"
}

# One entry per website. Each site's HTML is laid out differently, so each
# entry says WHERE to look. Supporting a new site = adding a new entry here.
SITES = {
    "1": {
        "name": "Hacker News",
        "kind": "headlines",
        "url": "https://news.ycombinator.com/",
        "item": "span.titleline",      # the box that holds one headline
        "link": "a",                   # the link inside that box
        "title_from": "text",          # headline = the link's visible text
        "extra": None,                 # nothing else to collect
        "max": 30,
    },
    "2": {
        "name": "Books to Scrape (practice site)",
        "kind": "books",
        "url": "https://books.toscrape.com/",
        "item": "article.product_pod",
        "link": "h3 a",
        "title_from": "title",         # visible text is cut short; full title is in the title="" attribute
        "extra": "p.price_color",      # also collect the price
        "max": 20,
    },
}


# ---------- Downloading ----------
def fetch_page(url):
    """Download a page. Return its raw bytes, or None if something went wrong."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        # .content (bytes) lets BeautifulSoup detect the page's encoding itself,
        # which avoids garbled symbols such as the pound sign.
        return response.content
    except requests.exceptions.Timeout:
        print("Error: the website took too long to respond (timeout).")
    except requests.exceptions.ConnectionError:
        print("Error: could not connect. Check your internet connection.")
    except requests.exceptions.HTTPError as error:
        print(f"Error: the website returned an error: {error}")
    except requests.exceptions.RequestException as error:
        print(f"Error: something went wrong with the request: {error}")
    return None


# ---------- Extracting ----------
def parse_items(html, site, limit):
    """Use the site's settings to pull out a list of {'title', 'url', 'extra'} dictionaries."""
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for box in soup.select(site["item"])[:limit]:
        link = box.select_one(site["link"])
        if link is None:
            continue

        href = link.get("href")
        if site["title_from"] == "text":
            title = link.get_text(strip=True)
        else:
            title = (link.get(site["title_from"]) or "").strip()

        if not href or not title:
            continue   # skip anything incomplete

        extra = ""
        if site["extra"]:
            extra_tag = box.select_one(site["extra"])
            if extra_tag:
                extra = extra_tag.get_text(strip=True)

        results.append({"title": title, "url": urljoin(site["url"], href), "extra": extra})

    return results


# ---------- Presenting ----------
def display_items(site, items):
    print("\n" + "=" * 70)
    print(f"  TOP {len(items)} FROM {site['name'].upper()}")
    print("=" * 70)

    for number, item in enumerate(items, start=1):
        line = f"\n{number:>2}. {item['title']}"
        if item["extra"]:
            line += f"   [{item['extra']}]"
        print(line)
        print(f"    {item['url']}")

    print("\n" + "=" * 70)


def save_to_file(site, items):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            file.write(f"{site['name']} - scraped on {stamp}\n\n")
            for number, item in enumerate(items, start=1):
                extra = f" [{item['extra']}]" if item["extra"] else ""
                file.write(f"{number}. {item['title']}{extra}\n   {item['url']}\n")
        print(f'Saved to "{OUTPUT_FILE}".')
    except OSError as error:
        print(f"Error: could not save the file: {error}")


# ---------- User input ----------
def choose_site():
    """Return the chosen site's settings, or None to quit."""
    print("\n=== WEB SCRAPER ===")
    for key, site in SITES.items():
        print(f"{key}. {site['name']}")
    print("Q. Quit")

    while True:
        choice = input("Choose a website: ").strip().lower()
        if choice in SITES:
            return SITES[choice]
        if choice in ("q", "quit"):
            return None
        print("Please choose one of the options above.")


def ask_count(maximum, default=10):
    while True:
        answer = input(f"How many? (1-{maximum}, Enter for {default}): ").strip()

        if answer == "":
            return min(default, maximum)
        if not answer.isdigit():
            print("Please enter a whole number.")
            continue

        number = int(answer)
        if 1 <= number <= maximum:
            return number
        print(f"Please choose a number between 1 and {maximum}.")


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
    while True:
        site = choose_site()
        if site is None:
            break

        count = ask_count(site["max"])

        print(f"\nFetching from {site['name']}...")
        html = fetch_page(site["url"])
        if html is None:
            continue

        items = parse_items(html, site, count)
        if not items:
            print("Nothing found. The website's layout may have changed.")
            continue

        display_items(site, items)

        if ask_yes_no("Save these results to a file?"):
            save_to_file(site, items)

    print("\nGoodbye!")


if __name__ == "__main__":
    main()