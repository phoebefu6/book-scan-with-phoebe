#!/usr/bin/env python3
"""Build the Book Scan with Phoebe village into docs/ (GitHub Pages).

Stdlib only. Reads:
  books/<slug>/book.json   public book content (written by the book-scan skill)
  books/<slug>/mindmap.md  markmap outline
  sprouts.json             to-read titles (sprouts, not counted toward the goal)
  config/village.json      districts, landmarks, growth thresholds

Privacy: this script never reads ~/knowledge. Everything it publishes must already be
in books/ — the skill decides what is public before writing book.json.
"""
import datetime
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
DOCS = ROOT / "docs"
SPRITES = DOCS / "assets" / "sprites"
CFG = json.loads((ROOT / "config" / "village.json").read_text(encoding="utf-8"))
DISTRICTS = {d["id"]: d for d in CFG["districts"]}
READ_WITH_PHOEBE = "https://phoebefu6.github.io/read-with-phoebe/"

D3 = "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"
MM_LIB = "https://cdn.jsdelivr.net/npm/markmap-lib@0.18.12/dist/browser/index.iife.min.js"
MM_VIEW = "https://cdn.jsdelivr.net/npm/markmap-view@0.18.12/dist/browser/index.min.js"

FALLBACK_EMOJI = {"house-life": "🏠", "house-work": "🏪", "house-mind": "🔭", "house-history": "🏯",
                  "house-story": "🍄", "sprout": "🌱", "ghost-plot": "🪧", "lm-bakery": "🥐",
                  "lm-fountain": "⛲", "lm-library": "📚", "lm-townhall": "🏛️", "lm-station": "🚂",
                  "lm-castle": "🏰"}

e = html.escape


def house_sprite(d, st, alt="", cls="", prefix=""):
    """A district's house at growth stage st. Auto-created districts borrow a base family, hue-shifted,
    until their own art is drawn."""
    sid = f"{d['sprite']}-{st}"
    if not (SPRITES / f"{sid}.webp").exists() and d.get("base"):
        img = sprite(f"{d['base']}-{st}", alt, cls, prefix)
        return img.replace("<img ", f'<img style="filter:hue-rotate({int(d.get("hue", 90))}deg)" ', 1)
    return sprite(sid, alt, cls, prefix)


def sprite(sid, alt="", cls="", prefix=""):
    """<img> if the sprite exists, else a big emoji stand-in so the site works before art lands."""
    if (SPRITES / f"{sid}.webp").exists():
        return f'<img class="{cls}" src="{prefix}assets/sprites/{sid}.webp" alt="{e(alt)}" loading="lazy">'
    base = re.sub(r"-\d$", "", sid)
    emo = FALLBACK_EMOJI.get(base, FALLBACK_EMOJI.get(sid, "🐰"))
    return f'<span class="{cls} emoji-sprite" role="img" aria-label="{e(alt)}">{emo}</span>'


def stage(book):
    n = book.get("thought_count", len(book.get("thoughts", [])))
    g = CFG["growth"]
    return 3 if n >= g["stage3_at"] else 2 if n >= g["stage2_at"] else 1


def load_books():
    books = []
    for p in sorted((ROOT / "books").glob("*/book.json")):
        b = json.loads(p.read_text(encoding="utf-8"))
        b["slug"] = p.parent.name
        mm = p.parent / "mindmap.md"
        b["mindmap"] = mm.read_text(encoding="utf-8") if mm.exists() else ""
        books.append(b)
    books.sort(key=lambda b: (b.get("scanned", ""), b["title"]))
    return books


