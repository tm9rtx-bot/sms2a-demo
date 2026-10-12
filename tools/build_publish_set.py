#!/usr/bin/env python3
"""Build the restricted static publish set for demo.arkivklar.no (AK-BUG-010).

Copies ONLY the allow-listed, tracked production files named in tools/publish_manifest.json
into an output folder (default: dist/), verifying SHA256 and size of every source and copy
against the manifest. It never encrypts, transforms or normalises anything, never reads
outside the repository, and fails (exit 1) on any mismatch or on any unexpected file in the
output. Helper/history files in the repository (encrypt*.py, .staticrypt.json,
old_version_temp.html, encrypted/) are intentionally NOT part of the web deliverable.

Usage: python3 tools/build_publish_set.py [--out dist] [--manifest tools/publish_manifest.json]
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--manifest", default=os.path.join("tools", "publish_manifest.json"))
    args = ap.parse_args()

    manifest_path = os.path.join(REPO, args.manifest)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    files = manifest["files"]
    excluded = manifest.get("excluded", [])

    out = os.path.abspath(os.path.join(REPO, args.out))
    if not out.startswith(REPO + os.sep):
        print("refusing to write outside the repository: %s" % out, file=sys.stderr)
        return 1
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    errors = []
    result = {}
    for rel, expect in files.items():
        if rel in excluded or rel.startswith("tools/") or rel.startswith(".github/"):
            errors.append("%s: not allowed in the web deliverable" % rel)
            continue
        src = os.path.join(REPO, *rel.split("/"))
        if not os.path.isfile(src):
            errors.append("%s: source missing" % rel)
            continue
        src_sha, src_size = sha256_of(src), os.path.getsize(src)
        if src_sha != expect["sha256"] or src_size != expect["bytes"]:
            errors.append("%s: source sha256/size %s/%d != manifest %s/%d"
                          % (rel, src_sha, src_size, expect["sha256"], expect["bytes"]))
            continue
        dst = os.path.join(out, *rel.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        dst_sha, dst_size = sha256_of(dst), os.path.getsize(dst)
        if dst_sha != expect["sha256"] or dst_size != expect["bytes"]:
            errors.append("%s: copy sha256/size mismatch" % rel)
            continue
        result[rel] = {"sha256": dst_sha, "bytes": dst_size}

    present = sorted(
        os.path.relpath(os.path.join(r, f), out).replace(os.sep, "/")
        for r, _, fs in os.walk(out) for f in fs
    )
    for p in present:
        if p not in files:
            errors.append("%s: unexpected file in output" % p)
    for p in excluded:
        if os.path.exists(os.path.join(out, *p.split("/"))):
            errors.append("%s: excluded file present in output" % p)

    summary = {"out": os.path.relpath(out, REPO).replace(os.sep, "/"), "files": result,
               "present": present, "excluded_absent": excluded, "ok": not errors, "errors": errors}
    print(json.dumps(summary, indent=1))
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as f:
            f.write("### Restricted publish set\n\n```json\n%s\n```\n" % json.dumps(summary, indent=1))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
