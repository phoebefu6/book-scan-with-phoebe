"""Turn codex sprites (white background) into trimmed transparent webp for the site.
Run with the project venv:  .venv/bin/python scripts/clean_sprites.py
Flood-fills near-white from the image border only, so white *inside* the outline
(the bunny's fur) survives."""
import pathlib, sys
from collections import deque
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "art" / "raw", ROOT / "docs" / "assets" / "sprites"
OUT.mkdir(parents=True, exist_ok=True)
MAX = 480

def near_white(p, tol=28):
    return p[0] > 255 - tol and p[1] > 255 - tol and p[2] > 255 - tol

def clean(src, dst):
    im = Image.open(src).convert("RGBA")
    im.thumbnail((720, 720))
    w, h = im.size
    px = im.load()
    bg = bytearray(w * h)
    q = deque()
    for x in range(w):
        q.append((x, 0)); q.append((x, h - 1))
    for y in range(h):
        q.append((0, y)); q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        i = y * w + x
        if bg[i] or not near_white(px[x, y]):
            continue
        bg[i] = 1
        if x > 0: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y > 0: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))
    mask = Image.frombytes("L", (w, h), bytes(0 if b else 255 for b in bg))
    mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    im.putalpha(mask)
    box = im.getbbox()
    if box:
        im = im.crop(box)
    im.thumbnail((MAX, MAX))
    im.save(dst, "WEBP", quality=88, method=6)

names = sys.argv[1:]
for src in sorted(RAW.glob("*.png")):
    if names and src.stem not in names:
        continue
    dst = OUT / f"{src.stem}.webp"
    if dst.exists() and dst.stat().st_mtime > src.stat().st_mtime and not names:
        continue
    clean(src, dst)
    print("cleaned", src.stem, round(dst.stat().st_size / 1024), "KB")
