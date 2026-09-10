# Changelog

All notable changes to this skill are documented here. Versions match `skill.json` / `.claude-plugin/plugin.json`.

## 0.3.0 — 2026-09-10

### Fixed
- `check_doc.py` no longer prints any part of a matched credential when it
  reports a BLOCKING finding — only the line number and pattern label. It
  previously echoed up to 70 characters of the offending line, which could
  put a credential fragment into console output or CI logs — exactly what
  the tool exists to prevent.
- The "Undated cost figure" check now looks at the surrounding lines (a
  6-line window) instead of only the line the price is on, so a date stated
  once above a cost table no longer causes every row below it to be
  flagged as undated.

### Added
- `tests/` — a synthetic fixture repo and sample docs, with `unittest`
  coverage for `safe_inventory.py`'s never-read guarantee and
  `check_doc.py`'s credential/slop detectors.
- `.github/workflows/test.yml` — runs the test suite on push/PR (Python 3.9
  and 3.12) and runs `check_doc.py` against the shipped templates as a
  regression gate.

## 0.2.0 and earlier

Not tracked in this file. See git history.
