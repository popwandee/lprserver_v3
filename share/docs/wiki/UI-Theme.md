# UI Theme Guidelines

- Base: Bootstrap 5, responsive layout
- Typography: single family across server/edge pages
- Colors: shared palette (primary, secondary, success, danger, warning, info, light, dark)
- Components: navbar, cards, tables, buttons with consistent spacing
- Icons: pick a single set (e.g., Bootstrap Icons)
- Layout blocks: shared header/footer/alerts
- Accessibility: sufficient contrast, semantic HTML, keyboard navigation

Implementation steps:
1) Establish a base `base.html` and partial blocks
2) Refactor pages to extend shared layout
3) Add a small CSS layer for theme tokens