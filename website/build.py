"""Build the static companion website using Python's standard library."""
from pathlib import Path
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import re
import runpy
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site'
SOURCE = ROOT / 'website'
BASE = 'https://auraofintelligence.github.io/aura-disaster-resilience/'
REPO = 'https://github.com/auraofintelligence/aura-disaster-resilience'
DATE = '2026-10-30'
E = html.escape


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)


def plain(value):
    parser = PlainText()
    parser.feed(value)
    return re.sub(r'\s+', ' ', ' '.join(parser.parts)).strip()


def slugify(value):
    return re.sub(r'[^a-z0-9]+', '-', plain(value).lower()).strip('-')


def references(value, reader=False):
    def replace(match):
        ids = []
        for group in match.group(1).split(','):
            group = group.strip()
            span = re.fullmatch(r'([PRN])(\d+)-([PRN])?(\d+)', group)
            if span:
                prefix, first, other, last = span.groups()
                if other and other != prefix:
                    return match.group(0)
                ids.extend(prefix + str(n) for n in range(int(first), int(last)+1))
            else:
                ids.append(group)
        if not all(re.fullmatch(r'[PRN]\d+', identifier) for identifier in ids):
            return match.group(0)
        return ' '.join(f'<a class="source-ref" href="{"" if reader else "library.html"}#source-{identifier}" aria-label="Source {identifier}">[{identifier}]</a>' for identifier in ids)
    return re.sub(r'\[([PRN]\d+(?:[-, ]+[PRN]?\d+)*)\]', replace, value)


def add_section_ids(value):
    sections = []
    used = set()
    def replace(match):
        attributes, inner = match.groups()
        heading = re.search(r'<h2>(.*?)</h2>', inner, re.S)
        if not heading:
            return match.group(0)
        explicit = re.search(r'\bid="([^"]+)"', attributes)
        identifier = explicit.group(1) if explicit else slugify(heading.group(1))
        original, count = identifier, 2
        while identifier in used:
            identifier = original + '-' + str(count)
            count += 1
        used.add(identifier)
        if not explicit:
            attributes += f' id="{identifier}"'
        sections.append((identifier, plain(heading.group(1))))
        return '<section' + attributes + '>' + inner + '</section>'
    return re.sub(r'<section([^>]*)>(.*?)</section>', replace, value, flags=re.S), sections


def image_html(slug, assets, hero=False):
    asset = assets[slug]
    loading = 'fetchpriority="high"' if hero else 'loading="lazy"'
    return f'<img src="assets/images/{slug}-1536.webp" srcset="assets/images/{slug}-768.webp 768w, assets/images/{slug}-1536.webp 1536w" sizes="(max-width: 650px) 90vw, {"91vw" if hero else "(max-width: 1100px) 65vw, 830px"}" width="1536" height="1024" alt="{E(asset["alt"], quote=True)}" {loading} decoding="async">'


def inline_image(slug, assets):
    return f'<figure class="inline-art">{image_html(slug, assets)}<figcaption>{E(assets[slug]["caption"])} · AI-generated concept</figcaption></figure>'


def render_table(rows):
    parts = ['<div class="table-wrap"><table><thead><tr>']
    parts.extend('<th scope="col">' + E(cell) + '</th>' for cell in rows[0])
    parts.append('</tr></thead><tbody>')
    for row in rows[1:]:
        parts.append('<tr>')
        for i, cell in enumerate(row):
            tag = 'th scope="row"' if i == 0 else 'td'
            parts.append('<' + tag + '>' + E(cell).replace('\n', '<br>') + '</' + ('th' if i == 0 else 'td') + '>')
        parts.append('</tr>')
    parts.append('</tbody></table></div>')
    return ''.join(parts)


