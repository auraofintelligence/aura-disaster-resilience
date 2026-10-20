# Portable website and repository sources

These packages bring the connected source material into this repository so a
future team can inspect it, restore it and carry the useful work forward.
Each package contains the selected local working files, including code, static
assets, documents, original licences and notices. Its source manifest records
the Git commit, working changes, capture time and a fingerprint for every file.
A SHA-256 fingerprint is a content check: matching fingerprints mean the saved
bytes match the recorded edition.

The destination, Aura Disaster Resilience, preserves its own files and version
history directly. Its source manifest entry explains that relationship. The
other ecosystem repositories each have a source package here.

## Check the packages

From the top level of this repository, with Python available:

```text
python scripts/verify_sites.py --deep
```

The check reads every saved file and compares its fingerprint. It also checks
each package part, the complete ZIP and the source manifest. Larger ZIPs are
split into 32 MiB parts so they travel through GitHub as ordinary files.

## Restore a source edition

```text
python scripts/restore_site.py --list
python scripts/restore_site.py shared-table-initiative --output ../restored-shared-table
```

Choose a new or empty destination. The restorer joins package parts when
needed, checks the contents and creates the source files. Follow the restored
project's own README to prepare its dependencies, run it or publish it.

## What travels with a package

The capture includes Git-tracked working files and untracked files that Git
does not ignore. This preserves the current local source edition, including
work awaiting a commit. Original repositories remain intact. File-by-file
records identify exactly what was saved.

Git history, dependency installations, caches, temporary build output and
credential or key files are excluded. Each package lists any excluded candidate
paths and their reason. The source's original licence and notices continue to
apply; this collection does not replace those terms.

The [site manifest](../../data/site-manifest.json) maps the packages and public
addresses. The public source for auraofintelligence.com and p4a.xyz is represented
by the related repository packages. Hosting settings, external databases and any
separate WordPress export have their own handover when supplied. A source
snapshot records an edition of the work; running and testing a site is a further
milestone.
