# AGENTS Notes — pii-core-lib

## Use only existing tools — write no new code they cover (operator, strict)

Before writing any function, helper, wrapper, constant, data-access method or service, search for one that already does the job: this repo, core-lib (`core_lib/helpers/`, its decorators) and every `*-core-lib` it imports, with their Helper maps. Use it even when it is a near fit: adapt the call site, never a variant. New code only for what nothing in the workspace does, the smallest change, and the summary names what was searched. Never a copy, a thin wrapper or a second version of an existing tool.

## No overbuilding (operator, strict)

Build only what the task asks: no rule tables, enums, status markers, retries, background workers, config or parameters for cases the task does not name, and no flexibility "for later". The smallest code that does the job; when in doubt, leave it out.

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
