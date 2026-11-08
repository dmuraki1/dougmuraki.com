#!/usr/bin/env python3
"""Builds the /notes/ section of dougmuraki.com from _build/posts.json.

Add a post: append an entry to posts.json (slug, date, title, desc, linkedin, body[]),
then run `python3 _build/build.py` from the repo root and commit. Rules: no em dashes,
no employee names, nothing the website doesn't already say.
"""
import json, re, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://dougmuraki.com"
posts = json.loads((ROOT / "_build/posts.json").read_text())
posts.sort(key=lambda p: p["date"], reverse=True)

for p in posts:
    text = json.dumps(p)
    assert "—" not in text and "–" not in text, f"dash in {p['slug']}"

index_html = (ROOT / "index.html").read_text()
style = re.search(r"<style>.*?</style>", index_html, re.S).group(0)
extra_css = """<style>
.note-list{list-style:none;padding:0;margin:0;display:grid;gap:1.5rem}
.note-list li{border-top:1px solid var(--line);padding-top:1.1rem}
.note-list li:first-child{border-top:0;padding-top:0}
.note-list a.t{font-weight:800;font-size:1.2rem;letter-spacing:-0.015em;text-decoration:none;line-height:1.3}
.note-list a.t:hover{color:var(--coral)}
.note-list p{margin:0.35rem 0 0;color:var(--ink-soft);max-width:60ch}
.meta{font-size:0.9rem;color:var(--ink-soft);margin:0 0 0.4rem}
.post{padding:2.5rem 0 4rem}
.post .wrap{max-width:44rem}
.post h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.08;margin:0 0 1rem}
.post .body p{font-size:1.1rem;margin:0 0 1.2rem}
.byline{display:flex;align-items:center;gap:0.85rem;margin:0 0 2rem;padding-bottom:1.5rem;border-bottom:1px solid var(--line)}
.byline img{width:52px;height:52px;border-radius:50%;object-fit:cover;object-position:50% 30%}
.byline span{font-size:0.95rem;line-height:1.4}
.after{margin-top:2.5rem;padding-top:1.5rem;border-top:1px solid var(--line);font-size:0.98rem}
.after p{margin:0 0 0.6rem}
</style>"""

def fmt(d):
    dt = datetime.date.fromisoformat(d)
    return dt.strftime("%B ") + str(dt.day) + dt.strftime(", %Y")

def header(prefix):
    return (f'<header><div class="wrap"><a class="name" href="/">Doug Muraki</a>'
            f'<nav aria-label="Site"><a href="/#about">About</a><a href="/notes/">Notes</a>'
            f'<a href="/#crew">Crew</a><a href="/#contact">Contact</a></nav></div></header>')

FOOTER = ('<footer><div class="wrap"><span>Doug Muraki, Sacramento, California</span>'
          '<span>Sunfish Pool Service is operated by The Village Tree LLC</span></div></footer>')

PERSON = {"@type": "Person", "@id": SITE + "/#doug", "name": "Doug Muraki", "url": SITE + "/",
          "jobTitle": "Owner", "worksFor": {"@type": "LocalBusiness", "name": "Sunfish Pool Service", "url": "https://sunfishswim.com/"}}

def page(title, desc, canonical, body, schema, og_type="article"):
    e = html.escape
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/doug-muraki.jpg">
<meta name="author" content="Doug Muraki">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;700;800&display=swap" rel="stylesheet">
<script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False)}
</script>
{style}
{extra_css}
</head>
<body>
{header('/')}
<main>
{body}
</main>
{FOOTER}
</body>
</html>
"""

out = ROOT / "notes"
out.mkdir(exist_ok=True)

for i, p in enumerate(posts):
    url = f"{SITE}/notes/{p['slug']}/"
    paras = "\n".join(f"<p>{html.escape(x)}</p>" for x in p["body"])
    others = [q for q in posts if q is not p][:3]
    more = "".join(f'<li><a href="/notes/{q["slug"]}/">{html.escape(q["title"])}</a></li>' for q in others)
    body = f"""<article class="post"><div class="wrap">
