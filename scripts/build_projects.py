#!/usr/bin/env python3
"""Build the Projects section (projects/) from content/projects/.

Each project is a folder content/projects/<slug>/ with meta.yaml, one <lang>.md per
language and an optional assets/ folder. Folders whose name starts with "_" (such as
the _template/ to copy) are skipped. See content/projects/README.md.

Output, next to the hand-written projects/style.css:
  projects/index.html            list in the default language
  projects/<lang>/index.html     list per language
  projects/<lang>/<slug>/        one page per project and language
  projects/<slug>/index.html     redirect to the default language
  projects/<slug>/assets/        the project's assets, shared by its languages
  projects/manifest.json         read by the home page's Projects section
"""
from __future__ import annotations

import html, json, re, shutil
from datetime import date, datetime
from pathlib import Path
import mistune, yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "projects"
OUT = ROOT / "projects"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MONTH_RE = re.compile(r"^(\d{4})(?:-(\d{2}))?$")
GENERATED = "<!-- Generated from content/projects/ by scripts/build_projects.py -->"


def load_yaml(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping")
    return data


def esc(v): return html.escape(str(v), quote=True)


def loc(v, lang, default_lang):
    """A plain string, or a {lang: string} mapping with a fallback to the default language."""
    if isinstance(v, dict): return v.get(lang) or v.get(default_lang) or ""
    return "" if v is None else str(v)


def month(v, where):
    """YYYY or YYYY-MM (a YAML date is cut to its month)."""
    if v is None: return None
    if isinstance(v, (date, datetime)): return v.isoformat()[:7]
    s = str(v)
    if not MONTH_RE.fullmatch(s): raise ValueError(f"{where}: expected YYYY or YYYY-MM, got {v!r}")
    return s


def fmt_month(v, cfg):
    y, m = MONTH_RE.fullmatch(v).groups()
    if not m: return y
    return cfg["month_format"].format(year=y, month=cfg["months"][int(m) - 1])


def period(p, cfg):
    start = fmt_month(p["started"], cfg)
    if not p["ended"]: return f"{start} –" if p["stage"] == "active" else start
    if p["ended"] == p["started"]: return start
    return f"{start} – {fmt_month(p['ended'], cfg)}"


def load_projects(site):
    projects = []; slugs = set(); dl = site["default_language"]
    for p in sorted(CONTENT.glob("*/meta.yaml")):
        if p.parent.name.startswith("_"): continue
        m = load_yaml(p)
        for k in ("id", "slug", "status", "stage", "started", "languages", "tags", "title", "summary"):
            if k not in m: raise ValueError(f"{p}: missing {k}")
        if not SLUG_RE.fullmatch(str(m["slug"])): raise ValueError(f"{p}: invalid slug")
        if m["slug"] != p.parent.name: raise ValueError(f"{p}: slug must match the folder name")
        if m["slug"] in slugs: raise ValueError(f"{p}: duplicate slug")
        slugs.add(m["slug"])
        if m["status"] not in ("published", "draft"): raise ValueError(f"{p}: status must be published or draft")
        if m["stage"] not in site["stages"]: raise ValueError(f"{p}: unknown stage {m['stage']} (see site.yaml)")
        for lang in m["languages"]:
            if lang not in site["languages"]: raise ValueError(f"{p}: unknown language {lang}")
            if not (p.parent / f"{lang}.md").exists(): raise ValueError(f"{p}: missing {lang}.md")
            if not loc(m["title"], lang, dl) or not loc(m["summary"], lang, dl): raise ValueError(f"{p}: missing {lang} title or summary")
        for link in m.get("links") or []:
            if not link.get("label") or not link.get("url"): raise ValueError(f"{p}: every link needs label and url")
        for fact in m.get("facts") or []:
            if not fact.get("value") or not fact.get("label"): raise ValueError(f"{p}: every fact needs value and label")
        if m.get("cover") and not (str(m["cover"]).startswith("assets/") and (p.parent / m["cover"]).is_file()):
            raise ValueError(f"{p}: cover must be a file under assets/")
        m["started"] = month(m["started"], p)
        m["ended"] = month(m.get("ended"), p)
        m["default_language"] = m.get("default_language", dl)
        m["dir"] = p.parent
        if m["status"] == "published": projects.append(m)
    # Pinned first, then the most recently started.
    return sorted(projects, key=lambda m: (bool(m.get("pinned")), m["started"], m["slug"]), reverse=True)


def fonts():
    return ('<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700'
            '&family=Noto+Sans+Khmer:wght@400;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">')


def doc(lang, title, desc, css, body, extra=""):
    return (f'<!DOCTYPE html><html lang="{esc(lang)}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title>'
            f'<meta name="description" content="{esc(desc)}">{extra}{fonts()}<link rel="stylesheet" href="{esc(css)}">'
            f'</head><body>{body}</body></html>')


def og(title, desc, url, image=None):
    tags = [f'<meta property="og:type" content="website">', f'<meta property="og:title" content="{esc(title)}">',
            f'<meta property="og:description" content="{esc(desc)}">', f'<meta property="og:url" content="{esc(url)}">']
    if image:
        tags += [f'<meta property="og:image" content="{esc(image)}">', '<meta name="twitter:card" content="summary_large_image">']
    return "".join(tags)


def switch(site, current, hrefs):
    out = []
    for code, cfg in site["languages"].items():
        if code not in hrefs: continue
        label = esc(cfg["label"])
        out.append(f'<span aria-current="page">{label}</span>' if code == current else f'<a href="{esc(hrefs[code])}">{label}</a>')
    return '<span class="sep">/</span>'.join(out)


def header(site, lang, brand, home, hrefs):
    return (f'<header class="site-head"><a class="brand" href="{brand}"><span class="brand-name">Mengsay Loem</span>'
            f'<span class="brand-sep">/</span><span class="brand-section">Projects</span></a><div class="head-actions">'
            f'<div class="lang-switch">{switch(site, lang, hrefs)}</div>'
            f'<a class="home-link" href="{home}">{esc(site["languages"][lang]["home"])}</a></div></header>')


def stage_badge(site, p, lang):
    return f'<span class="stage stage-{esc(p["stage"])}">{esc(loc(site["stages"][p["stage"]], lang, site["default_language"]))}</span>'


def links_html(p, lang, dl, cls="project-links"):
    links = p.get("links") or []
    if not links: return ""
    items = "".join(f'<a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(loc(l["label"], lang, dl))} ↗</a>' for l in links)
    return f'<div class="{cls}">{items}</div>'


def index(site, projects, lang, root=False):
    cfg = site["languages"][lang]; dl = site["default_language"]
    # up: from this list page to projects/
    if root:
        css = "./style.css"; home = "../"; up = "./"; hrefs = {c: ("./" if c == lang else f"./{c}/") for c in site["languages"]}
    else:
        css = "../style.css"; home = "../../"; up = "../"; hrefs = {c: ("./" if c == lang else f"../{c}/") for c in site["languages"]}
    cards = []
    for p in projects:
        plang = lang if lang in p["languages"] else p["default_language"]
        href = f'{up}{plang}/{esc(p["slug"])}/'
        cover = ""
        if p.get("cover"):
            cover = (f'<a class="project-cover" href="{href}" tabindex="-1" aria-hidden="true">'
                     f'<img src="{up}{esc(p["slug"])}/{esc(p["cover"])}" alt="" loading="lazy"></a>')
        tags = " ".join(f'<span class="tag">#{esc(t)}</span>' for t in p["tags"])
        cards.append(
            f'<article class="project-card">{cover}<div class="project-body">'
            f'<div class="project-meta">{stage_badge(site, p, plang)}<span>{esc(period(p, cfg))}</span></div>'
            f'<h2 class="project-title"><a href="{href}">{esc(loc(p["title"], plang, dl))}</a></h2>'
            f'<p class="project-summary">{esc(loc(p["summary"], plang, dl))}</p>'
            f'<div class="project-tags">{tags}</div>'
            f'<a class="project-more" href="{href}">{esc(cfg["read_more"])} →</a></div></article>')
    body = (f'{GENERATED}<div class="shell">{header(site, lang, "./", home, hrefs)}<main>'
            f'<section class="hero"><div class="kicker">{esc(cfg["kicker"])}</div><h1>{esc(cfg["title"])}</h1>'
            f'<p class="deck">{esc(cfg["description"])}</p></section>'
            f'<div class="project-list">{"".join(cards)}</div></main>'
            f'<footer>Projects by Mengsay Loem · Tokyo</footer></div>')
    url = site["base_url"].rstrip("/") + ("/projects/" if root else f"/projects/{lang}/")
    return doc(cfg["html_lang"], "Projects — Mengsay Loem", cfg["description"], css, body,
               f'<link rel="canonical" href="{url}">' + og("Projects — Mengsay Loem", cfg["description"], url))


def facts_html(p, lang, dl):
    facts = p.get("facts") or []
    if not facts: return ""
    items = "".join(f'<div class="fact"><div class="fact-value">{esc(loc(f["value"], lang, dl))}</div>'
                    f'<div class="fact-label">{esc(loc(f["label"], lang, dl))}</div></div>' for f in facts)
    return f'<div class="facts">{items}</div>'


def page(site, p, lang):
    cfg = site["languages"][lang]; dl = site["default_language"]; slug = p["slug"]
    # escape=False: the Markdown may hold raw HTML such as <figure> or <video>.
    md = mistune.create_markdown(escape=False, plugins=["table", "strikethrough", "url"])
    # Assets live once in projects/<slug>/assets/; point the Markdown's assets/... there.
    shared = f"../../{slug}/"
    prose = md((p["dir"] / f"{lang}.md").read_text(encoding="utf-8"))
    prose = prose.replace('src="assets/', f'src="{shared}assets/').replace('href="assets/', f'href="{shared}assets/')
    prose = prose.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    hrefs = {c: ("./" if c == lang else f"../../{c}/{slug}/") for c in p["languages"]}
    base = site["base_url"].rstrip("/")
    url = f"{base}/projects/{lang}/{slug}/"
    title = loc(p["title"], lang, dl); summary = loc(p["summary"], lang, dl)
    image = f"{base}/projects/{slug}/{p['cover']}" if p.get("cover") else None
    extra = "".join(f'<link rel="alternate" hreflang="{c}" href="{base}/projects/{c}/{slug}/">' for c in p["languages"])
    extra += f'<link rel="canonical" href="{url}">' + og(f"{title} — Mengsay Loem", summary, url, image)
    kicker = loc(p.get("kicker"), lang, dl)
    meta = " · ".join(x for x in (kicker, period(p, cfg)) if x)
    cover = ""
    if p.get("cover"):
        cover = f'<figure class="project-hero"><img src="{shared}{esc(p["cover"])}" alt="{esc(loc(p.get("cover_alt"), lang, dl))}"></figure>'
    tags = " ".join(f'<span class="tag">#{esc(t)}</span>' for t in p["tags"])
    body = (f'{GENERATED}<div class="shell">{header(site, lang, "../", "../../../", hrefs)}<article class="article">'
            f'<header class="article-head"><div class="project-meta">{stage_badge(site, p, lang)}<span>{esc(meta)}</span></div>'
            f'<h1>{esc(title)}</h1><p class="deck">{esc(summary)}</p>{links_html(p, lang, dl)}{facts_html(p, lang, dl)}</header>'
            f'{cover}<div class="prose">{prose}</div><div class="project-tags article-tags">{tags}</div></article>'
            f'<footer><a href="../">← {esc(cfg["all_projects"])}</a></footer></div>')
    return doc(cfg["html_lang"], f"{title} — Mengsay Loem", summary, "../../style.css", body, extra)


def redirect(site, p):
    lang = p["default_language"]; target = f'../{lang}/{p["slug"]}/'
    return (f'<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={target}">'
            f'<link rel="canonical" href="{site["base_url"]}/projects/{lang}/{p["slug"]}/"></head>'
            f'<body><a href="{target}">Continue</a></body></html>')


def manifest(site, projects):
    dl = site["default_language"]
    rows = []
    for p in projects:
        rows.append({
            "id": p["id"], "slug": p["slug"], "stage": p["stage"],
            "stage_label": {l: loc(site["stages"][p["stage"]], l, dl) for l in site["languages"]},
            "started": p["started"], "ended": p["ended"], "tags": p["tags"],
            "languages": p["languages"], "default_language": p["default_language"],
            "title": {l: loc(p["title"], l, dl) for l in p["languages"]},
            "summary": {l: loc(p["summary"], l, dl) for l in p["languages"]},
            "links": [{"label": loc(l["label"], dl, dl), "url": l["url"]} for l in p.get("links") or []],
            "urls": {l: f'/projects/{l}/{p["slug"]}/' for l in p["languages"]},
        })
    return {"default_language": dl, "languages": list(site["languages"]), "projects": rows}


def main():
    site = load_yaml(CONTENT / "site.yaml"); projects = load_projects(site)
    OUT.mkdir(exist_ok=True)
    for c in list(OUT.iterdir()):
        if c.is_dir(): shutil.rmtree(c)
        elif c.name in {"index.html", "manifest.json"}: c.unlink()
    (OUT / "index.html").write_text(index(site, projects, site["default_language"], True), encoding="utf-8")
    for lang in site["languages"]:
        d = OUT / lang; d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(index(site, projects, lang), encoding="utf-8")
    for p in projects:
        for lang in p["languages"]:
            d = OUT / lang / p["slug"]; d.mkdir(parents=True, exist_ok=True)
            (d / "index.html").write_text(page(site, p, lang), encoding="utf-8")
        d = OUT / p["slug"]; d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(redirect(site, p), encoding="utf-8")
        assets = p["dir"] / "assets"
        if assets.is_dir(): shutil.copytree(assets, d / "assets", dirs_exist_ok=True)
    (OUT / "manifest.json").write_text(json.dumps(manifest(site, projects), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(projects)} project(s)")


if __name__ == "__main__": main()
