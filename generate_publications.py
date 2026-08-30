import requests
import json
import argparse
import sys
import unicodedata
import re
from urllib.parse import quote as urllib_quote
from urllib.request import Request, urlopen

CROSSREF_UA = "ZylaLabSite/1.0 (https://zylalab.org; mailto:dawid.zyla@cuanschutz.edu)"

# --- Helper Functions ---

# Characters that NFKD does NOT decompose but that we still want folded to ASCII
# (e.g. Polish ł, Nordic ø/æ, Croatian đ). Ż/ż/á/é etc. are handled by NFKD.
SPECIAL_FOLD = str.maketrans({
    'ł': 'l', 'Ł': 'l', 'ø': 'o', 'Ø': 'o', 'đ': 'd', 'Đ': 'd',
    'ħ': 'h', 'Ħ': 'h', 'ı': 'i', 'İ': 'i', 'ß': 'ss', 'æ': 'ae',
    'Æ': 'ae', 'œ': 'oe', 'Œ': 'oe', 'þ': 'th', 'ð': 'd',
})

def strip_accents(text):
    """Fold accented/special letters to ASCII: 'Żyła' -> 'zyla'."""
    text = text.translate(SPECIAL_FOLD)
    text = unicodedata.normalize('NFKD', text)
    return "".join(c for c in text if not unicodedata.combining(c))

def normalize_to_tokens(text):
    """
    Converts text into a set of normalized word tokens.
    "Zyla, Dawid S." -> {'zyla', 'dawid', 's'};  "Żyła" -> {'zyla'}
    """
    if not text:
        return set()
    text = strip_accents(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)     # punctuation -> space, "D.S." -> "d s"
    return set(text.split())

def parse_identity(name):
    """
    Parse a canonical highlight name into a {surname, given} identity.

    Handles both orders:
      "Dawid Zyla"      -> {surname: 'zyla',  given: 'dawid'}
      "Zyla, Dawid S."  -> {surname: 'zyla',  given: 'dawid'}
      "Zyla"            -> {surname: 'zyla',  given: ''}
    You only need to supply ONE canonical spelling per person; the matcher
    recognizes initials, reordered forms, and accented variants automatically.
    """
    if not name or not name.strip():
        return None
    raw = name.strip()
    norm = strip_accents(raw).lower()

    if ',' in raw:
        # "Surname, Given" order
        surname_part, _, given_part = norm.partition(',')
    else:
        # "Given ... Surname" order -> last token is the surname
        toks = re.sub(r'[^\w\s]', ' ', norm).split()
        if not toks:
            return None
        surname_part, given_part = toks[-1], " ".join(toks[:-1])

    surname_toks = re.sub(r'[^\w\s]', ' ', surname_part).split()
    given_toks = re.sub(r'[^\w\s]', ' ', given_part).split()
    surname = surname_toks[-1] if surname_toks else ''
    # first *word-length* given token is the given name; else first initial
    given = ''
    for t in given_toks:
        given = t
        break
    return {'surname': surname, 'given': given}

def author_matches_identity(author_str, identity):
    """
    True if a single author string refers to the target identity.

    Rule: surname must be present, AND the given name must match either in
    full ('dawid') or by first initial ('d'). Full given names are never
    reduced to initials, so 'Daniel Zyla' does NOT match 'Dawid Zyla', while
    'Zyla, D.' and 'D. Zyla' do.
    """
    if not identity or not identity.get('surname'):
        return False
    toks = normalize_to_tokens(author_str)
    if identity['surname'] not in toks:
        return False
    given = identity.get('given') or ''
    if not given:
        return True                      # surname-only target
    if given in toks:
        return True                      # full given name present
    return given[0] in toks              # initial present (token 'd')

def find_highlighted_authors(authors_string, identities):
    """
    Return the exact author substrings (as they appear) that match any identity.
    These are what the template bolds, so format variations are irrelevant.
    """
    result = []
    for author in authors_string.split(';'):
        author = author.strip()
        if not author:
            continue
        if any(author_matches_identity(author, ident) for ident in identities):
            if author not in result:
                result.append(author)
    return result

# --- Manual curation -----------------------------------------------------

# ORCID indexes some records that are not publications of the lab: machine
# translations of an existing paper, eLife peer-review "Author response"
# stubs, conference meeting abstracts, and pre-lab work from another field.
# Matched on the normalized title (see title_key), so punctuation and case do
# not matter. Kept here rather than hand-edited out of the JSON, because a
# full ORCID re-sync rewrites that file from scratch.
EXCLUDED_TITLES = [
    # Japanese machine translation of the EMBO Journal chaperone paper
    "胆汁応答性シャペロンとしての代謝産物結合蛋白質ムーンライト【JST・京大機械翻訳】",
    # eLife peer-review artifacts, not papers
    "Author response: The cryo-EM structure of the human uromodulin filament "
    "core reveals a unique assembly mechanism",
    # Biophysical Society meeting abstract
    "BPS2025 - Structural analysis of human endogenous retrovirus K envelope "
    "protein",
    # Undergraduate entomology, unrelated to the lab
    "Drugie stanowisko Myrmeleon inconspicuus, RAMBUR, 1842 w Polsce "
    "(Neuroptera: Myrmeleontidae)",
]

