"""Tests for the severity-tier categories and the replacement mark — the
structural follow-up borrowed from pii-codex (tiering).

Three layers of coverage:

* :class:`TestCategoryFor` — every locked pattern name is tier-classified;
  the lookup function returns the right category; unknown names return
  ``None``.
* :class:`TestReplacementFor` — every mark is full, ``[redacted:<name>]``:
  nothing of the value is kept.
* :class:`TestReplacementsDoNotReMatch` — the replacement mark must NOT
  re-match the same pattern (the round-trip property
  ``scrub_pii → find_pii_patterns → []`` is what the chat boundary
  relies on).
"""
from __future__ import annotations

import unittest

from pii_core_lib.pii_patterns import (
    PII_PATTERN_NAMES,
    _PATTERN_CATEGORIES,
    CATEGORY_ADDRESS,
    CATEGORY_CONTACT,
    CATEGORY_CREDENTIAL,
    CATEGORY_FINANCIAL,
    CATEGORY_GOVERNMENT_ID,
    CATEGORY_NETWORK_DEVICE,
    CATEGORY_POSTAL,
    CATEGORY_TEMPORAL,
    CATEGORY_VEHICLE,
    category_for,
    find_pii_patterns,
    replacement_for,
)


_VALID_CATEGORIES = frozenset({
    CATEGORY_CONTACT,
    CATEGORY_GOVERNMENT_ID,
    CATEGORY_FINANCIAL,
    CATEGORY_POSTAL,
    CATEGORY_NETWORK_DEVICE,
    CATEGORY_VEHICLE,
    CATEGORY_ADDRESS,
    CATEGORY_TEMPORAL,
    CATEGORY_CREDENTIAL,
})


class TestCategoryFor(unittest.TestCase):
    def test_every_locked_pattern_has_a_category(self):
        missing = [name for name in PII_PATTERN_NAMES if name not in _PATTERN_CATEGORIES]
        self.assertEqual(
            missing, [],
            f'pattern names without a category — add them to '
            f'_PATTERN_CATEGORIES in pii_patterns.py: {missing}',
        )

    def test_every_category_value_is_a_known_tier(self):
        for pattern_name, category in _PATTERN_CATEGORIES.items():
            with self.subTest(pattern=pattern_name):
                self.assertIn(category, _VALID_CATEGORIES)

    def test_category_for_known_pattern(self):
        self.assertEqual(category_for('email'), CATEGORY_CONTACT)
        self.assertEqual(category_for('ssn'), CATEGORY_GOVERNMENT_ID)
        self.assertEqual(category_for('credit_card'), CATEGORY_FINANCIAL)
        self.assertEqual(category_for('us_zip'), CATEGORY_POSTAL)
        self.assertEqual(category_for('ipv4'), CATEGORY_NETWORK_DEVICE)
        self.assertEqual(category_for('vin'), CATEGORY_VEHICLE)
        self.assertEqual(category_for('po_box'), CATEGORY_ADDRESS)
        self.assertEqual(category_for('date_of_birth'), CATEGORY_TEMPORAL)
        self.assertEqual(category_for('jwt'), CATEGORY_CREDENTIAL)
        self.assertEqual(category_for('il_id'), CATEGORY_GOVERNMENT_ID)

    def test_category_for_unknown_returns_none(self):
        self.assertIsNone(category_for('made_up_pattern'))


class TestReplacementFor(unittest.TestCase):
    def test_every_mark_is_the_pattern_name_alone(self):
        for pattern_name in ('ssn', 'us_passport', 'credit_card', 'phone', 'email', 'gps_coordinates'):
            with self.subTest(pattern=pattern_name):
                self.assertEqual(replacement_for(pattern_name), f'[redacted:{pattern_name}]')


class TestReplacementsDoNotReMatch(unittest.TestCase):
    """Critical round-trip property: the replacement mark must NOT itself
    match the same pattern. The chat boundary's audit path uses
    ``scrub_pii`` then ``assert_no_pii`` — if the replacement re-matched,
    the audit would fail on the very output the scrubber produced.
    """

    _PATTERN_NAMES = ('credit_card', 'phone', 'email', 'gps_coordinates')

    def test_replacement_does_not_re_match_its_own_pattern(self):
        for pattern_name in self._PATTERN_NAMES:
            with self.subTest(pattern=pattern_name):
                replacement = replacement_for(pattern_name)
                round_trip = find_pii_patterns(replacement)
                same_pattern_hits = [
                    finding.pattern_name for finding in round_trip
                    if finding.pattern_name == pattern_name
                ]
                self.assertEqual(
                    same_pattern_hits, [],
                    f'{pattern_name} replacement {replacement!r} re-matches '
                    f'its own pattern — round-trip ``scrub_pii → '
                    f'find_pii_patterns`` would loop forever / re-trigger '
                    f'the audit.',
                )
