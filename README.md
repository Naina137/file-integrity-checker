\# 🔐 File Integrity Checker

## SHA-256 Based File Tamper Detection System

### CodeNova Cybersecurity Internship - Task 3

A Python-based cybersecurity tool that detects unauthorized file modifications using SHA-256 cryptographic hashing. The system creates a trusted baseline of files and later verifies file integrity by comparing cryptographic hashes instead of relying on file metadata such as size or timestamps.

---

## 📖 Overview

File integrity monitoring is an important security practice used to detect unauthorized changes to critical files. Traditional methods often depend on file size and timestamps, which attackers can manipulate to hide malicious modifications.

This project solves that problem by using SHA-256 cryptographic hashing. Any change, even a single-byte modification, produces a completely different hash value and is immediately detected.

---

## 🎯 Objectives

- Generate SHA-256 hashes for files.
- Create a baseline manifest for future verification.
- Detect modified files.
- Detect newly added files.
- Detect deleted files.
- Generate security reports.
- Demonstrate tamper detection techniques used in cybersecurity.

---

## ✨ Features

- SHA-256 Cryptographic Hashing
- Recursive Directory Scanning
- Supports Nested Folders
- Detects Modified Files
- Detects New Files
- Detects Missing Files
- CSV Alert Report Generation
- JSON Baseline Storage
- Permission Error Handling
- Dependency-Free Implementation
- Detects Stealth Tampering Even When Size and Timestamp Remain Unchanged

---

## 🛠️ Technologies Used

- Python 3.8+
- hashlib
- json
- csv
- pathlib
- os

---

## ⚙️ How It Works

### Step 1: Create Baseline

The tool scans all files inside a directory and stores:

- File Path
- SHA-256 Hash
- File Size
- Last Modified Timestamp

in a JSON manifest.

### Step 2: Verify Integrity

The directory is scanned again and compared against the saved baseline.

Detected file states include:

| Status | Meaning |
|----------|----------|
| MODIFIED | File content changed |
| NEW | New file detected |
| MISSING | File deleted |
| UNREADABLE | Permission denied or inaccessible |

---

## 🚀 Usage

### Create Baseline

```bash
python integrity_checker.py baseline test_folder -m baseline_manifest.json
```

### Verify Integrity

```bash
python integrity_checker.py verify test_folder -m baseline_manifest.json
```

### Generate CSV Report

```bash
python integrity_checker.py verify test_folder -m baseline_manifest.json --csv alert_report.csv
```

---

## 🧪 Tamper Detection Demonstration

### Original Content

```ini
admin_enabled=false
```

### Modified Content

```ini
admin_enabled=talse
```

Only one character is changed.

The attacker restores:

- Original timestamp
- Original file size

Even though metadata appears unchanged, SHA-256 generates a completely different hash, allowing the system to detect tampering successfully.

Example Result:

```text
[MODIFIED] config/app.ini

SIZE & TIMESTAMP UNCHANGED

old:
37679f575b1a33822a4e8950dbc2c7619392d3c151eaa328c04d7c103829a386

new:
6e863c6c0ec14f3b2c05f275b85f19b31f1494e2a33e2631ca05aca9d119a9fb
```

---

## 📊 Sample Alert Report

```text
FILE INTEGRITY REPORT

[MODIFIED] config/app.ini
[NEW] docs/backdoor.sh
[MISSING] data/students.csv

ALERT:
1 Modified
1 New
1 Missing
0 Unreadable
```

---

## 📂 Project Structure

```text
task3_file_integrity_checker/
│
├── integrity_checker.py
├── demo_tamper.py
├── test_integrity_checker.py
# 🔐 File Integrity Checker

## 🧪 Testing

Run the test suite using:

```bash
python -m unittest -v test_integrity_checker
```

Example Output:

```text
test_hash_generation ..... ok
test_baseline_creation ... ok
test_detection_logic ..... ok
test_csv_report .......... ok

---------------------------------------
Ran 4 tests

OK
```

The test cases validate:

- SHA-256 hash generation
- Baseline manifest creation
- File modification detection
- CSV report generation
- Error handling and verification logic

---

## 🔒 Security Applications

This project demonstrates concepts commonly used in:

- File Integrity Monitoring (FIM)
- Intrusion Detection Systems (IDS)
- Security Auditing
- Digital Forensics
- Malware Investigation
- Incident Response
- Compliance Monitoring

Organizations use similar techniques to detect unauthorized modifications to sensitive files, system configurations, and business-critical data.

---

## 📈 Future Enhancements

Future improvements may include:

- Real-Time File Monitoring
- Email Alert Notifications
- HMAC-Signed Baseline Manifests
- Dashboard Visualization

- ## 🎓 Learning Outcomes

Through the development of this project, the following cybersecurity and software engineering concepts were explored and implemented:

- Cryptographic Hash Functions
- SHA-256 Hashing Algorithm
- File Integrity Verification
- Tamper Detection Techniques
- Recursive Directory Traversal
- JSON Manifest Management
- CSV Report Generation
- Exception Handling
- Secure Python Programming
- Cybersecurity Monitoring Fundamentals

This project provided practical experience in building security-focused applications and understanding how integrity monitoring systems are used to protect critical files from unauthorized modifications.

---

## 🔒 Security Applications

The techniques implemented in this project are commonly used in:

- File Integrity Monitoring (FIM)
- Intrusion Detection Systems (IDS)
- Digital Forensics
- Security Auditing
- Incident Response
- Malware Investigation
- Compliance Monitoring

By monitoring changes in file hashes, organizations can quickly identify suspicious activity and maintain the integrity of critical systems.

---

## 📈 Future Enhancements

Potential improvements for future development include:

- Real-Time File Monitoring
- HMAC-Signed Manifests
- Email Alert Notifications
- Scheduled Automated Scans
- Dashboard Visualization
- SIEM Integration
- File Permission and Ownership Tracking
- Multi-User Environment Support

---

## 👩‍💻 Author

**Naina Kumari**  
B.E. Computer Science & Engineering (Data Science)  
AMC Engineering College, VTU

Cybersecurity Enthusiast | Python Developer | Aspiring Security Analyst

**CodeNova Cybersecurity Internship – Batch 01**

---

## 🙏 Acknowledgement

This project was developed as part of the **CodeNova Cybersecurity Internship Program** to gain practical experience in cryptographic hashing, file integrity monitoring, secure coding practices, and real-world cybersecurity applications.

---

## ⭐ Final Note

> **"Trust the hash, not the metadata."**

File sizes and timestamps can be manipulated, but cryptographic hashes provide a reliable way to verify the true integrity of data. By leveraging SHA-256 hashing, this project demonstrates how even the smallest unauthorized modification can be detected with confidence.

A single changed byte may go unnoticed by traditional methods, but it cannot

