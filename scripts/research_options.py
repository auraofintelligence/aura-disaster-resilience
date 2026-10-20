"""Read and present clearly attributed AI-generated options and primary sources."""
from __future__ import annotations

import json
from urllib.parse import urlsplit

FILES = ('research-hardware.json', 'research-service.json', 'research-digital.json')
KINDS = {'adaptation', 'future_concept'}
SOURCE_TYPES = {'official_guidance', 'official_case_study', 'vendor_documentation', 'research'}


def load(root):
    brief_path = root / 'data/research-brief.json'
    brief = json.loads(brief_path.read_text(encoding='utf-8')) if brief_path.exists() else {}
    result = {'brief': brief, 'sources': [], 'answers': [], 'provenance': []}
    for name in FILES:
        path = root / 'data' / name
        if path.exists():
            part = json.loads(path.read_text(encoding='utf-8'))
            result['sources'].extend(part['sources'])
            result['answers'].extend(part['answers'])
            result['provenance'].append(part.get('provenance', {}))
    return result


def validate(research, question_ids):
    if not research.get('answers') and not research.get('sources'):
        if research.get('brief'):
            raise ValueError('The research request needs complete AI options and their sources before publication.')
        return
    sources = {s['id']: s for s in research['sources']}
    answers = {a['question_id']: a for a in research['answers']}
    if len(sources) != len(research['sources']) or len(answers) != len(research['answers']):
        raise ValueError('Research source IDs and question options must be unique.')
    if set(answers) != set(question_ids):
        raise ValueError('AI options must cover every question exactly once; check missing or extra question IDs.')
    brief = research.get('brief', {})
    if not brief.get('verbatim_prompt') or not brief.get('id'):
        raise ValueError('Preserve the user prompt and its reference ID with the research.')
    if not research.get('provenance'):
        raise ValueError('Research needs explicit AI provenance and the matching prompt reference.')
    for provenance in research['provenance']:
        if provenance.get('ai_generated') is not True or provenance.get('prompt_id') != brief['id']:
            raise ValueError('Each research group needs explicit AI provenance and the matching prompt reference.')
    required = {'id', 'title', 'url', 'publisher', 'checked_on', 'evidence_type', 'fact', 'local_fit'}
    for source in sources.values():
        if not required <= source.keys() or any(not source[k] for k in required):
            raise ValueError(f'{source.get("id")}: complete the source identity, claim and local-fit record.')
        if source['evidence_type'] not in SOURCE_TYPES or urlsplit(source['url']).scheme != 'https':
            raise ValueError(f'{source["id"]}: use a classified primary source with a secure public address.')
    for answer in answers.values():
        qid = answer['question_id']
        if not answer.get('summary') or not answer.get('next_checks') or not answer.get('comparators'):
            raise ValueError(f'{qid}: include an option, comparator and useful next checks.')
        kinds = {option['kind'] for option in answer['options']}
        if kinds != KINDS:
            raise ValueError(f'{qid}: distinguish an adaptation and a future concept.')
        references = []
        for option in answer['options']:
            if not option.get('text') or not option.get('label'):
                raise ValueError(f'{qid}: explain each research option.')
            references.extend(option['source_ids'])
        references.extend(c['source_id'] for c in answer['comparators'])
        if not references or any(ref not in sources for ref in references):
            raise ValueError(f'{qid}: a research reference does not match the source catalogue.')


def evidence_for(question_ids, research):
    """Bind the displayed options and their exact source records to a review."""
    selected = {a['question_id']: a for a in research.get('answers', []) if a['question_id'] in question_ids}
    if not selected:
        return {}
    used = {source for a in selected.values() for option in a['options'] for source in option['source_ids']}
    used.update(c['source_id'] for a in selected.values() for c in a['comparators'])
    return {'brief': research['brief'], 'provenance': research['provenance'], 'options': selected,
            'sources': {s['id']: s for s in research['sources'] if s['id'] in used}}


def source_link(source):
    url = source['url'].replace('(', '%28').replace(')', '%29').replace(' ', '%20')
    return f'[{source["title"]}]({url})'


def source_links(ids, sources):
    return ' · '.join(source_link(sources[ref]) for ref in dict.fromkeys(ids))


