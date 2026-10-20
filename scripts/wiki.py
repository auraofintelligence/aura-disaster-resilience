"""Build the linked GitHub wiki and check its question and review records."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote, unquote
from urllib.request import Request, urlopen

import research_options

ROOT = Path(__file__).resolve().parents[1]
REPO = 'auraofintelligence/aura-disaster-resilience'
BASE = f'https://github.com/{REPO}'
WORK_STATES = {'open', 'researching', 'options_ready', 'in_review', 'answer_recorded', 'deferred'}


def read_json(name, root=ROOT):
    return json.loads((root / 'data' / name).read_text(encoding='utf-8'))


def load(root=ROOT):
    data = {key: read_json(key + '.json', root) for key in
            ('questions', 'domains', 'decisions', 'reviews', 'roles', 'constraints', 'tasks', 'ecosystem')}
    data['research'] = research_options.load(root)
    return data


def content_digest(path):
    """Keep review fingerprints stable across Git's text line-ending conversion."""
    if path.suffix == '.json':
        content = json.dumps(json.loads(path.read_text(encoding='utf-8')),
                             sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
    elif path.suffix in {'.md', '.txt', '.py', '.yml', '.yaml'}:
        content = path.read_text(encoding='utf-8').encode()
    else:
        content = path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def evidence_fingerprint(decision, root=ROOT, questions=None, research=None):
    """Identify the evidence presented with this choice, including source snapshots."""
    proposal = dict(decision['proposal'])
    files = {}
    for name in proposal.get('files', []):
        p = (root / name).resolve()
        if not p.is_relative_to(root.resolve()) or not p.is_file():
            raise ValueError(f'{decision["id"]}: supporting file is unavailable: {name}')
        files[name] = content_digest(p)
    question_index = {q['id']: q for q in (questions if questions is not None else read_json('questions.json', root))}
    selected = {qid: {k: v for k, v in question_index[qid].items()
                     if k not in {'work_status', 'assigned_to', 'answer', 'decision_id'}}
                for qid in proposal['question_ids']}
    manifests = {}
    for name in ('document-manifest.json', 'site-manifest.json', 'web-page-manifest.json'):
        path = root / 'data' / name
        if path.exists():
            if name in {'site-manifest.json', 'web-page-manifest.json'} and json.loads(path.read_text(encoding='utf-8')).get('capture_status') != 'complete':
                continue
            manifests[name] = content_digest(path)
    research = research if research is not None else research_options.load(root)
    payload = {'files': files, 'questions': selected, 'source_manifests': manifests,
               'ai_options': research_options.evidence_for(proposal['question_ids'], research)}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def fingerprint(decision, root=ROOT, questions=None, research=None):
    payload = {'proposal': decision['proposal'], 'evidence_sha256': evidence_fingerprint(decision, root, questions, research)}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def github_comment(url):
    match = re.fullmatch(r'https://github\.com/' + re.escape(REPO) +
                         r'/issues/(\d+)#issuecomment-(\d+)', url)
    if not match:
        raise ValueError('Use a comment link from an issue in this repository.')
    issue, number = match.groups()
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Aura-Resilience-Wiki',
               'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = Request(f'https://api.github.com/repos/{REPO}/issues/comments/{number}', headers=headers)
    with urlopen(request, timeout=25) as response:
        value = json.load(response)
    if value.get('html_url') != url or not value.get('issue_url', '').endswith('/' + issue):
        raise ValueError('The returned comment does not match its review link.')
    return value


def verify_review(review, decision, roles, root=ROOT, fetch=github_comment, questions=None, research=None):
    """Read the source comment each time; saved JSON alone never grants approval."""
    digest = fingerprint(decision, root, questions, research)
    if review.get('proposal_sha256') != digest:
        raise ValueError(f'{decision["id"]}: the proposal changed; a fresh review is needed.')
    role = review.get('role')
    if role not in decision['proposal']['required_roles']:
        raise ValueError(f'{decision["id"]}: review role is outside this proposal.')
    people = roles.get(role, {}).get('github_users', [])
    if not people:
        raise ValueError(f'{decision["id"]}: confirm the person for role {role} first.')
    comment = fetch(review['evidence_url'])
    person = comment.get('user', {})
    if person.get('type') != 'User' or person.get('login') not in people:
        raise ValueError(f'{decision["id"]}: the commenter is not a named reviewer for {role}.')
    if review.get('reviewer') != person['login']:
        raise ValueError('The saved reviewer and source comment differ.')
    outcome = review.get('outcome')
    words = {'approved': 'APPROVE', 'conditional': 'APPROVE', 'changes_requested': 'CHANGE', 'rejected': 'REJECT'}
    if outcome not in words:
        raise ValueError('Choose APPROVE, CHANGE or REJECT.')
    line = f'HITL {words[outcome]} {decision["id"]} {digest} scope={decision["proposal"]["scope"]}'
    lines = [x.strip() for x in comment.get('body', '').splitlines() if x.strip()]
    statements = [x for x in lines if re.match(r'HITL (APPROVE|CHANGE|REJECT) ' + re.escape(decision['id']) + r'\b', x)]
    if statements != [line]:
        raise ValueError('The source comment does not contain the matching review statement.')
    conditions_lines = [x for x in lines if x.startswith('Conditions: ')]
    validity_lines = [x for x in lines if x.startswith('Valid-until: ')]
    if len(conditions_lines) != 1 or len(validity_lines) > 1:
        raise ValueError('Record one Conditions field; use Conditions: none for unconditional agreement.')
    conditions = conditions_lines[0].split(': ', 1)[1].strip()
    if outcome in {'approved', 'conditional'}:
        allowed = [line] + conditions_lines + validity_lines
        if sorted(lines) != sorted(allowed):
            raise ValueError('Keep the approval record to the statement, Conditions and optional Valid-until fields; discuss reasons in a separate comment.')
        expected = 'approved' if conditions.lower() == 'none' else 'conditional'
        if outcome != expected:
            raise ValueError('Record conditional agreement separately until its conditions receive a fresh human decision.')
    valid_until = None
    current_outcome = outcome
    if validity_lines:
        valid_until = validity_lines[0].split(': ', 1)[1]
        expiry = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
        if expiry.tzinfo is None:
            raise ValueError('Give the validity time an explicit timezone.')
        if expiry <= datetime.now(timezone.utc):
            current_outcome = 'expired'
    return {**review, 'outcome': current_outcome, 'conditions': conditions, 'valid_until': valid_until,
            'source_created_at': comment['created_at'], 'source_updated_at': comment['updated_at'],
            'source_comment_id': int(review['evidence_url'].rsplit('-', 1)[1])}


def validate(data, root=ROOT, fetch=github_comment):
    questions = data['questions']
    index = {q['id']: q for q in questions}
    if len(index) != len(questions):
        raise ValueError('Question IDs must be unique.')
    research = data['research'] if 'research' in data else research_options.load(root)
    research_options.validate(research, index)
    domains = {d['id'] for d in data['domains']}
    required = {'id', 'domain', 'question', 'why', 'expected_deliverable', 'depends_on',
                'decision_authority_role', 'current_evidence', 'work_status'}
    for q in questions:
        if not required <= q.keys():
            raise ValueError(f'{q.get("id")}: missing fields {required - q.keys()}')
        if q['domain'] not in domains or not q['id'].startswith(q['domain'] + '-'):
            raise ValueError(f'{q["id"]}: question and work area differ.')
        if q['work_status'] not in WORK_STATES:
            raise ValueError(f'{q["id"]}: unknown work state.')
        for dep in q['depends_on']:
            if dep not in index:
                raise ValueError(f'{q["id"]}: missing connected question {dep}')
    active, seen = set(), set()
    def visit(qid):
        if qid in active:
            raise ValueError(f'Questions depend on one another in a circle at {qid}.')
        if qid in seen:
            return
        active.add(qid)
        for dep in index[qid]['depends_on']:
            visit(dep)
        active.remove(qid)
        seen.add(qid)
    for qid in index:
        visit(qid)
    decisions = {d['id']: d for d in data['decisions']}
    if len(decisions) != len(data['decisions']):
        raise ValueError('Decision IDs must be unique.')
    for d in data['decisions']:
        if not d['proposal'].get('scope') or not d['proposal'].get('required_roles'):
            raise ValueError(f'{d["id"]}: give the proposal a review scope and named roles.')
        if not set(d['proposal'].get('answers', {})) <= set(d['proposal']['question_ids']):
            raise ValueError(f'{d["id"]}: proposed answers must belong to the reviewed questions.')
        fingerprint(d, root, questions, research)
        for qid in d['proposal']['question_ids']:
            if qid not in index:
                raise ValueError(f'{d["id"]}: missing question {qid}')
    latest = {}
    for review in data['reviews']:
        if review['decision_id'] not in decisions:
            raise ValueError('Review refers to a missing decision.')
        current_digest = fingerprint(decisions[review['decision_id']], root, questions, research)
        if not review.get('active', True) and review['proposal_sha256'] != current_digest:
            continue
        verified = verify_review(review, decisions[review['decision_id']], data['roles'], root, fetch, questions, research)
        key = (review['decision_id'], review['role'])
        if key not in latest or (verified['source_created_at'], verified['source_comment_id']) > (
                latest[key]['source_created_at'], latest[key]['source_comment_id']):
            latest[key] = verified
    approved = set()
    for d in data['decisions']:
        reviews = [latest.get((d['id'], role)) for role in d['proposal']['required_roles']]
        if all(r and r['outcome'] == 'approved' for r in reviews):
            approved.add(d['id'])
    for q in questions:
        if q.get('answer') and q['work_status'] != 'answer_recorded':
            raise ValueError(f'{q["id"]}: a recorded answer needs the answer_recorded work state and its checked review.')
        if q['work_status'] == 'answer_recorded':
            if q.get('decision_id') not in approved or not q.get('answer'):
                raise ValueError(f'{q["id"]}: an answer needs its matching human-reviewed decision.')
            decision = decisions[q['decision_id']]['proposal']
            if q['id'] not in decision['question_ids'] or decision.get('answers', {}).get(q['id']) != q['answer']:
                raise ValueError(f'{q["id"]}: this exact answer must be part of the reviewed proposal scope.')
    for collection in ('tasks', 'ecosystem'):
        for row in data[collection]:
            for qid in row['question_ids']:
                if qid not in index:
                    raise ValueError(f'{row["id"]}: missing question {qid}')
    text = json.dumps(data, ensure_ascii=False)
    if re.search(r'(?i)[cgl]:[/\\]|ready\s+set\b|\bSETCo\b|\bSET Co\b|P4A[- ]cinema', text):
        raise ValueError('Check private workstation paths and agreed organisation names.')
    return approved, latest


def link(qid):
    return f'[{qid}](Question-{qid}.md)'


def table(headers, rows):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(map(cell, headers)) + ' |',
                     '| ' + ' | '.join('---' for _ in headers) + ' |'] +
                    ['| ' + ' | '.join(map(cell, row)) + ' |' for row in rows])


