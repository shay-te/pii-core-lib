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

## Caller strings ride the same single pass, and every mark is full

- `strings_to_scrub` (both entry points): the library never knows what the strings are (a name, a customer code, ...);
  the caller passes them. Each becomes a literal whole-word, case-insensitive, any-script regex
  (`build_string_regexes`, pattern `custom_string`) resolved with the pattern set in `_scrub_string`'s one pass, so a
  string inside an email or URL never splits it and a placeholder is never re-matched. `None`, blank and
  one-character values are skipped. A string glued to a prefix (Hebrew "ודנה") is kept.
- Every mark is full, `replacement_for(pattern_name)` = `[redacted:<pattern>]` (operator): no partial mask exists, so no
  mark keeps an email host, a phone country code, a card's last 4 or a coarse GPS. Never add one back, or a flag for it.
- NER (`_pii_ner`, spaCy, English only) only reports findings; it is not part of `scrub`.
- A tie (same start and length) goes to the pattern declared first, and the shape-only patterns are broad: a 9-digit
  number marks as `us_passport`; 5-8 uppercase letters, digits, spaces or dashes (`DANA ` too) as `us_license_plate`,
  before a name; a lone 5-digit number as `us_zip`. A test pinning an exact mark picks a value one pattern alone matches; else it asserts the raw
  value is gone.

## Helper map

- `data_layers/service/pii_service.py` — `PiiService.scrub` (cleaned copy) / `PiiService.validate` (findings only).
- `pii_scrub.py` — `scrub_pii`, `scrub_pii_with_findings` (one walk, findings + copy), `find_pii_in_payload`,
  `assert_no_pii`, `PIIDetectedError`.
- `pii_patterns.py` — `find_pii_patterns`, `find_pii_strict`, `replacement_for`, `redact_preview`, `category_for`,
  `summarize_pii_findings`, `iter_pattern_names_and_regexes`, `get_validator_for`, `build_string_regexes`;
  constants `PII_PATTERN_NAMES`, `STRING_TO_SCRUB_PATTERN_NAME`, `STRING_MIN_LENGTH`, `CATEGORY_*`.
- `pii_scan.py` — text-stream WARNING-log helper; `credential_scan.py` / `credential_patterns.py` — vendor secrets.

## Empty `__init__.py` per package

Per the workspace rule, every package `__init__.py` is empty — no
re-exports. Callers import from the module that owns the symbol
(`from pii_core_lib.pii_patterns import find_pii_patterns`,
`from pii_core_lib.data_layers.service.pii_service import PiiService`).

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
