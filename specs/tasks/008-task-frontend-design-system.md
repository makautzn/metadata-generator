# 008 — Frontend Design System (Rheinpfalz-Inspired)

## Description

Establish the visual design system for the PoC web application, inspired by the clean editorial aesthetic of *DIE RHEINPFALZ*. This includes design tokens (colors, typography, spacing), base component styles, and reusable UI primitives (button, card, badge/chip, layout containers). Covers requirements WEB-15, WEB-16, WEB-17.

## Dependencies

- **002** — Frontend web app scaffolding

## Technical Requirements

### Design Tokens

Define in `styles/theme.ts` and map to CSS custom properties:

- **Color palette**: Neutral, editorial tones — white/off-white backgrounds, dark gray text, a single accent color (inspired by Rheinpfalz brand — e.g., a warm red or deep blue). Include success, error, and warning semantic colors.
- **Typography**: Clean sans-serif stack (Inter, system-ui, or similar). Define heading scales (H1–H4), body text, caption, and label sizes with appropriate line heights.
- **Spacing**: Consistent spacing scale (4px base: 4, 8, 12, 16, 24, 32, 48, 64).
- **Border radius**: Subtle rounding (4px for cards, 16px for badges/chips).
- **Shadows**: Minimal — light card shadow for tile elevation.

### Base Components

Create reusable UI components in `components/ui/`:

- **Button**: Primary, secondary, ghost variants. Support disabled state and loading spinner.
- **Card**: Content container with optional header, body, and footer sections. Used as the tile wrapper.
- **Badge / Chip**: Small labeled element for displaying keywords/tags. Support color variants.
- **Container**: Max-width centered layout wrapper with responsive padding.
- **Header**: Application header bar with logo/title area.

### Layout

- **Page Layout**: Single-column centered layout with max-width constraint (1200px recommended)
- **Grid**: CSS Grid or Flexbox-based responsive grid for tile view (auto-fill columns, minimum 320px per tile)
- **Responsive**: Must work on desktop screens (≥ 1024px); tablet/mobile is not required for PoC but should not break

### Global Styles

- CSS reset / normalize
- Global font family and base font size
- Focus styles for accessibility (keyboard navigation)
- Smooth transitions for interactive elements

## Acceptance Criteria

- [x] Design tokens are defined and accessible via CSS custom properties
- [x] All base components render correctly in isolation
- [x] Color palette conveys a neutral, editorial tone (not flashy or playful)
- [x] Typography is clean and readable with proper heading hierarchy
- [x] Card component can contain arbitrary content with consistent padding and shadow
- [x] Badge/Chip component renders keyword-style labels
- [x] Layout is centered, max-width constrained, and responsive on desktop
- [x] Focus styles are visible for keyboard navigation
- [x] Components use only design tokens — no hard-coded color/spacing values

## Testing Requirements

- Unit test: each base component renders without errors
- Unit test: Button renders all variants (primary, secondary, ghost, disabled, loading)
- Unit test: Card renders with header, body, and footer slots
- Unit test: Badge renders with text content
- Snapshot test: each component matches expected visual structure
- Accessibility: components have proper ARIA roles and labels
- Coverage: ≥ 85%

---

## E2E Testing Findings

The following issue was discovered and resolved during end-to-end testing:

| # | Finding | Root Cause | Resolution |
|---|---------|------------|------------|
| 1 | **Dark mode variants causing unintended styling** | The main page layout used Tailwind `dark:` variants (e.g., `dark:bg-neutral-900`, `dark:border-neutral-700`), which could activate depending on the user's OS theme preference. This conflicted with the intended clean, light editorial aesthetic inspired by *DIE RHEINPFALZ*. | Removed all `dark:` Tailwind variants from `page.tsx`. Replaced with explicit light-only values: `bg-[#f9fafb]` for page background, `border-[#e5e7eb]` for borders, and `text-[#9ca3af]` for muted text. The design system now enforces a consistent light editorial appearance regardless of the user's system theme. |
