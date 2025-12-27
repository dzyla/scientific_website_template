## 2024-05-22 - Skip to Content Implementation
**Learning:** Even if a theme has `baseof.html`, it might be missing standard accessibility features like "Skip to content". Adding this requires coordination between HTML (link + target ID) and CSS (visually hidden styles). Using `tabindex="-1"` on the target container is critical for programmatic focus to stick in some browsers.
**Action:** Always check `baseof.html` for `skip-link` presence. When adding, ensure the main container gets an ID and `tabindex="-1"`.
