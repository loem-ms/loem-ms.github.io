# Design

The style is a simple, modern researcher/engineer site: content first, one column, quiet colors, monospace for
metadata. When unsure, leave it out.

## Principles

- **One column, one width.** Everything sits in `.wrap`, which is 820 px wide minus a 20 px gutter on each side.
  Long-form pages (notes, project stories) narrow to 720 px.
- **The home page is short.** It shows a few of everything and links to the full page. Don't grow it.
  Add to a full page (Publications, CV, Notes, Projects) instead.
- **Text over decoration.** No icons, illustrations or animation beyond small hover transitions. Images only
  where they carry content (a project cover, a figure, a demo).
- **Mono for metadata, sans for content.** Dates, venues, tags, buttons and section kickers use Space Mono.
  Titles and prose use Instrument Sans.
- **Light and dark from the same tokens.** Dark mode follows the system (`prefers-color-scheme`). There is no
  toggle. Every color must come from a token.
- **Works without JavaScript and at 390 px.** Filters enhance the page, and lists are complete without them.
  No horizontal scroll on phones: wide tables sit in `.table-wrap`, code blocks scroll on their own.

## Tokens (`assets/site.css`, `:root`)

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#fbfaf7` | `#141413` | page background (warm paper) |
| `--surface` | `#f3f1eb` | `#1c1c1a` | hover fill, inline code, thumbnails |
| `--ink` | `#201f1c` | `#ecebe6` | text, heading rules |
| `--ink-2` | `#3f3d38` | `#d2d0c9` | intro and deck text |
| `--muted` | `#6b6862` | `#a5a299` | secondary text (authors, summaries) |
| `--faint` | `#9e9a91` | `#75726b` | dates, kickers, tags |
| `--line` | `#e6e3dc` | `#2b2a27` | row separators, borders |
| `--accent` | `#2d5f8a` | `#84b4de` | links, buttons, emphasis underline |
| `--accent-line` | `#c6d6e4` | `#33506a` | button borders |
| `--award` / `--award-soft` | `#8a5a12` / `#f6ecd9` | `#e2b46a` / `#2c2416` | award badges |
| `--code-bg` / `--code-ink` | `#22211e` / `#f1efe9` | `#0e0e0d` / same | code blocks |

`projects/style.css` adds `--ok` / `--ok-line` (green) for the "Active" stage.

## Type

| Element | Font | Size |
|---|---|---|
| Home name (`.intro-name`) | Instrument Sans 600, tracking −0.04em | clamp(40px, 7vw, 60px) |
| Page title (`.page-head h1`) | Instrument Sans 600, tracking −0.035em | clamp(34px, 6vw, 50px) |
| Section heading (`.block-head h2`) | Instrument Sans 600 | 22px |
| Row title (`.row-title`) | Instrument Sans 600 | 15.5px |
| Body / prose | Instrument Sans 400 | 16px / 17px (phone 15.5 / 16) |
| Metadata, buttons, kickers | Space Mono | 10–11.5px; kickers uppercase, tracking 0.14em |
| Khmer | Noto Sans Khmer (fallback in `--sans`) | — |
| Japanese | system (Hiragino Sans) via `--sans` | — |

Fonts load from Google Fonts in `sitekit.fonts()`.

## Components (class names in `assets/site.css`)

- **Top bar** `.topbar`: sticky, translucent, with the wordmark, `.topnav` (the current page has
  `aria-current="page"`) and an optional `.lang-switch`. On phones the nav wraps to a scrollable second row.
- **Page head** `.page-head`: `.kicker`, `h1`, then `.deck`.
- **Section** `.block` + `.block-head`: an `h2`, an optional `.count` and an optional `.more` link
  ("All 26 →") on the right, over a 1 px ink rule.
- **Row** `.row`: a 120 px `.row-side` (mono date or venue) beside the body (`.row-title`, `.row-sub`). It
  stacks on phones. Used for news, publications, notes, CV entries and talks; the CV widens the side to 150 px.
- **Publication** `.row.pub`: side = `venue_short` (bold) + year; body = title (linked to the first link),
  `.pub-authors` (owner's name in `<b>`), `.pub-venue` (italic; skipped when it equals `venue_short`), and
  `.links` with an optional `.badge` for an award.
- **Links and buttons** `.links a`, `.btn`: small mono outlined buttons in the accent color, filled on hover.
  External links get `target="_blank" rel="noopener"`; social buttons end with ↗.
- **Chips** `.chip`: rounded outlines for interests. **Filter chips** `.filter-chips button[aria-pressed]`
  are filled ink when active.
- **Project row** (home) `.proj-row`: a 16:9 thumbnail beside the title, summary and stage.
- **Project card and page** (`projects/style.css`): `.project-card`, `.stage`, `.facts` (a grid of key
  numbers), `.project-links`, `.project-hero`.
- **Prose** `.prose`: h2/h3, lists, blockquote (accent rule), inline code, dark code blocks, `.table-wrap`
  tables with mono headers, `figure` / `figure.phone` (320 px, for portrait media) with `figcaption`.

## Responsive

- ≤ 720 px: project cards stack (cover first), and the notes' editorial block stacks.
- ≤ 640 px: rows and news stack; the nav moves to a second row; type steps down; facts become two columns.

## Accessibility

- Skip link to `#main`, one `h1` per page, and `aria-current` on the active nav item and language.
- Every `<img>` has `alt`: descriptive for content images, `alt=""` for decorative thumbnails.
  `check_site.py` enforces that the attribute is there.
- Filter buttons use `aria-pressed`, and the result counts are `aria-live`.

## Don't

- Hard-code colors, or add a second accent color.
- Add a component that only one page uses when an existing one fits. Prefer `.row`, `.block` and `.links`.
- Put long lists on the home page, or add sections there without a decision entry.
- Add web fonts, icon fonts, CSS frameworks or JavaScript libraries.