def inline(text):
    """Tiny markdown: **bold**, *em*, `code`. Input is escaped first."""
    t = e(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<em>\1</em>", t)
    return t


def paras(text):
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().splitlines()
        if all(l.lstrip().startswith(("- ", "• ")) for l in lines):
            out.append("<ul>" + "".join(f"<li>{inline(l.lstrip()[2:])}</li>" for l in lines) + "</ul>")
        else:
            out.append(f"<p>{inline(' '.join(l.strip() for l in lines))}</p>")
    return "".join(out)


def src_link(label, url):
    if not label:
        return ""
    if url:
        return f'<a class="src" href="{e(url)}" target="_blank" rel="noopener">{e(label)} ↗</a>'
    return f'<span class="src">{e(label)}</span>'


# ---------------------------------------------------------------- page shell

FONTS = ("https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800"
         "&family=Nunito:wght@400;600;700&family=ZCOOL+KuaiLe&display=swap")


def shell(title, body, prefix="", extra_head="", desc=""):
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc or 'Phoebe 的读书小镇 · a cute village that grows one house per book')}">
<link rel="icon" href="{prefix}assets/sprites/bunny-hero.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/village.css">
{extra_head}
</head>
<body>
{body}
<footer class="foot">
  <p>🐰 Book Scan with Phoebe · 菲比的读书小镇</p>
  <p class="small">Notes stay private · 笔记原文不公开 · quotes are short and sourced · 引用简短并附来源</p>
  <p class="small"><a href="{READ_WITH_PHOEBE}">More book art → read-with-phoebe 读书图集</a></p>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------- homepage

ENCOURAGE = [
    ("Every 💭 you write makes a house taller.", "每写一条想法，房子就长高一点。"),
    ("Type any title on the Scan Desk and a sprout appears.", "在扫书台写下书名，就会冒出一棵小芽。"),
    ("Your next house already has a plot waiting.", "下一本书的空地已经留好啦。"),
    ("Small notes count. One sentence of your own is a brick.", "一句自己的话，就是一块砖。"),
    ("The bunny saved you a sunny spot.", "小兔子给你留了个向阳的位置。"),
]


def milestone_track(n):
    lms = CFG["landmarks"]
    stops = [0] + [l["at"] for l in lms]
    # equal-width segments between milestones, so 10 and 25 aren't squashed against 400
    seg = 100 / (len(stops) - 1)
    pos = 0.0
    for i in range(1, len(stops)):
        lo, hi = stops[i - 1], stops[i]
        if n >= hi:
            pos = seg * i
        else:
            pos = seg * (i - 1) + seg * max(0, n - lo) / (hi - lo)
            break
    marks = []
    for i, l in enumerate(lms, 1):
        got = n >= l["at"]
        marks.append(
            f'<li class="mark {"got" if got else ""}" style="left:{seg * i:.2f}%">'
            f'<span class="dot">{"✓" if got else l["at"]}</span>'
            f'<span class="mlabel">{e(l["zh"])}</span></li>')
    nxt = next((l for l in lms if n < l["at"]), None)
    if nxt:
        left = nxt["at"] - n
        msg = (f'再盖 <b>{left}</b> 座房子，<b>{e(nxt["zh"])}</b> 就会开张 · '
               f'{left} more {"house" if left == 1 else "houses"} to open the {e(nxt["en"])}')
    else:
        msg = "城堡建成啦！The Castle of Books is open! 🏰"
    return f"""
<section class="track" aria-label="progress to {CFG['goal']} books">
  <div class="track-top">
    <div class="count"><span class="big">{n}</span><span class="of">/ {CFG['goal']}</span>
      <span class="unit">座房子 houses</span></div>
    <p class="next">{msg}</p>
  </div>
  <div class="bar"><div class="fill" style="width:{pos:.2f}%"></div>
    <ul class="marks">{''.join(marks)}</ul></div>
</section>"""


def house_card(b, prefix=""):
    d = DISTRICTS[b["district"]]
    st = stage(b)
    n = b.get("thought_count", len(b.get("thoughts", [])))
    hearts = f'<span class="tc" title="{n} 条想法 thoughts">💭 {n}</span>' if n else ""
    return f"""<a class="house st{st}" href="{prefix}books/{e(b['slug'])}.html">
  {house_sprite(d, st, b['title'], 'hs')}
  <span class="hname">{e(b['short_title'] if b.get('short_title') else b['title'])}</span>
  <span class="hmeta">{e(b.get('author', ''))} {hearts}</span>
</a>"""


def ghost_card(d):
    return f"""<a class="house ghost" href="add.html" title="Plant your next {e(d['en'])} book">
  {sprite('ghost-plot', 'empty plot', 'hs')}
  <span class="hname">下一本住这里</span>
  <span class="hmeta">your next book lives here</span>
</a>"""