# Papers ORCID has not indexed yet, fetched from Crossref on every run. ORCID
# can lag months behind publication, and a journal version listed here also
# retires its own preprint through the normal superseded-preprint pairing.
EXTRA_DOIS = [
    "10.1038/s41467-026-71373-4",   # Nat Commun 2026, measles fusion protein
    "10.64898/2026.01.14.699513",   # bioRxiv 2026, lyssavirus antigenic landscape
]


# --- Preprint handling ---------------------------------------------------

# Servers whose "journal" is really a preprint venue. Matched case-insensitively
# against the journal name; DOI prefixes cover the cases where ORCID reports a
# generic title.
PREPRINT_VENUES = {
    'biorxiv', 'medrxiv', 'arxiv', 'chemrxiv', 'ssrn', 'preprint',
    'research square', 'authorea', 'osf preprints',
}
PREPRINT_DOI_PREFIXES = ('10.1101/', '10.64898/', '10.2139/', '10.48550/',
                         '10.21203/')


def is_preprint(journal, doi=None):
    """True if an entry is a preprint rather than a peer-reviewed article."""
    name = (journal or '').strip().lower()
    if name in PREPRINT_VENUES:
        return True
    if doi and str(doi).startswith(PREPRINT_DOI_PREFIXES):
        return True
    return False


def title_key(title):
    """Normalized title used to pair a preprint with its published version."""
    return re.sub(r'[^a-z0-9]', '', strip_accents(title or '').lower())


# Papers are frequently retitled between preprint and publication ("...at
# highest field" -> "...at 1200 MHz"), so exact title matching is not enough.
# On this corpus every genuine preprint/published pair scores >= 0.81 word
# overlap while no unrelated pair exceeds 0.5, so 0.7 sits in a wide gap.
SAME_WORK_SIMILARITY = 0.7


def title_tokens(title):
    """Normalized word set of a title, for preprint/published pairing."""
    return set(re.findall(r'[a-z0-9]+', strip_accents(title or '').lower()))


def _same_work(a, b):
    """True if two titles almost certainly describe the same manuscript."""
    if title_key(a) == title_key(b):
        return True
    ta, tb = title_tokens(a), title_tokens(b)
    if not ta or not tb:
        return False
    return len(ta & tb) / len(ta | tb) >= SAME_WORK_SIMILARITY


def drop_superseded_preprints(publications):
    """
    Remove preprints that have since appeared in a peer-reviewed venue, and
    collapse the same preprint posted to several servers (e.g. bioRxiv + SSRN).

    An entry can also opt out of the automatic pairing with "keep": true, or
    force removal with "superseded": true, for the cases heuristics get wrong.
    """
    published = [p['title'] for p in publications if not p.get('preprint')]

    kept, seen_preprints = [], []
    for p in publications:
        if not p.get('preprint'):
            kept.append(p)
            continue
        if p.get('superseded'):
            continue                      # manually retired
        if p.get('keep'):
            kept.append(p)                # manually pinned
            continue
        title = p['title']
        if any(_same_work(title, t) for t in published):
            continue                      # superseded by the journal version
        if any(_same_work(title, t) for t in seen_preprints):
            continue                      # same manuscript on a second server
        seen_preprints.append(title)
        kept.append(p)
    return kept


def canonicalize_authors(authors_string, identities, canonical_names):
    """
    Rewrite every author string that matches one of the tracked identities to a
    single canonical spelling, so the same person is not rendered as
    'Dawid Zyla', 'Dawid S Zyla' and 'Dawid S. Żyła' across the list.

    Returns (authors_string, highlight_list).
    """
    out, highlights = [], []
    for author in authors_string.split(';'):
        author = author.strip()
        if not author:
            continue
        replacement = None
        for ident, canonical in zip(identities, canonical_names):
            if author_matches_identity(author, ident):
                replacement = canonical
                break
        if replacement:
            out.append(replacement)
            if replacement not in highlights:
                highlights.append(replacement)
        else:
            out.append(author)
    return "; ".join(out), highlights


def drop_excluded(publications):
    """Remove records listed in EXCLUDED_TITLES."""
    blocked = {title_key(t) for t in EXCLUDED_TITLES}
    return [p for p in publications if title_key(p.get('title')) not in blocked]


