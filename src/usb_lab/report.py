"""Compare USB inventory snapshots without collecting private data."""
from __future__ import annotations

from collections import Counter


def _device_counts(devices: list[dict[str, str]]) -> Counter[tuple[str, str]]:
    return Counter((dev["vendor_id"], dev["product_id"]) for dev in devices)


def compare_snapshots(before: list[dict[str, str]], after: list[dict[str, str]]) -> dict:
    """Compare aggregate VID:PID counts; avoids unstable sysfs path matching."""
    before_counts = _device_counts(before)
    after_counts = _device_counts(after)
    added = after_counts - before_counts
    removed = before_counts - after_counts

    def format_counts(items: Counter[tuple[str, str]]) -> list[dict[str, object]]:
        return [
            {"vendor_id": vid, "product_id": pid, "count": count}
            for (vid, pid), count in sorted(items.items())
        ]

    return {"added": format_counts(added), "removed": format_counts(removed),
            "unchanged": not added and not removed}
