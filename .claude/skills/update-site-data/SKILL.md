---
name: update-site-data
description: Update the YAML data behind loem-ms.github.io's home, Publications and CV pages — add a publication, news item, talk or award; change the selected publications; update a job, education, roles, intro or social links. Use when the owner says things like "add my new paper", "add this talk", "I got an award", "I changed jobs", "update the news", "feature this paper on the home page".
---

# Update site data

All of it lives in `content/site/`. Formats and templates are in `docs/content-guide.md`; follow them exactly.

## Gather the facts first

Ask the owner, or read the source they point to (an arXiv page, a proceedings page, an event page), for every
field you need. Never guess a venue, a page range, a coauthor's spelling or a date. If a field is unknown, leave
it out (pages, location) or ask (title, authors, venue, year).

## What to edit

| Request | Files |
|---|---|
| New paper or preprint | `publications.yaml` (new item at the top of `items:`); usually also a `news.yaml` item; `selected: true` if the owner wants it on the home page (then consider unselecting one, keeping about 5) |
| Preprint accepted at a venue | add the venue version as a new item, keep the preprint, move `selected` to the new item, add a news item |
| Paper award | the item's `award:` field, plus a line in `awards.yaml` linking the paper |
| Talk | `talks.yaml` (top); a news item if it is recent |
| Award or scholarship | `awards.yaml` (top); a news item if it is recent |
| New job | `cv.yaml` experience (top; close the previous period), `profile.yaml` roles, a news item |
| Degree | `cv.yaml` education |
| Intro, interests, links | `profile.yaml` |
| News only | `news.yaml` (top); one line of Markdown, linking the thing itself |

## Rules

- Keep each list newest first. Within a year, publications keep the written order.
- `venue_short` reuses existing tags when the venue is the same (`NLP` for 言語処理学会年次大会, `YANS`, `MIRU`,
  `COLM`, `ACL Findings`, …). Look at the file before inventing a new one.
- Link labels are lower case: `paper`, `arXiv`, `code`, `slides`, `video`, `project`.
- Author names exactly as in the paper. "Mengsay Loem" is bolded automatically.
- Internal links in news use absolute paths (`/projects/en/<slug>/`, `/notes/`).
- Don't edit `index.html`, `publications/` or `cv/`: they are generated.

## Then

Run the `ship-site-change` skill: build, check, preview the home page and the page you changed, then open a PR.
