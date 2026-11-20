# Architecture

A static site with no framework and no JavaScript build step. A few Python scripts turn YAML and Markdown in
`content/` into plain HTML files, which are committed. GitHub Pages serves the `gh-pages` branch root as it is
(the "legacy" build, with `.nojekyll`), so every committed file is public at its path.

## Layout

```
content/                      ← edit here
  README.md                   which file controls what
  site/                       profile, news, publications, talks, awards, cv  (YAML)
  notes/YYYY/MM/<slug>/       meta.yaml, en.md, ja.md, assets/
  projects/                   site.yaml, _template/, <slug>/ (meta.yaml, en.md, ja.md, assets/)
scripts/
  sitekit.py                  shared page shell: <head>, top bar (NAV), footer, helpers
  build_notes.py              content/notes    → notes/
  build_projects.py           content/projects → projects/
  build_site.py               content/site + both manifests → index.html, publications/, cv/, 404.html
  check_site.py               links, titles, descriptions, alt text in the generated pages
assets/site.css               shared styles (hand-written)
notes/style.css               Notes styles (hand-written; the builder keeps it)
projects/style.css            Projects styles (hand-written; the builder keeps it)
index.html, publications/, cv/, 404.html, notes/**, projects/**   ← generated, committed
docs/                         these notes
.claude/skills/               task checklists for AI agents
.github/workflows/build-site.yml
```

## Build

| Step | Reads | Writes |
|---|---|---|
| `build_notes.py` | `content/notes/site.yaml`, every `meta.yaml` with `status: published` | `notes/` (wipes its subfolders, keeps `style.css`), `notes/manifest.json` |
| `build_projects.py` | `content/projects/site.yaml`, `*/meta.yaml` (skips `_*/` and drafts) | `projects/` (same), `projects/manifest.json`, `projects/<slug>/assets/` |
| `build_site.py` | `content/site/*.yaml`, `notes/manifest.json`, `projects/manifest.json` | `index.html`, `publications/index.html`, `cv/index.html`, `404.html` |

The order matters: the home page lists the latest notes and the projects from the two manifests. `make build`
runs the three steps in order. The builders check their input and stop with an error naming the file, for
example a missing field, an unknown type or stage, a missing `<lang>.md`, or a cover outside `assets/`.

Dependencies are `mistune` 3 and `PyYAML` 6 (`requirements-notes.txt`; the name is historical). The scripts run
on Python 3.9 (local `.venv`) and 3.12 (the Action).

## URLs

| URL | Source |
|---|---|
| `/` | home: intro, news, selected publications, projects, recent notes |
| `/publications/` | every publication, grouped by year; `?type=journal` etc. preselects a filter |
| `/cv/` | experience, education, talks, awards |
| `/notes/`, `/notes/<lang>/`, `/notes/<lang>/<slug>/` | notes list and pages; `/notes/<slug>/` redirects to the default language |
| `/projects/`, `/projects/<lang>/`, `/projects/<lang>/<slug>/` | projects list and pages; `/projects/<slug>/` redirects; `/projects/<slug>/assets/` holds the images, once for all languages |
| `/404.html` | GitHub Pages serves it for unknown paths |

Links between pages are absolute paths (`/publications/`), which works because this is a user site at the
domain root.

## Page shell

`sitekit.document()` writes every page: the head (title, description, canonical, Open Graph, fonts,
`/assets/site.css` plus the section's CSS), the sticky top bar (`NAV`: Publications · Projects · Notes · CV,
plus an EN / 日本語 switch when the page has more than one language), `<main class="wrap">`, and the footer
(built from `profile.yaml`). To add a top-level section, add it to `NAV` and give its builder `active="<key>"`.

JavaScript is used for three things only, all inline and optional: the publication filters, the notes filters,
and the "copy email" button. Without JavaScript, every item is still listed.

## Deploy

1. Branch → change `content/` (and code) → `make check` → commit the content and the generated pages → PR into `gh-pages`.
2. After the merge, the Action "Build site" runs on pushes that touch `content/**`, `scripts/**`, the requirements
   or the workflow. It runs the three builders and commits any difference as `Build site [skip ci]`. When the
   committed pages are already up to date, it commits nothing.
3. GitHub's "pages build and deployment" publishes the branch, usually within a minute or two.

## Local folder

The clone lives at `~/Personal/loem-ms.github.io`. `make setup` creates `.venv` (git-ignored), `make serve`
previews at http://localhost:8765/, and `.claude/launch.json` gives the same server to Claude Code's preview.
