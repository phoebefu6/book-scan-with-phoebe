#!/usr/bin/env python3
"""WeRead → village. Runs on Phoebe's Mac during "scan" (needs WEREAD_API_KEY and the
book-partner scripts in ~/knowledge). Nothing here publishes on its own.

    python3 scripts/weread_village.py status          # what's new in WeRead (read-only)
    python3 scripts/weread_village.py grow <slug> [--public 1,3]
        count that house's new WeRead 想法 (house grows); publish only the numbered ones she OKs
    python3 scripts/weread_village.py init [--count <slug> ...]
        one-time: mark every current WeRead 想法 as already counted, except for the named houses

Privacy: thought texts are printed to the terminal only. They reach books/<slug>/book.json
(public) ONLY via --public, which she must approve. Highlights are never read here.
The ledger of counted thoughts is private: ~/knowledge/03-inbox/book-scan/weread-ledger.json
"""
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BP = pathlib.Path("~/knowledge/skills/book-partner/scripts").expanduser()
LEDGER = pathlib.Path("~/knowledge/03-inbox/book-scan/weread-ledger.json").expanduser()
sys.path.insert(0, str(BP))
from weread_sync import api            # noqa: E402  (book-partner owns the WeRead client)
from thoughts_census import classify   # noqa: E402  (same "full sentence" rule as her scoreboard)


def houses():
    out = {}
    for p in sorted((ROOT / "books").glob("*/book.json")):
        b = json.loads(p.read_text(encoding="utf-8"))
        if b.get("weread_id"):
            out[p.parent.name] = (p, b)
    return out


def ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}


def save_ledger(d):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def full_thoughts(book_id):
    """Her own 想法 (not 书评, type 4), full sentences only. -> [(reviewId, text)]"""
    d = api("/review/list/mine", bookid=book_id, count=100)
    out = []
    for v in d.get("reviews", []):
        r = v.get("review", {})
        t = (r.get("content") or "").strip()
        if r.get("type") == 4 or not t:
            continue
        if classify(t, (r.get("abstract") or ""))[0] == "full":
            out.append((r.get("reviewId") or t[:40], t))
    return out


def new_thoughts(slug, book_id, led):
    seen = set(led.get(book_id, []))
    return [(rid, t) for rid, t in full_thoughts(book_id) if rid not in seen]


def unhoused_books(housed_ids):
    """Books she finished or wrote notes on in WeRead that have no house yet, newest first."""
    rows = {}
    shelf = api("/shelf/sync")
    for b in shelf.get("books", []):
        if b.get("finishReading") == 1:
            rows[str(b["bookId"])] = {"title": b.get("title", "?"), "finished": True,
                                      "t": b.get("readUpdateTime") or b.get("updateTime") or 0}
    nb, last = [], None
    while True:
        d = api("/user/notebooks", count=100, lastSort=last)
        page = d.get("books", [])
        nb += page
        if not d.get("hasMore") or not page:
            break
        last = page[-1]["sort"]
    for b in nb:
        bid = str(b["bookId"])
        r = rows.setdefault(bid, {"title": b.get("book", {}).get("title", "?"), "finished": False,
                                  "t": b.get("sort") or 0})
        r["highlights"] = b.get("noteCount", 0)
        r["t"] = max(r["t"], b.get("sort") or 0)
    return sorted(((k, v) for k, v in rows.items() if k not in housed_ids), key=lambda kv: -kv[1]["t"])


def cmd_status():
    led, hs = ledger(), houses()
    print("🏠 Houses with new WeRead 想法 (text shown here only, not published):")
    any_new = False
    for slug, (_, b) in hs.items():
        new = new_thoughts(slug, b["weread_id"], led)
        if new:
            any_new = True
            print(f"\n  {slug}  ({b.get('short_title') or b['title']})  +{len(new)}")
            for i, (_, t) in enumerate(new, 1):
                print(f"    {i}. {t}")
    if not any_new:
        print("  (none)")
    print("\n📚 WeRead books with no house yet (newest first):")
    rows = unhoused_books({b["weread_id"] for _, b in hs.values()})
    for bid, r in rows[:15]:
        tag = "✅ finished" if r["finished"] else "📖 reading"
        print(f"  {bid:>12}  {tag}  {r.get('highlights', 0):>4} highlights  {r['title']}")
    if len(rows) > 15:
        print(f"  … and {len(rows) - 15} more")


def cmd_grow(slug, public_idx):
    led, hs = ledger(), houses()
    if slug not in hs:
        sys.exit(f"no house {slug} with a weread_id")
    p, b = hs[slug]
    new = new_thoughts(slug, b["weread_id"], led)
    if not new:
        print("nothing new"); return
    b["thought_count"] = b.get("thought_count", len(b.get("thoughts", []))) + len(new)
    pubs = [new[i - 1][1] for i in public_idx if 1 <= i <= len(new)]
    b["thoughts"] = b.get("thoughts", []) + [t for t in pubs if t not in b.get("thoughts", [])]
    p.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    led.setdefault(b["weread_id"], []).extend(rid for rid, _ in new)
    save_ledger(led)
    print(f"{slug}: +{len(new)} thoughts (now {b['thought_count']}), {len(pubs)} published")


def cmd_init(count_slugs):
    led, hs = ledger(), houses()
    for slug, (_, b) in hs.items():
        if slug in count_slugs:
            continue
        led[b["weread_id"]] = [rid for rid, _ in full_thoughts(b["weread_id"])]
    save_ledger(led)
    print("ledger:", {k: len(v) for k, v in led.items()})


if __name__ == "__main__":
    if not os.environ.get("WEREAD_API_KEY"):
        sys.exit("WEREAD_API_KEY is not set")
    a = sys.argv[1:]
    if not a or a[0] == "status":
        cmd_status()
    elif a[0] == "grow" and len(a) >= 2:
        idx = [int(x) for x in a[a.index("--public") + 1].split(",")] if "--public" in a else []
        cmd_grow(a[1], idx)
    elif a[0] == "init":
        cmd_init(set(a[a.index("--count") + 1:]) if "--count" in a else set())
    else:
        sys.exit(__doc__)
