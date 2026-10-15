"""List or close book-scan requests waiting in Phoebe's PRIVATE vault repo (GitHub issues).
Needs `gh` logged in as phoebefu6. Notes never leave the vault: this prints them to the
terminal for Claude to read; book.json gets only public parts.

    python3 scripts/scan_queue.py list            # JSON of open requests (parsed form fields)
    python3 scripts/scan_queue.py done <n> <slug> # comment the house link, label scanned, close
"""
import json, re, subprocess, sys

VAULT = "phoebefu6/phoebe-reading-vault"
SITE = "https://phoebefu6.github.io/book-scan-with-phoebe/books/"
FIELDS = {"📖": "book", "✍️": "author", "🏘️": "category", "📒": "notes",
          "🌍": "public_thoughts", "🔒": "private_thoughts"}


def parse(body):
    out = {}
    for m in re.finditer(r"^### (\S+)[^\n]*\n+(.*?)(?=\n### |\Z)", body or "", re.S | re.M):
        key = FIELDS.get(m.group(1))
        if key:
            v = m.group(2).strip()
            out[key] = "" if v == "_No response_" else v
    for k in ("public_thoughts", "private_thoughts"):
        out[k] = [l.strip(" -•\t") for l in out.get(k, "").splitlines() if l.strip(" -•\t")]
    return out


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        # Open OR closed: closing the issue is not "cancel" (Phoebe closed one expecting it to
        # submit). Waiting = labelled book-scan and not yet labelled scanned.
        issues = json.loads(gh("issue", "list", "-R", VAULT, "--label", "book-scan", "--state", "all",
                               "--json", "number,title,body,createdAt,state,labels", "--limit", "100"))
        waiting = [i for i in issues if "scanned" not in {l["name"] for l in i["labels"]}]
        print(json.dumps([{"number": i["number"], "state": i["state"], "created": i["createdAt"],
                           **parse(i["body"])} for i in waiting], ensure_ascii=False, indent=1))
    elif cmd == "done":
        n, slug = sys.argv[2], sys.argv[3]
        gh("issue", "comment", n, "-R", VAULT, "-b", f"🏠 House built → {SITE}{slug}.html")
        gh("issue", "edit", n, "-R", VAULT, "--add-label", "scanned")
        gh("issue", "close", n, "-R", VAULT)
        print("closed", n)
