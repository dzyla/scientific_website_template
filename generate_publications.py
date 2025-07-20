import requests
import json
import argparse
import sys

def format_authors(contributors):
    """Formats a list of contributor objects into a single string."""
    if not contributors:
        return "N/A"
    
    author_names = []
    for contributor in contributors:
        # The 'credit-name' is the author's preferred public name
        if name := contributor.get('credit-name', {}).get('value'):
            author_names.append(name)
            
    return ", ".join(author_names)

def fetch_publications(orcid_id):
    """
    Fetches and formats publication data from the ORCID public API.
    """
    print(f"Fetching publications for ORCID iD: {orcid_id}...")
    API_URL = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/json"}

    try:
        # First, get the summary of all works to get their put-codes
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
        data = response.json()

        publications = []
        work_summaries = data.get('group', [])

        if not work_summaries:
            print("No public works found for this ORCID iD.")
            return []

        print(f"Found {len(work_summaries)} publication groups. Fetching details...")

        # Iterate through each work summary to get the full details
        for i, summary_group in enumerate(work_summaries):
            # The first item in 'work-summary' is usually the preferred version
            put_code = summary_group['work-summary'][0]['put-code']
            
            # Fetch the full details for this specific work
            work_url = f"https://pub.orcid.org/v3.0/{orcid_id}/work/{put_code}"
            work_response = requests.get(work_url, headers=headers)
            work_response.raise_for_status()
            work_data = work_response.json()

            # Extract the required fields safely, handling cases where parts of the data are None
            title = (work_data.get('title') or {}).get('title', {}).get('value', 'Title not available')
            journal = (work_data.get('journal-title') or {}).get('value', 'Journal not available')

            pub_date_obj = work_data.get('publication-date') or {}
            year = (pub_date_obj.get('year') or {}).get('value')

            contributors_obj = work_data.get('contributors') or {}
            authors = format_authors(contributors_obj.get('contributor', []))
            # Add to our list if we have a title and year
            if title and year:
                publications.append({
                    "title": title,
                    "authors": authors,
                    "journal": journal,
                    "year": int(year)
                })
            sys.stdout.write(f"\rProcessed {i+1}/{len(work_summaries)}")
            sys.stdout.flush()

        print("\nSuccessfully fetched all publication details.")
        # Sort publications by year, descending
        publications.sort(key=lambda p: p['year'], reverse=True)
        return publications

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.reason}")
        if e.response.status_code == 404:
            print(f"Could not find an ORCID record for iD: {orcid_id}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate a publications.json file from an ORCID iD.")
    parser.add_argument("orcid_id", help="The ORCID iD of the researcher (e.g., 0000-0002-1825-0097).")
    parser.add_argument("-o", "--output", default="publications.json", help="The name of the output JSON file.")
    args = parser.parse_args()

    publications_data = fetch_publications(args.orcid_id)

    if publications_data is not None:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(publications_data, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully created '{args.output}' with {len(publications_data)} entries.")

if __name__ == "__main__":
    main()