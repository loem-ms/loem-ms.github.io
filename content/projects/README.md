# Projects

Source of https://loem-ms.github.io/projects/. `scripts/build_projects.py` turns this folder into `projects/`;
the GitHub Action "Build site" runs it on every push to `gh-pages` that touches `content/`, so only this folder
needs to be edited. The home page's Projects section reads `projects/manifest.json`, so a new project shows up
there too.

## Add a project

1. Copy `_template/` to `content/projects/<slug>/` (lowercase words joined by `-`, e.g. `samdei-type`).
2. Edit `meta.yaml`: title, summary, stage, dates, tags, and optionally cover, facts and links.
3. Write the story in `en.md` and `ja.md` (Markdown; raw HTML such as `<figure>` is allowed). Put images in
   `assets/` and link them as `assets/<file>`. A project can have only one language: list just that one in
   `languages`.
4. Set `status: published`, then build and preview locally:

   ```bash
   pip install -r requirements-notes.txt
   python scripts/build_projects.py
   python -m http.server 8000   # http://localhost:8000/projects/
   ```

5. Commit `content/projects/<slug>/` (and the generated `projects/`, or let the Action build it) and push.

## Files

| Path | What it is |
|---|---|
| `site.yaml` | Section texts per language, and the labels of each `stage` |
| `<slug>/meta.yaml` | One project's metadata (fields explained in `_template/meta.yaml`) |
| `<slug>/<lang>.md` | The story, one file per language |
| `<slug>/assets/` | Images and other files, published once at `/projects/<slug>/assets/` |
| `../../projects/style.css` | The section's stylesheet (hand-written; the builder keeps it) |

Generated pages: `/projects/` (list), `/projects/<lang>/`, `/projects/<lang>/<slug>/`, and `/projects/<slug>/`,
which redirects to the default language.
