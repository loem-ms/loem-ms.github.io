# Working on this site (for AI agents and people)

This repository is Mengsay Loem's personal site, https://loem-ms.github.io/. GitHub Pages serves the `gh-pages`
branch as it is (no Jekyll, `.nojekyll`). Every page is generated from `content/` by the scripts in `scripts/`.

## Rules

1. **Edit `content/`, never the generated HTML.** `index.html`, `publications/`, `cv/`, `404.html`,
   `notes/**/index.html`, `projects/**/index.html` and the `manifest.json` files are overwritten on every build.
   Hand-written files outside `content/`: `assets/site.css`, `notes/style.css`, `projects/style.css`, `scripts/`.
2. **Build in order, then check:** `make check` runs the notes, projects and site builders in that order, then
   `scripts/check_site.py`. Fix every problem it reports, or tell the owner about it. Run `make setup` once first.
3. **Look at it.** Run `make serve` (or the "site" preview in `.claude/launch.json`) and check the pages you
   changed at desktop width, at phone width (about 390 px, with no horizontal scroll) and in dark mode.
4. **Ship through a pull request into `gh-pages`.** Use one branch per change. Commit the content and the
   regenerated pages together. Never push to `gh-pages` directly or merge without the owner's OK. After a merge,
   the Action "Build site" rebuilds the pages, and its output should match yours. Then confirm that the live
   pages load.
5. **Public facts only.** The repository is public, and so is everything in it (this file and `docs/` too).
   - Write only what is already public or what the owner gave you: papers, release articles, READMEs, model cards.
   - Never invent numbers, dates, affiliations or motives. If a fact is missing, ask.
   - Don't mention unreleased work, private repositories or anything the owner hasn't announced.
   - Don't add personal data beyond what `content/site/profile.yaml` already shows.
6. **Keep the design system.** Use the tokens and components in `assets/site.css`, and don't hard-code colors
   (dark mode depends on the tokens). Read `docs/design.md` before changing how anything looks.
7. **Record decisions.** When you change the structure, the design or a rule, add an entry to
   `docs/decisions.md`: the date, what changed, and why.

## Where things are

| Task | Start here |
|---|---|
| Update news, publications, talks, awards, CV, profile | `content/site/*.yaml`; skill `update-site-data` |
| Add a side project page | `content/projects/_template/`; skill `add-project` |
| Add a note | `content/notes/YYYY/MM/<slug>/`; skill `add-note` |
| Build, check, preview, open the PR, verify after merge | skill `ship-site-change` |
| How the build works | `docs/architecture.md` |
| Colors, type, components, layout rules | `docs/design.md` |
| Why things are the way they are | `docs/decisions.md` |
| Writing style and field formats | `docs/content-guide.md` |

The skills live in `.claude/skills/<name>/SKILL.md`. Other agents can read them as plain Markdown checklists.

## Commands

```bash
make setup   # once: .venv with mistune and PyYAML
make check   # build every page, then check links, titles and alt text
make serve   # http://localhost:8765/
```
