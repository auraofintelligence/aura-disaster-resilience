# Companion website

This is the static GitHub Pages introduction to the disaster document and wiki.
The publication target is `https://auraofintelligence.github.io/aura-disaster-resilience/`.

## Edit and build

Edit `website/content.py`, `website/assets.css` and `website/assets.js`, then run:

```text
python3 website/build.py
python3 website/check.py
```

The build uses the Python standard library and writes the static reading pages to
`site/`. Commit source and generated pages together. The site runs without a
framework, analytics, a backend or external fonts. Core reading and navigation
work without JavaScript; search, document expansion controls and the local
interest-note helper progressively enhance the pages.

`document.json` preserves the supplied 27 October 2026 Word edition in its original
block order, including six tables and all 37 references. The full reading copy
appears on the library page. `document-crosswalk.json` maps every main document
section to its introductory page. PDF and Word downloads retain their supplied
checksums. Updating the document is a separate editorial decision; it is not
required for routine website changes.

If an authorised new Word edition is supplied, extraction requires `python-docx`:

```text
python3 website/extract_document.py path/to/authorised-edition.docx
```

Update the expected document metadata and checksums at that point. Never silently
replace a supplied edition to match a website summary.

## Artwork

The sixteen pages each have a distinct generated hero. Three further generated
illustrations appear in context. The new raster mark supplies the favicon,
manifest icons and header identity. Full compositions are retained in responsive
768 and 1536 pixel WebP variants. Captions identify imagined concepts, rather than
deployed equipment or measured results.

`site/assets/image-provenance.json` records the full prompts, source checksums,
dimensions and generated outputs. Generation originals remain in the local
ignored `site/assets/originals/` workspace. The full-resolution published WebP
editions and prompt provenance are versioned with the repository. Re-preparing
new artwork uses Pillow and the explicit generation manifests:

```text
python3 website/prepare_images.py path/to/image-manifest.json
```

## Publish

The Pages workflow checks and uploads only `site/`, preserving the existing wiki,
source archive and review records. It avoids checking out the large source
archives. Configure the repository's Pages source as **GitHub Actions**. An initial
settings action needs a repository administrator; the publication workflow does
not attempt to bypass that setting or claim an unobserved deployment.

The project `robots.txt` records crawler preferences, while the effective Pages
policy lives at the shared origin root. The project-scoped snippet is provided
for the origin owner to merge while preserving neighbouring projects.

The existing Strange But True Public Source Licence remains authoritative.
