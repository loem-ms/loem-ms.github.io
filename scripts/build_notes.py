#!/usr/bin/env python3
from __future__ import annotations

import html, json, re, shutil
from datetime import date, datetime
from pathlib import Path
import mistune, yaml
from sitekit import document, lang_switch

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "notes"
OUT = ROOT / "notes"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
GENERATED = "<!-- Generated from content/notes/ by scripts/build_notes.py -->"


def load_yaml(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping")
    return data


def dstr(v):
    if isinstance(v, (date, datetime)): return v.isoformat()[:10]
    if isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v): return v
    raise ValueError(f"invalid date: {v}")


def dtstr(v):
    if isinstance(v, datetime): return v.isoformat()
    if isinstance(v, str):
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            pass
    raise ValueError(f"invalid datetime: {v}")


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
        if m["type"] == "paper-note":
            paper=m.get("paper")
            if not isinstance(paper,dict): raise ValueError(f"{p}: paper-note requires paper metadata")
            for k in ("title","authors","venue_short","year","url"):
                if not paper.get(k): raise ValueError(f"{p}: paper metadata missing {k}")
            if not isinstance(paper["authors"],list) or not paper["authors"]: raise ValueError(f"{p}: paper authors must be a non-empty list")
        m["published_at"]=dstr(m["published_at"])
        m["updated_at"]=dstr(m["updated_at"]) if m.get("updated_at") else None
        m["added_at"]=dtstr(m["added_at"]) if m.get("added_at") else None
        m["default_language"]=m.get("default_language",site["default_language"])
        m["dir"]=p.parent
        if m["status"]=="published": notes.append(m)
    def sort_key(n):
        added=n.get("added_at")
        if added:
            return (1, datetime.fromisoformat(added.replace("Z", "+00:00")).timestamp(), n["slug"])
        return (0, datetime.fromisoformat(n["published_at"] + "T00:00:00+00:00").timestamp(), n["slug"])
    return sorted(notes,key=sort_key,reverse=True)


def list_url(site, lang):
    return "/notes/" if lang == site["default_language"] else f"/notes/{lang}/"


def filter_script(empty_text):
    return f'''<script>(()=>{{const input=document.getElementById('note-search');const year=document.getElementById('note-year');const rows=Array.from(document.querySelectorAll('.note-row'));const count=document.getElementById('note-count');const empty=document.getElementById('note-empty');function apply(){{const q=(input.value||'').trim().toLocaleLowerCase();const y=year.value;let shown=0;rows.forEach(row=>{{const okYear=!y||row.dataset.year===y;const okText=!q||row.textContent.toLocaleLowerCase().includes(q);const visible=okYear&&okText;row.hidden=!visible;if(visible)shown++;}});count.textContent=shown+' / '+rows.length;empty.hidden=shown!==0;}}input.addEventListener('input',apply);year.addEventListener('change',apply);apply();}})();</script>'''


