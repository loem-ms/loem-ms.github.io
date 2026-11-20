#!/usr/bin/env python3
"""Build the home page, /publications/, /cv/ and 404.html from content/site/.

Run after build_notes.py and build_projects.py: the home page lists the latest notes and the
projects from their manifest.json files. See content/README.md.
"""
from __future__ import annotations

import json
from collections import Counter
from sitekit import ROOT, esc, document, fmt_month, inline_md, load_yaml, profile

CONTENT = ROOT / "content" / "site"
GENERATED = "<!-- Generated from content/site/ by scripts/build_site.py -->"


def load():
    pubs = load_yaml(CONTENT / "publications.yaml")
    for i, p in enumerate(pubs["items"]):
        for k in ("title", "authors", "venue", "venue_short", "year", "type"):
            if not p.get(k): raise ValueError(f"publications.yaml item {i}: missing {k}")
        if p["type"] not in pubs["types"]: raise ValueError(f"publications.yaml item {i}: unknown type {p['type']}")
        p["links"] = p.get("links") or []
    # Newest year first; the order inside a year stays as written.
    pubs["items"].sort(key=lambda p: -int(p["year"]))
    data = {"pubs": pubs, "talks": load_yaml(CONTENT / "talks.yaml"), "awards": load_yaml(CONTENT / "awards.yaml"),
            "cv": load_yaml(CONTENT / "cv.yaml"), "news": load_yaml(CONTENT / "news.yaml")}
    data["notes"] = json.loads((ROOT / "notes" / "manifest.json").read_text(encoding="utf-8"))
    data["projects"] = json.loads((ROOT / "projects" / "manifest.json").read_text(encoding="utf-8"))
    return data


def links_html(links, extra=""):
    items = "".join(f'<a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["label"])}</a>' for l in links)
    return f'<div class="links">{extra}{items}</div>' if (items or extra) else ""


def pub_row(p, show_year=True):
    name = profile()["name"]
    authors = esc(p["authors"]).replace(esc(name), f"<b>{esc(name)}</b>")
    title = esc(p["title"])
    if p["links"]: title = f'<a href="{esc(p["links"][0]["url"])}" target="_blank" rel="noopener">{title}</a>'
    award = f'<span class="badge">★ {esc(p["award"])}</span>' if p.get("award") else ""
    year = f'<span>{esc(p["year"])}</span>' if show_year else ""
    venue = f'<div class="pub-venue">{esc(p["venue"])}</div>' if p["venue"] != p["venue_short"] else ""
    return (f'<article class="row pub" data-type="{esc(p["type"])}"><div class="row-side pub-tag">'
            f'<span class="venue">{esc(p["venue_short"])}</span>{year}</div>'
            f'<div><div class="row-title">{title}</div><div class="pub-authors">{authors}</div>'
            f'{venue}{links_html(p["links"], award)}</div></article>')


def block(title, inner, *, id=None, count=None, more=None):
    head = f'<h2>{esc(title)}</h2>'
    if count is not None: head += f'<span class="count">{count:02d}</span>'
    if more: head += f'<a class="more" href="{esc(more[1])}">{esc(more[0])} →</a>'
    attr = f' id="{esc(id)}"' if id else ""
    return f'<section class="block"{attr}><div class="block-head">{head}</div>{inner}</section>'


# ---------------------------------------------------------------- home

COPY_SCRIPT = """<script>(()=>{const b=document.getElementById('copy-email');if(!b)return;b.addEventListener('click',()=>{const e=b.dataset.email;const done=()=>{b.textContent='Copied ✓';b.classList.add('done');setTimeout(()=>{b.textContent='Email';b.classList.remove('done');},1600);};if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(e).then(done,()=>{location.href='mailto:'+e;});}else{location.href='mailto:'+e;}});})();</script>"""


