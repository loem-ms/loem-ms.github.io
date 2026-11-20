# Site content

For rules, design notes and agent checklists, see `../AGENTS.md`, `../docs/` and `../.claude/skills/`.

Everything on https://loem-ms.github.io/ is edited here, in YAML and Markdown. The scripts in `scripts/` turn it
into HTML. On every push to `gh-pages` that touches `content/` or `scripts/`, the GitHub Action "Build site"
rebuilds the pages and commits them. **Don't edit the generated HTML** (`index.html`, `publications/`, `cv/`,
`404.html`, `notes/**/index.html`, `projects/**/index.html`): it is overwritten.

| To change | Edit | Shows up on |
|---|---|---|
| Name, roles, intro, interests, social links | `site/profile.yaml` | Home, footer |
| News | `site/news.yaml` (newest first; the home page shows the first 5) | Home |
| Publications | `site/publications.yaml` (`selected: true` puts one on the home page) | Home, `/publications/` |
| Talks | `site/talks.yaml` | `/cv/` |
| Awards | `site/awards.yaml` | `/cv/` |
| Experience, education | `site/cv.yaml` | `/cv/` |
| Notes | `notes/` (one folder per note) | `/notes/`, Home (latest 3) |
| Projects | `projects/` (see `projects/README.md`) | `/projects/`, Home |

Styles: `assets/site.css` is shared by every page (colors, with a dark mode, the top bar, rows, prose).
`notes/style.css` and `projects/style.css` add their section's rules. The page shell (head, top bar, footer)
is `scripts/sitekit.py`; the top bar's links are its `NAV` list.

## Build and preview locally

```bash
make setup   # once
make check   # build every page, then check links
make serve   # http://localhost:8765/
```

The order matters: `build_site.py` reads `notes/manifest.json` and `projects/manifest.json` for the home page.
