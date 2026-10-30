# Companion website publication record

## Work scope

User request: build a GitHub Pages website accompanying the disaster document and
wiki, following the existing site pattern, with licence, crawler preferences,
navigation, a new favicon, generated hero and inline images, sitemap and associated
links. Consider the newer Installing the Missing Middle and Escape Room Team
Building publications without converting their research into settled deployments.

Primary question context: AUR-01. Related context: OPS-01 and DAT-02.
This publication explains the proposal; it does not answer those implementation
questions, allocate operational duties or record a human approval.

Source baseline: `e781e7c2f24c2cf38f6ab422790247cde86b889f`.
Work date: 30 October 2026. Preparation: Codex, with bounded source-research and
image-asset assistance. Website integration and publication are owned by the
primary build task. No existing question, decision, review or research-answer
record is changed by the website.

## Produced

- Sixteen static reading pages, with a distinct generated hero on every page.
- Three generated inline illustrations and a new generated raster identity.
- Complete HTML reading copy of the supplied 39-page document, including its
  original ordered blocks, six tables, 33 main sections and five reference sections.
- Unchanged PDF and Word downloads, original 37 sources and three clearly labelled
  newer source connections. Every main section has an introductory-page crosswalk.
- Responsive navigation, local page search, readable references, document expansion
  controls, previous/next routes and an optional browser-only interest-note helper.
- HTML and XML sitemaps, existing licence text, project crawler preferences,
  origin-root snippet, plain-text reading guide, social metadata and image provenance.
- Source, build instructions, publication workflow and a structural/integrity check.

## Checks before publication

`python3 website/build.py` and `python3 website/check.py` passed. The latter checks
internal targets and fragments, main titles, unique artwork, all 38 document
chapters, all 40 source entries, document crosswalk coverage, the unchanged licence
and download checksums, manifest icons and public files for private runtime paths.
`node --check website/assets.js` passed.

Browser QA covered the desktop introduction, a 390-pixel iframe viewport, menu and
search, Escape dismissal, a direct minimum-viable-self chapter link, all-chapter
expansion and collapse, and copying a sample interest note. The narrow viewport
had equal content and client widths. No application-script error was observed;
browser-extension metadata errors were unrelated to this site.

The local existing wiki checks were attempted in a partial checkout and encountered
absent preserved source downloads. Their validation requires the full source
archive; the existing repository workflow retains that check in its full checkout.
The website workflow separately checks the publication using its complete required
inputs. Publication and actual workflow results are recorded by GitHub against
the published commit.

## Boundaries and continuation

The website introduces design and research. Equipment endurance, protected personal
storage, receiving services, Guardian integration, clinical offerings, co-operative
formation and field operation retain their separate development and review paths.
AI-generated images are concept illustrations, not deployment evidence.

GitHub Pages is configured to use the dedicated Actions workflow. The existing
wiki, source archive and decision records remain in place. The Pages workflow and
deployment environment supply the authoritative publication receipt and URL.