def home(d):
    p = profile(); n = p.get("home", {})
    roles = " <span class=\"dot\">·</span> ".join(inline_md(r) for r in p["roles"])
    social = "".join(f'<a class="btn" href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])} ↗</a>' for s in p["social"])
    social += f'<button class="btn" id="copy-email" type="button" data-email="{esc(p["email"])}">Email</button>'
    tags = "".join(f'<span class="chip">{esc(t)}</span>' for t in p["interests"])
    intro = (f'<section class="intro"><h1 class="intro-name">{esc(p["name"])}</h1>'
             f'<p class="intro-role">{roles} <span class="dot">·</span> {esc(p["location"])}</p>'
             f'<p class="intro-text">{inline_md(p["intro"])}</p>'
             f'<div class="chips intro-tags">{tags}</div>'
             f'<div class="intro-links">{social}</div></section>')

    news = "".join(f'<li><time class="row-side">{esc(fmt_month(x["date"]))}</time><span>{inline_md(x["text"])}</span></li>'
                   for x in d["news"][: n.get("news", 5)])
    news = block("News", f'<ul class="news">{news}</ul>', id="news")

    selected = [x for x in d["pubs"]["items"] if x.get("selected")]
    pubs = block("Selected publications", "".join(pub_row(x) for x in selected), id="publications",
                 more=(f'All {len(d["pubs"]["items"])}', "/publications/"))

    pm = d["projects"]; lang = pm["default_language"]
    rows = []
    for x in pm["projects"]:
        pl = lang if lang in x["urls"] else x["default_language"]
        thumb = f'<img class="proj-thumb" src="{esc(x["cover"])}" alt="" loading="lazy">' if x.get("cover") else '<span class="proj-thumb"></span>'
        rows.append(f'<a class="proj-row" href="{esc(x["urls"][pl])}">{thumb}<div><div class="row-title">{esc(x["title"][pl])}</div>'
                    f'<div class="row-sub">{esc(x["summary"][pl])}</div>'
                    f'<div class="proj-meta">{esc(x["stage_label"][pl])} · {esc(fmt_month(x["started"]))}</div></div></a>')
    projects = block("Projects", "".join(rows), id="projects", more=("All projects", "/projects/")) if rows else ""

    nm = d["notes"]; lang = nm["default_language"]
    rows = []
    for x in nm["notes"][: n.get("notes", 3)]:
        pl = lang if lang in x["urls"] else x["default_language"]
        rows.append(f'<div class="row"><time class="row-side">{esc(x["published_at"])}</time><div>'
                    f'<div class="row-title"><a href="{esc(x["urls"][pl])}">{esc(x["title"][pl])}</a></div>'
                    f'<div class="row-sub">{esc(x["summary"][pl])}</div></div></div>')
    notes = block("Recent notes", "".join(rows), id="notes", more=("All notes", "/notes/")) if rows else ""

    body = intro + news + pubs + projects + notes
    return document(title=p["name"], description=p["description"], body=body, canonical=p["base_url"] + "/",
                    scripts=COPY_SCRIPT, comment=GENERATED)


# ---------------------------------------------------------------- publications

FILTER_SCRIPT = """<script>(()=>{const q=document.getElementById('pub-q');const btns=[...document.querySelectorAll('[data-filter]')];const pubs=[...document.querySelectorAll('.pub')];const groups=[...document.querySelectorAll('.year-group')];const count=document.getElementById('pub-count');const empty=document.getElementById('pub-empty');let type=new URLSearchParams(location.search).get('type')||'all';if(!btns.some(b=>b.dataset.filter===type))type='all';function apply(){const s=q.value.trim().toLocaleLowerCase();let n=0;pubs.forEach(p=>{const ok=(type==='all'||p.dataset.type===type)&&(!s||p.textContent.toLocaleLowerCase().includes(s));p.hidden=!ok;if(ok)n++;});groups.forEach(g=>{g.hidden=!g.querySelector('.pub:not([hidden])');});btns.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===type)));count.textContent=n+' / '+pubs.length;empty.hidden=n!==0;}btns.forEach(b=>b.addEventListener('click',()=>{type=b.dataset.filter;const u=new URL(location.href);if(type==='all')u.searchParams.delete('type');else u.searchParams.set('type',type);history.replaceState(null,'',u);apply();}));q.addEventListener('input',apply);apply();})();</script>"""


