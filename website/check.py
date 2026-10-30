"""Check publication links, document integrity, unique artwork and source coverage."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.images, self.errors = set(), [], [], []
        self.h1 = 0
        self.anchor_depth = 0
        self.elements = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append('duplicate id: ' + attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'a':
            if self.anchor_depth: self.errors.append('nested link')
            self.anchor_depth += 1
            self.links.append(attrs.get('href', ''))
        if tag == 'link' or (tag == 'script' and 'src' in attrs):
            self.links.append(attrs.get('href', attrs.get('src', '')))
        if tag == 'img':
            self.images.append(attrs)
            self.links.append(attrs.get('src', ''))
            for variant in attrs.get('srcset', '').split(','):
                if variant.strip(): self.links.append(variant.strip().split()[0])
            if 'alt' not in attrs: self.errors.append('image missing alt')
            if not attrs.get('width') or not attrs.get('height'): self.errors.append('image missing dimensions')
        if tag == 'svg': self.errors.append('SVG image violates requested raster artwork pattern')
    def handle_endtag(self, tag):
        if tag == 'a': self.anchor_depth = max(0,self.anchor_depth-1)


def main():
    errors, pages = [], {}
    files = list(SITE.glob('*.html'))
    for path in files:
        page = Page(); page.feed(path.read_text())
        pages[path.resolve()] = page
        errors.extend(path.name + ': ' + e for e in page.errors)
        if page.h1 != 1: errors.append(f'{path.name}: expected one main title, found {page.h1}')
        if '{{' in path.read_text(): errors.append(path.name + ': unreplaced template token')
    for path, page in pages.items():
        for href in page.links:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc: continue
            if not href: errors.append(path.name + ': empty URL'); continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not target.is_relative_to(SITE.resolve()):
                errors.append(path.name + ': path outside public site: ' + href); continue
            if not target.exists():
                errors.append(path.name + ': missing target: ' + href); continue
            if parsed.fragment and target.suffix == '.html':
                other = pages.get(target)
                if other and unquote(parsed.fragment) not in other.ids:
                    errors.append(path.name + ': missing fragment: ' + href)
    assert len(files) == 16, len(files)
    assets = json.loads((SITE / 'assets/image-provenance.json').read_text())['assets']
    assert len(assets) == 20, len(assets)
    assert len({a['original_sha256'] for a in assets}) == 20
    for path, page in pages.items():
        expected = 'assets/images/' + path.stem + '-1536.webp'
        if sum(image.get('src') == expected for image in page.images) != 1:
            errors.append(path.name + ': unique page hero is missing or repeated')
    downloads = SITE / 'downloads'
    for filename, checksum in [
        ('Aura_of_Intelligence_Disaster_Resilience_and_Recovery.docx','6d0866a7bb057717bf2ed6ce47b4c4f4bc762717560aa7c598171a895295bb39'),
        ('Aura_of_Intelligence_Disaster_Resilience_and_Recovery.pdf','63dd851d09f862adf657dd4fdc997c2bc77276823086e8cce4cb605c3e8bede9')]:
        if hashlib.sha256((downloads / filename).read_bytes()).hexdigest() != checksum:
            errors.append('supplied document changed: ' + filename)
    if (SITE / 'LICENCE.md').read_bytes() != (ROOT / 'LICENCE.md').read_bytes():
        errors.append('licence copy differs from repository terms')
    library = pages[(SITE / 'library.html').resolve()]
    for number in range(1,39):
        if f'document-{number:02d}' not in library.ids: errors.append(f'missing document chapter {number}')
    for prefix,count in [('P',13),('R',24),('N',3)]:
        for number in range(1,count+1):
            if f'source-{prefix}{number}' not in library.ids: errors.append(f'missing source {prefix}{number}')
    crosswalk = json.loads((ROOT / 'website/document-crosswalk.json').read_text())
    assert len(crosswalk) == 33
    assert all(row['pages'] for row in crosswalk), 'A document chapter lacks an introductory page.'
    sitemap = ET.parse(SITE / 'sitemap.xml')
    assert len(sitemap.getroot()) == 16
    manifest = json.loads((SITE / 'site.webmanifest').read_text())
    for icon in manifest['icons']:
        if not (SITE / icon['src']).is_file(): errors.append('missing manifest icon: ' + icon['src'])
    for path in SITE.rglob('*'):
        if path.suffix == '.webp':
            data = path.read_bytes()
            if len(data) < 44 or data[:4] != b'RIFF' or data[8:12] != b'WEBP':
                errors.append('invalid or empty image: ' + str(path.relative_to(SITE)))
        if path.suffix == '.png':
            data = path.read_bytes()
            if len(data) < 33 or data[:8] != b'\x89PNG\r\n\x1a\n':
                errors.append('invalid or empty PNG: ' + str(path.relative_to(SITE)))
        if path.suffix == '.ico' and path.stat().st_size < 22:
            errors.append('invalid or empty favicon: ' + str(path.relative_to(SITE)))
        if path.suffix in ['.html','.json','.js','.css','.txt','.xml','.md']:
            text = path.read_text()
            if re.search(r'/workspace/|/root/\.codex|file_000000|completion_token', text):
                errors.append('private runtime detail in public file: ' + str(path.relative_to(SITE)))
    if errors:
        print('\n'.join(errors)); sys.exit(1)
    print('PASS: 16 pages; internal URLs and fragments; 20 unique generated assets; 38 full-document chapters; 40 sources; all 33 main sections mapped; unchanged downloads and licence; no private runtime details.')


if __name__ == '__main__':
    main()
