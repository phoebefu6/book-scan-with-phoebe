"""Write books/<slug>/book.json + mindmap.md from a Python dict file.
Usage: python3 scripts/new_book.py seeds/<slug>.py   (the file defines BOOK = {...} and MINDMAP = '''...''')"""
import json, pathlib, runpy, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
for src in sys.argv[1:]:
    ns = runpy.run_path(src)
    b, mm = ns["BOOK"], ns["MINDMAP"]
    for k in ("title", "author", "district", "intro", "quotes", "takeaways", "pushback"):
        assert b.get(k), f"{src}: missing {k}"
    assert len(b["takeaways"]) == 5 and len(b["pushback"]) == 5, f"{src}: need 5 + 5"
    assert len(b["quotes"]) <= 10
    for q in b["quotes"]:
        assert q.get("source_label"), f"{src}: quote without source: {q['text'][:20]}"
    d = ROOT / "books" / b.pop("slug")
    d.mkdir(parents=True, exist_ok=True)
    (d / "book.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    (d / "mindmap.md").write_text(mm.strip() + "\n", encoding="utf-8")
    print("wrote", d.name)