def publications(d):
    p = profile(); pubs = d["pubs"]; items = pubs["items"]
    counts = Counter(x["type"] for x in items)
    labels = pubs.get("tab_labels", {})
    chips = f'<button type="button" data-filter="all" aria-pressed="true">All<span class="n">{len(items)}</span></button>'
    chips += "".join(f'<button type="button" data-filter="{esc(t)}" aria-pressed="false">{esc(labels.get(t, label))}<span class="n">{counts[t]}</span></button>'
                     for t, label in pubs["types"].items() if counts[t])
    scholar = next((s["url"] for s in p["social"] if "scholar" in s["url"]), None)
    deck = "Journal and conference papers, preprints, and papers at Japanese venues, newest first."
    if scholar: deck += f' Citations are on <a href="{esc(scholar)}" target="_blank" rel="noopener">Google Scholar</a>.'
    head = f'<header class="page-head"><div class="kicker">Research</div><h1>Publications</h1><p class="deck">{deck}</p></header>'
    tools = (f'<div class="tools"><div class="filter-chips" role="group" aria-label="Type">{chips}</div>'
             f'<input id="pub-q" class="search" type="search" placeholder="Search title, author or venue" aria-label="Search publications" autocomplete="off">'
             f'<span id="pub-count" class="result-count" aria-live="polite"></span></div>')
    groups = []
    for year in sorted({int(x["year"]) for x in items}, reverse=True):
        rows = "".join(pub_row(x, show_year=False) for x in items if int(x["year"]) == year)
        groups.append(f'<section class="year-group"><h2 class="year">{year}</h2>{rows}</section>')
    body = head + tools + "".join(groups) + '<p id="pub-empty" class="empty" hidden>No publications match.</p>'
    return document(title=f'Publications — {p["name"]}', description=f'Publications by {p["name"]}.', body=body,
                    active="publications", canonical=p["base_url"] + "/publications/", scripts=FILTER_SCRIPT, comment=GENERATED)


# ---------------------------------------------------------------- CV

def cv(d):
    p = profile(); c = d["cv"]
    exp = "".join(f'<div class="row"><div class="row-side">{esc(x["period"])}</div><div><div class="row-title">{esc(x["role"])}</div>'
                  f'<div class="row-sub">{esc(x["org"])}</div></div></div>' for x in c["experience"])
    edu = "".join(f'<div class="row"><div class="row-side">{esc(x["period"])}</div><div><div class="row-title">{esc(x["degree"])}</div>'
                  f'<div class="row-sub">{esc(x["org"])}</div></div></div>' for x in c["education"])
    talks = "".join(f'<div class="row"><div class="row-side">{esc(x["date"])}</div><div><div class="row-title">{esc(x["title"])}</div>'
                    f'<div class="row-sub">{esc(x["venue"])}</div>{links_html(x.get("links") or [])}</div></div>' for x in d["talks"])
    awards = "".join(f'<div class="row"><div class="row-side">{esc(x["date"])}</div><div><div class="row-text">{esc(x["text"])}</div>'
                     f'{links_html(x.get("links") or [])}</div></div>' for x in d["awards"])
    toc = '<nav class="toc" aria-label="On this page"><a href="#experience">Experience</a><a href="#education">Education</a><a href="#talks">Talks</a><a href="#awards">Awards</a><a href="/publications/">Publications →</a></nav>'
    roles = " · ".join(inline_md(r) for r in p["roles"])
    head = f'<header class="page-head"><div class="kicker">Curriculum vitae</div><h1>CV</h1><p class="deck">{roles} · {esc(p["location"])}</p>{toc}</header>'
    body = (head + '<div class="cv">' + block("Experience", exp, id="experience") + block("Education", edu, id="education")
            + block("Talks", talks, id="talks", count=len(d["talks"])) + block("Awards & Honors", awards, id="awards") + '</div>')
    return document(title=f'CV — {p["name"]}', description=f'Experience, education, talks and awards of {p["name"]}.', body=body,
                    active="cv", canonical=p["base_url"] + "/cv/", comment=GENERATED)


def not_found():
    body = ('<header class="page-head"><div class="kicker">404</div><h1>Page not found</h1>'
            '<p class="deck">This page doesn’t exist, or it moved. Try the <a href="/">home page</a>, '
            '<a href="/publications/">publications</a>, <a href="/projects/">projects</a> or <a href="/notes/">notes</a>.</p></header>')
    return document(title=f'Not found — {profile()["name"]}', description="Page not found.", body=body, comment=GENERATED)


def main():
    d = load()
    (ROOT / "index.html").write_text(home(d), encoding="utf-8")
    for name, page in (("publications", publications), ("cv", cv)):
        out = ROOT / name; out.mkdir(exist_ok=True)
        (out / "index.html").write_text(page(d), encoding="utf-8")
    (ROOT / "404.html").write_text(not_found(), encoding="utf-8")
    print(f'Built home, {len(d["pubs"]["items"])} publications, CV and 404')


if __name__ == "__main__": main()
