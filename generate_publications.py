import requests
import json
import argparse
import sys
import unicodedata
import re

# --- Helper Functions ---

def normalize_to_tokens(text):
    """
    Converts text into a set of normalized word tokens.
    "Zyla, Dawid S." -> {'zyla', 'dawid', 's'}
    """
    if not text:
        return set()
    
    # 1. Lowercase
    text = text.lower()
    
    # 2. Decompose accents (Ż -> Z)
    text = unicodedata.normalize('NFKD', text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    
    # 3. Replace punctuation with SPACE (preserves "D.S." -> "d s")
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 4. Split into set of unique words
    return set(text.split())

def is_match(highlight_input, full_author_string):
    """
    Determines if a highlight term matches an author using strict token subsets.
    Prevents "D" from matching "Dawid".
    """
    if not highlight_input or not full_author_string:
        return False

    # Get tokens for both the search term and the author string
    # e.g. Input: "Dawid Zyla" -> {'dawid', 'zyla'}
    # e.g. Author: "Dawid S. Zyla" -> {'dawid', 's', 'zyla'}
    input_tokens = normalize_to_tokens(highlight_input)
    author_tokens = normalize_to_tokens(full_author_string)
    
    if not input_tokens:
        return False

    # CHECK: Are ALL input words present in the author's name?
    # This allows "Dawid Zyla" to match "Dawid S. Zyla" (Subset is True)
    # This prevents "Zyla D" from matching "Dawid Zyla" ('d' is not in {'dawid', 'zyla'})
    return input_tokens.issubset(author_tokens)

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
            found_highlights = []
            if highlight_list and authors != "N/A":
                for term in highlight_list:
                    # Check each user-provided variation against the author list
                    if is_match(term, authors):
                        found_highlights.append(term)

            if title and year:
                entry = {
                    "title": title,
                    "authors": authors,
                    "journal": journal,
                    "year": int(year),
                    "highlight": list(set(found_highlights)) # Dedup matches
                }
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
    parser.add_argument("-o", "--output", default="publications.json")
    parser.add_argument("-hl", "--highlight", default="", help="Semicolon separated list (e.g. 'Name One; Name Two')")
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