"""Command-line interface for inventory, snapshot and regression checks."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from usb_lab.inventory import scan_usb
from usb_lab.report import compare_snapshots


def _load_snapshot(path: Path) -> list[dict[str, str]]:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("vendor_id"), str)
        and isinstance(item.get("product_id"), str)
        for item in data
    ):
        raise ValueError("Snapshot must be a list of USB device objects with vendor_id and product_id")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Linux USB inventory and regression testing")
    parser.add_argument("--sysfs-root", type=Path, default=Path("/sys/bus/usb/devices"),
                        help="USB sysfs directory; use a fixture directory for offline testing")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("scan", help="Print an inventory in JSON")
    save = sub.add_parser("snapshot", help="Save a JSON inventory baseline")
    save.add_argument("file", type=Path)
    diff = sub.add_parser("diff", help="Compare two snapshot JSON files")
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    check = sub.add_parser("check", help="Compare a baseline to current devices; fail if changed")
    check.add_argument("baseline", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command in ("scan", "snapshot"):
            devices = scan_usb(args.sysfs_root)
            result = json.dumps(devices, indent=2) + "\n"
            if args.command == "scan":
                print(result, end="")
            else:
                args.file.write_text(result, encoding="utf-8")
                print(f"Saved {len(devices)} devices to {args.file}")
            return 0
        if args.command == "diff":
            report = compare_snapshots(_load_snapshot(args.before), _load_snapshot(args.after))
        else:
            report = compare_snapshots(_load_snapshot(args.baseline), scan_usb(args.sysfs_root))
        print(json.dumps(report, indent=2))
        return 0 if report["unchanged"] or args.command == "diff" else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"usb-lab: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
