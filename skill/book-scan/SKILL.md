---
name: book-scan
description: Phoebe's Book Scan village (book-scan-with-phoebe). Use when she says "scan it", "scan this book", "扫书", "盖房子", "add a book to the village", gives a book title and notes to tidy and enrich, wants a book's author + intro + famous lines + 5 takeaways + 5 counter-arguments + mindmap, wants to plant a to-read sprout, open the Scan Desk, or publish/update a house on the village site. Also use when she asks how the village, districts, landmarks or the 400-book goal work.
---

# book-scan

```
Scan Desk (private, 127.0.0.1:4600)  →  ~/knowledge/03-inbox/book-scan/*.md   (status: waiting)
        "scan it"  →  research  →  seeds/<slug>.py  →  books/<slug>/{book.json,mindmap.md}
        →  python3 build.py  →  preview /village/  →  her 👍  →  commit + push  →  GitHub Pages
```

Repo: `~/book-scan-with-phoebe` → `phoebefu6/book-scan-with-phoebe` (public) →
https://phoebefu6.github.io/book-scan-with-phoebe/

## Hard rules (privacy and sourcing)

1. **Public repo.** Nothing from `~/knowledge` goes public except: her 想法 marked
   `[公开 public]` on the Desk (or, for seed books, the non-personal `- 💭` lines she already
   publishes on read-with-phoebe). **Never** her notes text, never her `*-划线.md` highlights.
   Three seed thoughts are held back as too personal (two about betrayal, one about 寻秦记);
   they still count toward `thought_count`. Ask before publishing any of them.
2. **Never edit her 想法.** Copy them byte for byte. Tidy *her notes* into the note sections in
   your own words; her sentences stay hers.
3. **Every quote has a source.** Best source: WeRead popular highlights
   (`weread_sync.py best <bookId>`, label "微信读书热门划线 · N 人划过"). Else a web page that
   quotes it. Max 10, short (cut long ones and mark 节选). Skip lines the book itself quotes from
   someone else unless labelled.
4. **Push-backs cite a real critic, review or study**, verified by a search result you actually
   saw. Otherwise leave `source_label` empty; the page shows 【补充】 Claude's own argument.
5. **Preview, then her 👍, then push.** "scan it" authorises that one book only. Design changes
   always ask first.

## "scan it" — steps

1. Read waiting files in `~/knowledge/03-inbox/book-scan/` (frontmatter `status: waiting`).
2. **Identify the book.** WeRead first (key in `WEREAD_API_KEY`):
   `/store/search` → bookId → `/book/info` (intro, author, publisher) →
   `python3 ~/knowledge/skills/book-partner/scripts/weread_sync.py best <bookId>` (famous lines) →
   `weread_link.py <bookId>` (public link). Not on WeRead → `anysearch` (Douban, Goodreads).
3. **Research push-backs** with `anysearch` `batch_search` (max 5 queries per call): Douban
   reviews, critics, replication studies. `extract` often fails on Douban/Goodreads/Zhihu; search
   snippets with URLs are acceptable sources.
4. **District** (`config/village.json`): life 🌸 people/feelings/memoir · work 💼 work/leadership ·
   mind 🔭 thinking/science/AI/data · history 🏯 · story 🍄 fiction/poetry. Her Desk choice wins.
5. **Write `seeds/<slug>.py`** (copy any existing seed; slug is ascii pinyin/english) with
   `BOOK` + `MINDMAP`, then `python3 scripts/new_book.py seeds/<slug>.py` (it validates 5 + 5,
   ≤10 quotes, every quote sourced). `thought_count` = all her full-sentence thoughts, public or not.
6. **Private full note** → `~/knowledge/01-books/<title>/<title>-扫书.md` with vault provenance
   tags (【我】 her words verbatim, 【补充】 your enrichment). This is where the full tidy lives.
7. `python3 build.py`, then set the inbox file to `status: scanned` and `slug: <slug>`.
8. **Preview** with `preview_start {name: "scan-desk"}` → `/village/books/<slug>.html`. Screenshots
   only capture at scrollY 0: hide sections above with JS to inspect lower ones. Show her.
9. On her 👍: `git add -A && git commit && git push` (SSH remote on the main Mac).

## Sprouts and growth

- 🌱 Desk "just plant a sprout" appends to `sprouts.json` (title only). Not counted toward 400.
- 🏠 a scanned book is a house and counts. Stage by `thought_count`: 0-1 → 1, 2-4 → 2, 5+ → 3.
- Landmarks unlock at 10 / 25 / 50 / 100 / 200 / 400 houses.
- Encourage the **next** book, never audit old ones (past is past, no homework).

## Art

New sprites go through the `cute-village-art` skill (style bible, rejects log, throttled codex
runner). This repo's `art/sprites.json` + `art/gen.py` is the book-scan sprite set;
`.venv/bin/python scripts/clean_sprites.py` turns `art/raw/*.png` into `docs/assets/sprites/*.webp`.

## Traps that cost time

- markmap measures before CJK webfonts load → all nodes stack on one line. `build.py` re-runs
  `mm.setData()` + `fit()` after `document.fonts.ready`. Don't remove it.
- The preview tool reads `~/.claude/launch.json` (home), not a per-project file.

## Self-iterate

After every scan, add anything learned (with its cost) to `CHANGELOG.md` next to this file and fix
any stale line above.
