"""Shared page layout for every builder: head, top bar, footer and small helpers.

Used by build_site.py (home, publications, CV, 404), build_notes.py and build_projects.py,
so all pages share one header and /assets/site.css.
"""
from __future__ import annotations

import html, re
from functools import lru_cache
from pathlib import Path
import mistune, yaml

ROOT = Path(__file__).resolve().parents[1]
NAV = [("publications", "Publications", "/publications/"), ("projects", "Projects", "/projects/"),
       ("notes", "Notes", "/notes/"), ("cv", "CV", "/cv/")]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_yaml(path):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if data is None: raise ValueError(f"{path}: empty")
    return data


def esc(v): return html.escape(str(v), quote=True)


@lru_cache(maxsize=1)
def profile():
    return load_yaml(ROOT / "content" / "site" / "profile.yaml")


_md_inline = mistune.create_markdown(escape=False)


def inline_md(text):
    """One line of Markdown (links, *emphasis*, `code`) without the wrapping <p>."""
    out = _md_inline(str(text)).strip()
    return re.sub(r"^<p>(.*)</p>$", r"\1", out, flags=re.S)


def fmt_month(value):
    """2026-11 or 2026-11-05 -> Nov 2026; 2026 -> 2026."""
    s = str(value)
    m = re.fullmatch(r"(\d{4})(?:-(\d{2}))?(?:-\d{2})?", s)
    if not m: return s
    y, mo = m.groups()
    return f"{MONTHS[int(mo) - 1]} {y}" if mo else y


def fonts():
    return ('<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400'
            '&family=Noto+Sans+Khmer:wght@400;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">')


def lang_switch(languages, current, hrefs):
    """languages: {code: {label: ...}}; hrefs: {code: url} for the languages this page has."""
    out = []
    for code, cfg in languages.items():
        if code not in hrefs: continue
        label = esc(cfg["label"])
        out.append(f'<span aria-current="page">{label}</span>' if code == current else f'<a href="{esc(hrefs[code])}" hreflang="{esc(code)}">{label}</a>')
    return '<div class="lang-switch">' + '<span class="sep">/</span>'.join(out) + '</div>' if len(out) > 1 else ""


def header(active=None, switch=""):
    links = "".join(f'<a href="{href}"' + (' aria-current="page"' if key == active else "") + f'>{label}</a>'
                    for key, label, href in NAV)
    return (f'<a class="skip" href="#main">Skip to content</a><header class="topbar"><div class="wrap topbar-inner">'
            f'<a class="wordmark" href="/">{esc(profile()["name"])}</a>'
            f'<nav class="topnav" aria-label="Main">{links}</nav>{switch}</div></header>')


def footer():
    p = profile()
    links = "".join(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a>' for s in p["social"])
    links += f'<a href="mailto:{esc(p["email"])}">Email</a>'
    return (f'<footer class="site-foot"><div class="wrap foot-inner"><span>{esc(p["name"])} · {esc(p["location"])}</span>'
            f'<span class="foot-links">{links}</span></div></footer>')


def document(*, lang="en", title, description, body, active=None, css=(), switch="", canonical=None,
             og_image=None, head="", scripts="", comment=""):
    """A full page: body goes inside <main class="wrap">."""
    p = profile()
    meta = [f'<meta name="description" content="{esc(description)}">']
    if canonical:
        meta += [f'<link rel="canonical" href="{esc(canonical)}">', f'<meta property="og:url" content="{esc(canonical)}">']
    meta += ['<meta property="og:type" content="website">', f'<meta property="og:title" content="{esc(title)}">',
             f'<meta property="og:description" content="{esc(description)}">', f'<meta property="og:site_name" content="{esc(p["name"])}">']
    if og_image:
        meta += [f'<meta property="og:image" content="{esc(og_image)}">', '<meta name="twitter:card" content="summary_large_image">']
    sheets = "".join(f'<link rel="stylesheet" href="{esc(c)}">' for c in ("/assets/site.css", *css))
    return (f'<!DOCTYPE html>{comment}<html lang="{esc(lang)}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="color-scheme" content="light dark"><title>{esc(title)}</title>{"".join(meta)}{head}'
            f'{fonts()}{sheets}</head><body>{header(active, switch)}<main id="main" class="wrap">{body}</main>'
            f'{footer()}{scripts}</body></html>')
