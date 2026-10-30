"""Prepare full-frame WebP images and a clean public prompt provenance file.

Pillow is needed only when adding artwork, not for routine text builds.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifests', nargs='+', type=Path)
    args = parser.parse_args()
    (OUT / 'images').mkdir(parents=True, exist_ok=True)
    assets = []
    for path in args.manifests:
        value = json.loads(path.read_text())
        entries = value if isinstance(value, list) else value['assets']
        for entry in entries:
            slug = entry['slug']
            original = ROOT / 'site/assets/originals' / (slug + '.png')
            image = Image.open(original).convert('RGB')
            if slug == 'brand-mark':
                for size, filename in [(84,'brand-mark.png'),(32,'favicon-32.png'),(180,'apple-touch-icon.png'),(192,'icon-192.png'),(512,'icon-512.png')]:
                    target = OUT / filename
                    temporary = ROOT / '.local' / filename
                    temporary.parent.mkdir(exist_ok=True)
                    image.resize((size,size), Image.Resampling.LANCZOS).save(temporary, format='PNG', optimize=True)
                    with Image.open(temporary) as check:
                        check.verify()
                    temporary.replace(target)
                temporary = ROOT / '.local/favicon.ico'
                image.save(temporary, format='ICO', sizes=[(16,16),(32,32),(48,48)])
                temporary.replace(ROOT / 'site/favicon.ico')
                outputs = ['assets/'+filename for filename in ['brand-mark.png','favicon-32.png','apple-touch-icon.png','icon-192.png','icon-512.png']] + ['favicon.ico']
            else:
                assert image.size == (1536,1024), (slug,image.size)
                outputs = []
                for width in [768,1536]:
                    resized = image.resize((width, width*2//3), Image.Resampling.LANCZOS)
                    target = OUT / 'images' / f'{slug}-{width}.webp'
                    temporary = ROOT / '.local' / target.name
                    temporary.parent.mkdir(exist_ok=True)
                    resized.save(temporary, 'WEBP', quality=88, method=6)
                    with Image.open(temporary) as check:
                        check.verify()
                    temporary.replace(target)
                    outputs.append('assets/images/'+target.name)
            assets.append(dict(slug=slug,alt=entry['alt'],caption=entry.get('caption',entry.get('concept_caption')),prompt=entry.get('prompt',entry.get('final_prompt')),generator='Built-in image generation',created='2026-10-30',original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),original_dimensions=list(image.size),outputs=outputs,frame='Complete generated composition; no cropping',status='AI-generated concept, not documentary evidence of deployed services'))
    manifest = dict(title='Aura disaster resilience website artwork',created='2026-10-30',rights='Original project artwork is provided under the Strange But True Public Source Licence.',assets=assets)
    (OUT / 'image-provenance.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Prepared {len(assets)} distinct generated assets, including the raster brand mark.')


if __name__ == '__main__':
    main()
