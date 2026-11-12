import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from usb_lab.cli import main
from usb_lab.inventory import scan_usb
from usb_lab.report import compare_snapshots


class UsbLabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make_device(self, name, vendor="1234", product="abcd", speed="480"):
        device = self.root / name
        device.mkdir()
        (device / "idVendor").write_text(vendor)
        (device / "idProduct").write_text(product)
        (device / "speed").write_text(speed)
        return device

    def test_empty_directory(self):
        self.assertEqual(scan_usb(self.root), [])

    def test_one_device(self):
        self.make_device("1-1")
        self.assertEqual(scan_usb(self.root)[0]["vendor_id"], "1234")

    def test_ignores_interface_entry(self):
        self.make_device("1-1")
        (self.root / "1-1:1.0").mkdir()
        self.assertEqual(len(scan_usb(self.root)), 1)

    def test_ignores_serial_number(self):
        device = self.make_device("1-1")
        (device / "serial").write_text("private-serial")
        self.assertNotIn("serial", scan_usb(self.root)[0])
        self.assertNotIn("private-serial", json.dumps(scan_usb(self.root)))

    def test_missing_speed_allowed(self):
        device = self.make_device("1-1")
        (device / "speed").unlink()
        self.assertNotIn("speed_mbps", scan_usb(self.root)[0])

    def test_missing_root(self):
        with self.assertRaises(FileNotFoundError):
            scan_usb(self.root / "missing")

    def test_count_diff(self):
        before = [{"vendor_id": "1234", "product_id": "abcd"}]
        after = before * 2
        report = compare_snapshots(before, after)
        self.assertEqual(report["added"][0]["count"], 1)
        self.assertFalse(report["unchanged"])

    def test_same_hardware_new_path(self):
        first = [{"path": "1-1", "vendor_id": "1234", "product_id": "abcd"}]
        second = [{"path": "2-1", "vendor_id": "1234", "product_id": "abcd"}]
        self.assertTrue(compare_snapshots(first, second)["unchanged"])

    def test_cli_snapshot(self):
        self.make_device("1-1")
        target = self.root / "baseline.json"
        self.assertEqual(main(["--sysfs-root", str(self.root), "snapshot", str(target)]), 0)
        self.assertEqual(len(json.loads(target.read_text())), 1)

    def test_cli_check_changed_exit_one(self):
        target = self.root / "baseline.json"
        target.write_text("[]")
        self.make_device("1-1")
        self.assertEqual(main(["--sysfs-root", str(self.root), "check", str(target)]), 1)

    def test_cli_check_unchanged_exit_zero(self):
        target = self.root / "baseline.json"
        target.write_text("[]")
        self.assertEqual(main(["--sysfs-root", str(self.root), "check", str(target)]), 0)

    def test_cli_invalid_snapshot_exit_two(self):
        target = self.root / "baseline.json"
        target.write_text('{"unexpected": true}')
        self.assertEqual(main(["--sysfs-root", str(self.root), "check", str(target)]), 2)


if __name__ == "__main__":
    unittest.main()
