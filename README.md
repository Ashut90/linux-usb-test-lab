# Linux USB Test Lab

A personal, open-source Linux USB diagnostics and regression-checking CLI written in Python. It helps firmware developers and QA engineers observe which USB devices enumerate, save a baseline, and detect unexpected changes during manual regression testing. **No privileged access, network access, or USB payload capture is required.**

## Status

**Early prototype (v0.1.0).** Supports local USB inventory, JSON snapshots, and VID:PID count comparisons. Not yet a full USB compliance or performance test framework. No external users or releases are claimed.

## Platform and requirements

- Python 3.10+; Linux with USB sysfs at `/sys/bus/usb/devices`
- Unit tests can run on other platforms using temporary sysfs fixtures
- No third-party runtime dependencies

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
usb-lab scan
usb-lab snapshot before.json
# Connect/disconnect your own test USB device, then:
usb-lab snapshot after.json
usb-lab diff before.json after.json
usb-lab check before.json  # exits 1 if VID:PID counts differ
```

A laptop may show built-in USB devices as well as external peripherals. These commands only read public sysfs attributes from your local Linux machine.

## Offline test (no hardware needed)

```bash
python -m unittest discover -s tests -v
```

## Privacy and data handling

Only Linux sysfs device path, vendor ID, product ID, device class, and negotiated speed are collected. Serial numbers, hostnames, usernames, MAC addresses, file contents, and personal/customer records are **not** read. JSON files are saved only when explicitly requested by the user and should still be inspected before publishing. Never check in real device inventories if unsure of the disclosure implications.

## Known limitations

- Comparing VID:PID *counts* cannot distinguish two identical devices swapped between ports.
- Device polling, reconnect timing, logs, CSV reports, test suites, and CI hardware runs are not implemented.
- Device identification is not a security audit or USB-IF compliance test.

## Development

See [ROADMAP.md](ROADMAP.md) and GitHub issues once created. Meaningful, independently tested increments are the goal, not artificially manufactured history.

## License

MIT. See [LICENSE](LICENSE).
