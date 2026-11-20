import os
import string
import sys
from collections import Counter

DEFAULT_FILE = "sample_text.txt"
TOP_N = 10
BAR_WIDTH = 15


def get_filename():
    """Use the command-line argument if given, otherwise ask the user."""
    if len(sys.argv) > 1:
        return sys.argv[1].strip().strip('"').strip("'")
    answer = input(f"Enter file name [{DEFAULT_FILE}]: ").strip().strip('"').strip("'")
    return answer or DEFAULT_FILE


def read_file(filename):
    """Return the file's text, or raise a clear error message via ValueError."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise ValueError(f"File not found: '{filename}'")
    except IsADirectoryError:
        raise ValueError(f"'{filename}' is a folder, not a file.")
    except PermissionError:
        raise ValueError(f"No permission to read '{filename}'.")
    except UnicodeDecodeError:
        raise ValueError(f"'{filename}' is not a UTF-8 text file (is it a PDF/Word/image?).")
    except OSError as error:
        raise ValueError(f"Could not read '{filename}': {error}")


def clean_words(content):
    words = []
    for raw_word in content.split():
        word = raw_word.strip(string.punctuation).lower()
        if word:
            words.append(word)
    return words


def analyze(content):
    words = clean_words(content)
    frequency = Counter(words)
    ranked = sorted(frequency.items(), key=lambda item: (-item[1], item[0]))
    return {
        "lines": len(content.splitlines()),
        "words": len(words),
        "chars": len(content),
        "chars_no_spaces": len("".join(content.split())),
        "unique": len(frequency),
        "avg_length": sum(len(w) for w in words) / len(words) if words else 0,
        "longest": max(words, key=len) if words else "",
        "ranked": ranked,
    }


def build_report(filename, stats, top_n=TOP_N):
    """Return the whole report as one string (so we can print AND save it)."""
    line = "=" * 56
    out = [
        line,
        "WORD COUNT REPORT".center(56),
        line,
        f"File                    : {filename}",
        f"Lines                   : {stats['lines']}",
        f"Words                   : {stats['words']}",
        f"Unique words            : {stats['unique']}",
        f"Characters (with spaces): {stats['chars']}",
        f"Characters (no spaces)  : {stats['chars_no_spaces']}",
        f"Average word length     : {stats['avg_length']:.2f}",
        f"Longest word            : {stats['longest']}",
        "",
        f"TOP {top_n} WORDS",
        "-" * 56,
        f"{'Rank':<5}{'Word':<14}{'Count':>5}{'%':>8}  Frequency",
        "-" * 56,
    ]
    top = stats["ranked"][:top_n]
    max_count = top[0][1] if top else 1
    for rank, (word, count) in enumerate(top, start=1):
        percent = count / stats["words"] * 100
        bar = "█" * max(1, round(count / max_count * BAR_WIDTH))
        out.append(f"{rank:<5}{word:<14}{count:>5}{percent:>7.1f}%  {bar}")
    out.append(line)
    return "\n".join(out)


def save_text(path, text):
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(text + "\n")
        print(f"Report saved to {path}")
    except OSError as error:
        print(f"Could not save report: {error}")


def save_chart(stats, outfile, top_n=TOP_N):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not installed - skipping image chart (pip install matplotlib).")
        return

    top = stats["ranked"][:top_n]
    labels = [word for word, _ in top][::-1]
    counts = [count for _, count in top][::-1]

    plt.figure(figsize=(8, 5))
    plt.barh(labels, counts)
    plt.xlabel("Occurrences")
    plt.title(f"Top {top_n} words")
    plt.tight_layout()
    try:
        plt.savefig(outfile, dpi=150)
        print(f"Chart saved to {outfile}")
    except OSError as error:
        print(f"Could not save chart: {error}")
    finally:
        plt.close()


def main():
    filename = get_filename()

    try:
        content = read_file(filename)
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    stats = analyze(content)
    if stats["words"] == 0:
        print(f"'{filename}' has no words to analyze (empty or only punctuation).")
        return 1

    report = build_report(filename, stats)
    print(report)

    stem = os.path.splitext(filename)[0]
    save_text(f"{stem}_report.txt", report)
    save_chart(stats, f"{stem}_frequency.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())