
"""Tests for USB vendor and product filtering."""

import argparse
import unittest

from usb_lab.cli import filter_usb_devices, validate_usb_id


class TestUsbFiltering(unittest.TestCase):

    def setUp(self):
        self.devices = [
            {"path": "1-1", "vendor_id": "046d", "product_id": "c548"},
            {"path": "1-2", "vendor_id": "8087", "product_id": "0aaa"},
            {"path": "1-3", "vendor_id": "046d", "product_id": "c52b"},
        ]

    def test_filter_by_vendor(self):
        result = filter_usb_devices(self.devices, vendor="046d")
        self.assertEqual(len(result), 2)

    def test_filter_by_product(self):
        result = filter_usb_devices(self.devices, product="c548")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["path"], "1-1")

    def test_filter_by_vendor_and_product(self):
        result = filter_usb_devices(
            self.devices, vendor="046d", product="c548"
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["path"], "1-1")

    def test_no_matching_devices(self):
        result = filter_usb_devices(self.devices, vendor="ffff")
        self.assertEqual(result, [])

    def test_case_insensitive_filter(self):
        result = filter_usb_devices(
            self.devices, vendor="046D", product="C548"
        )
        self.assertEqual(len(result), 1)

    def test_no_filter(self):
        result = filter_usb_devices(self.devices)
        self.assertEqual(result, self.devices)

    def test_valid_usb_id(self):
        self.assertEqual(validate_usb_id("C548"), "c548")

    def test_invalid_usb_id(self):
        for value in ("XYZ", "12345", "12G4", ""):
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError):
                    validate_usb_id(value)


if __name__ == "__main__":
    unittest.main()
