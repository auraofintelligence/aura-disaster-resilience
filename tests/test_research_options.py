import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import research_options


class ResearchOptionChecks(unittest.TestCase):
    def setUp(self):
        self.research = {
            'brief': {'id': 'USER-PROMPT', 'verbatim_prompt': 'Research possible answers.',
                      'recorded_on': '2026-10-20'},
            'provenance': [{'ai_generated': True, 'prompt_id': 'USER-PROMPT'}],
            'sources': [{'id': 'S-01', 'title': 'Official example', 'url': 'https://example.org/case',
                         'publisher': 'Example publisher', 'checked_on': '2026-10-20',
                         'evidence_type': 'official_case_study', 'fact': 'A limited published fact.',
                         'local_fit': 'The local setting requires its own assessment.'}],
            'answers': [{'question_id': 'OPS-01', 'summary': 'Compare a bounded local service with its alternatives.',
                         'options': [{'label': 'Existing pattern', 'kind': 'adaptation',
                                      'text': 'Prepare a local adaptation.', 'source_ids': ['S-01']},
                                     {'label': 'Future direction', 'kind': 'future_concept',
                                      'text': 'Explore a future service with a measured trial.', 'source_ids': ['S-01']}],
                         'comparators': [{'source_id': 'S-01', 'lesson': 'Compare the design choices.',
                                          'local_difference': 'Local exposure and responsibilities differ.'}],
                         'next_checks': ['Prepare the comparison and acceptance test.']}]}

    def test_complete_distinguished_options_are_valid(self):
        research_options.validate(self.research, {'OPS-01'})

    def test_unknown_reference_is_rejected(self):
        self.research['answers'][0]['options'][0]['source_ids'] = ['MISSING']
        with self.assertRaisesRegex(ValueError, 'reference'):
            research_options.validate(self.research, {'OPS-01'})

    def test_missing_question_cannot_be_published_as_complete(self):
        with self.assertRaisesRegex(ValueError, 'every question'):
            research_options.validate(self.research, {'OPS-01', 'OPS-02'})

    def test_future_concept_cannot_be_silently_presented_as_existing(self):
        self.research['answers'][0]['options'][1]['kind'] = 'adaptation'
        with self.assertRaisesRegex(ValueError, 'future concept'):
            research_options.validate(self.research, {'OPS-01'})

    def test_ai_attribution_and_prompt_reference_are_required(self):
        self.research['provenance'][0]['ai_generated'] = False
        with self.assertRaisesRegex(ValueError, 'AI provenance'):
            research_options.validate(self.research, {'OPS-01'})

    def test_empty_options_cannot_silently_disappear_after_the_request(self):
        self.research.update(answers=[], sources=[])
        with self.assertRaisesRegex(ValueError, 'research request'):
            research_options.validate(self.research, {'OPS-01'})

    def test_empty_provenance_cannot_remove_ai_attribution(self):
        self.research['provenance'] = []
        with self.assertRaisesRegex(ValueError, 'AI provenance'):
            research_options.validate(self.research, {'OPS-01'})

    def test_options_and_their_sources_are_both_bound_to_review_evidence(self):
        original = research_options.evidence_for({'OPS-01'}, self.research)
        changed = copy.deepcopy(self.research)
        changed['answers'][0]['summary'] += ' A revised proposal.'
        self.assertNotEqual(original, research_options.evidence_for({'OPS-01'}, changed))
        changed = copy.deepcopy(self.research)
        changed['sources'][0]['fact'] = 'A changed source finding.'
        self.assertNotEqual(original, research_options.evidence_for({'OPS-01'}, changed))

    def test_inline_and_card_keep_ai_status_and_primary_links_visible(self):
        answer = self.research['answers'][0]
        sources = {s['id']: s for s in self.research['sources']}
        inline = research_options.inline(answer, sources)
        card = research_options.detail(answer, self.research)
        self.assertIn('AI-generated option', inline)
        self.assertIn('AI-generated future concept', inline)
        self.assertIn('https://example.org/case', inline)
        self.assertIn('Research-brief.md', card)
        self.assertIn('AI transfer assessment', card)
        self.assertNotIn('## Recorded answer', card)


if __name__ == '__main__':
    unittest.main()
