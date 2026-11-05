import os, tempfile, unittest
from pathlib import Path
from unittest import mock
import integrity_checker as ic


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "a" / "b").mkdir(parents=True)
        (self.root / "a" / "b" / "deep.txt").write_text("deep")
        (self.root / "top.bin").write_bytes(bytes(range(256)))

    def tearDown(self):
        self.tmp.cleanup()

    def test_nested_and_binary_files_hashed(self):
        rec, err = ic.scan_directory(self.root, set())
        self.assertEqual(set(rec), {"a/b/deep.txt", "top.bin"})
        self.assertFalse(err)

    def test_single_byte_change_same_size_and_mtime(self):
        base, _ = ic.scan_directory(self.root, set())
        f = self.root / "top.bin"
        st = f.stat()
        data = bytearray(f.read_bytes()); data[10] ^= 1
        f.write_bytes(bytes(data)); os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns))
        cur, err = ic.scan_directory(self.root, set())
        res = ic.compare(base, cur, err)
        self.assertEqual(len(res["modified"]), 1)
        self.assertTrue(res["modified"][0]["stealth"])

    def test_new_and_missing(self):
        base, _ = ic.scan_directory(self.root, set())
        (self.root / "new.txt").write_text("x"); (self.root / "top.bin").unlink()
        cur, err = ic.scan_directory(self.root, set())
        res = ic.compare(base, cur, err)
        self.assertEqual(res["new"], ["new.txt"]); self.assertEqual(res["missing"], ["top.bin"])

    def test_permission_error_does_not_crash(self):
        base, _ = ic.scan_directory(self.root, set())
        with mock.patch("integrity_checker.sha256_of_file", side_effect=PermissionError):
            cur, err = ic.scan_directory(self.root, set())
        self.assertEqual(len(err), 2)
        res = ic.compare(base, cur, err)
        self.assertEqual(len(res["unreadable"]), 2)
        self.assertFalse(res["missing"])  # unreadable is not reported as missing


if __name__ == "__main__":
    unittest.main()
