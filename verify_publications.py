#!/usr/bin/env python3
"""Verify data/publications.json: valid JSON, year desc order, and every
highlighted name appears verbatim in its authors list (the bolding rule)."""
import json
from pathlib import Path

f = Path(__file__).resolve().parent / "data" / "publications.json"
pubs = json.loads(f.read_text(encoding="utf-8"))
print(f"entries: {len(pubs)}")

bad = 0
years = [e.get("year") for e in pubs]
if years != sorted(years, reverse=True):
    print("WARNING: not sorted year-desc")
for e in pubs:
    authors = [a.strip() for a in e.get("authors", "").split(";")]
    for h in e.get("highlight", []):
        if h not in authors:
            bad += 1
            print(f"HIGHLIGHT MISMATCH: {e['title'][:60]} | bold={h!r}")
    if not e.get("highlight"):
        print(f"NO HIGHLIGHT: {e['title'][:60]}")

dois = [e.get("doi") for e in pubs if e.get("doi")]
if len(dois) != len(set(d.lower() for d in dois)):
    print("WARNING: duplicate DOIs")

print("highlight mismatches:", bad)
print("new DOIs present:", [d for d in (
    "10.1038/s41564-026-02465-6", "10.64898/2026.01.14.699513",
    "10.1016/j.bpj.2024.11.428", "10.7554/elife.60265.sa2") if d in dois])