def index(site,notes,lang,root=False):
    cfg=site["languages"][lang]
    hrefs={c:list_url(site,c) for c in site["languages"]}
    localized=[n for n in notes if lang in n["languages"]]
    rows=[]
    for n in localized:
        tags=' '.join(f'<span class="tag">#{esc(t)}</span>' for t in n["tags"])
        year=n["published_at"][:4]
        rows.append(f'<a class="note-row" data-year="{year}" href="/notes/{lang}/{esc(n["slug"])}/"><div class="note-date">{n["published_at"]}</div><div><div class="note-title">{esc(n["title"][lang])}</div><div class="note-desc">{esc(n["summary"][lang])}</div><div class="note-tags">{tags}</div></div></a>')
    years=sorted({n["published_at"][:4] for n in localized}, reverse=True)
    year_options=''.join(f'<option value="{y}">{y}</option>' for y in years)
    search_placeholder=cfg.get("search_placeholder","Search notes")
    all_years=cfg.get("all_years","All years")
    empty_text=cfg.get("no_results","No notes match these filters.")
    filters=f'''<div class="note-tools"><input id="note-search" class="note-search" type="search" autocomplete="off" placeholder="{esc(search_placeholder)}" aria-label="{esc(search_placeholder)}"><select id="note-year" class="note-year" aria-label="{esc(all_years)}"><option value="">{esc(all_years)}</option>{year_options}</select><span id="note-count" class="note-count" aria-live="polite"></span></div>'''
    about_more=''.join(f'<p>{esc(p)}</p>' for p in cfg.get('about', []))
    about=f'''<div class="editorial-note"><div><div class="kicker">{esc(cfg.get("about_title","About these notes"))}</div><p>{esc(cfg.get("about_summary",""))}</p><details><summary>{esc(cfg.get("about_more_label","Details"))}</summary><div class="editorial-more">{about_more}</div></details></div><div class="collab-note"><div class="kicker">{esc(cfg.get("collaboration_title","Collaboration"))}</div><p>{esc(cfg.get("collaboration",""))}</p></div></div>'''
    body=f'''<header class="page-head"><div class="kicker">{esc(cfg["notebook_kicker"])}</div><h1>Notes</h1><p class="deck">{esc(cfg["description"])}</p></header>{about}{filters}<div class="note-list">{"".join(rows)}</div><p id="note-empty" class="note-empty" hidden>{esc(empty_text)}</p>'''
    canonical=site["base_url"].rstrip('/') + ('/notes/' if root else f'/notes/{lang}/')
    return document(lang=cfg["html_lang"],title="Notes — Mengsay Loem",description=cfg["description"],body=body,active="notes",css=("/notes/style.css",),switch=lang_switch(site["languages"],lang,hrefs),canonical=canonical,scripts=filter_script(empty_text),comment=GENERATED)


def paper_ref(n):
    paper=n.get("paper")
    if not paper: return ""
    first=str(paper["authors"][0]).strip().split()[-1]
    author_label=f"{first} et al." if len(paper["authors"]) > 1 else first
    venue=paper.get("venue_short") or paper.get("venue") or ""
    compact=" · ".join(x for x in (author_label, f'{venue} {paper["year"]}'.strip()) if x)
    return f'''<div class="paper-ref"><span class="paper-ref-label">Reading</span><div><a class="paper-ref-title" href="{esc(paper["url"])}" target="_blank" rel="noopener">{esc(paper["title"])} ↗</a><span class="paper-ref-cite">{esc(compact)}</span></div></div>'''


def article(site,n,lang):
    cfg=site["languages"][lang]; slug=n["slug"]
    md=mistune.create_markdown(plugins=["table"])((n["dir"]/f"{lang}.md").read_text(encoding="utf-8"))
    md=md.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    hrefs={c:f"/notes/{c}/{slug}/" for c in n["languages"]}
    alts=''.join(f'<link rel="alternate" hreflang="{c}" href="{site["base_url"]}/notes/{c}/{slug}/">' for c in n["languages"])
    kicker=n.get("kicker",{}).get(lang,n["type"].replace('-',' ').title()) if isinstance(n.get("kicker",{}),dict) else n["type"]
    meta=n["published_at"] + (f' · updated {n["updated_at"]}' if n.get("updated_at") else '') + ' · ' + ' / '.join(n["tags"])
    ref=paper_ref(n)
    body=f'''<article class="article"><header class="article-head"><div class="kicker">{esc(kicker)}</div><h1>{esc(n["title"][lang])}</h1><div class="meta">{esc(meta)}</div>{ref}</header><div class="prose">{md}</div><p class="back"><a href="{list_url(site,lang)}">← {esc(cfg["all_notes"])}</a></p></article>'''
    return document(lang=cfg["html_lang"],title=f'{n["title"][lang]} — Mengsay Loem',description=n["summary"][lang],body=body,active="notes",css=("/notes/style.css",),switch=lang_switch(site["languages"],lang,hrefs),canonical=f'{site["base_url"]}/notes/{lang}/{slug}/',head=alts,comment=GENERATED)


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
    manifest={"default_language":site["default_language"],"languages":list(site["languages"]),"notes":[{k:n.get(k) for k in ("id","slug","published_at","updated_at","added_at","type","tags","languages","default_language","title","summary","paper")} | {"urls":{l:f'/notes/{l}/{n["slug"]}/' for l in n["languages"]}} for n in notes]}
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Built {len(notes)} note(s)")

if __name__=="__main__": main()
