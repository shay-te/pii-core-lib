# pii-core-lib

Personally-identifiable-information detection + scrubbing for any
JSON-shaped payload, packaged as a `core-lib` consumer.

## What's in here

* **`pii_core_lib.pii_service.PiiService`** — one-call facade with two
  methods:
  * `validate(payload, ...) -> List[PIIPatternFinding]` — scan only.
  * `scrub(payload, ...) -> Any` — scan + return a cleaned copy.

  Both share four knobs: `strict` / `raise_on_pii` / `audit_logger` /
  `context`.

* **`pii_core_lib.pii_patterns`** — the canonical pattern set (150+
  named PII families, US + intl gov IDs, crypto chains, postcodes,
  social handles, vehicle plates, etc.) plus the per-pattern
  validators / categories / replacement strategies.

* **`pii_core_lib.pii_scrub`** — structured-payload helpers:
  `find_pii_in_payload`, `assert_no_pii`, `scrub_pii`,
  `scrub_pii_with_findings` (the single-pass scrub+report the
  service uses).

* **`pii_core_lib.pii_scan`** — text-stream WARNING-log helper for
  callers that want to scan a string rather than a payload.

* **Strict detectors** (library-backed; optional deps):
  `_pii_strict_phone` (`phonenumbers`), `_pii_strict_dob`
  (`dateparser`), `_pii_ner` (spaCy).

## Zero-leak audit policy

Every finding the package emits carries `redacted_preview =
[REDACTED, len=N]` — zero bytes of the matched value. Operators
triage by pattern name + length; no preview-side disclosure is
possible.

## Composition root

`pii_core_lib.pii_core_lib.PiiCoreLib(CoreLib)` is the hydra-loadable
entry point. Host apps add `pii_core_lib` to their config search path
and read settings under `core_lib.pii.*`.
