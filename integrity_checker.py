#!/usr/bin/env python3
"""
File Integrity Checker  (CodeNova Cybersecurity - Task 3)

Computes SHA-256 hashes for every file in a directory tree, stores them in a
JSON baseline manifest, and later verifies the directory against that
manifest, reporting MODIFIED, NEW, MISSING and UNREADABLE files.

Usage:
    python integrity_checker.py baseline <directory> [-m manifest.json]
    python integrity_checker.py verify   <directory> [-m manifest.json] [--csv report.csv]

Exit codes: 0 = clean, 1 = changes detected, 2 = usage/manifest error
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ALGORITHM = "sha256"
CHUNK_SIZE = 1024 * 1024  # 1 MB chunks, so large files never fill memory
DEFAULT_MANIFEST = "baseline_manifest.json"


def sha256_of_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file (read in chunks)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")


def scan_directory(root: Path, skip: set):
    """
    Walk `root` (including nested subdirectories) and hash every regular file.
    Returns (records, errors):
      records = {relative_posix_path: {sha256, size, modified}}
      errors  = {relative_posix_path: reason}   (files that could not be read)
    Symlinks are skipped on purpose so we never hash files outside the tree.
    """
    records, errors = {}, {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        for name in sorted(filenames):
            full = Path(dirpath) / name
            rel = full.relative_to(root).as_posix()
            if full.resolve() in skip or full.is_symlink():
                continue
            try:
                st = full.stat()
                records[rel] = {
                    "sha256": sha256_of_file(full),
                    "size": st.st_size,
                    "modified": iso(st.st_mtime),
                }
            except PermissionError:
                errors[rel] = "permission denied"
            except OSError as exc:  # vanished mid-scan, I/O error, etc.
                errors[rel] = f"os error: {exc.strerror or exc}"
    return records, errors


def create_baseline(directory: Path, manifest_path: Path) -> int:
    records, errors = scan_directory(directory, {manifest_path.resolve()})
    manifest = {
        "tool": "CodeNova File Integrity Checker",
        "algorithm": ALGORITHM,
        "root": str(directory.resolve()),
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "file_count": len(records),
        "files": records,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[+] Baseline created: {manifest_path}")
    print(f"    Files hashed : {len(records)}")
    for rel, reason in errors.items():
        print(f"    [!] Skipped  : {rel} ({reason})")
    return 0


def compare(baseline: dict, current: dict, errors: dict) -> dict:
    """Pure comparison logic: returns the categorised differences."""
    modified, new, missing, unreadable = [], [], [], []
    for rel, now in current.items():
        old = baseline.get(rel)
        if old is None:
            new.append(rel)
        elif old["sha256"] != now["sha256"]:
            stealth = old["size"] == now["size"] and old["modified"] == now["modified"]
            modified.append({
                "path": rel,
                "old_hash": old["sha256"],
                "new_hash": now["sha256"],
                "size_changed": old["size"] != now["size"],
                "mtime_changed": old["modified"] != now["modified"],
                "stealth": stealth,  # size AND timestamp identical, only hash differs
            })
    for rel in baseline:
        if rel in errors:
            unreadable.append({"path": rel, "reason": errors[rel]})
        elif rel not in current:
            missing.append(rel)
    for rel, reason in errors.items():
        if rel not in baseline:
            unreadable.append({"path": rel, "reason": reason})
    return {"modified": modified, "new": sorted(new),
            "missing": sorted(missing), "unreadable": unreadable}


def print_report(result: dict, checked: int) -> None:
    total = sum(len(v) for v in result.values())
    print("=" * 64)
    print(" FILE INTEGRITY REPORT")
    print("=" * 64)
    print(f" Files checked: {checked}")
    if total == 0:
        print(" [OK] No changes detected. All files match the baseline.")
        return
    for m in result["modified"]:
        flag = "  <-- SIZE & TIMESTAMP UNCHANGED (stealth tamper)" if m["stealth"] else ""
        print(f" [MODIFIED]   {m['path']}{flag}")
        print(f"              old: {m['old_hash']}")
        print(f"              new: {m['new_hash']}")
    for p in result["new"]:
        print(f" [NEW]        {p}")
    for p in result["missing"]:
        print(f" [MISSING]    {p}")
    for u in result["unreadable"]:
        print(f" [UNREADABLE] {u['path']} ({u['reason']})")
    print("-" * 64)
    print(f" ALERT: {len(result['modified'])} modified, {len(result['new'])} new, "
          f"{len(result['missing'])} missing, {len(result['unreadable'])} unreadable")


def write_csv(result: dict, path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["status", "path", "detail"])
        for m in result["modified"]:
            w.writerow(["MODIFIED", m["path"], f"{m['old_hash']} -> {m['new_hash']}"])
        for p in result["new"]:
            w.writerow(["NEW", p, ""])
        for p in result["missing"]:
            w.writerow(["MISSING", p, ""])
        for u in result["unreadable"]:
            w.writerow(["UNREADABLE", u["path"], u["reason"]])


def verify(directory: Path, manifest_path: Path, csv_path=None) -> int:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        baseline = manifest["files"]
    except FileNotFoundError:
        print(f"[!] Manifest not found: {manifest_path}. Run 'baseline' first.", file=sys.stderr)
        return 2
    except (json.JSONDecodeError, KeyError):
        print(f"[!] Manifest is corrupt or not valid: {manifest_path}", file=sys.stderr)
        return 2
    current, errors = scan_directory(directory, {manifest_path.resolve()})
    result = compare(baseline, current, errors)
    print_report(result, len(current))
    if csv_path:
        write_csv(result, csv_path)
        print(f" CSV report saved: {csv_path}")
    return 1 if any(result.values()) else 0


def main() -> int:
    p = argparse.ArgumentParser(description="SHA-256 file integrity checker")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, help_ in (("baseline", "create baseline manifest"), ("verify", "verify against baseline")):
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("directory", type=Path)
        sp.add_argument("-m", "--manifest", type=Path, default=Path(DEFAULT_MANIFEST))
        if name == "verify":
            sp.add_argument("--csv", type=Path, help="also save the alert report as CSV")
    args = p.parse_args()
    if not args.directory.is_dir():
        print(f"[!] Not a directory: {args.directory}", file=sys.stderr)
        return 2
    if args.cmd == "baseline":
        return create_baseline(args.directory, args.manifest)
    return verify(args.directory, args.manifest, args.csv)


if __name__ == "__main__":
    sys.exit(main())
