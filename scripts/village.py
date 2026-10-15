"""Shared village helpers. stdlib only (runs in GitHub Actions too).

ensure_district(name) -> district id. Matches an existing district by id / Chinese / English name or
a keyword; otherwise CREATES a new district in config/village.json. A new district borrows an
existing house family with a hue shift ("base" + "hue") until real art is drawn for it
(cute-village-art; then set "sprite": "house-<id>" and drop base/hue)."""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG_PATH = ROOT / "config" / "village.json"

KEYWORDS = {
    "story": ["小说", "故事", "文学", "诗", "fiction", "novel", "story", "poetry", "literature"],
    "history": ["历史", "传记", "朝", "history", "biography"],
    "mind": ["思维", "科技", "科学", "数据", "ai", "人工智能", "决策", "tech", "science", "data", "thinking"],
    "work": ["管理", "领导", "职场", "商业", "创业", "work", "leadership", "business", "career"],
    "life": ["人生", "心理", "情感", "成长", "生活", "life", "psychology", "self"],
}
NEW_EMOJI = ["🌈", "🎨", "✈️", "🍰", "🎵", "🌿", "🧸", "🏝️", "🪐", "🧶", "🍵", "🦋"]
BASES = ["house-life", "house-story", "house-mind", "house-work", "house-history"]


def load():
    return json.loads(CFG_PATH.read_text(encoding="utf-8"))


def save(cfg):
    CFG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def match(cfg, name):
    n = (name or "").strip().lower()
    if not n:
        return ""
    for d in cfg["districts"]:
        if n in (d["id"], d["zh"].lower(), d["en"].lower()) or n in d["zh"].lower() or n in d["en"].lower() \
                or d["zh"].lower() in n:
            return d["id"]
    if len(n) <= 6:  # short category words like "心理" or "AI": try the keyword map
        for did, kws in KEYWORDS.items():
            if any(k in n for k in kws) and any(d["id"] == did for d in cfg["districts"]):
                return did
    return ""


def slug(name, taken):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not s:
        s = "d" + str(len(taken) + 1)
    base, i = s[:20], 2
    s = base
    while s in taken:
        s, i = f"{base}-{i}", i + 1
    return s


def ensure_district(name, en="", emoji="", about=""):
    """Return the id of the district for `name`, creating it if nothing matches. '' if name empty."""
    cfg = load()
    hit = match(cfg, name)
    if hit or not (name or "").strip():
        return hit
    taken = {d["id"] for d in cfg["districts"]}
    k = len(cfg["districts"])
    d = {"id": slug(en or name, taken), "emoji": emoji or NEW_EMOJI[k % len(NEW_EMOJI)],
         "zh": name.strip()[:12], "en": (en or name).strip()[:24], "sprite": "",
         "base": BASES[k % len(BASES)], "hue": 60 + (k * 67) % 240, "about": about, "auto": True}
    d["sprite"] = "house-" + d["id"]
    cfg["districts"].append(d)
    save(cfg)
    return d["id"]


if __name__ == "__main__":
    import sys
    print(ensure_district(*sys.argv[1:]))
