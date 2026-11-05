<div align="center">

# 🔐 File Integrity Checker

### SHA-256 Baseline • Tamper Detection • Alert Report

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Hash](https://img.shields.io/badge/Hash-SHA--256-red)
![Tests](https://img.shields.io/badge/Tests-4%20passing-brightgreen)
![Dependencies](https://img.shields.io/badge/Dependencies-None-blue)
![Status](https://img.shields.io/badge/Status-Complete-success)
![CodeNova](https://img.shields.io/badge/CodeNova-Cybersecurity%20Batch%2001-orange)

**Task 3 | CodeNova Internship Program | Cryptographic Hashes & Tamper Detection**

</div>

---

## 📑 Table of Contents
[Overview](#-overview) • 
[Features](#-features) •
[Alert Types](#-alert-types) 
[Quick Start](#-quick-start) • 
[Manifest](#-sample-baseline-manifest) •
[Simulation](#-simulation-single-byte-tamper-detection) • 
[How it works](#-how-it-works) •
[Tests](#-test-scenarios) • 
[Criteria](#-acceptance-criteria) • 
[Author](#-author-note)

## 🎯 Overview

Attackers often change a file and then **fake its size and date** so nothing looks different.
This tool defeats that. It calculates a **SHA-256 fingerprint** for every file in a folder, saves them
in a **baseline manifest**, and later compares the folder against it. Even a **one-byte change** gives a
completely different hash, so tampering cannot hide.

## ✨ Features

-  SHA-256 hashing with `hashlib`, read in 1 MB chunks (safe for large files)
-  Recursive scan of **nested subdirectories** and every file type (text, binary, empty)
-  JSON manifest storing **relative path, SHA-256, size, modified timestamp**
-  Catches tampering **even when size and timestamp are identical** (stealth flag)
-  Handles permission errors gracefully, never crashes
-  Optional CSV alert report (`--csv`)
-  Exit codes for automation: `0` clean, `1` changes found, `2` error
-  Symlinks skipped so files outside the folder are never hashed

## 🚨 Alert Types

| Status | Meaning | Example |
|---|---|---|
| 🟡 **MODIFIED** | hash differs from baseline | `config/app.ini` |
| 🟢 **NEW** | file not present in baseline | `docs/backdoor.sh` |
| 🔴 **MISSING** | in baseline but deleted | `data/students.csv` |
| ⚪ **UNREADABLE** | permission denied, skipped safely | locked file |
| 🕵️ **STEALTH** | modified with same size and timestamp | single-byte tamper |

## 🚀 Quick Start

```bash
1. Create baseline
python integrity_checker.py baseline test_folder -m baseline_manifest.json

2. Verify later
python integrity_checker.py verify test_folder -m baseline_manifest.json

3. Verify and export CSV
python integrity_checker.py verify test_folder -m baseline_manifest.json --csv alert_report.csv

 4. Tamper simulation and tests
python demo_tamper.py
python -m unittest -v test_integrity_checker
```

Requirements: Python 3.8+, standard library only.

## 🧾 Sample Baseline Manifest

Generated from `test_folder` (7 files, nested folders, text + binary + empty):

| File | SHA-256 (first 16 chars) | Size |
|---|---|---|
| `config/app.ini` | `37679f575b1a3382...` | 54 B |
| `config/settings.json` | `80cee392b8acdf70...` | 43 B |
| `data/empty.dat` | `e3b0c44298fc1c14...` | 0 B |
| `data/students.csv` | `d51fc51574c04323...` | 34 B |
| `data/bin/blob.bin` | `b916f09cc48b7cf4...` | 4096 B |
| `docs/notes.txt` | `afcd1f52f54f0900...` | 52 B |
| `docs/reports/q3_report.txt` | `806a271e1d4e8104...` | 64 B |

## 🧪 Simulation: Single-Byte Tamper Detection

The attacker flips **one byte** (`false` to `talse`) and restores the original timestamp.
Size and date look untouched, **SHA-256 still catches it**.

```text
### STEP 1 - Create baseline

$ python integrity_checker.py baseline test_folder -m baseline_manifest.json
[+] Baseline created: baseline_manifest.json
    Files hashed : 7

### STEP 2 - Verify untouched folder

$ python integrity_checker.py verify test_folder -m baseline_manifest.json

 FILE INTEGRIT
 Files checked: 7
 [OK] No changes detected. All files match the baseline.

### STEP 3 - Attacker flips ONE byte (admin_enabled=false -> admin_enabled=talse)
    size before/after : 54 / 54
    mtime restored    : True

### STEP 4 - Verify again (tamper must be caught)

$ python integrity_checker.py verify test_folder -m baseline_manifest.json

 FILE INTEGRITY REPORT

 Files checked: 7
 [MODIFIED]   config/app.ini  <-- SIZE & TIMESTAMP UNCHANGED (stealth tamper)
              old: 37679f575b1a33822a4e8950dbc2c7619392d3c151eaa328c04d7c103829a386
              new: 6e863c6c0ec14f3b2c05f275b85f19b31f1494e2a33e2631ca05aca9d119a9fb

 ALERT: 1 modified, 0 new, 0 missing, 0 unreadable

### STEP 5 - Also add a new file and delete another

$ python integrity_checker.py verify test_folder -m baseline_manifest.json --csv alert_report.csv

 FILE INTEGRITY REPORT

 Files checked: 7
 [MODIFIED]   config/app.ini  <-- SIZE & TIMESTAMP UNCHANGED (stealth tamper)
              old: 37679f575b1a33822a4e8950dbc2c7619392d3c151eaa328c04d7c103829a386
              new: 6e863c6c0ec14f3b2c05f275b85f19b31f1494e2a33e2631ca05aca9d119a9fb
 [NEW]        docs/backdoor.sh
 [MISSING]    data/students.csv

 ALERT: 1 modified, 1 new, 1 missing, 0 unreadable
 CSV report saved: alert_report.csv
```

## ⚙️ How it works

```
 baseline            verify
 ────────            ──────
 walk folder         walk folder again
    │                     │
 SHA-256 each file    SHA-256 each file
    │                     │
 save manifest.json   compare with manifest
                          │
              MODIFIED / NEW / MISSING / UNREADABLE
```

## 🧫 Test Scenarios

| Scenario | Result |
|---|---|
| Nested folders and binary files hashed | ✅ pass |
| One-byte change, same size and mtime | ✅ detected as MODIFIED + stealth |
| New file added and file deleted | ✅ detected as NEW and MISSING |
| Permission denied while reading | ✅ UNREADABLE, no crash, not reported as missing |

## 📂 Project Structure

```
task3_file_integrity_checker/
├── integrity_checker.py        # main tool
├── demo_tamper.py              # tamper simulation
├── test_integrity_checker.py   # unit tests
├── test_folder/                # sample folder
├── baseline_manifest.json      # sample baseline
├── alert_report.csv            # sample alert report
├── simulation_transcript.txt   # raw demo output
└── README.md
```

## ✅ Acceptance Criteria

| Criterion | Status |
|---|---|
| Detects unauthorized changes even if size and timestamp are identical | ✅ |
| Handles nested subdirectories and diverse file types | ✅ |
| Gracefully catches permission errors without crashing | ✅ |
| Sample baseline manifest from a test folder | ✅ |
| README with single-byte tampering simulation transcript | ✅ |

## ⚠️ Limitations & Future Work

- A baseline stored beside the files can also be tampered with. Keep it read-only, off-host, or sign it with HMAC.
- Ideas: permission/owner tracking, scheduled scans, email alerts.

## 👩‍💻 Author Note

Built by **Naina Kumari**, 5th semester Data Science student at AMC Engineering College (VTU), as part of the
**CodeNova Cybersecurity Internship, Batch 01**.

This project taught me how cryptographic hashes work as digital fingerprints, why timestamps and file
sizes alone cannot be trusted, and how to write security tools that fail safely.

📫 Feedback and suggestions are welcome through GitHub issues.

---

<div align="center">⭐ If this helped you, star the repo! ⭐<br><sub>Made with 🐍 and ☕ by Naina Kumari | CodeNova Cybersecurity Internship, Batch 01</sub></div>
