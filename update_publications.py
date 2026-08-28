#!/usr/bin/env python3
"""
update_publications.py — merge NEW publications from ORCID into data/publications.json.

- Fetches all works for the given ORCID iD (summary level).
- Fetches per-work details ONLY for works whose DOI is not already in the file.
- Keeps all existing entries untouched (curation, manual links, etc.).
- De-duplicates by normalized DOI *and* normalized title, so e.g. an entry that
  already exists without a DOI (SSRN/scopus link) is not added twice.
- Reuses the identity helpers from generate_publications.py so the `highlight`
  field bolds the target name exactly like the existing entries do.

Usage:
    python3 update_publications.py
"""

import json
import re
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from generate_publications import (  # noqa: E402
    parse_identity,
    find_highlighted_authors,
    format_authors,
    get_authors_from_crossref,
    strip_accents,
)

ORCID = "0000-0001-8471-469X"
HIGHLIGHT = ["Dawid Zyla"]          # one canonical spelling; variants auto-matched
DATA_FILE = HERE / "data" / "publications.json"
HDRS = {"Accept": "application/json"}


def norm(s):
    """Lowercase, accent-stripped, alphanumeric-only key for de-duplication."""
    s = strip_accents(s or "").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def doi_of(work):
    for ext in (work.get("external-ids") or {}).get("external-id", []):
        if (ext.get("external-id-type") or "").lower() == "doi":
            return ext.get("external-id-value")
    return None


def build_entry(work, identities):
    """Same field extraction logic as generate_publications.fetch_publications."""
    title = (work.get("title") or {}).get("title", {}).get("value")
    pub_date = work.get("publication-date") or {}
    year = (pub_date.get("year") or {}).get("value")

    authors = format_authors((work.get("contributors") or {}).get("contributor", []))

    doi = doi_of(work)
    link = f"https://doi.org/{doi}" if doi else (work.get("url") or {}).get("value")

    if (not authors or authors == "N/A") and doi:
        cr = get_authors_from_crossref(doi)
        if cr:
            authors = cr
    if not authors:
        authors = "N/A"

    journal = (work.get("journal-title") or {}).get("value")
    if not journal:
        if doi and doi.startswith("10.1101/"):
            journal = "bioRxiv"
        elif doi and (doi.startswith("10.64898/") or doi.startswith("10.1130/")):
            journal = "medRxiv"
        elif work.get("type") == "preprint":
            journal = "Preprint"
        else:
            journal = "Journal not available"

    # Year fallback: bioRxiv/medRxiv DOIs embed YYYY.MM.DD
    if not year and doi:
        m = re.search(r"/(\d{4})\.\d{2}\.\d{2}\.", doi)
        if m:
            year = m.group(1)

    found_highlights = []
    if identities and authors != "N/A":
        found_highlights = find_highlighted_authors(authors, identities)

    if not (title and year):
        return None
    entry = {
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": int(year),
        "highlight": found_highlights,
    }
    if doi:
        entry["doi"] = doi
    if link:
        entry["link"] = link
    return entry


def main():
    existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    have_dois = {norm(e.get("doi")) for e in existing if e.get("doi")}
    have_titles = {norm(e.get("title")) for e in existing}
    identities = [i for i in (parse_identity(t) for t in HIGHLIGHT) if i and i["surname"]]

    r = requests.get(f"https://pub.orcid.org/v3.0/{ORCID}/works", headers=HDRS, timeout=60)
    r.raise_for_status()
    groups = r.json().get("group", [])

    # doi -> put-code (first occurrence)
    todo = {}
    no_doi = 0
    for g in groups:
        gids = (g.get("external-ids") or {}).get("external-id", [])
        gdoi = next(
            (e["external-id-value"] for e in gids
             if (e.get("external-id-type") or "").lower() == "doi"),
            None,
        )
        put = g.get("work-summary", [{}])[0].get("put-code") if g.get("work-summary") else None
        if not gdoi:
            no_doi += 1
            continue
        if norm(gdoi) in have_dois:
            continue
        todo.setdefault(norm(gdoi), (gdoi, put))

    print(f"Existing entries: {len(existing)} | candidate new DOIs: {len(todo)} | "
          f"ORCID groups without DOI (skipped): {no_doi}")

    added, dup_title = [], []
    for _, (doi, put) in todo.items():
        if not put:
            print(f"  ! no put-code for {doi}, skipping")
            continue
        w = requests.get(
            f"https://pub.orcid.org/v3.0/{ORCID}/work/{put}", headers=HDRS, timeout=60
        )
        if w.status_code != 200:
            print(f"  ! {doi}: HTTP {w.status_code}, skipping")
            continue
        entry = build_entry(w.json(), identities)
        if entry is None:
            print(f"  - {doi}: no title/year, skipping")
            continue
        if norm(entry["title"]) in have_titles:
            dup_title.append(entry["title"])
            continue
        added.append(entry)
        have_titles.add(norm(entry["title"]))

    # sanity: every highlighted name must exist verbatim in the authors string
    for e in added:
        for h in e["highlight"]:
            assert h in [a.strip() for a in e["authors"].split(";")], (
                f"highlight mismatch: {h!r} not in authors of {e['title']!r}"
            )

    merged = existing + added
    merged.sort(key=lambda x: x.get("year", 0), reverse=True)

    backup = HERE / "data" / "publications.json.bak"
    backup.write_text(DATA_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    DATA_FILE.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"\nADDED {len(added)} new publication(s):")
    for e in added:
        hl = ", ".join(e["highlight"]) or "(NONE BOLD)"
        print(f"  + {e['year']} | {e['journal']} | {e['title'][:80]}\n"
              f"      doi: {e.get('doi', '-')} | bold: {hl}")
    if dup_title:
        print(f"\nSKIPPED (already present, title match): {len(dup_title)}")
        for t in dup_title:
            print(f"  = {t[:90]}")
    print(f"\nSaved {DATA_FILE} (backup: {backup.name})")


if __name__ == "__main__":
    main()
