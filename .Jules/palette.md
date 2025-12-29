## 2025-02-21 - Carousel Accessibility & LCP
**Learning:** The custom carousel implementation used `opacity` for transitions but kept all slides in the accessibility tree, confusing screen readers. It also lazy-loaded the LCP image.
**Action:** When using opacity-based transitions, manually toggle `aria-hidden="true"` on non-active slides. Always eager-load the first slide in a hero carousel.