def sprout_card(s):
    return f"""<div class="house sprout" title="想读 want to read">
  {sprite('sprout', s['title'], 'hs')}
  <span class="hname">{e(s['title'])}</span>
  <span class="hmeta">🌱 想读 want to read</span>
</div>"""


def build_home(books, sprouts):
    n = len(books)
    by_d = {d: [b for b in books if b["district"] == d] for d in DISTRICTS}
    sp_d = {d: [s for s in sprouts if s.get("district") == d] for d in DISTRICTS}
    loose = [s for s in sprouts if s.get("district") not in DISTRICTS]

    lm_html = []
    for l in CFG["landmarks"]:
        got = n >= l["at"]
        lm_html.append(f"""<figure class="lm {'got' if got else 'locked'}">
  {sprite(l['id'], l['en'], 'ls')}
  <figcaption>{e(l['zh'])}<br><small>{e(l['en'])} · {'开张啦 open' if got else f'🔒 {l["at"]}'}</small></figcaption>
</figure>""")

    islands = []
    for d in CFG["districts"]:
        hs = by_d[d["id"]]
        cards = [house_card(b) for b in hs] + [sprout_card(s) for s in sp_d[d["id"]]] + [ghost_card(d)]
        islands.append(f"""<section class="island" id="{d['id']}">
  <header class="sign"><span class="semoji">{d['emoji']}</span>
    <h2>{e(d['zh'])} <small>{e(d['en'])}</small></h2>
    <span class="scount">{len(hs)} 座</span></header>
  <div class="plots">{''.join(cards)}</div>
</section>""")
    if loose:
        islands.append(f"""<section class="island garden" id="garden">
  <header class="sign"><span class="semoji">🌱</span><h2>小芽花园 <small>Sprout Garden</small></h2>
    <span class="scount">{len(loose)} 棵</span></header>
  <div class="plots">{''.join(sprout_card(s) for s in loose)}</div>
</section>""")

    enc = json.dumps(ENCOURAGE, ensure_ascii=False)
    body = f"""
<header class="hero">
  <div class="cloud c1"></div><div class="cloud c2"></div><div class="cloud c3"></div>
  <div class="hero-in">
    {sprite('bunny-hero', 'Reading bunny mascot', 'mascot')}
    <div>
      <p class="kicker">Book Scan with Phoebe</p>
      <h1>菲比的读书小镇</h1>
      <p class="lede">每读完一本书，小镇就多一座房子。<br>One book, one little house. Let's build a town of 400.</p>
      <div class="bubble" id="bubble">…</div>
      <p><a class="addbig" href="add.html">＋ 加一本书 · Add a book</a></p>
    </div>
  </div>
</header>
<main class="town">
{milestone_track(n)}
<section class="island plaza" id="plaza">
  <header class="sign"><span class="semoji">⛲</span><h2>中心广场 <small>Town Plaza</small></h2>
    <span class="scount">{sum(n >= l['at'] for l in CFG['landmarks'])} / {len(CFG['landmarks'])} 地标</span></header>
  <div class="lms">{''.join(lm_html)}</div>
</section>
<div class="walkway" aria-hidden="true">{sprite('bunny-walk', '', 'walker')}</div>
<div class="islands">
{''.join(islands)}
</div>
<section class="howto">
  <h2>怎么盖房子 <small>How a house gets built</small></h2>
  <ol class="steps">
    <li>{sprite('bunny-write', '', 'step-img')}<b>写下书名和笔记</b><span>Tap ＋ Add a book. Notes stay in a private form</span></li>
    <li>{sprite('bunny-reading', '', 'step-img')}<b>小兔子去查资料</b><span>Claude searches the web, tidies and enriches your notes</span></li>
    <li>{sprite('bunny-cheer', '', 'step-img')}<b>新房子落成</b><span>A house with a mindmap, famous lines, 5 takeaways and 5 push-backs</span></li>
  </ol>
</section>
</main>
<script>
(function(){{
  var msgs = {enc};
  var el = document.getElementById('bubble'), i = Math.floor(Math.random()*msgs.length);
  function show(){{ var m = msgs[i % msgs.length]; el.innerHTML = m[1] + '<br><small>' + m[0] + '</small>'; i++; }}
  show(); setInterval(show, 6000);
}})();
</script>"""
    (DOCS / "index.html").write_text(shell("Book Scan with Phoebe · 菲比的读书小镇", body), encoding="utf-8")


