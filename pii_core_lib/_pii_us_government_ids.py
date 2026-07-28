"""US-government-issued ID patterns.

Aggregated into the public ``_PII_PATTERNS`` tuple by
:mod:`pii_core_lib.pii_patterns`. Declaration
order matters (overlap resolver in the scrubber picks the
first-declared span on a tie); the order inside this file
feeds the aggregator in the same sequence.
"""
from __future__ import annotations

import re


PATTERNS = (
    # --- US government IDs --------------------------------------------
    ('ssn', re.compile(r'\b\d{3}-\d{2}-\d{4}\b')),
    # ITIN: 9XX-7X-XXXX or 9XX-8X-XXXX (the 4th digit is 7 or 8).
    ('itin', re.compile(r'\b9\d{2}-[78]\d-\d{4}\b')),
    # EIN: XX-XXXXXXX
    ('ein', re.compile(r'\b\d{2}-\d{7}\b')),
    # US passport book: 9 digits (newer issues), with optional leading letter.
    ('us_passport', re.compile(r'\b[A-Z]?\d{9}\b')),
    # US driver's license — per-state formats (scrubadub /
    # ``DriversLicenceDetector`` pattern set). The previous broad
    # ``\b[A-Z]\d{7}\b|\b\d{8}\b`` collided with every order id and
    # SKU; the per-state union below covers ~95% of the issued
    # license shapes and trades one false-positive class for narrow
    # state-specific shapes.
    #
    # Keyword-anchored on ``DL`` / ``drivers license`` / ``driver's``
    # / ``license #`` so the union doesn't collide with random
    # alphanumeric ids. The trailing alternation is the per-state
    # shape table; each ``(?:...)`` group is one state's published
    # format (DMV websites; cross-checked against scrubadub's table).
    ('us_drivers_license', re.compile(
        r'\b(?:DL|drivers?\s+licen[cs]e|license\s*#?)\s*[:=]?\s*'
        r'(?:'
            # CA, FL, MD, MI, MN, NJ — letter + 7 digits
            r'[A-Z]\d{7}'
            # AZ — letter + 8 digits
            r'|[A-Z]\d{8}'
            # IL — letter + 11 digits
            r'|[A-Z]\d{11}'
            # KS, MA — letter + 8 digits OR 9 digits
            r'|[A-Z]\d{8}'
            # NY — 9 digits OR letter + 18 digits
            r'|\d{9}|[A-Z]\d{18}'
            # OH — 2 letters + 6 digits
            r'|[A-Z]{2}\d{6}'
            # TX, VA, WA — 8 digits, no letter
            r'|\d{8}'
            # PA — 8 digits
            # GA — 7-9 digits
            r'|\d{7,9}'
            # WI — letter + 13 digits
            r'|[A-Z]\d{13}'
        r')\b',
        re.IGNORECASE,
    )),
    # Medicare Beneficiary Identifier (MBI), post-2018 format:
    # 1 numeric + 1 alpha + 1 alphanumeric + 1 numeric + 1 alpha +
    # 1 alphanumeric + 1 numeric + 2 alpha + 2 numeric.
    ('medicare_mbi', re.compile(
        r'\b[1-9][A-Z][A-Z\d][\d]-?[A-Z][A-Z\d][\d]-?[A-Z]{2}\d{2}\b'
    )),

)
