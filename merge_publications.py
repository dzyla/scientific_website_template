#!/usr/bin/env python3
"""
merge_publications.py — fetch ALL ORCID works via generate_publications.fetch_publications
(the canonical fetcher, incl. Crossref fallback + highlight matching) and MERGE them into
data/publications.json without disturbing existing curated entries.

- Existing entries always win (manual curation, links, curation are preserved).
- An ORCID work is added only if its normalized DOI and title are not already present.
- EXCLUDE_DOIS are never added (e.g. eLife "Author response" — not a publication).
"""
import json
import re
import sys
from pathlib import Path

import generate_publications as gp

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "data" / "publications.json"
ORCID = "0000-0001-8471-469X"
HIGHLIGHT = ["Dawid Zyla"]
EXCLUDE_DOIS = {
    "10.7554/elife.60265.sa2",  # eLife author response — not a publication
}


def norm(s):
    s = gp.strip_accents(s or "").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def main():
    existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    have_dois = {norm(e.get("doi")) for e in existing if e.get("doi")}
    have_titles = {norm(e.get("title")) for e in existing}

    pubs = gp.fetch_publications(ORCID, HIGHLIGHT)
    if pubs is None:
        sys.exit("ORCID fetch failed")

    added, excluded = [], []
    for p in pubs:
        doi = p.get("doi")
        n = norm(doi) if doi else None
        if n and n in {norm(x) for x in EXCLUDE_DOIS}:
            excluded.append((doi, p["title"]))
            continue
        if n and n in have_dois:
            continue
        if norm(p.get("title")) in have_titles:
            continue
        added.append(p)
        if n:
            have_dois.add(n)
        have_titles.add(norm(p.get("title")))

    if added:
        backup = DATA_FILE.with_name(DATA_FILE.name + ".bak")
        backup.write_text(DATA_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        merged = existing + added
        merged.sort(key=lambda x: x.get("year", 0), reverse=True)
        DATA_FILE.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")

    print(f"\nExisting: {len(existing)} | ORCID works: {len(pubs)} | "
          f"newly added: {len(added)} | excluded: {len(excluded)}")
    for e in added:
        hl = ", ".join(e.get("highlight", [])) or "(NONE BOLD)"
        print(f"  + {e['year']} | {e['journal']} | {e['title'][:80]}\n"
              f"      doi: {e.get('doi', '-')} | bold: {hl}")
    for doi, t in excluded:
        print(f"  x excluded: {doi} | {t[:70]}")


if __name__ == "__main__":
    main()
