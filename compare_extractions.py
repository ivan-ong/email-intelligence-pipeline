"""
compare_extractions.py

Compares stored BigQuery extraction results (via the API) against a fresh
re-extraction using the current prompt. Useful for evaluating prompt changes.

Usage:
    python compare_extractions.py [--api-url http://localhost:8000] [--limit 100]
"""

import argparse
import json
from pathlib import Path

import httpx

from extraction.extractor import extract_from_email

DATA_DIR = Path("data")

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"


def fetch_stored(api_url: str, limit: int) -> dict[str, dict]:
    """Fetch all stored extractions from the API, keyed by filename."""
    resp = httpx.get(f"{api_url}/emails", params={"limit": limit}, timeout=10)
    resp.raise_for_status()
    return {e["filename"]: e for e in resp.json()["emails"]}


def diff_entities(old: list[str], new: list[str]) -> tuple[list[str], list[str]]:
    old_set, new_set = set(old), set(new)
    return sorted(new_set - old_set), sorted(old_set - new_set)


def print_field(label: str, old, new, width: int = 14):
    pad = " " * (width - len(label))
    if old == new:
        print(f"  {DIM}{label}{pad}{old}{RESET}")
    else:
        print(f"  {YELLOW}{label}{pad}{RED}{old}{RESET}  →  {GREEN}{new}{RESET}")


def compare(api_url: str, limit: int):
    print(f"\n{BOLD}Fetching stored results from {api_url}...{RESET}")
    stored = fetch_stored(api_url, limit)
    print(f"Found {len(stored)} stored emails.\n")

    email_files = sorted(DATA_DIR.glob("*.txt"))
    matched = [f for f in email_files if f.name in stored]
    unprocessed = [f for f in email_files if f.name not in stored]

    changed_count = 0

    for path in matched:
        filename = path.name
        old = stored[filename]

        print(f"{BOLD}{'─' * 64}{RESET}")
        print(f"{BOLD}  {filename}{RESET}")
        print(f"{'─' * 64}")

        print(f"\n  {DIM}Re-extracting with current prompt...{RESET}")
        try:
            new = extract_from_email(path.read_text()).model_dump()
        except Exception as e:
            print(f"  {RED}Extraction failed: {e}{RESET}\n")
            continue

        any_change = False

        # --- Intent ---
        print_field("intent", old["intent"], new["intent"])
        if old["intent"] != new["intent"]:
            any_change = True

        # --- Sender ---
        print_field("sender_name", old["sender_name"], new["sender_name"])
        print_field("sender_email", old["sender_email"], new["sender_email"])
        if (
            old["sender_name"] != new["sender_name"]
            or old["sender_email"] != new["sender_email"]
        ):
            any_change = True

        # --- Entities ---
        old_ents = old["key_entities"]
        new_ents = new["key_entities"]
        added, removed = diff_entities(old_ents, new_ents)

        count_label = f"entities"
        count_pad = " " * (14 - len(count_label))
        count_str = f"{len(old_ents)} → {len(new_ents)}"
        color = (
            GREEN
            if len(new_ents) < len(old_ents)
            else (RED if len(new_ents) > len(old_ents) else DIM)
        )
        print(f"  {DIM}{count_label}{count_pad}{RESET}{color}{count_str}{RESET}")
        if added:
            print(f"  {GREEN}  + {', '.join(added)}{RESET}")
        if removed:
            print(f"  {RED}  - {', '.join(removed)}{RESET}")
        if added or removed:
            any_change = True

        # --- Summary ---
        old_s = old["summary"]
        new_s = new["summary"]
        print(f"\n  {DIM}summary (before):{RESET}")
        print(f"    {old_s}")
        if old_s != new_s:
            print(f"  {GREEN}summary (after):{RESET}")
            print(f"    {new_s}")
            any_change = True
        else:
            print(f"  {DIM}summary (after):  (unchanged){RESET}")

        if any_change:
            changed_count += 1
            print(f"\n  {YELLOW}▲ changes detected{RESET}\n")
        else:
            print(f"\n  {DIM}✓ no changes{RESET}\n")

    if unprocessed:
        print(f"{BOLD}{'─' * 64}{RESET}")
        print(f"{YELLOW}Not yet in database ({len(unprocessed)} files):{RESET}")
        for f in unprocessed:
            print(f"  {f.name}")
        print()

    print(f"{BOLD}{'─' * 64}{RESET}")
    print(f"{BOLD}Summary: {changed_count}/{len(matched)} emails changed{RESET}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare stored vs fresh extractions.")
    parser.add_argument(
        "--api-url", default="http://localhost:8000", help="Base URL of the running API"
    )
    parser.add_argument(
        "--limit", type=int, default=100, help="Max emails to fetch from API"
    )
    args = parser.parse_args()
    compare(args.api_url, args.limit)
