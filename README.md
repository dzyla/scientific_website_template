# zylalab.org

Source for the [Zyla Lab](https://zylalab.org) website — Department of
Biochemistry and Molecular Genetics, University of Colorado Anschutz Medical
Campus.

Built with [Hugo](https://gohugo.io) and the in-repo `scilab` theme. Pushing to
`main` builds and deploys to GitHub Pages via `.github/workflows/hugo.yml`.

## Running locally

```bash
hugo server -D          # http://localhost:1313, -D includes drafts
hugo --gc --minify      # production build into public/
```

Hugo **extended** 0.154.1 is what CI uses; keep the local version in step with
`HUGO_VERSION` in the workflow.

## Where things live

| What | Where |
|---|---|
| Site-wide settings, menus, hero, contact details | `hugo.toml` |
| Page content | `content/` |
| Publications, research topics, open positions, alumni | `data/*.json`, `data/*.yaml` |
| Photos and figures | `assets/images/` (processed by Hugo) |
| Favicons, web manifest, self-hosted fonts | `static/` |
| Templates | `layouts/` (site) and `themes/scilab/layouts/` (theme) |
| Styles | `themes/scilab/assets/css/` — concatenated, minified, fingerprinted |
| Behaviour | `themes/scilab/assets/js/main.js` |

`layouts/` overrides `themes/scilab/layouts/` for the same path.

## Common tasks

**Add a news post** — create `content/news/<slug>.md` with `title`, `date` and
optional `tags`. It appears on the homepage widget (newest six) and on `/news/`.

**Add a team member** — create `content/team/<name>.md` with `title`, `role`,
`image`, optional `email`, and `type: "member"` (or `"pi"` for the lead card).
Ordering follows `weight`.

**Add a protocol** — create `content/protocols/<slug>.md`, then link it from the
`resources:` list in `content/resources/_index.md`. Protocols carry a
placeholder `date` and set `hide_date: true`; add `updated: YYYY-MM-DD` to show
a real revision date.

**Change the hero images** — edit `params.home.hero.carousel` in `hugo.toml`.
Every slide needs real `alt` text; it is what screen readers and image search
actually see.

## Publications

`data/publications.json` is generated from ORCID:

```bash
pip install requests
python3 generate_publications.py 0000-0001-8471-469X -hl "Dawid S. Zyla"
```

The script also:

- tags preprints (bioRxiv, SSRN, arXiv…) with `"preprint": true`, which the
  publications page renders as a separate section;
- drops preprints superseded by their published version, matching titles by
  word overlap so retitled manuscripts are still caught;
- rewrites every spelling of a tracked author to the one canonical form passed
  in `-hl`, so the list does not mix "Dawid Zyla", "Dawid S Zyla" and
  "Dawid S. Żyła".

To re-run just that post-processing over the existing file without hitting the
ORCID API:

```bash
python3 generate_publications.py --normalize data/publications.json \
  -hl "Dawid S. Zyla" -o data/publications.json
```

Per-entry escape hatches when the heuristics get it wrong: `"keep": true` pins a
preprint that would otherwise be dropped, `"superseded": true` forces one out.

## Conventions worth keeping

- **JSON-LD must be piped through `safeJS`.** Hugo treats `<script>` contents as
  a JS context, so a bare `jsonify` gets escaped twice and every string ends up
  wrapped in literal quotes. See `themes/scilab/layouts/partials/seo/`.
- **Accent colour must clear WCAG AA.** `params.highlightColor` (#8B6508) is
  5.3:1 on white. The dark theme lightens it to #D4AF37 and therefore overrides
  `--highlight-text` to a near-black — anything drawn on a gold fill must use
  that variable rather than a hardcoded `#fff`.
- **Fonts are self-hosted** in `static/fonts/` (SIL OFL, see `OFL.txt`). Do not
  reintroduce the Google Fonts `<link>`; it blocks rendering and leaks visitor
  IPs to a third party.
- **Nothing in `themes/scilab/content/`.** Theme content directories get merged
  into the site — that is how a set of lorem-ipsum demo posts ended up published
  and indexed at `/posts/`.
