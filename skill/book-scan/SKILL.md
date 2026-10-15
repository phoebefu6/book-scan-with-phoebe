---
name: book-scan
description: Phoebe's Book Scan village (book-scan-with-phoebe). Use when she says "scan", "scan it", "scan my books", "scan this book", "扫书", "盖房子", "add a book to the village", gives a book title and notes to tidy and enrich, wants a book's author + intro + famous lines + 5 takeaways + 5 counter-arguments + mindmap, wants to plant a to-read sprout, open the Scan Desk, or publish/update a house on the village site. Also use when she asks how the village, districts, landmarks or the 400-book goal work.
---

# book-scan

```
website "＋ 加一本书" (add.html)
  ├─ 📒 Add with notes → issue form in PRIVATE phoebe-reading-vault (label book-scan)
  │      "scan" on the Mac → scripts/scan_queue.py list → research → seeds/<slug>.py
  │      → books/<slug>/ → build.py → preview → her 👍 → push → scan_queue.py done <n> <slug>
  └─ 🌱 Just want to read → issue form in public repo → .github/workflows/sprout.yml
         (only if author is phoebefu6) → sprouts.json → build → commit → close   (≈1 min, automatic)
```

She chose (2026-10-15): add books **on the website**, notes stay private in the vault, and Claude
on her Mac builds the house when she says "scan" (no API key, no cost). The local Scan Desk
(`desk/desk.py`) still works as a preview server and an offline input, but it is not the main path.

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

## "scan" — steps

1. **Queue:** `python3 scripts/scan_queue.py list` (open `book-scan` issues in the private vault,
   fields parsed: book, author, category, notes, public_thoughts, private_thoughts). Also check
   `~/knowledge/03-inbox/book-scan/` for Desk files with `status: waiting`. Nothing waiting → say so.
2. **Identify the book.** WeRead first (key in `WEREAD_API_KEY`):
   `/store/search` → bookId → `/book/info` (intro, author, publisher) →
   `python3 ~/knowledge/skills/book-partner/scripts/weread_sync.py best <bookId>` (famous lines) →
   `weread_link.py <bookId>` (public link). Not on WeRead → `anysearch` (Douban, Goodreads).
3. **Research push-backs** with `anysearch` `batch_search` (max 5 queries per call): Douban
   reviews, critics, replication studies. `extract` often fails on Douban/Goodreads/Zhihu; search
   snippets with URLs are acceptable sources.
4. **Category:** `python3 scripts/village.py "<her category>" ["English name"] ["emoji"]` returns
   the district id. It matches existing ones (id / 中文 / English / keywords like 心理→life,
   小说→story); **if nothing matches it creates a new district** in `config/village.json` with a
   borrowed, hue-shifted house family so it renders at once. Empty category → you pick the best
   existing one (or create one if none fits). Sprouts from the website auto-create the same way.
5. **New district art** (any district with `"auto": true` and no `house-<id>-1.webp`): add three
   items `house-<id>-1/2/3` to `art/sprites.json` (stage 2 and 3 `ref` stage 1; give the family its
   own shape and a **closed puffy roof**), run `python3 art/gen.py house-<id>-1 house-<id>-2
   house-<id>-3` (~4 min, throttled), clean with `.venv/bin/python scripts/clean_sprites.py`, look
   at them, then remove `base`/`hue`/`auto` from the district. Follow `cute-village-art`.
6. **Write `seeds/<slug>.py`** (copy any existing seed; slug is ascii pinyin/english) with
   `BOOK` + `MINDMAP`, then `python3 scripts/new_book.py seeds/<slug>.py` (validates 5 + 5,
   ≤10 quotes, every quote sourced). `thoughts` = her public thoughts **verbatim**;
   `thought_count` = public + private full-sentence thoughts.
7. **Private full note** → `~/knowledge/01-books/<title>/<title>-扫书.md` with vault provenance
   tags (【我】 her words verbatim, 【补充】 your enrichment). This is where the full tidy lives.
8. `python3 build.py`. **Preview** with `preview_start {name: "scan-desk"}` →
   `/village/books/<slug>.html`. Screenshots only capture at scrollY 0: hide sections above with JS
   to inspect lower ones. Show her.
9. On her 👍: `git add -A && git commit && git push` (SSH remote on the main Mac), then
   `python3 scripts/scan_queue.py done <issue#> <slug>` (or set the Desk file to `status: scanned`).

## Sprouts and growth

- 🌱 sprouts come from the website form (automatic) or the Desk; `sprouts.json`, title only. Not counted toward 400.
- When a sprouted title gets scanned, remove it from `sprouts.json`.
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
- `build.py` deletes `docs/books/*.html` for books no longer in `books/`. Don't hand-place pages there.
- The sprout workflow runs only for issues opened by `phoebefu6`; anyone can open issues on a public repo.

## Self-iterate

After every scan, add anything learned (with its cost) to `CHANGELOG.md` next to this file and fix
any stale line above.
