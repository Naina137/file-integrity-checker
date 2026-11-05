#!/usr/bin/env python3
"""
Simulation: proves the checker detects a SINGLE-BYTE change even when the file
size and the modified timestamp are restored to their original values.
Run:  python demo_tamper.py
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "test_folder" / "config" / "app.ini"


def run(*args):
    cmd = [sys.executable, "integrity_checker.py", *args]
    print("$ python integrity_checker.py " + " ".join(args))
    subprocess.run(cmd, cwd=HERE)
    print()


print("### STEP 1 - Create baseline\n")
run("baseline", "test_folder", "-m", "baseline_manifest.json")

print("### STEP 2 - Verify untouched folder\n")
run("verify", "test_folder", "-m", "baseline_manifest.json")

print("### STEP 3 - Attacker flips ONE byte (admin_enabled=false -> admin_enabled=talse)")
st = TARGET.stat()
data = bytearray(TARGET.read_bytes())
i = data.index(b"false")
data[i] = ord("t")                      # single byte change, same length
TARGET.write_bytes(bytes(data))
os.utime(TARGET, ns=(st.st_atime_ns, st.st_mtime_ns))  # restore original timestamp
st2 = TARGET.stat()
print(f"    size before/after : {st.st_size} / {st2.st_size}")
print(f"    mtime restored    : {st.st_mtime_ns == st2.st_mtime_ns}\n")

print("### STEP 4 - Verify again (tamper must be caught)\n")
run("verify", "test_folder", "-m", "baseline_manifest.json")

print("### STEP 5 - Also add a new file and delete another\n")
(HERE / "test_folder" / "docs" / "backdoor.sh").write_text("echo pwned\n")
(HERE / "test_folder" / "data" / "students.csv").unlink()
run("verify", "test_folder", "-m", "baseline_manifest.json", "--csv", "alert_report.csv")

# restore the folder so the demo can be re-run
TARGET.write_bytes(TARGET.read_bytes().replace(b"talse", b"false"))
(HERE / "test_folder" / "docs" / "backdoor.sh").unlink()
(HERE / "test_folder" / "data" / "students.csv").write_text("id,name,score\n1,alice,90\n2,bob,85\n")
