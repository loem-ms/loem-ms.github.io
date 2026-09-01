#!/usr/bin/env python3
from __future__ import annotations

import html, json, re, shutil
from datetime import date, datetime
from pathlib import Path
import mistune, yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "notes"
OUT = ROOT / "notes"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_yaml(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping")
    return data


def dstr(v):
    if isinstance(v, (date, datetime)): return v.isoformat()[:10]
    if isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v): return v
    raise ValueError(f"invalid date: {v}")


def esc(v): return html.escape(str(v), quote=True)


def load_notes(site):
    notes=[]; ids=set(); slugs=set()
    for p in sorted(CONTENT.glob("**/meta.yaml")):
        m=load_yaml(p)
        for k in ("id","slug","published_at","status","type","languages","tags","title","summary"):
            if k not in m: raise ValueError(f"{p}: missing {k}")
        if not SLUG_RE.fullmatch(str(m["slug"])): raise ValueError(f"{p}: invalid slug")
        if m["id"] in ids or m["slug"] in slugs: raise ValueError(f"{p}: duplicate id/slug")
        ids.add(m["id"]); slugs.add(m["slug"])
        for lang in m["languages"]:
            if lang not in site["languages"]: raise ValueError(f"{p}: unknown language {lang}")
            if not (p.parent/f"{lang}.md").exists(): raise ValueError(f"{p}: missing {lang}.md")
            if not m["title"].get(lang) or not m["summary"].get(lang): raise ValueError(f"{p}: missing localized metadata")
        m["published_at"]=dstr(m["published_at"])
        m["updated_at"]=dstr(m["updated_at"]) if m.get("updated_at") else None
        m["default_language"]=m.get("default_language",site["default_language"])
        m["dir"]=p.parent
        if m["status"]=="published": notes.append(m)
    return sorted(notes,key=lambda x:(x["published_at"],x["slug"]),reverse=True)


def fonts():
    return '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">'


def doc(lang,title,desc,css,body,extra=""):
    return f'''<!DOCTYPE html><html lang="{esc(lang)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}">{extra}{fonts()}<link rel="stylesheet" href="{esc(css)}"></head><body>{body}</body></html>'''


def switch(site,current,hrefs):
    out=[]
    for code,cfg in site["languages"].items():
        if code not in hrefs: continue
        label=esc(cfg["label"])
        out.append(f'<span aria-current="page">{label}</span>' if code==current else f'<a href="{esc(hrefs[code])}">{label}</a>')
    return '<span class="sep">/</span>'.join(out)


def header(site,lang,brand,home,hrefs):
    return f'''<header class="site-head"><a class="brand" href="{brand}"><span class="brand-name">Mengsay Loem</span><span class="brand-sep">/</span><span class="brand-section">Notes</span></a><div class="head-actions"><div class="lang-switch">{switch(site,lang,hrefs)}</div><a class="home-link" href="{home}">{esc(site["languages"][lang]["home"])}</a></div></header>'''


def index(site,notes,lang,root=False):
    cfg=site["languages"][lang]
    if root:
        css="./style.css"; home="../"; prefix=f"./{lang}/"; hrefs={c:("./" if c==lang else f"./{c}/") for c in site["languages"]}
    else:
        css="../style.css"; home="../../"; prefix="./"; hrefs={c:("./" if c==lang else f"../{c}/") for c in site["languages"]}
    rows=[]
    for n in notes:
        if lang not in n["languages"]: continue
        tags=''.join(f'<span class="tag">{esc(t)}</span>' for t in n["tags"])
        rows.append(f'<a class="note-row" href="{prefix}{esc(n["slug"])}/"><div class="note-date">{n["published_at"]}</div><div><div class="note-title">{esc(n["title"][lang])}</div><div class="note-desc">{esc(n["summary"][lang])}</div><div class="note-tags">{tags}</div></div></a>')
    body=f'''<!-- Generated from content/notes/ by scripts/build_notes.py --><div class="shell">{header(site,lang,"./",home,hrefs)}<main><section class="hero"><div class="kicker">{esc(cfg["notebook_kicker"])}</div><h1>Notes</h1><p class="deck">{esc(cfg["description"])}</p></section><div class="note-list">{"".join(rows)}</div></main><footer>Notes by Mengsay Loem · Tokyo</footer></div>'''
    canonical=site["base_url"].rstrip('/') + ('/notes/' if root else f'/notes/{lang}/')
    return doc(cfg["html_lang"],"Notes — Mengsay Loem",cfg["description"],css,body,f'<link rel="canonical" href="{canonical}">')


