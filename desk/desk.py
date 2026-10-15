#!/usr/bin/env python3
"""Scan Desk — Phoebe's private note desk. Runs only on her Mac (127.0.0.1).

    python3 desk/desk.py            → http://127.0.0.1:4600

Saves notes to ~/knowledge/03-inbox/book-scan/ (her private vault), never to this repo.
Also serves the built village at /village/ so she can preview houses before publishing.
The only thing it writes into the public repo is sprouts.json (bare titles she wants to read).
"""
import datetime
import json
import os
import pathlib
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
DESK = ROOT / "desk"
INBOX = pathlib.Path(os.environ.get("BOOK_SCAN_INBOX", "~/knowledge/03-inbox/book-scan")).expanduser()
PORT = int(os.environ.get("PORT", "4600"))


def slugify(title):
    s = re.sub(r"[\s/\\:：*?\"<>|（）()「」“”]+", "-", title.strip()).strip("-")
    return s[:40] or "book"


def read_front(p):
    t = p.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---", t, re.S)
    meta = {}
    if m:
        for ln in m.group(1).splitlines():
            if ":" in ln:
                k, v = ln.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def state():
    books = []
    for p in sorted((ROOT / "books").glob("*/book.json")):
        b = json.loads(p.read_text(encoding="utf-8"))
        books.append({"slug": p.parent.name, "title": b.get("short_title") or b["title"],
                      "district": b["district"], "thoughts": b.get("thought_count", 0)})
    queue = []
    if INBOX.exists():
        for p in sorted(INBOX.glob("*.md"), reverse=True):
            m = read_front(p)
            queue.append({"file": p.name, "title": m.get("title", p.stem), "status": m.get("status", "waiting"),
                          "added": m.get("added", "")})
    sprouts = json.loads((ROOT / "sprouts.json").read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / "config" / "village.json").read_text(encoding="utf-8"))
    return {"books": books, "queue": queue, "sprouts": sprouts, "districts": cfg["districts"],
            "goal": cfg["goal"], "inbox": str(INBOX)}


def save_scan(d):
    title = (d.get("title") or "").strip()
    if not title:
        raise ValueError("书名不能为空 · title is required")
    INBOX.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now()
    name = f"{now:%Y%m%d-%H%M}-{slugify(title)}.md"
    thoughts = [t for t in d.get("thoughts", []) if (t.get("text") or "").strip()]
    lines = [
        "---",
        f"title: {title}",
        f"author: {(d.get('author') or '').strip()}",
        f"district: {d.get('district') or ''}",
        f"status: waiting",
        f"added: {now:%Y-%m-%d %H:%M}",
        "source: scan-desk",
        "---",
        "",
        f"# {title}",
        "",
        "## 📒 笔记 Notes（私人 private）",
        "",
        (d.get("notes") or "").strip() or "（还没写 · nothing yet）",
        "",
        "## 💭 我的想法 My thoughts",
        "",
    ]
    for t in thoughts:
        tag = "公开 public" if t.get("public") else "私人 private"
        lines.append(f"- 💭 [{tag}] {t['text'].strip()}")
    if not thoughts:
        lines.append("（还没有 · none yet）")
    (INBOX / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return name


def add_sprout(d):
    title = (d.get("title") or "").strip()
    if not title:
        raise ValueError("书名不能为空 · title is required")
    p = ROOT / "sprouts.json"
    sp = json.loads(p.read_text(encoding="utf-8"))
    if any(s["title"] == title for s in sp):
        return "already"
    sp.append({"title": title, "district": d.get("district") or "", "added": f"{datetime.date.today()}"})
    p.write_text(json.dumps(sp, ensure_ascii=False, indent=1), encoding="utf-8")
    return "ok"


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split("?", 1)[0]
        if path.startswith("/village/"):
            rel = path[len("/village/"):] or "index.html"
            return str(ROOT / "docs" / rel)
        if path in ("/", ""):
            return str(DESK / "index.html")
        return str(DESK / path.lstrip("/"))

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/state"):
            return self._json(200, state())
        if self.path.startswith("/village") and not self.path.startswith("/village/"):
            self.send_response(301); self.send_header("Location", "/village/"); self.end_headers(); return
        return super().do_GET()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        try:
            d = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/api/scan":
                return self._json(200, {"ok": True, "file": save_scan(d)})
            if self.path == "/api/sprout":
                return self._json(200, {"ok": True, "result": add_sprout(d)})
            return self._json(404, {"ok": False, "error": "not found"})
        except ValueError as e:
            return self._json(400, {"ok": False, "error": str(e)})

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"🐰 Scan Desk → http://127.0.0.1:{PORT}   (notes save to {INBOX})")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
