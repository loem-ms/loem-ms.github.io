---
name: add-note
description: Add a note (paper-reading memo or research thought) to loem-ms.github.io/notes/ from a draft or discussion the owner provides, in English and Japanese. Use when the owner says "publish this note", "add a paper note on X", "turn this discussion into a note", or asks to fix an existing note.
---

# Add a note

Notes are the owner's own writing. They are GenAI-assisted drafts from the owner's discussions, which the owner
reviews before publishing (the process is described on `/notes/`). Work from the draft or discussion the owner
gives you. Don't write a note about a paper on your own initiative, and don't add claims about the paper that are
not in it.

## 1. Folder and metadata

`content/notes/YYYY/MM/<slug>/` with `meta.yaml`, `en.md`, `ja.md`. The template and required fields are in the
Notes section of `docs/content-guide.md`; `content/notes/2026/09/romanized-pretraining-transfer/` is a full example.

- `type: paper-note` needs the `paper` block: title, authors (a list), venue, `venue_short`, year and url, all
  copied from the paper's page.
- `published_at`: the publication date; `added_at`: the current UTC time (it orders notes published the same day).
- Start with `status: draft`. Set it to `published` only when the owner says the note can go out.
- Japanese `summary` on one line.

## 2. Body

- Sections used so far: `## The question`, `## What they find`, `## Our take`, then ideas or follow-ups.
- Markdown only: raw HTML is escaped in notes. Tables are supported.
- Keep the owner's interpretation and voice. Edit for clarity, not for opinion.
- `ja.md` covers the same content in natural Japanese (です・ます), not a word-for-word translation.

## 3. Ship

Run `ship-site-change`. Check `/notes/`, both language pages, the paper reference block, and that the home page's
"Recent notes" shows the new note.
