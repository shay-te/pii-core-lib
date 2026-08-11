# AGENTS Notes — pii-core-lib

## Built on core-lib — read its rulebook first

This library is a `*-core-lib`. The shared architecture, conventions, and
scaffolding are **not** repeated here — they live in the `core-lib` package
(the `../core-lib/` checkout beside this repo, or the installed `core-lib`):

| Read | For |
|---|---|
| `core-lib/BUILDING_A_CORE_LIB.md` | **Read first** when building a new layer or feature — mental model, full anatomy, ordered build sequence, decision guide, recurring mistakes, Definition of Done. |
| `core-lib/AGENTS.md` | The engineering rules (§1–§8): coding conventions, file/package organization, data layer, service layer, connections, enums, testing. |
| `core-lib/skills/` | Copy-paste scaffolding templates, one per core-lib part. |

**MANDATORY — before you create or modify any part below, first load the
matching core-lib skill** (open and follow it). This is a hard rule: match the
row and load the skill *before* writing code. Never write core-lib code from
memory when a matching skill exists.

| If you are about to… | You MUST first load |
|---|---|
| add or change an entity / table / model / column / nested enum | `core-lib-entity` |
| add or change a DataAccess / DAO / repository / query / get_by / list | `core-lib-data-access` |
| add or change a Service / business logic / public method / caching | `core-lib-service` |
| add or change an external client / provider / SDK / connection factory | `core-lib-connection` |
| add a migration / alter / create / drop a table, column, index, constraint | `core-lib-migration` |
| add / fix / restructure tests or raise coverage | `core-lib-tests` |

Everything below this line is **pii-core-lib-specific** — lessons that apply only to
this library. Anything generic belongs in `core-lib/AGENTS.md` instead, so every
core-lib inherits it.

---

## Zero-leak invariant (non-negotiable)

This repo's concrete instance of core-lib **§4.9**. `redact_preview` in
`pii_core_lib.pii_patterns` returns `[REDACTED, len=N]` — **zero bytes** of the
matched value. The four `_redact` / `redact_preview` functions in this package
(`pii_patterns`, `_pii_strict_phone`, `_pii_strict_dob`, `_pii_ner`) all route
through that one definition.

Tests that lock the invariant:

- `tests/test_pii_service.py::TestValidateReturnsFindings::test_redacted_preview_leaks_zero_bytes_of_the_raw_value`
- `tests/test_pii_adversarial.py::TestScrubberFlows::test_flow_assert_no_pii_redacted_preview_never_carries_raw`

## Two entry points, one core

This repo's instance of core-lib **§4.8**: `PiiService.validate` and
`PiiService.scrub` share `_scan_and_announce`, so switching from one to the
other cannot change which detections an operator sees. Logging + raising is
identical on both paths.

## Optional detectors and their extras

Per core-lib **§5.4**, the library-backed detectors are opt-in:
`phonenumbers` (`_pii_strict_phone`), `dateparser` (`_pii_strict_dob`), and
`spacy` (`_pii_ner`) are **not** in `requirements.txt` — they are
`extras_require` in `setup.py` (`pii`, `dob`, `ner`, `all`), imported lazily
inside the function that needs them, so a caller who never opts into
`strict=True` pays nothing.
