---
name: add-project
description: Add or update a side-project page on loem-ms.github.io (/projects/), in English and optionally Japanese, from the project's public material. Use when the owner says "add my project X to the site", "write a project page for X", "update the Samdei Type page", or a project gets a new release.
---

# Add or update a project page

Read `content/projects/README.md` (steps), `content/projects/_template/meta.yaml` (fields) and the Projects
section of `docs/content-guide.md` (story structure). `content/projects/samdei-type/` is the reference example.

## 1. Collect the public facts

- Ask the owner where the public material is: the repository README, the release article, the paper or report,
  the model or dataset cards, the package page. Read all of it.
- Use only what is public there, or what the owner tells you. Write down where each number comes from (keep the
  list in your PR description, not on the page).
- Leave out anything unreleased, private or internal (closed models, private repositories, prototypes,
  planned work), even if the owner's other folders mention it. When unsure, ask.

## 2. Create the folder

```bash
cp -R content/projects/_template content/projects/<slug>
```

- `slug`: lowercase words joined by `-`, matching the folder.
- `status: draft` until the owner approves the text; set it to `published` for the PR they will merge.
- `stage`: `active`, `released`, `paused` or `archived`. `started` / `ended` as `YYYY-MM`. Ask if unknown.
- `summary`: one or two sentences, saying what it is and for whom.
- `facts`: 3–4 sourced numbers. `links`: code → models/data → paper → article → package.
- `cover`: a 16:9 image under `assets/` (JPEG around 1600×900, under 200 KB: `sips -s format jpeg -s formatOptions 82 in.png --out assets/cover.jpg`).
  If the project has no cover, leave the field out.
- Japanese strings on one line (a folded `>-` block inserts spaces).

## 3. Write the story

`en.md`: the problem → the idea → how it works → results (a table against the baselines) → what is released (a
table with licenses) → limitations → optional name or citation. First person, plain, every number sourced. Images
go in `assets/` and are linked as `assets/<file>`. Use `<figure class="phone">` for portrait demos.

`ja.md` (if the owner wants Japanese): natural です・ます Japanese, same structure and facts.

## 4. Update related places

- A `news.yaml` item for a new release ("Released [Name](/projects/en/<slug>/), …").
- The home page and `/projects/` pick the project up from the manifest; nothing else to edit.

## 5. Ship

Run `ship-site-change`. On the preview, check the list card, the page in both languages, the facts grid at
phone width, and the cover in dark mode.
