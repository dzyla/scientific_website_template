import requests
import json
import argparse
import sys
import unicodedata
import re

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
        headers = {"User-Agent": "PublicationFetcher/1.0 (mailto:example@test.com)"}
        resp = requests.get(url, headers=headers, timeout=5)
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
            
            # Authors
            contribs = work.get('contributors') or {}
            authors = format_authors(contribs.get('contributor', []))
            
            # Links
            link, doi = None, None
            for ext in (work.get('external-ids') or {}).get('external-id', []):
                if ext.get('external-id-type', '').lower() == 'doi':
                    doi = ext.get('external-id-value')
                    link = f"https://doi.org/{doi}"
                    break
            if not link:
                link = (work.get('url') or {}).get('value')

            # Fallback for Authors
            if (not authors or authors == "N/A") and doi:
                cr_authors = get_authors_from_crossref(doi)
                if cr_authors: authors = cr_authors
            
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
        publications.sort(key=lambda x: x['year'], reverse=True)
        return publications

    except Exception as e:
        print(f"\nError: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("orcid_id")
    parser.add_argument("-o", "--output", default="data/publications.json")
    parser.add_argument("-hl", "--highlight", default="",
                        help="Canonical name(s) to bold, semicolon-separated. "
                             "Give ONE spelling per person (e.g. 'Dawid Zyla'); "
                             "initials, reversed order, and accents are matched automatically.")
    args = parser.parse_args()

    # Split by semicolon and strip whitespace
    hl_list = [h.strip() for h in args.highlight.split(';') if h.strip()]

    data = fetch_publications(args.orcid_id, hl_list)
    
    if data:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()