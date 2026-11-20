---
name: ship-site-change
description: Build, check, preview and ship any change to loem-ms.github.io through a pull request, then verify it live after the owner merges. Use at the end of every site change (content, design or code), or when asked to "publish", "deploy", "open a PR" or "check the site".
---

# Ship a site change

Every change to this site ends here. Read `AGENTS.md` first if you haven't.

## 1. Branch

```bash
git switch gh-pages && git pull --ff-only
git switch -c <short-topic>      # e.g. news-2026-12, add-pub-emnlp, project-<slug>
```

## 2. Build and check

```bash
make setup    # only if .venv is missing
make check    # builds notes → projects → site, then runs scripts/check_site.py
```

- Builder errors name the file and field. Fix the content, not the builder, unless the builder is wrong.
- `check_site.py` must report 0 problems, apart from issues already listed under "Known issues" in
  `docs/decisions.md`. Mention those to the owner rather than hiding them.
- `git status` should list only the content you changed and the pages generated from it. If unrelated pages
  changed, find out why before going on.

## 3. Look at it

Start the "site" preview (`.claude/launch.json`) or run `make serve`, then open each page you changed:

- desktop width, and phone width (390 px): `document.documentElement.scrollWidth` must not exceed the
  viewport width;
- dark mode (emulate `prefers-color-scheme: dark`);
- every link you added opens the right place, and every image shows.

If the browser pane is hidden, scrolling screenshots come out blank. Set a tall viewport (e.g. 1100×2600) and
take one screenshot of the whole page instead. Reset the viewport afterwards.

## 4. Commit and open the PR

- Commit the content and the generated pages together, with a message that says what changed for a reader of
  the site.
- Push the branch and open a PR into `gh-pages`. In the description, list the pages that changed, any choice the
  owner should confirm (wording, which items are selected, facts you couldn't verify), and what you checked.
- If the change alters structure, design or rules, add an entry to `docs/decisions.md` in the same PR.

## 5. Merge only on the owner's word

Never merge on your own. When the owner says to merge:

```bash
gh pr merge <n> --repo loem-ms/loem-ms.github.io --merge
```

## 6. Verify after the merge

- `gh run list --repo loem-ms/loem-ms.github.io --limit 3`: "Build site" and "pages build and deployment" for
  the merge commit should both succeed. "Build site" should say the pages are already up to date. If it
  committed a rebuild instead, compare that commit with your local build.
- Each changed URL returns 200 on https://loem-ms.github.io/ and shows the change. An unknown path should still
  return 404 with the site's 404 page.
- `git switch gh-pages && git pull --ff-only` to leave the local clone up to date.
