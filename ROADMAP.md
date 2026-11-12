# Development roadmap

These are **planned, not implemented** enhancements. Estimated effort is a planning aid, not a claim of hours already worked.

## v0.1 — Prototype (implemented)

- [x] Read a conservative set of USB properties from Linux sysfs
- [x] CLI scan and JSON snapshot
- [x] Compare snapshots by VID:PID counts
- [x] Check mode with machine-readable exit status
- [x] Offline unit tests and GitHub Actions test workflow

## v0.2 — Robust device inventory (estimated 5–8 h)

- [ ] Strict validation of sysfs attribute formats
- [ ] USB topology hierarchy and port paths with privacy review
- [ ] Optional filters for vendor/product/class
- [ ] Command-line JSON schema and versioned report formats
- [ ] More filesystem-error and symlink tests

## v0.3 — Monitor and regression runner (estimated 8–12 h)

- [ ] Local timed polling with configurable intervals
- [ ] Detect attach/detach and temporary disconnect events
- [ ] Record latency metrics using monotonic clocks
- [ ] Add test profiles with expected VID:PID inventory
- [ ] Support cancellation and deterministic simulated replay

## v0.4 — QA reporting and CI (estimated 7–10 h)

- [ ] JUnit XML reports and CSV summaries
- [ ] Human-readable HTML summary without external resources
- [ ] Hardware-independent integration tests with injected fixtures
- [ ] Cross-Python CI matrix and lint/type checks
- [ ] Versioned releases and deployment examples

## v0.5 — Advanced diagnostics (estimated 6–10 h)

- [ ] Optional device speed-change checks
- [ ] Baseline templates for common USB peripheral categories
- [ ] Documentation of limitations, false positives, and privacy
- [ ] Performance benchmark harness on simulated USB inventories

**Total planned additional work: approximately 26–40 hours.** Scope may change based on testing and actual needs.