def make_reader(document):
    before, groups, group = [], [], None
    for block in document['blocks']:
        if block.get('style') == 'Heading 1':
            group = dict(title=block['text'], blocks=[])
            groups.append(group)
        elif group is not None:
            group['blocks'].append(block)
        else:
            before.append(block)
    assert len(groups) == 38, len(groups)
    output = ['<div class="document-title">']
    for block in before:
        cls = ' class="doc-title"' if block.get('style') == 'Title' else ''
        output.append(f'<p{cls}>{block.get("html", "")}</p>')
    output.append('</div>')
    for i, chapter in enumerate(groups, 1):
        label = f'{i:02d}' if i <= 33 else f'Refs {i-33}'
        output.append(f'<details class="document-chapter" id="document-{i:02d}"><summary><span class="chapter-number">{label}</span><span>{E(chapter["title"])}</span></summary><div class="chapter-body">')
        for block in chapter['blocks']:
            if block['type'] == 'table':
                output.append(render_table(block['rows']))
            elif block.get('style') == 'Heading 2':
                output.append('<h3>' + block['html'] + '</h3>')
            else:
                output.append('<p>' + references(block['html'], reader=True) + '</p>')
        output.append('</div></details>')
    return ''.join(output), groups


def source_list(document, newer):
    sources = document['sources'] + [dict(id=i, title=t, url=u, description=d) for i,t,u,d in newer]
    output = ['<ol class="source-list">']
    for item in sources:
        output.append(f'<li id="source-{item["id"]}"><span class="source-id">{item["id"]}</span><a class="source-title" href="{E(item["url"], quote=True)}">{E(item["title"])} ↗</a><p>{E(item["description"])}</p></li>')
    output.append('</ol>')
    return ''.join(output)


def licence_html():
    output, bullets = ['<div class="legal-copy">'], False
    for line in (ROOT / 'LICENCE.md').read_text().splitlines():
        if bullets and not line.startswith('- '):
            output.append('</ul>'); bullets = False
        if not line.strip():
            continue
        if line.startswith('# '):
            output.append('<h2>' + E(line[2:]) + '</h2>')
        elif line.startswith('## '):
            output.append('<h3>' + E(line[3:]) + '</h3>')
        elif line.startswith('- '):
            if not bullets: output.append('<ul>'); bullets = True
            output.append('<li>' + E(line[2:]) + '</li>')
        else:
            text = E(line)
            text = re.sub(r'(https://[^\s<]+)', r'<a href="\1">\1</a>', text)
            output.append('<p>' + text + '</p>')
    if bullets: output.append('</ul>')
    return ''.join(output) + '</div>'


def interest_builder():
    return '''<details class="draft-box"><summary>Prepare an interest note</summary><p>Choose a starting point and draft a short note. It stays in this page until you choose where to share it.</p><form id="interest-draft" class="draft-form"><label>My interest<select name="interest"><option>Personal or household learning</option><option>Hosting a demonstration</option><option>Paid work or mentoring</option><option>Voluntary civic stewardship</option><option>Research or professional input</option><option>Agency, supplier or community service</option><option>Equipment or another practical resource</option></select></label><label>Place or setting, if useful<input name="place" maxlength="120" placeholder="For example, a community hall in Redlands"></label><label>A useful question or possibility<textarea name="note" maxlength="4000" placeholder="Describe what you would like to explore. Keep sensitive records out of this note."></textarea></label></form><pre class="draft-preview" id="draft-preview" aria-label="Your interest note"></pre><div class="draft-actions"><button type="button" id="copy-draft">Copy note</button><button type="button" id="download-draft">Download text</button></div><p id="draft-status" class="draft-status" role="status"></p><noscript><p>Write your note in your own text editor, using the prompts above. Copy and download need JavaScript.</p></noscript></details>'''


