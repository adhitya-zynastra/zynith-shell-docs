#!/usr/bin/env python3
"""Audit the documentation against the live system.

Checks: (1) every commit hash mentioned exists, (2) every absolute path mentioned exists,
(3) internal markdown links resolve, (4) VERSION.json matches the repository HEAD.
Exit code is non-zero if anything fails, so it can gate a documentation build.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.expanduser("~/.local/src/noctalia-lockfade/source")
meta = json.load(open(os.path.join(ROOT, "VERSION.json")))

md = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in {".git", "99_Reports"}]
    md += [os.path.join(dirpath, f) for f in filenames if f.endswith(".md")]

fails, warns, checked = [], [], {"commits": 0, "paths": 0, "links": 0}

def git(*a):
    return subprocess.run(["git", "-C", SRC] + list(a), capture_output=True, text=True)

# 1 — commit hashes
known = set()
for line in git("log", "--pretty=%h").stdout.split():
    known.add(line)
for f in md:
    text = open(f).read()
    for h in set(re.findall(r"`([0-9a-f]{7})`", text)):
        checked["commits"] += 1
        if h not in known:
            fails.append(f"{os.path.relpath(f, ROOT)}: unknown commit `{h}`")

# 2 — absolute paths under ~ mentioned in backticks
home = os.path.expanduser("~")
for f in md:
    text = open(f).read()
    for p in set(re.findall(r"`(~/[^`\s]+)`", text)):
        p = p.rstrip(".,);:")
        if any(ch in p for ch in "*<>|"):      # globs/placeholders
            continue
        checked["paths"] += 1
        if not os.path.exists(os.path.expanduser(p)):
            warns.append(f"{os.path.relpath(f, ROOT)}: path not present: {p}")

# 3 — internal links
for f in md:
    text = open(f).read()
    for target in set(re.findall(r"\]\(([^)#:]+\.md)\)", text)) | set(re.findall(r"\]\(([^)#:]+/)\)", text)):
        checked["links"] += 1
        dest = os.path.normpath(os.path.join(os.path.dirname(f), target))
        if not os.path.exists(dest):
            fails.append(f"{os.path.relpath(f, ROOT)}: broken link -> {target}")

# 4 — version block vs HEAD
head = git("rev-parse", "--short", "HEAD").stdout.strip()
if head and head != meta["source_commit"]:
    fails.append(f"VERSION.json source_commit={meta['source_commit']} but repository HEAD={head}")
dirty = git("status", "--short").stdout.strip()
if dirty:
    warns.append("implementation repository has uncommitted changes; documentation may describe an unbuilt state")

print(f"audited {len(md)} markdown files "
      f"({checked['commits']} commit refs, {checked['paths']} paths, {checked['links']} links)")
for w in warns:
    print("  WARN ", w)
for e in fails:
    print("  FAIL ", e)
print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(1 if fails else 0)
