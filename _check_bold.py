import json
import generate_publications as gp

data = json.loads(open("data/publications.json").read())
IDENTITIES = [gp.parse_identity("Dawid Zyla")]
NEW = {  # entries added in this ORCID update (for reporting)
    "10.15253/aacc.2025366470", "10.64898/2026.01.14.699513",
    "10.1038/s41564-026-01359-9",
    "Drugie stanowisko Myrmeleon inconspicuus, RAMBUR, 1842 w Polsce (Neuroptera: Myrmeleontidae)",
}

def is_new(e):
    return (e.get("doi") in NEW) or (e.get("title") in NEW)

mismatch_new, mismatch_old, ok = [], [], 0
for e in data:
    calc = gp.find_highlighted_authors(e["authors"], IDENTITIES)
    stored = e.get("highlight") or []
    tag = "NEW" if is_new(e) else "   "
    if calc == stored:
        ok += 1
        status = "OK"
    else:
        status = "MISMATCH"
        (mismatch_new if is_new(e) else mismatch_old).append(
            f"  {tag} {e.get('year')} | {e.get('title','')[:60]} | stored={stored} recomputed={calc}")
    print(f"{status:9s} {tag} {e.get('year')} | bold={' '.join(stored) or '(none)':15s} | {e.get('title','')[:58]}")

print(f"\n{ok}/{len(data)} entries: stored bold == recomputed bold (identity: 'Dawid Zyla')")
print(f"NEW-entry mismatches: {len(mismatch_new)}")
for m in mismatch_new + mismatch_old:
    print(m)