def article(site,n,lang):
    cfg=site["languages"][lang]; slug=n["slug"]
    md=mistune.create_markdown(plugins=["table"])((n["dir"]/f"{lang}.md").read_text(encoding="utf-8"))
    hrefs={c:("./" if c==lang else f"../../{c}/{slug}/") for c in n["languages"]}
    alts=''.join(f'<link rel="alternate" hreflang="{c}" href="{site["base_url"]}/notes/{c}/{slug}/">' for c in n["languages"])
    alts+=f'<link rel="canonical" href="{site["base_url"]}/notes/{lang}/{slug}/">'
    kicker=n.get("kicker",{}).get(lang,n["type"].replace('-',' ').title()) if isinstance(n.get("kicker",{}),dict) else n["type"]
    meta=n["published_at"] + (f' · updated {n["updated_at"]}' if n.get("updated_at") else '') + ' · ' + ' / '.join(n["tags"])
    body=f'''<!-- Generated from content/notes/ by scripts/build_notes.py --><div class="shell">{header(site,lang,"../","../../../",hrefs)}<article class="article"><header class="article-head"><div class="kicker">{esc(kicker)}</div><h1>{esc(n["title"][lang])}</h1><div class="meta">{esc(meta)}</div></header><div class="prose">{md}</div></article><footer><a href="../">← {esc(cfg["all_notes"])}</a></footer></div>'''
    return doc(cfg["html_lang"],f'{n["title"][lang]} — Mengsay Loem',n["summary"][lang],"../../style.css",body,alts)


def redirect(site,n):
    lang=n["default_language"]; target=f'../{lang}/{n["slug"]}/'
    return f'<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{site["base_url"]}/notes/{lang}/{n["slug"]}/"></head><body><a href="{target}">Continue</a></body></html>'


def main():
    site=load_yaml(CONTENT/"site.yaml"); notes=load_notes(site)
    OUT.mkdir(exist_ok=True)
    for c in list(OUT.iterdir()):
        if c.is_dir(): shutil.rmtree(c)
        elif c.name in {"index.html","manifest.json"}: c.unlink()
    (OUT/"index.html").write_text(index(site,notes,site["default_language"],True),encoding="utf-8")
    for lang in site["languages"]:
        d=OUT/lang; d.mkdir(parents=True,exist_ok=True); (d/"index.html").write_text(index(site,notes,lang),encoding="utf-8")
    for n in notes:
        for lang in n["languages"]:
            d=OUT/lang/n["slug"]; d.mkdir(parents=True,exist_ok=True); (d/"index.html").write_text(article(site,n,lang),encoding="utf-8")
            assets=n["dir"]/"assets"
            if assets.is_dir(): shutil.copytree(assets,d/"assets",dirs_exist_ok=True)
        d=OUT/n["slug"]; d.mkdir(parents=True,exist_ok=True); (d/"index.html").write_text(redirect(site,n),encoding="utf-8")
    manifest={"default_language":site["default_language"],"languages":list(site["languages"]),"notes":[{k:n.get(k) for k in ("id","slug","published_at","updated_at","type","tags","languages","default_language","title","summary")} | {"urls":{l:f'/notes/{l}/{n["slug"]}/' for l in n["languages"]}} for n in notes]}
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Built {len(notes)} note(s)")

if __name__=="__main__": main()
