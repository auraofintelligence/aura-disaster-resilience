"""Import an existing human review comment after checking its proposal and role."""
import argparse
from datetime import datetime, timezone
import json
import sys

from wiki import ROOT, fingerprint, github_comment, load, verify_review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decision', required=True)
    parser.add_argument('--role', required=True)
    parser.add_argument('--comment-url', required=True)
    parser.add_argument('--outcome', choices=['approved', 'conditional', 'changes_requested', 'rejected'], default='approved')
    args = parser.parse_args()
    data = load()
    decision = next((x for x in data['decisions'] if x['id'] == args.decision), None)
    if not decision:
        raise ValueError('Choose an existing decision ID from the wiki.')
    comment = github_comment(args.comment_url)
    review = {'decision_id': decision['id'], 'proposal_sha256': fingerprint(decision, questions=data['questions']),
              'role': args.role, 'outcome': args.outcome, 'reviewer': comment['user']['login'],
              'evidence_url': args.comment_url, 'active': True,
              'recorded_at': datetime.now(timezone.utc).isoformat()}
    verified = verify_review(review, decision, data['roles'], fetch=lambda url: comment, questions=data['questions'])
    review.update(conditions=verified['conditions'], valid_until=verified['valid_until'],
                  source_created_at=verified['source_created_at'], source_updated_at=verified['source_updated_at'])
    if any(x.get('evidence_url') == args.comment_url and x.get('active', True) for x in data['reviews']):
        raise ValueError('This comment is already recorded; retain one active copy.')
    # Keep all current-proposal reviews. Their source chronology determines the outcome.
    for previous in data['reviews']:
        if previous['decision_id'] == decision['id'] and previous['proposal_sha256'] != review['proposal_sha256']:
            previous['active'] = False
    data['reviews'].append(review)
    (ROOT / 'data/reviews.json').write_text(json.dumps(data['reviews'], indent=2) + '\n', encoding='utf-8')
    print('Recorded the existing review. Rebuild the wiki and inspect the next authorised work.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
