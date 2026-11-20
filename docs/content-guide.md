# Content guide

How to write and format each kind of content. Each section ends with a template to copy.

## Voice

- First person singular ("I built…"), plain and concrete. Short sentences. No hype ("revolutionary",
  "state-of-the-art"), no exclamation marks.
- Every number, date, venue and name must come from a public source or from the owner. Never estimate.
  If a fact is missing, leave the field out and ask.
- English is the default. Notes and projects may also have Japanese (`ja.md`). Write the Japanese text as natural
  Japanese (です・ます), not word for word.
- Dates: `YYYY-MM` in YAML, shown as "Nov 2026". Talks and awards keep free text ("Nov 2026", "2022–24").
- Names: the owner is "Mengsay Loem" (bolded automatically in author lists). Keep author lists exactly as in
  the paper, in its language (Japanese names stay in Japanese for Japanese papers).

## News (`content/site/news.yaml`)

One line per item, newest first, past tense or noun phrase. Link the thing itself (paper, project page, event).
The home page shows the first `home.news` items (5), and older items stay in the file.

```yaml
- date: 2026-12
  text: New paper at [VENUE 2026](https://...): *Short title*.
```

## Publications (`content/site/publications.yaml`)

Add new items at the top of `items:` (the list is sorted by year; within a year, the order is as written).

| Field | Rule |
|---|---|
| `title` | exactly as published |
| `authors` | comma-separated, as in the paper; "and" if the paper uses it |
| `venue` | full venue line: name, volume and pages or location when known |
| `venue_short` | the tag shown next to the year: `arXiv`, `JNLP`, `COLM`, `ACL Findings`, `EMNLP`, `NLP` (言語処理学会年次大会), `YANS`, `MIRU`, … without the year |
| `year` | number |
| `type` | `journal`, `international`, `preprint` or `domestic` |
| `selected` | `true` to show it on the home page; keep about 5 selected |
| `award` | optional, e.g. `"Best Paper Award"`; also add it to `awards.yaml` |
| `links` | `[{label: "paper", url: "..."}]`; labels in lower case (`paper`, `arXiv`, `code`, `slides`); the first link is also the title's link |

When a preprint is published at a venue, add the venue version as a new item and keep the preprint. Move
`selected` to the venue version.

```yaml
  - title: "Paper Title"
    authors: "Mengsay Loem, Coauthor Name"
    venue: "Full Venue Name (ABBR 2026), City"
    venue_short: "ABBR"
    year: 2026
    type: international
    links: [{label: "paper", url: "https://..."}]
```

## Talks (`content/site/talks.yaml`) and awards (`content/site/awards.yaml`)

Newest first. In a talk's `venue`, put the kind first when it helps: "Invited Talk — Event", "Panel — Event".

```yaml
- date: "Dec 2026"
  title: "Talk title"
  venue: "Invited Talk — Event name, City"
  links: [{label: "slides", url: "https://..."}]
```

```yaml
- date: "2026"
  text: "Award name — Event or organization (Country)"
  links: [{label: "paper", url: "https://..."}]
```

## CV and profile (`content/site/cv.yaml`, `profile.yaml`)

- A new job goes at the top of `experience`. Close the previous one's period ("Jul 2026 —" → "Jul 2026 – Mar 2028").
- Update `profile.yaml` `roles` at the same time (current role first, then "formerly …").
- `intro` is one or two sentences of Markdown. `*word*` renders with the accent underline.

## Projects (`content/projects/<slug>/`)

Copy `_template/`. Fields are explained in `_template/meta.yaml`, and the steps are in
`content/projects/README.md`.

- `summary`: one or two sentences, saying what it is and for whom. It appears in lists, on the home page and in
  link previews.
- `facts`: 3–4 key numbers with short labels. Each one must appear in a public source.
- `links`: code, models/data, paper or report, article, package. Order them as a reader would use them.
- `cover`: 16:9 JPEG or PNG under `assets/`, about 1600×900 and ideally under 200 KB.
- Story (`en.md`), in this order: **the problem** (who has it, why existing tools fall short) → **the idea** →
  **how it works / training** → **results** (a table against the baselines) → **what is released** (a table with
  licenses) → **limitations** → optional name or citation. Use `<figure class="phone">` for portrait demos.
- Stage: `active` while working on it, `released` once the first public release is out, `paused` or `archived`
  later.

## Notes (`content/notes/YYYY/MM/<slug>/`)

Notes are paper-reading memos and research thoughts. Their process (GenAI-assisted drafts reviewed by the owner)
is described on `/notes/`. Only the owner decides to publish a note.

`meta.yaml` (required: `id`, `slug`, `published_at`, `status`, `type`, `languages`, `tags`, `title`, `summary`):

```yaml
id: my-note
slug: my-note
published_at: 2026-12-01
added_at: 2026-12-01T09:00:00Z     # sorts notes published on the same day
updated_at: null
status: published                  # anything else is not built
type: paper-note                   # paper-note needs the paper block below; or e.g. meta, idea
default_language: en
languages: [en, ja]
tags: [paper-reading, multilingual]
paper:
  title: "Paper title"
  authors: [First Author, Second Author]
  venue: Full venue name
  venue_short: ABBR
  year: 2026
  url: https://arxiv.org/abs/...
kicker: {en: Paper note, ja: Paper note}
title: {en: "Question-style title?", ja: "日本語のタイトル"}
summary:
  en: >-
    One or two sentences.
  ja: 日本語の要約は1行で書く。
```

Body sections used so far: `## The question`, `## What they find`, `## Our take`, and ideas at the end. Raw HTML is
escaped in notes, so use Markdown only.
