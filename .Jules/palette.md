# Palette's Journal

## 2024-05-22 - Carousel Accessibility
**Learning:** The "Visual Floor" hero carousel was explicitly overriding Reduced Motion preferences (`data-animate="always"`) and leaving hidden images in the accessibility tree (`opacity: 0` but no `aria-hidden`).
**Action:** Always check `prefers-reduced-motion` before initializing autoplay components, and ensure visual visibility state matches accessibility tree state (`aria-hidden`).