# ---------------------------------------------------------------- desk explainer (public)

VAULT_FORM = "https://github.com/phoebefu6/phoebe-reading-vault/issues/new?template=book-scan.yml"
SPROUT_FORM = "https://github.com/phoebefu6/book-scan-with-phoebe/issues/new?template=sprout.yml"


def build_add_page():
    opts = "".join(f'<option value="{e(d["zh"])}">{d["emoji"]} {e(d["zh"])} · {e(d["en"])}</option>'
                   for d in CFG["districts"])
    body = f"""
<main class="page narrow">
  <a class="back" href="index.html">← 回小镇 Back to town</a>
  <section class="card addcard">
    <div class="center">{sprite('bunny-write', 'bunny writing', 'mascot sm')}
      <h1>加一本书 <small>Add a book</small></h1>
      <p class="hint">写下书名，选个街区，然后选一个按钮。</p></div>
    <form id="addf" onsubmit="return false">
      <label for="t">📖 书名 <small>Book title</small></label>
      <input id="t" type="text" required placeholder="比如：被讨厌的勇气" autocomplete="off">
      <label for="a">✍️ 作者 <small>Author (optional)</small></label>
      <input id="a" type="text" placeholder="不知道也没关系" autocomplete="off">
      <label for="c">🏘️ 街区 <small>Category</small></label>
      <select id="c">
        <option value="">🐰 让小兔子决定 · let the bunny decide</option>
        {opts}
        <option value="__new">✨ 新街区… · a new category</option>
      </select>
      <input id="cn" type="text" placeholder="新街区的名字，比如：旅行与美食" hidden autocomplete="off">
      <div class="addbtns">
        <button class="btn" id="withnotes" type="button">📒 加书和笔记<small>Add with notes · 笔记私人保存</small></button>
        <button class="btn mint" id="sprout" type="button">🌱 只是想读<small>Just want to read · 1 分钟出现</small></button>
      </div>
      <p class="hint">📒 opens a private form in Phoebe's vault (only she can open it). The house is built next time she tells Claude <b>scan</b>.<br>
      🌱 opens the village's sprout form; the sprout appears in about a minute.</p>
    </form>
  </section>
</main>
<script>
(function(){{
  var $ = function(i){{ return document.getElementById(i); }};
  $('c').onchange = function(){{ $('cn').hidden = $('c').value !== '__new'; if (!$('cn').hidden) $('cn').focus(); }};
  function cat(){{ return $('c').value === '__new' ? $('cn').value.trim() : $('c').value; }}
  function go(base, emoji, withAuthor){{
    var t = $('t').value.trim();
    if (!t) {{ $('t').focus(); $('t').classList.add('shake'); setTimeout(function(){{ $('t').classList.remove('shake'); }}, 500); return; }}
    var q = '&title=' + encodeURIComponent(emoji + ' ' + t) + '&book=' + encodeURIComponent(t) + '&category=' + encodeURIComponent(cat());
    if (withAuthor) q += '&author=' + encodeURIComponent($('a').value.trim());
    window.open(base + q, '_blank', 'noopener');
  }}
  $('withnotes').onclick = function(){{ go({json.dumps(VAULT_FORM)}, '📚', true); }};
  $('sprout').onclick = function(){{ go({json.dumps(SPROUT_FORM)}, '🌱', false); }};
}})();
</script>"""
    (DOCS / "add.html").write_text(shell("Add a book · 加一本书", body), encoding="utf-8")
    old = DOCS / "desk.html"
    if old.exists():
        old.unlink()


# ---------------------------------------------------------------- book page

