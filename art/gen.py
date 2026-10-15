"""Generate village sprites via codex image_gen. Sequential, throttled, resumable.
Usage: python3 gen.py [id ...]   (no ids = all missing)"""
import json, os, subprocess, sys, time, pathlib
HERE = pathlib.Path(__file__).parent
WRAP = os.path.expanduser("~/.claude/baoyu-skills-src/packages/baoyu-codex-imagegen/src/main.ts")
spec = json.loads((HERE / "sprites.json").read_text())
want = set(sys.argv[1:])
log = open(HERE / "gen-log.jsonl", "a")
env = dict(os.environ, PATH=os.path.expanduser("~/.nvm/versions/node/v24.19.0/bin") + ":/Applications/ChatGPT.app/Contents/Resources:" + os.environ["PATH"])
first = True
for it in spec["items"]:
    if want and it["id"] not in want:
        continue
    out = HERE / "raw" / f"{it['id']}.png"
    if out.exists():
        continue
    if not first:
        time.sleep(25)
    first = False
    pf = HERE / "prompts" / f"{it['id']}.md"
    pf.write_text(spec["style"] + "\n\nSUBJECT: " + it["prompt"] + "\n")
    cmd = ["npx", "-y", "bun", WRAP, "--image", str(out), "--prompt-file", str(pf),
           "--aspect", "1:1", "--timeout", "600000", "--retries", "1"]
    if it.get("ref"):
        ref = HERE / "raw" / f"{it['ref']}.png"
        if ref.exists():
            cmd += ["--ref", str(ref)]
    t = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    rec = {"id": it["id"], "rc": p.returncode, "secs": round(time.time() - t),
           "ok": out.exists(), "stdout": p.stdout[-400:], "stderr": p.stderr[-600:]}
    log.write(json.dumps(rec, ensure_ascii=False) + "\n"); log.flush()
    print(it["id"], "ok" if out.exists() else "FAIL", rec["secs"], "s", flush=True)
