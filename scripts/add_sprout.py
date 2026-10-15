"""Append a sprout from a GitHub issue-form body (env ISSUE_BODY). Titles only; stdlib only."""
import datetime, json, os, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent

def field(body, label_start):
    m = re.search(r"^### " + re.escape(label_start) + r"[^\n]*\n+(.*?)(?=\n### |\Z)", body, re.S | re.M)
    v = (m.group(1).strip() if m else "")
    return "" if v == "_No response_" else v

body = os.environ.get("ISSUE_BODY", "")
title = field(body, "📖").splitlines()[0].strip() if field(body, "📖") else ""
cat = field(body, "🏘️").strip()
if not title:
    sys.exit("no title found")
sys.path.insert(0, str(ROOT / "scripts"))
from village import ensure_district
district = ensure_district(cat)   # creates a new category if nothing matches
p = ROOT / "sprouts.json"
sp = json.loads(p.read_text(encoding="utf-8"))
if any(s["title"] == title for s in sp):
    print("already a sprout:", title); sys.exit(0)
sp.append({"title": title[:80], "district": district, "added": str(datetime.date.today())})
p.write_text(json.dumps(sp, ensure_ascii=False, indent=1), encoding="utf-8")
print("planted:", title, district or "(garden)")
