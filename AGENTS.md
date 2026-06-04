# AGENTS Notes — pii-core-lib

## Zero-leak invariant (non-negotiable)

`redact_preview` in `pii_core_lib.pii_patterns` returns
`[REDACTED, len=N]` — **zero bytes** of the matched value. Operators
triage by pattern name + length; no preview-side disclosure is
allowed. The four `_redact` / `redact_preview` functions in this
package (`pii_patterns`, `_pii_strict_phone`, `_pii_strict_dob`,
`_pii_ner`) all route through the one definition. Do NOT add a
prefix / suffix / hash / partial-value back. If a debug flow needs
more, add a separate function with the trade-off in its docstring.

Tests that lock the invariant:

- `tests/test_pii_service.py::TestValidateReturnsFindings::test_redacted_preview_leaks_zero_bytes_of_the_raw_value`
- `tests/test_pii_adversarial.py::TestScrubberFlows::test_flow_assert_no_pii_redacted_preview_never_carries_raw`

## Two entry points, one core

`PiiService.validate` and `PiiService.scrub` share `_scan_and_announce`
so a switch from one to the other cannot change which detections an
operator sees. Logging + raising is identical on both paths.

## Empty `__init__.py` per package

Per the workspace rule, every package `__init__.py` is empty — no
re-exports. Callers import from the module that owns the symbol
(`from pii_core_lib.pii_patterns import find_pii_patterns`,
`from pii_core_lib.pii_service import PiiService`).

## Library-backed detectors are optional extras

`phonenumbers` (`_pii_strict_phone`), `dateparser` (`_pii_strict_dob`),
and `spacy` (`_pii_ner`) are NOT in `requirements.txt`. They are
declared as `extras_require` in `setup.py` (`pii`, `dob`, `ner`,
`all`). Imports are lazy — the strict modules only import their
backing library inside the function the first time it's called, so a
caller that never opts into `strict=True` doesn't pay the install
cost.

## Variable naming

Spell out what the value is. No `cfg`, `ws`, `bf`, `s`, `c`, `d`, `r`
shorthand. `pattern_name`, `matched_text`, `findings`, `scrubbed`,
`audit_logger` instead. See `library-core-lib/AGENTS.md` for the
canonical list.
