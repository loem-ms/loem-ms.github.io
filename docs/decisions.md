# Decisions

Newest first. Add an entry when you change the structure, the design or a rule: the date, the decision, and why.
Superseded entries stay, marked as such.

## 2026-11-20 — Agent docs, skills and a link check

- `AGENTS.md` (with `CLAUDE.md` importing it), `docs/`, and `.claude/skills/` (`update-site-data`,
  `add-project`, `add-note`, `ship-site-change`) describe how to maintain the site, so an AI agent can make
  routine updates safely.
- `make setup / build / check / serve`. `scripts/check_site.py` fails on broken internal links, missing titles
  or descriptions, and `<img>` without `alt`.
- Why: the owner wants to hand updates to an agent later. The rules make the agent edit `content/`, check its
  work and go through a PR.

## 2026-11-20 — Redesign: short home page, full pages, one layout (PR #6)

- The home page shows the intro, 5 news items, selected publications (`selected: true`), projects and the
  3 latest notes. The full lists moved to `/publications/` (filters, search, grouped by year) and `/cv/`
  (experience, education, talks, awards).
  Why: the publication list keeps growing and buried everything below it.
- The home page's data moved from a JavaScript `SITE` object in `index.html` to `content/site/*.yaml`.
  `build_site.py` writes static HTML.
  Why: several pages share the data, and static HTML needs no JavaScript to show content and is indexable.
- One shared shell (`sitekit.py`) and stylesheet (`assets/site.css`) for every page, Notes and Projects included.
  Notes and Projects lost their own headers. Why: one navigation and one look across the site.
- Dark mode follows the system, with no toggle. Why: modern and free with tokens, and a toggle adds state and JS.
- News is written by hand in `news.yaml`, not generated. Why: publications only have a year, so a feed built
  from them would sort badly, and news can also cover jobs and talks.
- Award badges sit on 4 publications, matched to the awards list by their paper links.
- GitHub (github.com/loem-ms) was added to the social links.
- Kept from the old site: colors, Instrument Sans + Space Mono, the warm background, every content item.

## 2026-11-20 — Projects section (PR #5)

- Projects are built like Notes: `content/projects/<slug>/` (meta.yaml, en.md, ja.md, assets/) →
  `build_projects.py` → `projects/`. Copy `_template/` to add one.
  Why: the owner wants future side projects in the same template, and Notes had a proven pattern.
- A project's assets are published once at `/projects/<slug>/assets/`, shared by its languages, so large
  media is not duplicated.
- Project pages state only public facts: the published article, README, technical report and model cards.
  Unreleased work is not mentioned.
- Japanese strings in YAML go on one line, because a folded `>-` block puts spaces between the lines.
- The Notes workflow became "Build site", which runs every builder in one job, so two jobs never race to push.
  It also stages new files before checking for changes.

## Before 2026-11

- The home page was hand-written HTML with a `SITE` object. Notes were generated from `content/notes/` by
  `build_notes.py`, through PRs (superseded in part by the redesign above).

## Known issues

- The talk "A Journey of Generative Model" (Jul 2024) links to `https://loem-ms.github.io/generative-model`,
  which returns 404 (it already did before the redesign). `check_site.py` reports it. Ask the owner where it
  should point.