def inline(answer, sources):
    future = next(option for option in answer['options'] if option['kind'] == 'future_concept')
    references = list(dict.fromkeys([c['source_id'] for c in answer['comparators']] +
                                   [ref for option in answer['options'] for ref in option['source_ids']]))
    return ('**AI-generated option:** ' + answer['summary'] + '<br><br>**AI-generated future concept:** ' +
            future['text'] + '<br><br>**Research examples:** ' + source_links(references[:2], sources))


def detail(answer, research):
    sources = {s['id']: s for s in research['sources']}
    brief = research['brief']
    body = f'''\n\n## AI-generated potential answers

**For discussion and review · research checked {brief['recorded_on']}.** These are AI-generated options and transfer assessments. [The user's request and research method](Research-brief.md) identify the source of this work. The [source catalogue](Research-sources.md) states what the references establish. The decision and approval record retains its own status.

{answer['summary']}
'''
    for option in answer['options']:
        kind = 'AI-generated adaptation of an existing pattern' if option['kind'] == 'adaptation' else 'AI-generated future concept'
        body += f'\n### {option["label"]}\n\n**{kind}.** {option["text"]}\n'
        if option['source_ids']:
            body += '\nResearch basis: ' + source_links(option['source_ids'], sources) + '.\n'
    body += '\n### Examples and local differences\n'
    for comparator in answer['comparators']:
        body += ('\n- ' + source_link(sources[comparator['source_id']]) + ': **AI transfer assessment:** ' +
                 comparator['lesson'] + ' **Local difference to check:** ' + comparator['local_difference'] + '\n')
    body += '\n### Evidence to bring back next\n\n' + '\n'.join('- ' + check for check in answer['next_checks'])
    return body


def brief_page(research):
    brief = research['brief']
    prompt = '\n'.join('> ' + line for line in brief['verbatim_prompt'].splitlines())
    return f'''# The request behind the AI-generated options

[Question register](Question-register.md) · [Research sources](Research-sources.md) · [People decide](Human-review.md)

**Reference:** `{brief['id']}` · **Requested by:** {brief['requested_by']} · **Recorded:** {brief['recorded_on']}, {brief['timezone']}.

## User prompt, preserved verbatim

{prompt}

## How to read the options

{brief['scope']}

The question register shows potential answers and future concepts inline. Each question card adds alternatives, examples, local differences and the next useful checks. The source catalogue records the limited facts established by each primary reference, its publisher and checked date. **AI-generated** labels apply to the options, synthesis and local transfer assessments. Source owners are responsible for their own published claims.

{brief['source_policy']}

{brief['future_policy']}

**Generated by:** {brief['generated_by']}.

**Human-review status:** {brief['human_approval']} Existing-source research, a suggested option, a model, an actual agreement and field performance each have their own meaning. Discuss and compare these options through [professional review](Professional-review.md) and [human review](Human-review.md).

## Use comparisons to ask better local questions

Compare exposure, salt and heat, settlement size, transport dependencies, power autonomy, message capacity, maintenance skills, ownership and the actual decision responsibilities. A regional case can establish that its own service was described or demonstrated; adopting the pattern here needs the local design, permissions, measurements and practical checks shown on the question card.

Source dates identify the reviewed edition. Recheck changing products, prices, eligibility, operating status and source instructions when preparing a real commitment. Future concepts are proposals for development and testing, with actual capability recorded as evidence grows.
'''


def sources_page(research):
    body = '''# Existing examples and primary research sources

[Question register](Question-register.md) · [The user prompt and method](Research-brief.md)

These references support the AI-generated options. Official guidance, an official case study, manufacturer documentation and research each establish different things. A vendor's page records its own product claims; local suitability, a complete system's performance and an operating agreement are assessed through their own work.

The short source facts below are separated from the AI-generated local-fit assessments. The question cards connect the sources to proposed answers and tests. These references identify examples to learn from; partnerships and endorsements are established through actual agreements.
'''
    for source in sorted(research['sources'], key=lambda s: s['id']):
        kind = source['evidence_type'].replace('_', ' ')
        body += (f'\n## {source["id"]}\n\n' + source_link(source) +
                 f'\n\n**Publisher:** {source["publisher"]} · **Reference type:** {kind} · **Checked:** {source["checked_on"]}.' +
                 '\n\n**Limited fact established by the source:** ' + source['fact'] +
                 '\n\n**AI-generated local-fit assessment:** ' + source['local_fit'] + '\n')
    return body