def postprocess(publications, identities, canonical_names):
    """Tag preprints, drop superseded ones, and normalize highlighted names."""
    publications = drop_excluded(publications)
    for p in publications:
        p['preprint'] = is_preprint(p.get('journal'), p.get('doi'))
        if identities and p.get('authors') and p['authors'] != 'N/A':
            p['authors'], p['highlight'] = canonicalize_authors(
                p['authors'], identities, canonical_names
            )
    publications = drop_superseded_preprints(publications)
    publications.sort(key=lambda x: (-x['year'], x['title'].lower()))
    return publications


def entry_from_crossref(doi):
    """
    Build a publication entry straight from Crossref.

    ORCID can lag months behind publication — a paper that has already appeared
    in a journal may still be listed only as its preprint, which then keeps the
    superseded preprint visible on the site. This lets a DOI be added by hand
    in the meantime; the next full ORCID sync simply overwrites it.
    """
    clean = doi.replace("https://doi.org/", "").strip()
    url = f"https://api.crossref.org/works/{urllib_quote(clean)}"
    req = Request(url, headers={"User-Agent": CROSSREF_UA})
    with urlopen(req, timeout=30) as resp:
        msg = json.load(resp)["message"]

    authors = []
    for a in msg.get("author", []) or []:
        given, family = a.get("given", ""), a.get("family", "")
        if given and family:
            authors.append(f"{given} {family}")
        elif family:
            authors.append(family)

    # Prefer the print/online publication year, falling back to the deposit date.
    date = (msg.get("published-print") or msg.get("published-online")
            or msg.get("issued") or {})
    year = (date.get("date-parts") or [[None]])[0][0]

    journal = (msg.get("container-title") or [None])[0]
    if not journal:
        journal = msg.get("institution", [{}])[0].get("name") if msg.get("institution") else None
    if not journal:
        journal = "Preprint" if msg.get("type") == "posted-content" else "Journal not available"
    # bioRxiv posts under its own prefix; Crossref reports no container title.
    if msg.get("type") == "posted-content" and clean.startswith("10.1101/"):
        journal = "bioRxiv"

    entry = {
        "title": (msg.get("title") or ["Untitled"])[0],
        "authors": "; ".join(authors) or "N/A",
        "journal": journal,
        "year": int(year) if year else None,
        "highlight": [],
        "doi": clean,
        "link": f"https://doi.org/{clean}",
    }
    return entry


def format_authors(contributors):
    """Formats ORCID contributors into a semicolon-separated string."""
    if not contributors:
        return ""
    names = []
    for c in contributors:
        name = (c.get('credit-name') or {}).get('value')
        if not name:
            name = (c.get('contributor-name') or {}).get('value')
        if name:
            names.append(name)
    return "; ".join(names)

def get_authors_from_crossref(doi):
    """Fetches author metadata from Crossref."""
    try:
        clean_doi = doi.replace("https://doi.org/", "").strip()
        url = f"https://api.crossref.org/works/{clean_doi}"
        headers = {"User-Agent": CROSSREF_UA}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None
        
        data = resp.json()
        authors = data.get("message", {}).get("author", [])
        formatted = []
        for a in authors:
            given = a.get("given", "")
            family = a.get("family", "")
            if given and family:
                formatted.append(f"{given} {family}")
            elif family:
                formatted.append(family)
        return "; ".join(formatted)
    except Exception:
        return None