def evidence(item):
    label = item['title']
    if item.get('url'):
        label = f'[{label}]({item["url"]})'
    else:
        label += ' — reviewed source; public copy can be added through the evidence process'
    return label + (f' ({item["locator"]})' if item.get('locator') else '')


def render(data, root=ROOT, fetch=github_comment):
    approved, reviews = validate(data, root, fetch)
    questions = data['questions']
    index = {q['id']: q for q in questions}
    research = data['research'] if 'research' in data else research_options.load(root)
    ai_answers = {a['question_id']: a for a in research['answers']}
    ai_sources = {s['id']: s for s in research['sources']}
    def question_table(items):
        if not ai_answers:
            return table(['Question', 'What we are working out', 'Work state'], [
                (link(q['id']), q['question'], q['work_status'].replace('_', ' ')) for q in items])
        return table(['Question', 'What we are working out', 'AI-generated potential answers and research', 'Work state'], [
            (link(q['id']), q['question'], research_options.inline(ai_answers[q['id']], ai_sources),
             q['work_status'].replace('_', ' ')) for q in items])
    out = {}
    nav = '[Start here](Home.md) · [Questions](Question-register.md) · [Progress](Progress.md) · [People decide](Human-review.md)'
    def page(name, title, body):
        out[name + '.md'] = f'# {title}\n\n{nav}\n\n{body.strip()}\n'
    ready = [d for d in data['decisions'] if d.get('work_status') == 'ready_for_review' and d['id'] not in approved]
    page('Home', 'Aura Disaster Resilience', f'''
We are designing a community-owned network that helps people every day and keeps useful information and coordination available through storms, cyclones, fires and longer disruptions. A kiosk is its public front door: a place to find a notice, check a service, ask for assistance or learn the next step in a practical job.

This wiki turns that ambition into connected questions, clear jobs and reviewable choices. It welcomes practical knowledge from tradespeople, drivers, artists, carers, nurses, retirees, students, researchers and everyone who knows their place and their work. Planning and design are underway; community discussion, prototypes and field trials are the next milestones.

**Ready S.E.T. Co-op**, fully **Ready Sustainable Employment and Training Cooperative**, is the proposed operating intermediary. **Aura of Intelligence** is the personal AI operating system [Luke Nathan Hayes](https://github.com/auraofintelligence/open-record-luke-nathan-hayes/tree/main) is designing, from light to ultra high definition, helping people navigate the network and learn when they need to. **GAJRA Earth**, the Global Association for Joyful Responsible Abundance on Earth, provides the values starting point.

## Choose your way in

{table(['Start with', 'What you can do'], [
('[The whole system](Stack-map.md)', 'See how people, equipment, power, communications and information fit together.'),
('[The first choices](First-review.md)', 'Read concrete alternatives and help decide the starting design.'),
('[All-weather kiosk design](All-weather-design.md)', 'Work through shelter, weather exposure, cabinet design, power and maintenance.'),
('[The question register](Question-register.md)', 'Choose a question, inspect its evidence and prepare a useful answer.'),
('[Council plans and Aura integration](Council-integration.md)', 'Connect the design to documented arrangements and demonstrate improvements through a shared comparison.'),
('[AI assistant jobs](Agent-work.md)', 'Give an assistant a bounded job while other work moves alongside it.'),
('[Working together](Working-together.md)', 'Explore the proposed council, team and committee model, including XR, personal Auras, AI/SI and robotics.'),
('[Progress](Progress.md)', 'See work produced, decisions awaiting people and the next milestones.'),
('[Documents and site sources](Source-library.md)', 'Read the originals, find preserved source editions and carry the work into the next job.'),
('[People decide](Human-review.md)', 'Understand who reviews each choice and exactly what an approval covers.')])}

Luke drives the work as project initiator. [Professional review](Professional-review.md) compares proposals that overlap professional responsibilities with applicable good practice and legal sources, recording differences, improvements and deficiencies alongside the responsible people's decisions.

## Where we are

**{len(questions)} linked questions · {len(data['domains'])} work areas · {len(ready)} review packages ready · {len(approved)} approvals recorded and checked.**

The earlier kiosk research supplies the starting evidence. The next work produces drawings, measurements, source agreements, software demonstrations, budgets and practical exercises. Progress comes from evidence and people working together. [Read the agreed direction](Constraints.md) and [explore the project connections](Ecosystem.md).
''')
    page('Question-register', 'Questions across the whole system', '''
Each question is a job we can work through. It explains why the answer matters, what useful work to bring back, which other choices it connects to and who needs to review it. AI assistants can investigate several areas at once; agreed choices give later work a dependable foundation.

Work labels describe preparation: **open**, **researching**, **options ready**, **in review**, **answer recorded**, or **planned for later**. A produced drawing or report is progress. Human approval is recorded separately.

**AI-generated potential answers:** The inline options draw on existing services, equipment, regional communities, councils, jurisdictions, businesses and plausible future concepts. Open a question for the alternatives, local differences and next checks. [The user prompt and research method](Research-brief.md) preserve the request; the [source catalogue](Research-sources.md) separates source facts from AI local-fit assessments. These options are prepared for discussion and professional review. An agreed answer is recorded through its own human decision.

The [Council plan crosswalk](Council-plan-crosswalk.md) maps the supplied management and recovery plans to these questions, with precise source pages and practical checks. [Council plans and Aura integration](Council-integration.md) sets out the proposed interfaces, comparison measures and approach to Council as capability develops.

''' + table(['Work area', 'Questions', 'Where it helps'], [(f'[{d["name"]}](Domain-{d["id"]}.md)',
              sum(q['domain'] == d['id'] for q in questions), d['purpose']) for d in data['domains']]) + '\n\n' +
         question_table(questions))
    for d in data['domains']:
        subset = [q for q in questions if q['domain'] == d['id']]
        page('Domain-' + d['id'], d['name'], d['purpose'] + '\n\n' + question_table(subset))
    for q in questions:
        body = f'''## Why this matters

{q['why']}

## What to bring back

{q['expected_deliverable']}

## What we know so far

''' + '\n'.join('- ' + evidence(e) for e in q['current_evidence'])
        if q.get('proposed_answer'):
            body += '\n\n**Starting idea for review:** ' + q['proposed_answer']
        if q['id'] in ai_answers:
            body += research_options.detail(ai_answers[q['id']], research)
        body += f'''\n\n## People and connected choices

**Who reviews:** {q['decision_authority_role']}

**Connected questions:** {', '.join(link(dep) for dep in q['depends_on']) or 'This is a starting question.'}

**Work state:** {q['work_status'].replace('_', ' ')}. **Assigned person or AI assistant:** {q.get('assigned_to') or 'Ready to be assigned'}.

Research and alternatives can move ahead while connected decisions develop. Before acting on a choice, check the people, evidence and approved scope in [People decide](Human-review.md).
'''
        if q.get('answer'):
            body += '\n\n## Recorded answer\n\n' + q['answer']
        page('Question-' + q['id'], q['id'] + ' ' + q['question'], body)
    page('Constraints', 'The direction already agreed', '''
These directions come from [Luke Nathan Hayes's](https://github.com/auraofintelligence/open-record-luke-nathan-hayes/tree/main) instructions in this planning conversation on 20 October 2026. They let people and AI assistants move forward without repeatedly reopening settled requirements. They establish the design direction; the decision register records specific proposals and their reviews.

''' + '\n\n'.join(f'**{c["id"]}** {c["constraint"]}' for c in data['constraints']))
    page('Ecosystem', 'How the wider projects connect', '''
The kiosk and its resilience network are the first delivery focus. The wider ecosystem brings useful information, learning, services and future capability. Each connection has a clear place in the design, so teams can work across the whole system without making the first kiosk wait for every project.

**Core** means a responsibility this service needs. **Interface** means a defined connection we can develop with another project. **Context** means a wider direction or research horizon. The source websites and demonstrations provide starting material; operating partnerships grow through their own conversations and agreements.

''' + table(['Connection', 'How it contributes', 'Place in this build', 'Questions'], [
                (r['name'], r['role'], r['scope'], ', '.join(link(q) for q in r['question_ids'])) for r in data['ecosystem']]) +
         '\n\n## Explore the source projects\n\n' + '\n\n'.join('**' + r['name'] + '**\n\n' +
             ' · '.join(f'[{url.rstrip("/").split("/")[-1]}]({url})' for url in r.get('repositories', []) + r.get('public_urls', [])) for r in data['ecosystem']))
    for d in data['decisions']:
        p = d['proposal']
        digest = fingerprint(d, root, questions, research)
        evidence_digest = evidence_fingerprint(d, root, questions, research)
        body = f'**Review scope:** {p["scope_label"]}. **State:** ' + ('approval recorded and checked' if d['id'] in approved else 'ready for people to review')
        body += '\n\n' + p['summary'] + '\n\n## The choices\n\n' + table(['Choice', 'What it brings', 'What to plan for'], [
                    (x['name'], x['benefit'], x['tradeoff']) for x in p['options']])
        body += '\n\n## Recommended next step\n\n' + p['recommendation']
        body += '\n\n## What this decision moves forward\n\n' + '\n'.join('- ' + x for x in p['authorises'])
        body += '\n\n## Later milestones with their own reviews\n\n' + '\n'.join('- ' + x for x in p['later_reviews'])
        body += '\n\n## What people review\n\n' + '\n'.join('- ' + x for x in p['review_checks'])
        body += '\n\n**Questions:** ' + ', '.join(link(q) for q in p['question_ids'])
        if p.get('answers'):
            body += '\n\n## Exact answers covered by this proposal\n\n' + '\n\n'.join(
                f'**{link(qid)}**\n\n{answer}' for qid, answer in p['answers'].items())
        body += '\n\n**Reviewers:** ' + ', '.join(data['roles'][r]['label'] for r in p['required_roles'])
        if d.get('github_issue_url'):
            body += f'\n\n[Open the GitHub review conversation]({d["github_issue_url"]}).'
        body += f'''\n\n## Record the human decision

The fingerprint below identifies this exact proposal and its supporting files. A changed proposal gets a fresh fingerprint and review. A person may approve, request changes or reject it. [How reviews work](Human-review.md).

`{digest}`

Evidence fingerprint: `{evidence_digest}`.

For approval, the named person posts this line in the linked GitHub issue after reading the proposal:

```text
HITL APPROVE {d['id']} {digest} scope={p['scope']}
Conditions: none
```

Use `CHANGE` or `REJECT` in place of `APPROVE` to record that outcome. For conditional agreement, state the conditions in the Conditions field; that record awaits a fresh decision when they are met. Keep an approval comment to the displayed fields and discuss reasons in a separate comment. An optional `Valid-until:` field takes an ISO date/time with its timezone. AI assistants prepare the proposal and carry out authorised follow-up; the human decision belongs to the named person.
'''
        for review in data['reviews']:
            if review['decision_id'] == d['id']:
                current = reviews.get((d['id'], review['role']))
                is_current = current and current['evidence_url'] == review['evidence_url']
                label = current['outcome'] if is_current else review['outcome'] + ' — earlier record'
                body += f'\n\n[Review by {review["reviewer"]}: {label}]({review["evidence_url"]})'
                if is_current:
                    body += '\n\nConditions: ' + current['conditions']
                    if current['valid_until']:
                        body += '\n\nValid until: ' + current['valid_until']
        page('Decision-' + d['id'], d['id'] + ' ' + p['title'], body)
    page('Decisions', 'Decision register', 'A decision joins the evidence, the choice and the people responsible for its scope.\n\n' + table(
        ['Decision', 'Scope', 'Review state'], [(f'[{d["id"]} {d["proposal"]["title"]}](Decision-{d["id"]}.md)',
        d['proposal']['scope_label'], 'approval recorded and checked' if d['id'] in approved else 'ready for review') for d in data['decisions']]))
    page('First-review', 'The first choices to work through together', '''
These three packages give parallel work a common starting point. Each offers alternatives, a recommended next step and a defined review scope. We can prepare research across the stack while people consider these choices.

''' + '\n\n'.join(f'## [{d["id"]} {d["proposal"]["title"]}](Decision-{d["id"]}.md)\n\n{d["proposal"]["summary"]}\n\n**Recommended:** {d["proposal"]["recommendation"]}' for d in data['decisions']))
    page('Progress', 'Progress and the next useful jobs', f'''
This board separates work produced, human decisions and performance demonstrated in testing. It gives a practical picture of what we can do next.

{table(['Measure', 'Current record'], [
('Questions mapped', len(questions)), ('Work areas connected', len(data['domains'])),
('Questions with AI-generated options prepared', len(ai_answers)), ('Primary research references', len(ai_sources)),
('Council integration analysis', '[Two supplied plans, source crosswalk and proposed comparison path](Council-integration.md)'),
('Review packages prepared', len(data['decisions'])), ('Human approvals recorded and checked', len(approved)),
('Operating pilot sites', 'Site discussions and pilot preparation are ahead'),
('All-weather performance', 'Design basis, drawings and measurements are the next evidence'),
('Research baseline', '[AI options and preserved user prompt](Research-brief.md), [primary-source comparisons](Research-sources.md), and the original library; see [Evidence](Evidence.md)')])}

## Parallel jobs

''' + table(['Job', 'Useful output', 'Questions', 'Work state'], [(r['id'] + ' ' + r['title'], r['output'],
                ', '.join(link(q) for q in r['question_ids']), r['status']) for r in data['tasks']]) + '''

## Keep the record useful

Update the question's assigned person or AI assistant, work state and evidence when work changes. Bring a completed proposal to the human review queue. Record measurements against a named configuration and test, so a drawing, a bench result and a field result each show their own contribution.

The dashboard is generated from the records in the repository. It is refreshed when those records are rebuilt and published; it is not a background monitor of people or devices.
''')
    page('Evidence', 'Evidence people can check and build on', '''
Evidence can be a source document, a photo with permission, a measurement, a drawing, a test result or an operating agreement. It tells the next person what was checked, when, by whom and under what conditions.

For each important claim, keep its source, date, version, location or test setup, uncertainty and the person responsible for updating it. Distinguish an observation, an official instruction, an estimate, a simulation and an agreed decision. A clear source trail helps people challenge, improve and reuse the work.

The question cards carry the starting sources. The [source library](Source-library.md) holds the supplied originals and preserved website source editions, with packing lists, checksums and restoration instructions. Public releases carry information people can safely use; private household, welfare, contact and cultural records keep their chosen access conditions.

[Research baseline and original-document register](../docs/source-register.md) · [Earlier kiosk proposal](https://github.com/auraofintelligence/straddie-disaster-kiosks) · [UNGA81 reference library](https://auraofintelligence.github.io/UNGA81-Luke-Hayes/library.html)

For a new piece of evidence, record the question IDs it helps answer, the file or public link, the exact section or test, what it establishes, and the next check needed. Personal and cultural permissions travel with copies and summaries.
''')
    library = '''The source library keeps the documents and site editions behind the work available to the next person or AI assistant. Checksums identify the exact files, and manifests act as packing lists. Original material keeps its rights and source context. [Rights and discovery](Rights-and-discovery.md) explains reuse and crawler preferences.

## Original documents

'''
    manifest_path = root / 'data/document-manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        summary = manifest['summary']
        library += f'**{summary["unique_documents"]} distinct documents · {summary["packaged_requests"]} supplied originals accounted for · {summary["missing_requests"]} awaiting a file.** Identical copies share one preserved file with their source aliases recorded.\n\n'
        library += table(['Document', 'Format and extent', 'Size'], [
            (f'[{d["original_filename"]}](../{quote(d["public_path"], safe="/")})',
             d['format'] + (f', {d["pages"]} pages' if 'pages' in d else ''),
             f'{d["size_bytes"] / 1048576:.2f} MiB') for d in manifest['documents']])
        library += '\n\n[Document packing list and full checksums](../data/document-manifest.json).\n'
    else:
        library += 'The original documents and their packing list are being prepared.\n'
    library += '\n## Website source editions\n\n'
    site_path = root / 'data/site-manifest.json'
    sites = json.loads(site_path.read_text(encoding='utf-8')) if site_path.exists() else {}
    if sites.get('capture_status') == 'complete':
        rows = []
        for record in sites['records']:
            if record.get('state') != 'source_packaged':
                continue
            parts = record['archive']['parts']
            downloads = ' · '.join(f'[Part {i}](../{quote(p["path"], safe="/")})' for i, p in enumerate(parts, 1))
            rows.append((f'[{record["slug"]}]({record["repository"]})', record['file_count'],
                         f'{record["archive"]["bytes"] / 1048576:.1f} MiB', downloads))
        library += table(['Source project', 'Files', 'Archive size', 'Download'], rows)
        library += '\n\n[Site packing list, source revisions and checksums](../data/site-manifest.json). Large ZIPs use numbered parts that the restore helper joins and checks. Source snapshots preserve website files; live outside services retain their own operating arrangements.\n'
    else:
        library += 'Website-source snapshots are being packaged with their existing licences, source editions, per-file checksums and restoration instructions. The complete packing list and downloads will appear here when the capture is checked.\n'
    web_path = root / 'data/web-page-manifest.json'
    if web_path.exists():
        web_pages = json.loads(web_path.read_text(encoding='utf-8'))
        if web_pages.get('capture_status') == 'complete':
            library += '\n## Saved public page editions\n\nThese dated HTML copies preserve the linked public pages as received. HTML is the page source a browser reads. The project-source packages above preserve the related code and assets; separate hosting services and databases have their own handovers.\n\n'
            library += table(['Public address', 'Saved page source', 'Captured, UTC'], [
                (f'[{r["url"]}]({r["url"]})',
                 f'[Open saved edition](../{quote(r["public_path"], safe="/")})' if r['status'] == 'captured' else r['status'],
                 r.get('captured_utc', 'See the packing list')) for r in web_pages['records']])
            library += '\n\n[Public-page packing list, response details and checksums](../data/web-page-manifest.json).\n'
    library += '\n## Carry the work forward\n\n[Swarm handover](../SWARM_HANDOVER.md) · [Question register](Question-register.md) · [Evidence](Evidence.md). The handover gives the next team the agreed direction, current work, decisions and next jobs.\n'
    library += '\n## Council plans and design analysis\n\nThe supplied management and recovery plans are preserved above as DOC-033 and DOC-034. [Council plans and Aura integration](Council-integration.md) records their editions, current publication context, proposed interfaces and evidence for improvements. The [detailed crosswalk](Council-plan-crosswalk.md) gives printed/PDF page references and linked design questions.\n'
    page('Source-library', 'Documents and website source library', library)
    if research.get('brief'):
        out['Research-brief.md'] = research_options.brief_page(research)
        out['Research-sources.md'] = research_options.sources_page(research)
    for p in sorted((root / 'content').glob('*.md')):
        out[p.name] = p.read_text(encoding='utf-8')
    out['_Sidebar.md'] = '\n'.join(['**Aura Disaster Resilience**', '', '- [Start here](Home.md)', '- [The whole system](Stack-map.md)',
        '- [First choices](First-review.md)', '- [All-weather design](All-weather-design.md)', '- [Questions](Question-register.md)',
        '- [Progress](Progress.md)', '- [Working together](Working-together.md)', '- [People decide](Human-review.md)', '- [Professional review](Professional-review.md)', '- [AI assistant jobs](Agent-work.md)',
        '- [Council integration](Council-integration.md)', '- [Council plan crosswalk](Council-plan-crosswalk.md)',
        '- [Guardian IMS and QIT Plus](Guardian-IMS.md)',
        '- [Connections](Ecosystem.md)', '- [Agreed direction](Constraints.md)', '- [Evidence](Evidence.md)',
        '- [Source library](Source-library.md)', '- [AI research and prompt](Research-brief.md)', '- [Research sources](Research-sources.md)', '- [Useful words](Glossary.md)', '- [Rights and discovery](Rights-and-discovery.md)', '', '**Work areas**', ''] +
        [f'- [{d["name"]}](Domain-{d["id"]}.md)' for d in data['domains']]) + '\n'
    out['_Footer.md'] = 'Growing capability together · Planning and design underway · [People decide](Human-review.md) · [Repository](' + BASE + ')\n'
    # Every local link must resolve before anything is published.
    for name, text in out.items():
        naming_text = text
        if manifest_path.exists():
            for document in manifest['documents']:
                naming_text = naming_text.replace(document['original_filename'], 'Original source document')
        naming_text = re.sub(r'\]\([^)]+\)', ']', naming_text)
        if re.search(r'(?i)[cgl]:[/\\]', text) or re.search(r'(?i)ready\s+set\b|\bSETCo\b|\bSET Co\b|P4A[- ]cinema', naming_text):
            raise ValueError(f'{name}: check workstation paths and agreed names.')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            path = target.split('#', 1)[0]
            if path.startswith('../'):
                dest = (root / 'wiki' / unquote(path)).resolve()
                if not dest.is_relative_to(root.resolve()) or not dest.exists():
                    raise ValueError(f'{name}: missing reference {target}')
            elif path and path not in out:
                raise ValueError(f'{name}: missing wiki page {target}')
    return out