def make_page(page, pages, assets, body, sections, groups):
    slug = page['slug']
    index = next(i for i,p in enumerate(pages) if p['slug'] == slug)
    url = BASE if slug == 'index' else BASE + slug + '.html'
    title = page['title'] + ' | Aura of Intelligence'
    description = page['description']
    nav = ''.join(f'<a href="{p["slug"]}.html"' + (' aria-current="page"' if p['slug'] == slug else '') + '>' + E(p['nav']) + '</a>' for p in pages)
    toc = ''.join(f'<li><a href="#{i}">{E(t)}</a></li>' for i,t in sections)
    chapter_links = ', '.join(f'<a href="library.html#document-{n:02d}">{n:02d}</a>' for n in page['chapters'])
    source_jump = '<a class="source-jump" href="library.html#read-document">Full document and sources ↗</a>'
    if chapter_links:
        source_jump = '<p class="source-jump">Document sections<br>' + chapter_links + '</p>' + source_jump
    turns = []
    if index:
        previous = pages[index-1]
        turns.append(f'<a href="{previous["slug"]}.html"><small>← Previous</small>{E(previous["nav"])}</a>')
    else:
        turns.append('<a href="library.html"><small>Go to the source</small>Document and evidence</a>')
    if index < len(pages)-1:
        following = pages[index+1]
        turns.append(f'<a href="{following["slug"]}.html"><small>Next →</small>{E(following["nav"])}</a>')
    else:
        turns.append('<a href="index.html"><small>Return to</small>The overview →</a>')
    home_actions = '<div class="actions"><a class="button" href="personal-aura.html">Begin with the person →</a><a class="text-link" href="library.html#downloads">Read the document ↗</a></div>' if slug == 'index' else ''
    home_journeys = ''
    if slug == 'index':
        cards = []
        for key,label in [('preparedness','Before'),('disruption','During'),('recovery','After'),('people-work','People'),('c-hours','Reciprocity'),('build-together','A next step')]:
            target = next(p for p in pages if p['slug'] == key)
            cards.append(f'<a class="journey-card" href="{key}.html">{image_html(key, assets)}<small>{label}</small><h3>{E(target["nav"])} ↗</h3><p>{E(target["lead"])}</p></a>')
        home_journeys = '<section class="wrap home-journeys" aria-labelledby="explore-title"><div class="section-heading"><h2 id="explore-title">Follow a practical<br><em>question.</em></h2><p>Start where the proposal meets your life or work. Each page links back to the complete document and its evidence.</p></div><div class="journey-grid">' + ''.join(cards) + '</div></section>'
    schema = dict(**{'@context':'https://schema.org','@type':'WebPage'}, name=page['title'], url=url, description=description, inLanguage='en-AU', dateModified=DATE, author={'@type':'Person','name':'Luke Nathan Hayes','url':'https://github.com/auraofintelligence/open-record-luke-nathan-hayes/tree/main'}, isPartOf={'@type':'WebSite','name':'Aura of Intelligence for Disaster Resilience and Recovery','url':BASE})
    return f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#163c3d"><title>{E(title)}</title><meta name="description" content="{E(description, quote=True)}"><link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:site_name" content="Aura of Intelligence · Disaster Resilience and Recovery"><meta property="og:title" content="{E(page['title'], quote=True)}"><meta property="og:description" content="{E(description, quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}assets/images/{slug}-1536.webp"><meta property="og:image:alt" content="{E(assets[slug]['alt'], quote=True)}"><meta property="og:image:width" content="1536"><meta property="og:image:height" content="1024"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(page['title'], quote=True)}"><meta name="twitter:description" content="{E(description, quote=True)}"><meta name="twitter:image" content="{BASE}assets/images/{slug}-1536.webp"><meta name="twitter:image:alt" content="{E(assets[slug]['alt'], quote=True)}"><link rel="icon" href="favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="assets/apple-touch-icon.png"><link rel="manifest" href="site.webmanifest"><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script></head>
