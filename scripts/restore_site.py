#!/usr/bin/env python3
"""Restore a checked source package into a new directory.

List packages: python scripts/restore_site.py --list
Restore one:   python scripts/restore_site.py shared-table-initiative --output ../restored-shared-table

The selected directory must be new or empty. Restoration checks the fingerprints
of all parts, the complete ZIP and each restored file. Original licences and
notices travel with the files. This restores the captured source edition; use
its own README to prepare dependencies and hosting.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys
import zipfile

from verify_sites import (CHUNK, EMBEDDED_MANIFEST, MANIFEST, inspect_archive,
                          open_archive, read_json, safe_relative)


def restore(record, target):
    target = target.resolve()
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError("Choose a new or empty output directory; existing work is preserved")
    # Check the complete archive before creating source files.
    with open_archive(record) as stream:
        tree = inspect_archive(record, stream)
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(stream) as archive:
            for descriptor in tree["files"]:
                relative = safe_relative(descriptor["path"])
                destination = target.joinpath(*relative.parts)
                if not destination.resolve().is_relative_to(target):
                    raise ValueError("Package path leaves the chosen output directory")
                destination.parent.mkdir(parents=True, exist_ok=True)
                digest, count = hashlib.sha256(), 0
                with archive.open(descriptor["path"]) as saved, destination.open("xb") as output:
                    for block in iter(lambda: saved.read(CHUNK), b""):
                        digest.update(block)
                        output.write(block)
                        count += len(block)
                if count != descriptor["bytes"] or digest.hexdigest() != descriptor["sha256"]:
                    raise ValueError(f"Restored file fingerprint differs: {descriptor['path']}")
                info = archive.getinfo(descriptor["path"])
                mode = (info.external_attr >> 16) & 0o777
                if mode:
                    os.chmod(destination, mode)
            manifest_path = target / EMBEDDED_MANIFEST
            with manifest_path.open("xb") as output:
                output.write(archive.read(EMBEDDED_MANIFEST))
    print(f"Restored {record['slug']}: {record['file_count']} checked source files.")
    print(f"Recorded source commit: {record['head']}")
    print("The saved working changes and original licence files are included.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slug", nargs="?", help="Repository name from --list")
    parser.add_argument("--list", action="store_true", help="List saved source packages")
    parser.add_argument("--output", type=Path, help="New or empty directory for the restored source")
    args = parser.parse_args()
    try:
        manifest = read_json(MANIFEST)
        if manifest["capture_status"] != "complete":
            raise ValueError("Source capture is still in progress")
        records = {r["slug"]: r for r in manifest["records"]}
        if args.list:
            for record in records.values():
                print(f"{record['slug']}: {record['state']}")
            return 0
        if not args.slug or args.output is None:
            parser.error("Choose a repository name and --output, or use --list")
        if args.slug not in records:
            raise ValueError("Repository name is absent from the site manifest; use --list")
        record = records[args.slug]
        if record["state"] == "versioned_destination":
            raise ValueError("The destination is already a versioned repository; use its checked-out files")
        if record["state"] != "source_packaged":
            raise ValueError("This source package awaits capture")
        restore(record, args.output)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"Source restoration: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