def build(root=ROOT, check=False):
    pages = render(load(root), root)
    destination = root / 'wiki'
    destination.mkdir(exist_ok=True)
    changed = []
    for name, text in pages.items():
        p = destination / name
        if not p.exists() or p.read_text(encoding='utf-8') != text:
            changed.append(name)
            if not check:
                p.write_text(text, encoding='utf-8', newline='\n')
    extra = {p.name for p in destination.glob('*.md')} - pages.keys()
    if extra:
        raise ValueError('Review extra wiki pages before publishing: ' + ', '.join(sorted(extra)))
    if check and changed:
        raise ValueError('Rebuild these wiki pages: ' + ', '.join(changed))
    print(f'{len(pages)} wiki pages checked; {len(changed)} refreshed.' if not check else f'{len(pages)} wiki pages are current.')
    return pages


def export(destination, root=ROOT):
    pages = build(root, check=True)
    destination = Path(destination).resolve()
    if destination == root.resolve() or destination == (root / 'wiki').resolve():
        raise ValueError('Choose a separate wiki checkout or export folder.')
    destination.mkdir(parents=True, exist_ok=True)
    for name, text in pages.items():
        text = re.sub(r'\]\(\.\./([^)#]+)(#[^)]*)?\)',
                      lambda m: f']({BASE}/blob/main/{m[1]}{m[2] or ""})', text)
        text = re.sub(r'\]\(([A-Za-z0-9_-]+)\.md(#[^)]*)?\)',
                      lambda m: f']({m[1]}{m[2] or ""})', text)
        (destination / name).write_text(text, encoding='utf-8', newline='\n')
    print(f'Exported {len(pages)} pages to {destination}. Existing unrelated pages were preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--export', type=Path)
    args = parser.parse_args()
    try:
        export(args.export) if args.export else build(check=args.check)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
