import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import wiki


class WikiChecks(unittest.TestCase):
    def setUp(self):
        self.data = wiki.load()

    def review(self, *, person='auraofintelligence', kind='User', statement=True):
        decision = self.data['decisions'][0]
        digest = wiki.fingerprint(decision)
        url = wiki.BASE + '/issues/1#issuecomment-123'
        record = {'decision_id': decision['id'], 'proposal_sha256': digest,
                  'role': 'design_curator', 'outcome': 'approved', 'reviewer': person,
                  'evidence_url': url, 'active': True}
        comment = {'user': {'login': person, 'type': kind},
                   'created_at': '2026-10-20T04:00:00Z',
                   'updated_at': '2026-10-20T04:00:00Z',
                   'body': f'HITL APPROVE {decision["id"]} {digest} scope={decision["proposal"]["scope"]}\nConditions: none' if statement else 'Looks interesting.'}
        self.data['reviews'] = [record]
        return record, comment

    def test_baseline_has_questions_and_no_assumed_approvals(self):
        approved, _ = wiki.validate(self.data)
        self.assertGreaterEqual(len(self.data['questions']), 90)
        self.assertEqual(approved, set())

    def test_duplicate_question_is_rejected(self):
        self.data['questions'].append(copy.deepcopy(self.data['questions'][0]))
        with self.assertRaisesRegex(ValueError, 'unique'):
            wiki.validate(self.data)

    def test_missing_dependency_is_rejected(self):
        self.data['questions'][0]['depends_on'].append('MISSING-01')
        with self.assertRaisesRegex(ValueError, 'missing connected'):
            wiki.validate(self.data)

    def test_circular_work_is_detected(self):
        self.data['questions'][0]['depends_on'] = [self.data['questions'][1]['id']]
        self.data['questions'][1]['depends_on'] = [self.data['questions'][0]['id']]
        with self.assertRaisesRegex(ValueError, 'circle'):
            wiki.validate(self.data)

    def test_genuine_matching_comment_counts_for_its_scope(self):
        _, comment = self.review()
        approved, _ = wiki.validate(self.data, fetch=lambda url: comment)
        self.assertEqual(approved, {'D-001'})

    def test_general_encouragement_is_not_an_approval(self):
        _, comment = self.review(statement=False)
        with self.assertRaisesRegex(ValueError, 'review statement'):
            wiki.validate(self.data, fetch=lambda url: comment)

    def test_another_account_cannot_approve_for_the_named_role(self):
        _, comment = self.review(person='another-person')
        with self.assertRaisesRegex(ValueError, 'named reviewer'):
            wiki.validate(self.data, fetch=lambda url: comment)

    def test_bot_comment_cannot_supply_human_review(self):
        _, comment = self.review(kind='Bot')
        with self.assertRaisesRegex(ValueError, 'named reviewer'):
            wiki.validate(self.data, fetch=lambda url: comment)

    def test_changed_proposal_needs_a_fresh_review(self):
        _, comment = self.review()
        self.data['decisions'][0]['proposal']['recommendation'] += ' A material change.'
        with self.assertRaisesRegex(ValueError, 'fresh review'):
            wiki.validate(self.data, fetch=lambda url: comment)

    def test_confirm_specialist_before_accepting_specialist_review(self):
        record, comment = self.review()
        decision = self.data['decisions'][0]
        decision['proposal']['required_roles'] = ['qualified_electrical']
        record['role'] = 'qualified_electrical'
        record['proposal_sha256'] = wiki.fingerprint(decision)
        with self.assertRaisesRegex(ValueError, 'confirm the person'):
            wiki.validate(self.data, fetch=lambda url: comment)

    def test_answer_requires_a_reviewed_choice(self):
        self.data['questions'][0].update(work_status='answer_recorded', answer='An answer', decision_id='D-001')
        with self.assertRaisesRegex(ValueError, 'human-reviewed'):
            wiki.validate(self.data)

    def test_archived_reviews_keep_history_without_current_authority(self):
        record, _ = self.review()
        record['active'] = False
        record['proposal_sha256'] = 'an-earlier-proposal'
        approved, _ = wiki.validate(self.data, fetch=lambda url: self.fail('Archived review was fetched'))
        self.assertEqual(approved, set())

    def test_unrelated_approved_decision_cannot_answer_a_hardware_question(self):
        _, comment = self.review()
        question = next(q for q in self.data['questions'] if q['id'] == 'PHY-05')
        question.update(work_status='answer_recorded', answer='A hardware answer', decision_id='D-001')
        with self.assertRaisesRegex(ValueError, 'reviewed proposal scope'):
            wiki.validate(self.data, fetch=lambda url: comment)

    def test_contradictory_review_statements_are_rejected(self):
        record, comment = self.review()
        comment['body'] += f'\nHITL REJECT D-001 {record["proposal_sha256"]} scope=working_method'
        with self.assertRaisesRegex(ValueError, 'review statement'):
            wiki.validate(self.data, fetch=lambda url: comment)

    def test_conditions_keep_agreement_pending(self):
        record, comment = self.review()
        comment['body'] = comment['body'].replace('Conditions: none', 'Conditions: confirm the cost first')
        with self.assertRaisesRegex(ValueError, 'conditional agreement'):
            wiki.validate(self.data, fetch=lambda url: comment)
        record['outcome'] = 'conditional'
        approved, _ = wiki.validate(self.data, fetch=lambda url: comment)
        self.assertEqual(approved, set())

    def test_unstructured_approval_condition_is_not_ignored(self):
        _, comment = self.review()
        comment['body'] += '\nProvided the host agrees first.'
        with self.assertRaisesRegex(ValueError, 'separate comment'):
            wiki.validate(self.data, fetch=lambda url: comment)

    def test_newer_rejection_wins_regardless_of_import_order(self):
        approval, first = self.review()
        rejection = {**approval, 'outcome': 'rejected', 'evidence_url': wiki.BASE + '/issues/1#issuecomment-124'}
        last = {**first, 'created_at': '2026-10-20T05:00:00Z', 'body': first['body'].replace('HITL APPROVE', 'HITL REJECT')}
        self.data['reviews'] = [rejection, approval]
        approved, _ = wiki.validate(self.data, fetch=lambda url: last if url.endswith('124') else first)
        self.assertEqual(approved, set())

    def test_question_and_review_navigation_resolves(self):
        pages = wiki.render(self.data)
        self.assertIn('Home.md', pages)
        self.assertIn('Question-PHY-01.md', pages)
        self.assertIn('Decision-D-002.md', pages)
        self.assertIn('0 approvals', pages['Home.md'])


if __name__ == '__main__':
    unittest.main()