<p class="eyebrow">Notes from Sunfish Pool Service</p>
<h1>{html.escape(p['title'])}</h1>
<div class="byline"><img src="/doug-muraki.jpg" alt="Doug Muraki" width="52" height="52"><span><a href="/">Doug Muraki</a>, owner of <a href="https://sunfishswim.com/">Sunfish Pool Service</a>, Sacramento<br><time datetime="{p['date']}">{fmt(p['date'])}</time></span></div>
<div class="body">
{paras}
</div>
<div class="after">
<p>Also posted on <a href="{p['linkedin']}">LinkedIn</a>. Pool service in Sacramento: <a href="https://sunfishswim.com/">sunfishswim.com</a> or <a href="tel:+19163138754">(916) 313-8754</a>.</p>
<p><strong>More notes</strong></p>
<ul>{more}</ul>
<p><a href="/notes/">All notes</a></p>
</div>
</div></article>"""
    schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
              "description": p["desc"], "datePublished": p["date"], "dateModified": p["date"],
              "mainEntityOfPage": url, "url": url, "image": SITE + "/doug-muraki.jpg",
              "author": PERSON, "publisher": PERSON, "isPartOf": {"@type": "Blog", "@id": SITE + "/notes/#blog"}}
    d = out / p["slug"]
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(page(f"{p['title']} | Doug Muraki", p["desc"], url, body, schema))

items = "\n".join(
    f'<li><p class="meta"><time datetime="{p["date"]}">{fmt(p["date"])}</time></p>'
    f'<a class="t" href="/notes/{p["slug"]}/">{html.escape(p["title"])}</a><p>{html.escape(p["desc"])}</p></li>'
    for p in posts)
idx_body = f"""<div class="post"><div class="wrap">
<p class="eyebrow">Notes</p>
<h1>Notes from running Sunfish Pool Service</h1>
<p class="lede">How we run the company and why, what we see at Sacramento pools week to week, and what the crew does that makes it work. Written by Doug Muraki, owner.</p>
<ul class="note-list">
{items}
</ul>
</div></div>"""
idx_schema = {"@context": "https://schema.org", "@type": "Blog", "@id": SITE + "/notes/#blog",
              "name": "Notes from running Sunfish Pool Service", "url": SITE + "/notes/", "author": PERSON,
              "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/notes/{p['slug']}/", "datePublished": p["date"]} for p in posts]}
(out / "index.html").write_text(page("Notes | Doug Muraki, Sunfish Pool Service", "Notes from Doug Muraki on running Sunfish Pool Service in Sacramento: how the work gets done and why.", SITE + "/notes/", idx_body, idx_schema, "website"))

# homepage: latest three between markers
latest = "\n".join(
    f'<li><p class="meta"><time datetime="{p["date"]}">{fmt(p["date"])}</time></p>'
    f'<a class="t" href="/notes/{p["slug"]}/">{html.escape(p["title"])}</a></li>' for p in posts[:3])
block = (f'<!--NOTES-->\n<section id="notes"><div class="wrap"><h2>Notes from the business</h2><div class="body">\n'
         f'<ul class="note-list">\n{latest}\n</ul>\n<p style="margin-top:1.5rem"><a href="/notes/">All notes</a></p>\n'
         f'</div></div></section>\n<!--/NOTES-->')
if "<!--NOTES-->" in index_html:
    index_html = re.sub(r"<!--NOTES-->.*?<!--/NOTES-->", block, index_html, flags=re.S)
else:
    index_html = index_html.replace('<section id="work">', block + '\n\n<section id="work">', 1)
if ".note-list" not in index_html:
    index_html = index_html.replace("</style>", "\n".join(l for l in extra_css.splitlines() if l.startswith(".note-list") or l.startswith(".meta")) + "\n</style>", 1)
index_html = index_html.replace('<a href="#values">Values</a>', '<a href="/notes/">Notes</a>')
if '"@id"' not in index_html.split("</script>")[0]:
    index_html = index_html.replace('{"@context":"https://schema.org","@type":"Person",', '{"@context":"https://schema.org","@type":"Person","@id":"https://dougmuraki.com/#doug",', 1)
(ROOT / "index.html").write_text(index_html)

today = max(p["date"] for p in posts)
urls = [(SITE + "/", today), (SITE + "/notes/", today)] + [(f"{SITE}/notes/{p['slug']}/", p["date"]) for p in posts]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm += "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n  </url>\n" for u, d in urls)
sm += "</urlset>\n"
(ROOT / "sitemap.xml").write_text(sm)
print(f"built {len(posts)} notes")