def fetch_publications(orcid_id, highlight_list=None):
    print(f"Fetching publications for {orcid_id}...")
    API_URL = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/json"}
    highlight_list = highlight_list or []

    # Build robust identities once (surname + given name / initial).
    identities = [i for i in (parse_identity(t) for t in highlight_list) if i and i['surname']]
    if identities:
        print("Highlighting authors matching: " +
              ", ".join(f"{i['given'].title() or '?'} {i['surname'].title()}" for i in identities))

    try:
        resp = requests.get(API_URL, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        summaries = data.get('group', [])
        if not summaries:
            print("No works found.")
            return []

        print(f"Processing {len(summaries)} items...")
        publications = []

        for i, item in enumerate(summaries):
            put_code = item['work-summary'][0]['put-code']
            detail_url = f"https://pub.orcid.org/v3.0/{orcid_id}/work/{put_code}"
            
            w_resp = requests.get(detail_url, headers=headers)
            if w_resp.status_code != 200: continue
            work = w_resp.json()

            # --- Extract Data ---
            title = (work.get('title') or {}).get('title', {}).get('value', 'N/A')
            pub_date = work.get('publication-date') or {}
            year = (pub_date.get('year') or {}).get('value')
            
            # Links
            link, doi = None, None
            for ext in (work.get('external-ids') or {}).get('external-id', []):
                if ext.get('external-id-type', '').lower() == 'doi':
                    doi = ext.get('external-id-value')
                    link = f"https://doi.org/{doi}"
                    break
            if not link:
                link = (work.get('url') or {}).get('value')

            # Authors. ORCID's contributor list does not reliably preserve the
            # paper's author order (imported works often come back scrambled),
            # while Crossref does — so Crossref wins whenever there is a DOI,
            # and ORCID contributors are only the fallback.
            authors = get_authors_from_crossref(doi) if doi else None
            if not authors:
                contribs = work.get('contributors') or {}
                authors = format_authors(contribs.get('contributor', []))
            if not authors: authors = "N/A"

            # Journal
            journal = (work.get('journal-title') or {}).get('value')
            w_type = work.get('type')
            if not journal:
                if doi and doi.startswith('10.1101/'): journal = "bioRxiv"
                elif w_type == 'preprint': journal = "Preprint"
                else: journal = "Journal not available"

            # --- MATCHING LOGIC ---
            # Store the *exact author strings* to bold, so the template can do a
            # simple membership test regardless of how each paper spells the name.
            # postprocess() later rewrites these to one canonical spelling.
            found_highlights = []
            if identities and authors != "N/A":
                found_highlights = find_highlighted_authors(authors, identities)

            if title and year:
                entry = {
                    "title": title,
                    "authors": authors,
                    "journal": journal,
                    "year": int(year),
                    "highlight": found_highlights
                }
                if doi: entry["doi"] = doi
                if link: entry["link"] = link
                publications.append(entry)

            sys.stdout.write(f"\rProcessed {i+1}/{len(summaries)}")
            sys.stdout.flush()

        print("\nDone.")

        # Merge the hand-curated DOIs before postprocessing, so they take part
        # in preprint pairing and name normalization like any ORCID record.
        known = {(p.get('doi') or '').lower() for p in publications}
        for doi in EXTRA_DOIS:
            if doi.lower() in known:
                continue
            try:
                entry = entry_from_crossref(doi)
            except Exception as e:
                print(f"Could not fetch {doi}: {e}")
                continue
            print(f"Added from Crossref: {entry['year']} {entry['journal']} — "
                  f"{entry['title'][:60]}")
            publications.append(entry)

        before = len(publications)
        publications = postprocess(publications, identities, highlight_list)
        if before != len(publications):
            print(f"Dropped {before - len(publications)} superseded/duplicate preprint(s).")
        return publications

    except Exception as e:
        print(f"\nError: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("orcid_id", nargs="?",
                        help="ORCID iD to fetch. Omit when using --normalize.")
    parser.add_argument("-o", "--output", default="data/publications.json")
    parser.add_argument("-hl", "--highlight", default="",
                        help="Canonical name(s) to bold, semicolon-separated. "
                             "Give ONE spelling per person (e.g. 'Dawid S. Zyla'); "
                             "initials, reversed order, and accents are matched "
                             "automatically, and every match is rewritten to this "
                             "spelling so the list reads consistently.")
    parser.add_argument("--add-doi", metavar="DOI", action="append", default=[],
                        help="Fetch this DOI from Crossref and merge it into the "
                             "output file. Use for papers ORCID has not indexed "
                             "yet; repeatable. Combine with --normalize to add to "
                             "an existing file without a full re-sync.")
    parser.add_argument("--normalize", metavar="FILE",
                        help="Skip the ORCID fetch and re-run tagging, "
                             "deduplication and name normalization over an "
                             "existing publications JSON file.")
    args = parser.parse_args()

    # Split by semicolon and strip whitespace
    hl_list = [h.strip() for h in args.highlight.split(';') if h.strip()]

    if args.normalize:
        identities = [i for i in (parse_identity(t) for t in hl_list) if i and i['surname']]
        with open(args.normalize, encoding='utf-8') as f:
            existing = json.load(f)
        before = len(existing)
        for doi in EXTRA_DOIS + args.add_doi:
            known = {(p.get('doi') or '').lower() for p in existing}
            if doi.lower() in known:
                print(f"Already present, skipping: {doi}")
                continue
            entry = entry_from_crossref(doi)
            print(f"Added {entry['year']} {entry['journal']}: {entry['title'][:60]}")
            existing.append(entry)
        data = postprocess(existing, identities, hl_list)
        print(f"Normalized {before} entries -> {len(data)} "
              f"({sum(1 for p in data if p['preprint'])} preprints).")
    else:
        if not args.orcid_id:
            parser.error("orcid_id is required unless --normalize is given")
        data = fetch_publications(args.orcid_id, hl_list)

    if data:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()