<body id="top" class="page-{slug}"><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header wrap"><a class="brand" href="index.html"><img src="assets/brand-mark.png" width="42" height="42" alt=""><span>Aura of Intelligence<br><small>DISASTER RESILIENCE &amp; RECOVERY</small></span></a><nav class="primary-nav" aria-label="Main"><a href="personal-aura.html">The person</a><a href="build-together.html">Build together</a><a href="library.html">Document &amp; wiki</a></nav><details class="menu"><summary>Explore</summary><div class="menu-panel"><nav class="all-nav" aria-label="All pages">{nav}</nav><form class="search" role="search"><div style="flex:1;min-width:0"><label class="search-label" for="site-search">Search the reading pages</label><input id="site-search" name="q" type="search" autocomplete="off" placeholder="Try ‘minimum viable self’"></div><button type="submit">Find</button></form><p class="search-status" role="status"></p><ul class="search-results"></ul><noscript><p class="noscript-note">Search uses JavaScript. All pages are linked above.</p></noscript></div></details></header>
<main id="main"><div class="breadcrumb wrap"><a href="index.html">Aura · Disaster resilience</a> / {E(page['nav'])}</div><section class="page-intro wrap" aria-labelledby="page-title"><p class="eyebrow">{E(page['eyebrow'])}</p><div class="intro-grid"><h1 id="page-title">{E(page['title'])}</h1><div class="intro-copy"><p class="lead">{E(page['lead'])}</p><p class="intro-meta">An independent proposal by Luke Nathan Hayes<br>Beginning on Minjerribah and in Redlands · October 2026</p>{home_actions}</div></div></section>
<figure class="hero wrap">{image_html(slug, assets, hero=True)}<figcaption><span>{E(assets[slug]['caption'])}</span><span>AI-generated concept · Imagined scene</span></figcaption></figure>
<div class="reading-layout wrap"><aside class="local-toc" aria-label="On this page"><p class="toc-title">On this page</p><ol>{toc}</ol>{source_jump}</aside><article class="article-content" aria-labelledby="page-title">{body}</article></div>{home_journeys}</main>
<footer class="footer wrap"><nav class="page-turns" aria-label="Previous and next pages">{''.join(turns)}</nav><div class="footer-base"><a class="brand" href="index.html"><img src="assets/brand-mark.png" width="42" height="42" alt=""><span>Aura of Intelligence<br><small>PERSONAL CAPABILITY · SHARED FUTURES</small></span></a><p>Luke Nathan Hayes · Strange But True<br>A proposal for everyday capability and continuing recovery.</p><nav class="footer-links" aria-label="Footer"><a href="site-map.html">Site map</a><a href="licence.html">Licence</a><a href="about.html#site-privacy">Site privacy</a><a href="{REPO}/wiki">Wiki ↗</a><a href="{REPO}">GitHub ↗</a></nav></div><p class="footer-fine">Strange But True Public Source Licence · Commercial, institutional and government reuse requires written permission. Sources imply no endorsement.</p><a class="back-top" href="#top">Back to top ↑</a></footer></body></html>'''


def build():
    content = runpy.run_path(str(SOURCE / 'content.py'))
    pages = content['PAGES']
    document = json.loads((SOURCE / 'document.json').read_text())
    assets = {asset['slug']:asset for asset in json.loads((OUT / 'assets/image-provenance.json').read_text())['assets']}
    reader, groups = make_reader(document)
    sources = source_list(document, content['NEW_SOURCES'])
    page_list = '<ol class="map-list">' + ''.join(f'<li><a href="{p["slug"]}.html">{E(p["nav"])}</a><p>{E(p["description"])}</p></li>' for p in pages) + '</ol>'
    for page in pages:
        # The authored copy follows the user's preference for simple punctuation.
        for field in ['title','lead','description','body']:
            page[field] = page[field].replace('–','-').replace('—',', ')
        body = references(page['body']).replace('{{sources}}', sources).replace('{{reader}}', reader).replace('{{page-list}}', page_list).replace('{{licence}}', licence_html())
        body = re.sub(r'\{\{image:([a-z-]+)\}\}', lambda match: inline_image(match.group(1), assets), body)
        if page['slug'] == 'build-together':
            body = body.replace('<a class="button" href="' + REPO + '/issues">Open the project discussion space ↗</a>', '<a class="button" href="' + REPO + '/issues">Open the project discussion space ↗</a>' + interest_builder())
        body, sections = add_section_ids(body)
        (OUT / (page['slug'] + '.html')).write_text(make_page(page, pages, assets, body, sections, groups))
    shutil.copyfile(SOURCE / 'assets.css', OUT / 'assets/site.css')
    shutil.copyfile(SOURCE / 'assets.js', OUT / 'assets/site.js')
    shutil.copyfile(ROOT / 'LICENCE.md', OUT / 'LICENCE.md')
    (OUT / '.nojekyll').write_text('')
    # Project-path robots.txt is a published preference record. The root snippet
    # explicitly explains the GitHub Pages origin-wide policy boundary.
    robots = (ROOT / 'robots.txt').read_text().rstrip() + '\n\nSitemap: ' + BASE + 'sitemap.xml\n'
    (OUT / 'robots.txt').write_text(robots)
    snippet = (ROOT / '.github/robots-root-snippet.txt').read_text().replace('# Add a Sitemap line when a project sitemap has been published and verified.', 'Sitemap: ' + BASE + 'sitemap.xml')
    (OUT / 'crawler-root-snippet.txt').write_text(snippet)
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    sitemap = ET.Element('{' + namespace + '}urlset')
    for page in pages:
        url = ET.SubElement(sitemap, '{' + namespace + '}url')
        ET.SubElement(url, '{' + namespace + '}loc').text = BASE if page['slug'] == 'index' else BASE + page['slug'] + '.html'
        ET.SubElement(url, '{' + namespace + '}lastmod').text = DATE
    (OUT / 'sitemap.xml').write_bytes(ET.tostring(sitemap, encoding='utf-8', xml_declaration=True))
    guide = ['# Aura of Intelligence for Disaster Resilience and Recovery', '', '> Independent proposal by Luke Nathan Hayes. Planning, research and design; an integrated field service and agency agreements remain development work.', '', '## Reading pages']
    guide.extend(f'- [{p["nav"]}]({BASE}{p["slug"]}.html): {p["description"]}' for p in pages)
    guide.extend(['', '## Source and use', '- [Working wiki](' + REPO + '/wiki)', '- [Licence](' + BASE + 'LICENCE.md): Strange But True Public Source Licence. Discovery grants no additional commercial, institutional, government or AI-training permission.', '- [Full document PDF](' + BASE + 'downloads/Aura_of_Intelligence_Disaster_Resilience_and_Recovery.pdf)', '', 'Distinguish proposals, current browser-tool foundations, illustrative scenarios, AI-generated concepts, source facts and measured performance. Sources establish no endorsement. Essential assistance is independent of a personal Aura or C-Hour record.', ''])
    (OUT / 'llms.txt').write_text('\n'.join(guide))
    manifest = dict(name='Aura of Intelligence · Disaster Resilience and Recovery', short_name='Aura Resilience', start_url='./', scope='./', display='browser', background_color='#fbfaf4', theme_color='#163c3d', icons=[dict(src='assets/icon-192.png',sizes='192x192',type='image/png'),dict(src='assets/icon-512.png',sizes='512x512',type='image/png')])
    (OUT / 'site.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    search = [dict(title=p['title'],url=p['slug']+'.html',text=plain(p['body'])) for p in pages]
    (OUT / 'assets/search-index.json').write_text(json.dumps(search, ensure_ascii=False, separators=(',',':')) + '\n')
    crosswalk = [dict(section=i,title=group['title'],pages=[p['slug']+'.html' for p in pages if i in p['chapters']],reader='library.html#document-'+f'{i:02d}') for i,group in enumerate(groups[:33],1)]
    (SOURCE / 'document-crosswalk.json').write_text(json.dumps(crosswalk, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(pages)} reading pages; full document with {len(groups)} chapters; {len(document["sources"])+len(content["NEW_SOURCES"])} linked sources.')


if __name__ == '__main__':
    build()
