"""Read a limited, non-sensitive USB inventory from Linux sysfs."""
from __future__ import annotations

from pathlib import Path

# Keep this intentionally minimal: never capture serial numbers, machine IDs,
# hostnames, mountpoints, or connected-device filesystem contents.
FIELDS = ("idVendor", "idProduct", "bDeviceClass", "speed")


def _read_attribute(device_dir: Path, name: str) -> str | None:
    try:
        return (device_dir / name).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None


def scan_usb(sysfs_root: Path = Path("/sys/bus/usb/devices")) -> list[dict[str, str]]:
    """Return stable, limited metadata about USB devices, sorted by sysfs path.

    USB interfaces are skipped because their sysfs entries do not have an
    idVendor/idProduct pair. Permission-denied attributes are skipped.
    """
    if not sysfs_root.is_dir():
        raise FileNotFoundError(f"USB sysfs directory not found: {sysfs_root}")

    entries: list[dict[str, str]] = []
    for path in sorted(sysfs_root.iterdir(), key=lambda p: p.name):
        if not path.is_dir():
            continue
        vendor = _read_attribute(path, "idVendor")
        product = _read_attribute(path, "idProduct")
        if not vendor or not product:
            continue
        item = {"path": path.name, "vendor_id": vendor.lower(), "product_id": product.lower()}
        device_class = _read_attribute(path, "bDeviceClass")
        speed = _read_attribute(path, "speed")
        if device_class is not None:
            item["device_class"] = device_class
        if speed is not None:
            item["speed_mbps"] = speed
        entries.append(item)
    return entries
