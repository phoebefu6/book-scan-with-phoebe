# 🐰 Book Scan with Phoebe · 菲比的读书小镇

One book, one little house. A cute light-green and light-pink village that grows toward 400 books.

**Live:** https://phoebefu6.github.io/book-scan-with-phoebe/

Each house is a book page with: author and intro (sourced), up to 10 famous lines (sourced),
5 takeaways, 5 strong push-backs, a mindmap to recap, a tidied note, and Phoebe's own 想法.

## How a house gets built

1. On the site, tap **＋ 加一本书 · Add a book** (`add.html`): title, optional author, a category
   (pick one, let the bunny decide, or type a new one and it gets created).
   - **📒 Add with notes** opens a form in Phoebe's **private** vault repo. Notes and private
     thoughts stay there.
   - **🌱 Just want to read** opens this repo's sprout form; a GitHub Action plants the sprout in
     about a minute (only for issues Phoebe opens).
2. Phoebe tells Claude **"scan"** on her Mac. The `book-scan` skill (`skill/book-scan/SKILL.md`)
   reads the queue (`scripts/scan_queue.py`), researches the book, writes `books/<slug>/`, draws
   art for any new category, runs `python3 build.py`, and shows a preview.
3. After her 👍 it pushes; GitHub Pages serves `docs/`.

Optional local preview / offline input: `python3 desk/desk.py` → http://127.0.0.1:4600 (`/village/`).

## What is public and what is not

| Public (this repo) | Private (never here) |
|---|---|
| Book facts, intro, sourced quotes, takeaways, push-backs, mindmap | Her raw notes |
| 想法 she marked 🌍 public | 想法 she kept 🔒 private (they still grow the house) |
| To-read titles (sprouts) | Her WeRead highlights |

## Village rules

- 🌱 want-to-read = sprout (not counted) · 🏠 scanned = house (counts toward 400) · every 💭 grows it
- Houses grow to 2 floors at 2 thoughts, 3 floors at 5
- Landmarks open at 10 🥐 · 25 ⛲ · 50 📚 · 100 🏛️ · 200 🚂 · 400 🏰
- Districts: 🌸 Life Lane · 💼 Work Square · 🔭 Mind & Tech Park · 🏯 History Hill · 🍄 Story Woods,
  plus any new category typed on the add page (created automatically by `scripts/village.py`)

## Build

```bash
python3 build.py                                  # stdlib only → docs/
python3 -m venv .venv && .venv/bin/pip install pillow
.venv/bin/python scripts/clean_sprites.py         # art/raw/*.png → docs/assets/sprites/*.webp
python3 art/gen.py [id ...]                       # codex sprites, throttled; see cute-village-art skill
```

Art style, prompts and the rejects log live in the `cute-village-art` skill in
[phoebe-visual-skills](https://github.com/phoebefu6/phoebe-visual-skills).
