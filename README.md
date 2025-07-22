## Generating Publications Automatically

You can generate a `publications.json` file from an ORCID iD using the provided Python script:

1. Make sure you have Python 3 and `requests` installed:
   ```bash
   pip install requests
   ```

2. Run the script with your ORCID iD:
   ```bash
   python generate_publications.py <your_orcid_id>
   ```
   Example:
   ```bash
   python generate_publications.py 0000-0002-1825-0097
   ```
   This will create or update `data/publications.json` with your publications.

3. Optional: Highlight specific author names in the output:
   ```bash
   python generate_publications.py <your_orcid_id> --highlight "Alice Smith,Bob Johnson"
   ```

## Example Resources

See the `content/resources/` folder for template resources:

- `lab-safety.md`: Lab safety guidelines template
- `equipment-list.md`: Example equipment list template

Add your own Markdown files to this folder to share protocols, guidelines, or other resources with your lab.

# Scientific Website Template for Biochemistry Labs

This repository contains a minimal Hugo template for scientific labs, designed for easy setup and customization.

## Features

- Custom theme `SciLab` with a clean, responsive layout
- Pre-configured sections: Research, Team, Publications, Resources, Lab Fun, Philosophy, Protocols, News
- Shortcodes for news, publications, and carousel
- Example content for team members, publications, and protocols

## Prerequisites

- [Install Hugo](https://gohugo.io/getting-started/installing/)

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/scientific_website_template.git
   cd scientific_website_template
   ```

2. **Run the site locally:**
   ```bash
   hugo server -D
   ```
   Visit `http://localhost:1313` in your browser.

3. **Customize your content:**
   - Edit team members in `content/team/`
   - Add publications in `data/publications.json` and `content/publications/`
   - Add protocols in `content/protocols/`
   - Add news posts in `content/news/`
   - Update images in `static/images/`

4. **Customize styles:**
   - Edit CSS in `static/css/news.css` and other files in `static/css/`

5. **Shortcodes:**
   - Use shortcodes in your Markdown files: `{{< news >}}`, `{{< publications >}}`, `{{< carousel >}}`

## How to Add/Remove Team Members

- Add a new Markdown file in `content/team/` (see examples in that folder)
- Remove a member by deleting their file

## How to Add Publications

- Add entries to `data/publications.json` (see example format)
- Optionally, add Markdown files in `content/publications/` for detailed pages

## How to Add Protocols

- Add Markdown files in `content/protocols/`

## How to Add News Posts

- Add Markdown files in `content/news/`

## Customization

- Edit layouts in `layouts/` and `themes/scilab/layouts/` as needed
- Edit shortcodes in `layouts/shortcodes/`

## Cleaning Up

- Duplicated CSS/JS files have been removed; only use files in `static/`
- Unused archetypes and empty folders have been removed

## Deploying

- Build the site for production:
  ```bash
  hugo
  ```
- The output will be in the `public/` folder

---

For more details, see the Hugo documentation: https://gohugo.io/documentation/
