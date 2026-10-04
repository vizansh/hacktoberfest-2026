"""Fetch Wiktionary source pages for a small, reviewed etymology set.

The app stores paraphrased facts and source links in data/etymologies.json.
This helper is intentionally conservative: it downloads source text for
human review and never copies whole entries into the application dataset.
"""

import json
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "etymologies.json"
API = "https://en.wiktionary.org/w/api.php"


def fetch(title):
    query = urllib.parse.urlencode({
        "action": "parse",
        "page": title,
        "prop": "wikitext",
        "format": "json",
        "formatversion": "2",
    })
    request = urllib.request.Request(
        f"{API}?{query}",
        headers={"User-Agent": "LanguageMap/0.1 etymology-review"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return payload["parse"]["wikitext"]


def main():
    entries = json.loads(DATA.read_text(encoding="utf-8"))
    titles = sys.argv[1:] or list(entries)
    for title in titles:
        print(f"\n--- {title} ---")
        print(fetch(title)[:6000])
    print("\nReview the output, paraphrase only verified facts, and update the local JSON with a source link.")


if __name__ == "__main__":
    main()
