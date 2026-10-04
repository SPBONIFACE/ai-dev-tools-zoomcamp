# Design System

## Aesthetic & Tone
TableHop is a **crisp host-stand console**: calm, dense and typographic, closer to a well-made operations tool than a marketing dashboard. Warmth comes from the linen canvas and a single terracotta accent, not from decoration.

Avoid: serif display headings, letter-spaced all-caps labels, pill badges on every value, icons in tinted boxes, soft floating cards, decorative animation, filler captions.

## Tokens
Defined once in `frontend/src/index.css` (`@theme`) and used as Tailwind classes (`bg-canvas`, `text-ink-2`, `border-line`, …).

| Token | Value | Use |
|---|---|---|
| `canvas` | `#F7F5F0` | Page background |
| `header` | `#EFE9DF` | Top bar (deeper linen) |
| `surface` / `subtle` | `#FFFFFF` / `#FAF8F4` | Panels / table headers, footers, hover rows |
| `line` / `line-strong` | `#E7E2D9` / `#D6CFC3` | Hairline dividers / control borders |
| `ink` / `ink-2` / `ink-3` | `#1F1B16` / `#5F574C` / `#948B7E` | Primary / secondary / tertiary text |
| `accent` | `#B4531F` | Primary action, brand mark, focus, selection. Nothing else. |
| `waiting` | `#B7791F` | Status dot |
| `notified` | `#2F5E8C` | Status dot, guest "table ready" panel |
| `seated` | `#2F6B4B` | Status dot, open tables, exact-fit |
| `danger` | `#A23B32` | Overdue waits, destructive hovers, errors |

## Typography
- **Display:** Young Serif for the brand voice only: the wordmark, page title (30px) and panel titles (19px). Never for numbers: its old-style figures make 0 read as o.
- **Text:** IBM Plex Sans for everything else; IBM Plex Mono for phone numbers, clock, table codes and timestamps.
- **Scale:** stat values 36px/600, guest place in line 72px/600, body 14px, secondary 13px, meta 12px. Tighten tracking on 15px and up.
- **Numbers:** always `tabular-nums` (`.num`).
- **Case:** sentence case for all headings, labels and buttons. No all-caps.

## Components
- **Wordmark:** `Wordmark`: a round terracotta table with four ink chairs, then "Table" in ink and "Hop" in terracotta, set in Young Serif.
- **Panels:** `.panel`: white, 1px `line` border, 6px radius, no shadow. Shadows are reserved for overlays (dialogs, sheet).
- **Buttons:** 32px tall, 5px radius, 13px medium. `.btn-primary` (terracotta, one per view), `.btn-dark` (row-level commit such as Seat), `.btn-secondary` (bordered), `.btn-ghost` (toolbar, icon buttons).
- **Inputs:** `.field-input`, 36px tall, visible label above (`.field-label`), terracotta focus ring.
- **Status:** 6px colored dot plus plain text (`StatusLabel`). No pill badges.
- **Stats:** one divided strip (`KPICards`), label above a 28px number.
- **Tables:** 36px sentence-case header on `subtle`, 60px rows, hairline row dividers, actions right-aligned.
- **Overlays:** `Modal` (dialog or right sheet) with header, body and a `subtle` footer; Escape and backdrop click close it.
- **Icons:** lucide at 16px, stroke 1.75, only where they carry meaning (close, open guest view, reset).
- **Motion:** color transitions of 150ms and a 1px press on buttons. No pulsing or bouncing.
