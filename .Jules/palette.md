## 2024-05-23 - Skip to Content Link
**Learning:** Many "modern" minimal themes neglect basic keyboard accessibility like skip links, assuming the layout is simple enough. However, this forces keyboard users to tab through navigation on every page.
**Action:** Always check for `skip-link` in `baseof.html` or equivalent global layout template as the first step in accessibility review.

## 2024-05-23 - CSS Variables for Accessibility
**Learning:** Using existing CSS variables (like `--highlight-color`) ensures new accessibility features blend with the theme, but fallback values (e.g., `#fff` text) are crucial in case variables are undefined or provide poor contrast.
**Action:** Always define high-contrast fallbacks for accessibility-critical elements like focus rings or skip links.
