"""``is_partial_mask``: ``scrub`` is full by default and keeps a clue of an email, a phone and GPS coordinates only
when the caller asks (the matchmaker reading through the AI). A credit card is always full."""
from __future__ import annotations

import unittest

from pii_core_lib.data_layers.service.pii_service import PiiService
from pii_core_lib.pii_scrub import scrub_pii, scrub_pii_with_findings

EMAIL_TEXT = 'reach jane@example.com'
MIXED_TEXT = 'jane@example.com, +972 50 123 4567, card 4111111111111111, at 37.4220, -122.0841'


class TestPiiPartialMarks(unittest.TestCase):

    def test_scrub_is_full_by_default(self):
        self.assertEqual('reach [redacted:email]', PiiService().scrub(EMAIL_TEXT))
        self.assertEqual('reach [redacted:email]', scrub_pii(EMAIL_TEXT))

    def test_scrub_keeps_a_clue_when_partial_marks_are_asked(self):
        self.assertEqual('reach [redacted:email:host=example.com]',
                         PiiService().scrub(EMAIL_TEXT, is_partial_mask=True))

    def test_a_partial_scrub_of_mixed_text_keeps_a_clue_of_all_but_the_card(self):
        scrubbed = PiiService().scrub(MIXED_TEXT, is_partial_mask=True)
        self.assertIn('[redacted:email:host=example.com]', scrubbed)
        self.assertIn('[redacted:phone:+972]', scrubbed)
        self.assertIn('[redacted:gps_coordinates:37.4,-122.1]', scrubbed)
        self.assertIn('[redacted:credit_card]', scrubbed)
        self.assertNotIn('4111', scrubbed)

    def test_full_and_partial_scrubs_report_the_same_findings(self):
        full_findings, _ = scrub_pii_with_findings(MIXED_TEXT)
        partial_findings, _ = scrub_pii_with_findings(MIXED_TEXT, is_partial_mask=True)
        self.assertEqual(full_findings, partial_findings)

    def test_a_partial_scrub_walks_containers_too(self):
        scrubbed = PiiService().scrub({'note': [EMAIL_TEXT], 'id': 7}, is_partial_mask=True)
        self.assertEqual({'note': ['reach [redacted:email:host=example.com]'], 'id': 7}, scrubbed)


if __name__ == '__main__':
    unittest.main()
