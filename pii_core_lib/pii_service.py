"""Service facade for :mod:`pii_core_lib` — two entry points.

  * :meth:`PiiService.validate` — scan-only. Reports findings, audit-logs
    them, optionally raises. Does NOT modify the payload. Use when the
    payload itself is downstream-immutable (audit log, response text the
    caller has already shipped).

  * :meth:`PiiService.scrub` — scan + return a cleaned copy. Use on the
    prevention path (any payload about to leave the process).

Both methods share the same knobs:

  * ``strict=True`` — also runs ``phonenumbers`` + ``dateparser``
    (catches loose phones the regex misses and bare DOBs without a
    keyword anchor).
  * ``raise_on_pii=True`` — raise :class:`PIIDetectedError` on the
    first detection instead of returning. For tests / hard-gate flows.
  * ``audit_logger`` — destination for the WARNING line on any
    detection. Defaults to a module-level logger so detections never
    silently disappear.
  * ``context`` — short label woven into the audit log + raised-error
    message so operators can locate the source.

Callers needing the granular surface (single-pattern detection, NER,
category lookups, replacement-mask strategies) import directly from
``pii_core_lib.*`` — the package is the advanced API, the
service is the easy one.
"""
from __future__ import annotations

import json
import logging
from typing import Any, List, Optional, Tuple

from pii_core_lib.pii_patterns import (
    PIIPatternFinding,
    summarize_pii_findings,
)
from pii_core_lib.pii_scrub import (
    PIIDetectedError,
    scrub_pii_with_findings,
)


# Default destination for detection warnings when the caller doesn't
# pass an ``audit_logger``. Logging here (instead of going silent)
# means a misconfigured caller still leaves an operator-visible trail
# under the ``pii_core_lib.pii_service`` logger.
_DEFAULT_AUDIT_LOGGER = logging.getLogger(__name__)


class PiiService(object):
    """One-call PII scan / scrub for any JSON-shaped payload."""

    def validate(
        self,
        payload: Any,
        *,
        strict: bool = False,
        raise_on_pii: bool = False,
        audit_logger: Optional[logging.Logger] = None,
        context: str = 'payload',
    ) -> List[PIIPatternFinding]:
        """Scan ``payload`` and report what was found — do NOT modify it.

        Walks the payload recursively (``dict`` / ``list`` / ``tuple`` /
        ``str``) and matches every string against the canonical PII
        pattern set. The payload itself is unchanged on the way back.

        Args:
            payload: any JSON-shaped value.
            strict: when ``True``, also runs the library-backed
                detectors (``phonenumbers`` for stricter phone parsing,
                ``dateparser`` for bare DOBs without a keyword anchor).
            raise_on_pii: when ``True``, raise
                :class:`PIIDetectedError` on the first detection
                instead of returning the findings list.
            audit_logger: destination for the WARNING line emitted on
                any detection (pattern names + redacted previews — the
                raw matched value is never logged). Defaults to the
                module logger so detections never disappear.
            context: short label woven into the audit log so operators
                can locate the source (e.g. ``'admin_chat_response'``).

        Returns:
            The list of :class:`PIIPatternFinding` (empty when clean).
            Callers that just want a boolean can use truthiness.

        Raises:
            PIIDetectedError: when ``raise_on_pii=True`` and any
                pattern fires.
        """
        findings, _scrubbed = self._scan_and_announce(
            payload,
            strict=strict,
            raise_on_pii=raise_on_pii,
            audit_logger=audit_logger,
            context=context,
        )
        return findings

    def scrub(
        self,
        payload: Any,
        *,
        strict: bool = False,
        raise_on_pii: bool = False,
        audit_logger: Optional[logging.Logger] = None,
        context: str = 'payload',
    ) -> Any:
        """Scan ``payload`` and return a scrubbed copy.

        Same walker / pattern set as :meth:`validate`, but the returned
        value has every PII match rewritten to ``[redacted:<pattern>]``
        placeholders. Non-text primitives (``int`` / ``bool`` /
        ``None`` / dates / Decimals / UUIDs) pass through unchanged.
        The input object is never mutated.

        Args / Raises: see :meth:`validate`.

        Returns:
            A new payload safe to forward to the LLM / a downstream
            service. Container nodes (``dict`` / ``list`` / ``tuple``)
            are always rebuilt; non-text primitives pass through the
            same object.
        """
        findings, scrubbed = self._scan_and_announce(
            payload,
            strict=strict,
            raise_on_pii=raise_on_pii,
            audit_logger=audit_logger,
            context=context,
        )
        return scrubbed

    def _scan_and_announce(
        self,
        payload: Any,
        *,
        strict: bool,
        raise_on_pii: bool,
        audit_logger: Optional[logging.Logger],
        context: str,
    ) -> Tuple[List[PIIPatternFinding], Any]:
        """Shared core for :meth:`validate` and :meth:`scrub`.

        Always builds the scrubbed copy (the cost is one walk regardless),
        but the caller decides whether to expose it. Logging + raising is
        identical on both paths so a switch from ``validate`` to ``scrub``
        cannot change which detections an operator sees.
        """
        findings, scrubbed = scrub_pii_with_findings(payload)
        if strict:
            findings = findings + self._strict_only_findings(payload)
        if findings:
            # One summary string for both the audit log and the raised
            # error — operators reading either surface see the same
            # shape and can correlate them.
            summary = summarize_pii_findings(findings)
            logger = audit_logger if audit_logger is not None else _DEFAULT_AUDIT_LOGGER
            logger.warning('PII detected in %s: %s', context, summary)
            if raise_on_pii:
                raise PIIDetectedError(f'PII detected in {context}: {summary}')
        return findings, scrubbed

    def _strict_only_findings(self, payload: Any) -> List[PIIPatternFinding]:
        """Findings the regex pass cannot produce (``phonenumbers`` + ``dateparser``).

        Run only in ``strict=True`` mode; the regex set is already
        covered by :func:`scrub_pii_with_findings`. Calling the strict
        modules directly (instead of :func:`find_pii_strict`) avoids
        the duplicate regex sweep.
        """
        if payload is None:
            return []
        from pii_core_lib._pii_strict_dob import find_strict_dob
        from pii_core_lib._pii_strict_phone import find_strict_phone

        text = self._payload_as_text(payload)
        return list(find_strict_phone(text)) + list(find_strict_dob(text))

    @staticmethod
    def _payload_as_text(payload: Any) -> str:
        """Coerce ``payload`` into the single string the strict scan sees.

        Strings pass through; everything else is JSON-serialized with
        ``default=str`` so dates / Decimals / UUIDs don't crash the
        scan.
        """
        if isinstance(payload, str):
            return payload
        return json.dumps(payload, default=str, sort_keys=True)
