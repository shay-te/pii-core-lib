"""``is_partial_mask=False``: every mark is ``[redacted:<pattern>]``, keeping no part of the value. The default keeps
the per-pattern masks, so callers that pass nothing see no change."""
from __future__ import annotations

import unittest

from pii_core_lib.data_layers.service.pii_service import PiiService
from pii_core_lib.pii_patterns import replacement_for
from pii_core_lib.pii_scrub import scrub_pii_with_findings

EMAIL_TEXT = 'reach jane@example.com'
MIXED_TEXT = 'reach jane@example.com or +1 555 123 4567'


class TestPiiFullMasks(unittest.TestCase):

    def test_a_full_mask_keeps_nothing_of_a_masked_pattern(self):
        self.assertEqual('[redacted:email]', replacement_for('email', 'jane@example.com', is_partial_mask=False))
        self.assertEqual('[redacted:phone]', replacement_for('phone', '+972 50 123 4567', is_partial_mask=False))
        self.assertEqual('[redacted:credit_card]',
                         replacement_for('credit_card', '4111 1111 1111 1234', is_partial_mask=False))
        self.assertEqual('[redacted:gps_coordinates]',
                         replacement_for('gps_coordinates', '37.4220, -122.0841', is_partial_mask=False))

    def test_a_full_mask_of_an_unmasked_pattern_is_its_usual_mark(self):
        self.assertEqual('[redacted:ssn]', replacement_for('ssn', '123-45-6789', is_partial_mask=False))

    def test_the_default_keeps_the_partial_masks(self):
        self.assertEqual('[redacted:email:host=example.com]', replacement_for('email', 'jane@example.com'))
        self.assertEqual('[redacted:phone:+972]', replacement_for('phone', '+972 50 123 4567'))

    def test_scrub_with_full_masks_hides_the_email_host(self):
        self.assertEqual('reach [redacted:email]', PiiService().scrub(EMAIL_TEXT, is_partial_mask=False))

    def test_scrub_by_default_still_keeps_the_email_host(self):
        self.assertEqual('reach [redacted:email:host=example.com]', PiiService().scrub(EMAIL_TEXT))

    def test_full_masks_find_exactly_what_the_partial_masks_find(self):
        full_findings, full_scrubbed = scrub_pii_with_findings(MIXED_TEXT, is_partial_mask=False)
        partial_findings, partial_scrubbed = scrub_pii_with_findings(MIXED_TEXT)
        self.assertEqual(partial_findings, full_findings)
        self.assertNotIn('example.com', full_scrubbed)
        self.assertNotIn('+1', full_scrubbed)
        self.assertIn('example.com', partial_scrubbed)


if __name__ == '__main__':
    unittest.main()
