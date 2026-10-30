"""Extract the unchanged document into a portable, ordered reading source.

Run only when the supplied Word edition changes; normal website builds use
document.json and require Python's standard library alone.
"""
from pathlib import Path
import argparse
import html
import json
import re
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn


def run_text(node):
    parts = []
    for item in node.iter():
        if item.tag == qn('w:t'):
            parts.append(html.escape(item.text or ''))
        elif item.tag == qn('w:br'):
            if item.get(qn('w:type')) != 'page':
                parts.append('<br>')
        elif item.tag == qn('w:tab'):
            parts.append(' ')
    text = ''.join(parts)
    props = node.find(qn('w:rPr'))
    if props is not None:
        if props.find(qn('w:b')) is not None:
            text = '<strong>' + text + '</strong>'
        if props.find(qn('w:i')) is not None:
            text = '<em>' + text + '</em>'
    return text


def paragraph_html(para, document):
    parts = []
    for item in para._p:
        if item.tag == qn('w:r'):
            parts.append(run_text(item))
        elif item.tag == qn('w:hyperlink'):
            value = ''.join(run_text(run) for run in item if run.tag == qn('w:r'))
            rel_id = item.get(qn('r:id'))
            url = document.part.rels[rel_id].target_ref if rel_id else ''
            parts.append(f'<a href="{html.escape(url, quote=True)}">{value}</a>' if url else value)
    return ''.join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('docx', type=Path)
    args = parser.parse_args()
    document = Document(args.docx)
    blocks, sources = [], []
    for element in document.element.body:
        if element.tag == qn('w:p'):
            para = Paragraph(element, document)
            text = ''.join(element.itertext()) if False else para.text
            rendered = paragraph_html(para, document)
            plain = re.sub('<[^>]+>', '', rendered).strip()
            if not plain:
                continue
            block = dict(type='paragraph', style=para.style.name, text=html.unescape(plain), html=rendered)
            blocks.append(block)
        elif element.tag == qn('w:tbl'):
            table = Table(element, document)
            rows = [[cell.text for cell in row.cells] for row in table.rows]
            blocks.append(dict(type='table', rows=rows))
    relationships = [v.target_ref for v in document.part.rels.values() if 'hyperlink' in v.reltype]
    source_index = 0
    for i, block in enumerate(blocks):
        match = re.match(r'^(P\d+|R\d+)\s+(.+)', block.get('text', ''))
        if match:
            identifier, title = match.groups()
            description = blocks[i+1].get('text', '') if i+1 < len(blocks) else ''
            sources.append(dict(id=identifier, title=title, description=description, url=relationships[source_index]))
            source_index += 1
    assert len(sources) == 37 and len(relationships) == 37, (len(sources), len(relationships))
    output = dict(title='Aura of Intelligence for Disaster Resilience and Recovery',
                  author='Luke Nathan Hayes', date='2026-10-27', pages=39, blocks=blocks, sources=sources)
    target = Path(__file__).with_name('document.json')
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(f'Extracted {len(blocks)} ordered blocks, {sum(b["type"] == "table" for b in blocks)} tables, {len(sources)} sources.')


if __name__ == '__main__':
    main()
