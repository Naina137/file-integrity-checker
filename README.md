# Task 3 - File Integrity Checker

**CodeNova Internship Program - Batch 01 - Cybersecurity**
Domain: Cryptographic Hashes & Tamper Detection

A Python tool that computes **SHA-256** hashes for every file in a directory, saves them in a
JSON **baseline manifest**, and later **verifies** the directory against that baseline, reporting
modified, new and missing files.

## Features

- SHA-256 hashing with `hashlib` (files are read in 1 MB chunks, so large files are fine)
- Recursive scan of **nested subdirectories**, works with text, binary, empty and any other file type
- Baseline manifest (JSON) storing **relative path, SHA-256, size, modified timestamp**
- Verification mode with an alert report: `MODIFIED`, `NEW`, `MISSING`, `UNREADABLE`
- **Tamper detection is hash-based**, so it catches changes even when file size and modified
  timestamp are identical (flagged as a *stealth tamper*)
- Gracefully handles permission errors and files that vanish mid-scan (no crash, reported as `UNREADABLE`)
- Optional CSV alert report (`--csv`)
- Exit codes for automation: `0` clean, `1` changes found, `2` usage/manifest error
- Symlinks are skipped on purpose, so the tool never hashes files outside the target tree

## Project Structure

```
task3_file_integrity_checker/
├── integrity_checker.py          # main tool
├── demo_tamper.py                # single-byte tamper simulation
├── test_integrity_checker.py     # unit tests
├── test_folder/                  # sample folder (nested dirs, text/binary/empty files)
├── baseline_manifest.json        # sample baseline generated from test_folder
├── alert_report.csv              # sample CSV alert report
├── simulation_transcript.txt     # raw output of demo_tamper.py
└── README.md
```

Requirements: Python 3.8+ (standard library only, no pip install needed).

## Usage

```bash
# 1. Create the baseline
python integrity_checker.py baseline test_folder -m baseline_manifest.json

# 2. Verify later
python integrity_checker.py verify test_folder -m baseline_manifest.json

# 3. Verify and export CSV
python integrity_checker.py verify test_folder -m baseline_manifest.json --csv alert_report.csv

# Run the tests / simulation
python -m unittest -v test_integrity_checker
python demo_tamper.py
```

### Manifest format

```json
{
  "algorithm": "sha256",
  "created": "2026-11-05T10:00:00+00:00",
  "file_count": 7,
  "files": {
    "config/app.ini": { "sha256": "37679f57...", "size": 54, "modified": "2026-11-05T10:00:00+00:00" }
  }
}
```

## Simulation Transcript - Single-Byte Tamper Detection

The attacker changes **one byte** (`admin_enabled=false` to `admin_enabled=talse`), then restores
the original modified timestamp so that size *and* mtime look untouched. A naive size/date check
would miss this. The SHA-256 comparison catches it.

```text
### STEP 1 - Create baseline

$ python integrity_checker.py baseline test_folder -m baseline_manifest.json
[+] Baseline created: baseline_manifest.json
    Files hashed : 7

### STEP 2 - Verify untouched folder

$ python integrity_checker.py verify test_folder -m baseline_manifest.json
================================================================
 FILE INTEGRITY REPORT
================================================================
 Files checked: 7
 [OK] No changes detected. All files match the baseline.

### STEP 3 - Attacker flips ONE byte (admin_enabled=false -> admin_enabled=talse)
    size before/after : 54 / 54
    mtime restored    : True

### STEP 4 - Verify again (tamper must be caught)

$ python integrity_checker.py verify test_folder -m baseline_manifest.json
================================================================
 FILE INTEGRITY REPORT
================================================================
 Files checked: 7
 [MODIFIED]   config/app.ini  <-- SIZE & TIMESTAMP UNCHANGED (stealth tamper)
              old: 37679f575b1a33822a4e8950dbc2c7619392d3c151eaa328c04d7c103829a386
              new: 6e863c6c0ec14f3b2c05f275b85f19b31f1494e2a33e2631ca05aca9d119a9fb
----------------------------------------------------------------
 ALERT: 1 modified, 0 new, 0 missing, 0 unreadable

### STEP 5 - Also add a new file and delete another

$ python integrity_checker.py verify test_folder -m baseline_manifest.json --csv alert_report.csv
================================================================
 FILE INTEGRITY REPORT
================================================================
 Files checked: 7
 [MODIFIED]   config/app.ini  <-- SIZE & TIMESTAMP UNCHANGED (stealth tamper)
              old: 37679f575b1a33822a4e8950dbc2c7619392d3c151eaa328c04d7c103829a386
              new: 6e863c6c0ec14f3b2c05f275b85f19b31f1494e2a33e2631ca05aca9d119a9fb
 [NEW]        docs/backdoor.sh
 [MISSING]    data/students.csv
----------------------------------------------------------------
 ALERT: 1 modified, 1 new, 1 missing, 0 unreadable
 CSV report saved: alert_report.csv
```

## How it works

1. `baseline` walks the tree with `os.walk`, hashes each file and writes the manifest. The manifest file itself is excluded.
2. `verify` re-scans the tree and compares to the manifest:
   - path not in manifest: **NEW**
   - path in manifest but hash differs: **MODIFIED** (plus `stealth` flag if size and mtime are unchanged)
   - path in manifest but not on disk: **MISSING**
   - file exists but cannot be read: **UNREADABLE** (never reported as missing)
3. A summary line and exit code tell you at a glance whether the folder is clean.

## Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| Detects modifications even if size and timestamp are identical | Done (stealth flag, unit test + simulation) |
| Handles nested subdirectories and diverse file types | Done (`test_folder`: txt, ini, json, csv, binary, empty) |
| Catches permission errors without crashing | Done (`UNREADABLE`, unit test) |
| Sample baseline manifest from a test folder | Done (`baseline_manifest.json`) |
| README with single-byte tampering transcript | Done (above) |

## Limitations / Future Work

- A baseline stored next to the files can itself be tampered with; in real use, keep it read-only or off-host, or sign it (HMAC).
- Possible extensions: file-permission/owner tracking, scheduled scans, email alerts.