def build_book(b, books):
    d = DISTRICTS[b["district"]]
    st = stage(b)
    zh = b.get("lang", "zh") == "zh"
    L = (lambda z, en: z) if zh else (lambda z, en: en)

    quotes = "".join(
        f'<li><blockquote>“{inline(q["text"])}”</blockquote>{src_link(q.get("source_label"), q.get("source_url"))}</li>'
        for q in b.get("quotes", []))
    takes = "".join(
        f'<li><h3>{inline(t["title"])}</h3>{paras(t["body"])}</li>' for t in b.get("takeaways", []))
    pushes = "".join(
        f'''<li><p class="claim"><span class="tag">{L("书里说", "The book says")}</span>{inline(p["claim"])}</p>
<div class="argue"><span class="tag pink">{L("我们反驳", "Push back")}</span>{paras(p["argue"])}</div>
<p class="who">{src_link(p.get("source_label"), p.get("source_url")) if p.get("source_label") else '<span class="src">【补充】' + L("Claude 的论证，非引文", "Claude's own argument, not a citation") + '</span>'}</p></li>'''
        for p in b.get("pushback", []))
    note = "".join(f'<section class="nsec"><h3>{inline(s["heading"])}</h3>{paras(s["body"])}</section>'
                   for s in b.get("note", []))
    thoughts = b.get("thoughts", [])
    th_html = ("".join(f"<li>💭 {inline(t)}</li>" for t in thoughts) if thoughts else
               f'<li class="empty">{L("这里还空着。下次读到心动的句子，写一句自己的话，房子就会长高。", "Empty for now. One sentence of your own makes this house grow.")}</li>')
    n_th = b.get("thought_count", len(thoughts))
    nxt_stage = {1: CFG["growth"]["stage2_at"], 2: CFG["growth"]["stage3_at"]}.get(st)
    grow_msg = (L(f"再写 {nxt_stage - n_th} 条想法，房子长到第 {st + 1} 层", f"{nxt_stage - n_th} more thoughts to grow floor {st + 1}")
                if nxt_stage else L("房子已经长到最高啦 🎉", "Fully grown 🎉"))

    links = []
    if b.get("links", {}).get("read_with_phoebe"):
        links.append(f'<a class="pill" href="{e(b["links"]["read_with_phoebe"])}">🖼️ {L("信息图", "Infographics")}</a>')
    for k, label in (("douban", "豆瓣 Douban"), ("goodreads", "Goodreads"), ("weread", "微信读书 WeRead")):
        if b.get("links", {}).get(k):
            links.append(f'<a class="pill" href="{e(b["links"][k])}" target="_blank" rel="noopener">{label} ↗</a>')

    i = books.index(b)
    prev_b, next_b = books[i - 1] if i else None, books[i + 1] if i + 1 < len(books) else None
    nav = '<nav class="pn">' + (
        f'<a href="{e(prev_b["slug"])}.html">← {e(prev_b.get("short_title") or prev_b["title"])}</a>' if prev_b else "<span></span>") + (
        f'<a href="{e(next_b["slug"])}.html">{e(next_b.get("short_title") or next_b["title"])} →</a>' if next_b else "<span></span>") + "</nav>"

    mm = b["mindmap"]
    mm_json = json.dumps(mm, ensure_ascii=False).replace("</", "<\\/")
    head = f"""<script src="{D3}"></script>
<script src="{MM_VIEW}"></script>
<script src="{MM_LIB}"></script>"""

    body = f"""
<main class="page">
  <a class="back" href="../index.html#{d['id']}">← {d['emoji']} {e(d['zh'])} · {e(d['en'])}</a>
  <header class="bookhead card">
    <div class="bh-art">{house_sprite(d, st, b['title'], 'bh-house', '../')}
      <p class="grow">{grow_msg}</p></div>
    <div class="bh-text">
      <p class="kicker">{d['emoji']} {e(d['zh'])} · {L('扫书于', 'scanned')} {e(b.get('scanned', ''))}</p>
      <h1>{e(b['title'])}</h1>
      <p class="author">{e(b.get('author', ''))}{(' · ' + e(b['original_title'])) if b.get('original_title') else ''}</p>
      <p class="intro">{inline(b.get('intro', ''))}</p>
      <p class="intro-src">{src_link(b.get('intro_source', {}).get('label'), b.get('intro_source', {}).get('url'))}</p>
      <div class="pills">{''.join(links)}</div>
    </div>
  </header>

  <nav class="jump">
    <a href="#quotes">🌟 {L('名句', 'Famous lines')}</a>
    <a href="#take">🌿 {L('5 个收获', '5 takeaways')}</a>
    <a href="#push">🔥 {L('5 个质疑', '5 push-backs')}</a>
    <a href="#map">🗺️ {L('脑图', 'Mindmap')}</a>
    <a href="#note">📒 {L('笔记', 'Note')}</a>
    <a href="#mine">💭 {L('我的想法', 'My thoughts')}</a>
  </nav>

  {f'''<section class="card"><h2>👤 {L('关于作者', 'About the author')}</h2>{paras(b['about_author'])}</section>''' if b.get('about_author') else ''}

  <section class="card" id="quotes">
    <h2>🌟 {L('让这本书出名的句子', 'The lines that made it famous')}</h2>
    <ol class="quotes">{quotes}</ol>
  </section>

  <section class="card mint" id="take">
    <h2>🌿 {L('值得带走的 5 点', '5 things worth taking away')}</h2>
    <ol class="takes">{takes}</ol>
  </section>

  <section class="card pinkc" id="push">
    <h2>🔥 {L('5 个值得质疑的观点', '5 claims worth arguing with')}</h2>
    <ol class="pushes">{pushes}</ol>
  </section>

  <section class="card" id="map">
    <h2>🗺️ {L('脑图复习', 'Mindmap recap')}</h2>
    <p class="hint">{L('拖动、缩放，点圆点展开或收起。', 'Drag, zoom, click a dot to fold or unfold.')}</p>
    <div class="mmwrap"><svg id="mm"></svg></div>
  </section>

  <section class="card" id="note">
    <h2>📒 {L('整理后的笔记', 'The tidied note')}</h2>
    {note}
  </section>

  <section class="card mine" id="mine">
    <h2>💭 {L('我的想法', 'My own thoughts')} <small>{n_th}</small></h2>
    <ul class="thoughts">{th_html}</ul>
  </section>
  {nav}
</main>
<script>
(function(){{
  var md = {mm_json};
  var M = window.markmap;
  if (!md || !M || !M.Transformer) return;
  var r = new M.Transformer().transform(md);
  var opts = M.deriveOptions((r.frontmatter || {{}}).markmap);
  var pal = ['#E58BA3', '#5FB37F', '#E8A15C', '#8C7BD8', '#4FA7B8', '#D9708C'];
  opts.color = function (n) {{ var p = ((n.state && n.state.path) || '').split('.'); return pal[(parseInt(p[1] || '0', 10) || 0) % pal.length]; }};
  var mm = M.Markmap.create('#mm', opts, r.root);
  // markmap can measure before CJK webfonts settle -> every node size [0,0] and the layout
  // collapses into one overlapping line. setData() with no arg re-measures; then fit.
  function refit() {{ try {{ Promise.resolve(mm.setData()).then(function () {{ mm.fit(); }}); }} catch (e) {{}} }}
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
  requestAnimationFrame(function () {{ requestAnimationFrame(refit); }});
  setTimeout(refit, 400);
  window.addEventListener('resize', refit);
}})();
</script>"""
    out = DOCS / "books" / f"{b['slug']}.html"
    out.write_text(shell(f"{b['title']} · Book Scan with Phoebe", body, "../", head,
                         desc=b.get("intro", "")[:150]), encoding="utf-8")


def main():
    books = load_books()
    for b in books:
        assert b.get("district") in DISTRICTS, f"{b['slug']}: unknown district {b.get('district')}"
    sprouts = json.loads((ROOT / "sprouts.json").read_text(encoding="utf-8"))
    (DOCS / "books").mkdir(parents=True, exist_ok=True)
    css = ROOT / "assets" / "village.css"
    (DOCS / "assets" / "village.css").write_text(css.read_text(encoding="utf-8"), encoding="utf-8")
    build_home(books, sprouts)
    build_add_page()
    keep = {f"{b['slug']}.html" for b in books}
    for old in (DOCS / "books").glob("*.html"):
        if old.name not in keep:
            old.unlink()          # a book removed from books/ must not linger on the public site
    for b in books:
        build_book(b, books)
    (DOCS / ".nojekyll").write_text("")
    print(f"built {len(books)} houses, {len(sprouts)} sprouts -> docs/  ({datetime.date.today()})")


if __name__ == "__main__":
    main()
