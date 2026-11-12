
"""Command-line interface for Linux USB diagnostics and regression checks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from usb_lab.inventory import scan_usb
from usb_lab.report import compare_snapshots


def validate_usb_id(value: str) -> str:
    """Validate and normalize a four-digit hexadecimal USB ID."""
    if re.fullmatch(r"[0-9a-fA-F]{4}", value) is None:
        raise argparse.ArgumentTypeError(
            "USB ID must contain exactly 4 hexadecimal digits (e.g. 046d)"
        )
    return value.lower()


def _load_snapshot(path: Path) -> list[dict[str, str]]:
    """Load a previously saved USB inventory snapshot."""
    data: Any = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("vendor_id"), str)
        and isinstance(item.get("product_id"), str)
        for item in data
    ):
        raise ValueError(
            "Snapshot must be a list of USB device objects "
            "with vendor_id and product_id"
        )

    return data


def filter_usb_devices(
    devices: list[dict[str, str]],
    vendor: str | None = None,
    product: str | None = None,
) -> list[dict[str, str]]:
    """Filter devices by optional vendor and product IDs."""
    filtered = []

    for device in devices:
        if vendor is not None:
            if device["vendor_id"].lower() != vendor.lower():
                continue

        if product is not None:
            if device["product_id"].lower() != product.lower():
                continue

        filtered.append(device)

    return filtered


def main(argv: list[str] | None = None) -> int:
    """Run the USB diagnostics command-line interface."""

    parser = argparse.ArgumentParser(
        description="Linux USB inventory and regression testing"
    )

    parser.add_argument(
        "--sysfs-root",
        type=Path,
        default=Path("/sys/bus/usb/devices"),
        help="USB sysfs directory; use a fixture directory for offline testing",
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Scan connected USB devices
    scan = sub.add_parser(
        "scan",
        help="Print an inventory in JSON",
    )

    scan.add_argument(
        "--vendor",
        type=validate_usb_id,
        metavar="VID",
        help="Filter by USB vendor ID (e.g. 046d)",
    )

    scan.add_argument(
        "--product",
        type=validate_usb_id,
        metavar="PID",
        help="Filter by USB product ID (e.g. c548)",
    )

    # Save inventory snapshot
    save = sub.add_parser(
        "snapshot",
        help="Save a JSON inventory baseline",
    )
    save.add_argument("file", type=Path)

    # Compare two snapshots
    diff = sub.add_parser(
        "diff",
        help="Compare two snapshot JSON files",
    )
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)

    # Check current devices against a baseline
    check = sub.add_parser(
        "check",
        help="Compare a baseline to current devices; fail if changed",
    )
    check.add_argument("baseline", type=Path)

    args = parser.parse_args(argv)

    try:
        if args.command in ("scan", "snapshot"):
            devices = scan_usb(args.sysfs_root)

            # Apply filters only to the scan command
            if args.command == "scan":
                devices = filter_usb_devices(
                    devices,
                    vendor=args.vendor,
                    product=args.product,
                )

            result = json.dumps(devices, indent=2) + "\n"

            if args.command == "scan":
                print(result, end="")
            else:
                args.file.write_text(result, encoding="utf-8")
                print(
                    f"Saved {len(devices)} devices to {args.file}"
                )

            return 0

        if args.command == "diff":
            report = compare_snapshots(
                _load_snapshot(args.before),
                _load_snapshot(args.after),
            )
        else:
            report = compare_snapshots(
                _load_snapshot(args.baseline),
                scan_usb(args.sysfs_root),
            )

        print(json.dumps(report, indent=2))

        if args.command == "diff" or report["unchanged"]:
            return 0

        return 1

    except (OSError, ValueError) as exc:
        print(f"usb-lab: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

