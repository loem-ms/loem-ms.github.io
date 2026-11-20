#!/usr/bin/env python3
"""Check the generated pages: internal links and images resolve, every page has a title and a
description, every <img> has an alt attribute. Run after the builders (`make check` does both).

Exit code 1 if anything is broken. External links are not fetched; links to this site's own
domain (https://loem-ms.github.io/...) are checked as internal links.
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = "loem-ms.github.io"
SKIP_DIRS = {".git", ".venv", "content", "scripts", ".github", ".claude", "docs", "node_modules"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs = []; self.title = False; self.desc = False; self.no_alt = 0; self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title": self._in_title = True
        if tag == "meta" and a.get("name") == "description" and a.get("content"): self.desc = True
        if tag == "img" and "alt" not in a: self.no_alt += 1
        for key in ("href", "src"):
            if a.get(key) and not (tag == "link" and a.get("rel") in ("preconnect", "canonical", "alternate")):
                self.refs.append(a[key])

    def handle_data(self, data):
        if self._in_title and data.strip(): self.title = True

    def handle_endtag(self, tag):
        if tag == "title": self._in_title = False


def target(page: Path, ref: str):
    """The local file a link points to, or None when it is external or not a file link."""
    u = urlsplit(ref)
    if u.scheme in ("mailto", "tel", "data", "javascript"): return None
    if u.scheme in ("http", "https"):
        if u.netloc != SITE: return None
        path = u.path or "/"
    elif u.scheme or ref.startswith("#") or not u.path:
        return None
    else:
        path = u.path
    path = unquote(path)
    p = ROOT / path.lstrip("/") if path.startswith("/") else (page.parent / path)
    if path.endswith("/") or p.is_dir(): p = p / "index.html"
    return p


def main():
    pages = [p for p in ROOT.rglob("*.html") if not (set(p.relative_to(ROOT).parts) & SKIP_DIRS)]
    problems = []
    for page in sorted(pages):
        rel = page.relative_to(ROOT)
        parser = Page(); parser.feed(page.read_text(encoding="utf-8"))
        redirect = "http-equiv=\"refresh\"" in page.read_text(encoding="utf-8")
        if not redirect and not parser.title: problems.append(f"{rel}: no <title>")
        if not redirect and rel.name != "404.html" and not parser.desc: problems.append(f"{rel}: no meta description")
        if parser.no_alt: problems.append(f"{rel}: {parser.no_alt} <img> without alt")
        for ref in parser.refs:
            t = target(page, ref)
            if t is not None and not t.exists(): problems.append(f"{rel}: broken link {ref}")
    for line in problems: print(line)
    print(f"Checked {len(pages)} pages: {len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__": main()
