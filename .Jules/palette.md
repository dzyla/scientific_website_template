## 2024-01-01 - [Skip Link Absence]
**Learning:** Even with semantic HTML (`<header>`, `<main>`, `<nav>`), users relying on keyboards are forced to tab through the entire navigation menu on every page load if a "Skip to content" link is missing.
**Action:** Always check `baseof.html` for a skip link mechanism targeting the main content area (`id="main-content"`) and ensure the target element is programmatically focusable (`tabindex="-1"`).
