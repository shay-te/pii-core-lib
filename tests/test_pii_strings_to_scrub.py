"""``strings_to_scrub``: the caller lists literal strings, and each is redacted wherever it stands as a whole word, in
the scrubber's one pass."""
from __future__ import annotations

import unittest

from pii_core_lib.data_layers.service.pii_service import PiiService
from pii_core_lib.pii_patterns import STRING_TO_SCRUB_PATTERN_NAME, PIIPatternFinding
from pii_core_lib.pii_scrub import scrub_pii

NAME_MARK = f'[redacted:{STRING_TO_SCRUB_PATTERN_NAME}]'


class TestPiiStringsToScrub(unittest.TestCase):

    def setUp(self):
        self.pii_service = PiiService()

    def test_the_first_and_last_name_are_redacted(self):
        scrubbed = self.pii_service.scrub('Dana Cohen loves hiking', strings_to_scrub=['Dana', 'Cohen'])
        self.assertEqual(f'{NAME_MARK} {NAME_MARK} loves hiking', scrubbed)

    def test_a_name_matches_in_any_case(self):
        scrubbed = self.pii_service.scrub('ELI and eli', strings_to_scrub=['Eli'])
        self.assertEqual(f'{NAME_MARK} and {NAME_MARK}', scrubbed)

    def test_a_hebrew_name_is_redacted(self):
        scrubbed = self.pii_service.scrub('שמי דנה ואני אוהבת טיולים', strings_to_scrub=['דנה'])
        self.assertEqual(f'שמי {NAME_MARK} ואני אוהבת טיולים', scrubbed)

    def test_a_name_inside_a_longer_word_is_kept(self):
        scrubbed = self.pii_service.scrub('Danger Dan', strings_to_scrub=['Dan'])
        self.assertEqual(f'Danger {NAME_MARK}', scrubbed)

    def test_none_blank_and_one_letter_names_are_skipped(self):
        text = 'D. was here'
        self.assertEqual(text, self.pii_service.scrub(text, strings_to_scrub=[None, '', '   ', 'D']))

    def test_a_name_is_matched_as_written_not_as_a_pattern(self):
        scrubbed = self.pii_service.scrub('Jean-Luc said hi to JxL and J.L', strings_to_scrub=['Jean-Luc', 'J.L'])
        self.assertEqual(f'{NAME_MARK} said hi to JxL and {NAME_MARK}', scrubbed)

    def test_a_name_inside_an_email_leaves_one_email_mark(self):
        scrubbed = self.pii_service.scrub('write to dana.cohen@example.com', strings_to_scrub=['dana', 'cohen'])
        self.assertEqual('write to [redacted:email]', scrubbed)

    def test_a_name_spelled_like_a_mark_never_rewrites_a_mark(self):
        # One pass over the original text: the placeholder written for the email is never scanned again.
        scrubbed = self.pii_service.scrub('email me at jane@example.com', strings_to_scrub=['email', 'redacted'])
        self.assertEqual(f'{NAME_MARK} me at [redacted:email]', scrubbed)

    def test_the_same_name_twice_is_redacted_once(self):
        self.assertEqual(NAME_MARK, self.pii_service.scrub('Dana', strings_to_scrub=['Dana', 'dana', ' Dana ']))

    def test_names_are_redacted_in_every_value_and_never_in_a_key(self):
        scrubbed = self.pii_service.scrub({'Dana': 'Dana writes', 'notes': ['dana', 7]}, strings_to_scrub=('Dana',))
        self.assertEqual({'Dana': f'{NAME_MARK} writes', 'notes': [NAME_MARK, 7]}, scrubbed)

    def test_names_and_patterns_are_resolved_together(self):
        scrubbed = self.pii_service.scrub('Dana Cohen: dana@example.com', strings_to_scrub=['Dana', 'Cohen'])
        self.assertEqual(f'{NAME_MARK} {NAME_MARK}: [redacted:email]', scrubbed)

    def test_validate_reports_a_name_with_zero_bytes_of_it(self):
        findings = self.pii_service.validate('Dana says hi', strings_to_scrub=['Dana'])
        self.assertEqual([PIIPatternFinding(pattern_name=STRING_TO_SCRUB_PATTERN_NAME,
                                            redacted_preview='[REDACTED, len=4]')], findings)

    def test_without_names_a_name_stays(self):
        self.assertEqual('Dana Cohen', self.pii_service.scrub('Dana Cohen'))
        self.assertEqual('Dana Cohen', scrub_pii('Dana Cohen'))


if __name__ == '__main__':
    unittest.main()
