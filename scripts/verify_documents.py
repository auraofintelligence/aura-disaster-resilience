#!/usr/bin/env python3
"""Check the packaged source documents against their public contents list.

Run with Python's standard library. --check-pages also uses pypdf when available.
The check reads packaged files; it does not change originals or write outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile


MAX_DOCUMENT_BYTES = 90 * 1024 * 1024


def sha256_file(path: Path) -> str:
    fingerprint = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            fingerprint.update(chunk)
    return fingerprint.hexdigest()


def private_path_strings(value, location="manifest"):
    """Find workstation paths while allowing public URLs and original filenames."""
    found = []
    if isinstance(value, str):
        if re.search(r"(?:^|[\s\"'])(?:[A-Za-z]:[\\/]|\\\\[^\\])", value):
            found.append(location)
    elif isinstance(value, dict):
        for key, item in value.items():
            found.extend(private_path_strings(item, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(private_path_strings(item, f"{location}[{index}]"))
    return found


def check_manifest(repo_root: Path, manifest_path: Path, check_pages=False):
    errors = []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        errors.append("Unsupported or missing schema_version.")
    for location in private_path_strings(manifest):
        errors.append(f"Private workstation path in {location}.")

    page_reader = None
    if check_pages:
        try:
            from pypdf import PdfReader
            page_reader = PdfReader
        except ImportError:
            errors.append("Page checking needs pypdf; use the bundled document runtime.")

    documents = manifest.get("documents", [])
    requests = manifest.get("requests", [])
    by_id = {}
    fingerprints = set()
    public_paths = set()
    total_bytes = 0
    alias_count = 0
    package_root = (repo_root / "sources" / "documents").resolve()

    for document in documents:
        doc_id = document.get("id", "<missing ID>")
        if doc_id in by_id:
            errors.append(f"Duplicate document ID: {doc_id}.")
        by_id[doc_id] = document
        fingerprint = document.get("sha256", "")
        if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
            errors.append(f"{doc_id}: invalid SHA-256 fingerprint.")
        if fingerprint in fingerprints:
            errors.append(f"{doc_id}: identical bytes should share one document and aliases.")
        fingerprints.add(fingerprint)

        public_path = document.get("public_path", "")
        relative = PurePosixPath(public_path)
        if relative.is_absolute() or ".." in relative.parts or "\\" in public_path:
            errors.append(f"{doc_id}: unsafe public path.")
            continue
        if relative.parts[:2] != ("sources", "documents"):
            errors.append(f"{doc_id}: public path must be inside sources/documents.")
            continue
        if public_path in public_paths:
            errors.append(f"{doc_id}: repeated public path.")
        public_paths.add(public_path)
        target = (repo_root / Path(*relative.parts)).resolve()
        try:
            target.relative_to(package_root)
        except ValueError:
            errors.append(f"{doc_id}: resolved document escapes its package folder.")
            continue

        if document.get("availability") != "packaged":
            errors.append(f"{doc_id}: packaged document availability is not recorded.")
        if not target.is_file():
            errors.append(f"{doc_id}: packaged file is missing: {public_path}.")
            continue
        size = target.stat().st_size
        total_bytes += size
        if size != document.get("size_bytes"):
            errors.append(f"{doc_id}: byte count differs from the manifest.")
        if size > MAX_DOCUMENT_BYTES:
            errors.append(f"{doc_id}: exceeds the 90 MiB packaging limit.")
        if sha256_file(target) != fingerprint:
            errors.append(f"{doc_id}: content fingerprint differs from the manifest.")

        suffix = target.suffix.lower()
        if suffix == ".pdf":
            with target.open("rb") as stream:
                if b"%PDF-" not in stream.read(1024):
                    errors.append(f"{doc_id}: PDF file signature was not found.")
            if page_reader is not None:
                try:
                    pages = len(page_reader(target).pages)
                    if document.get("pages") != pages:
                        errors.append(f"{doc_id}: PDF page count differs from the manifest.")
                except Exception as exc:
                    errors.append(f"{doc_id}: PDF page check failed ({type(exc).__name__}).")
        elif suffix == ".docx":
            try:
                with zipfile.ZipFile(target) as archive:
                    names = set(archive.namelist())
                    if not {"[Content_Types].xml", "word/document.xml"} <= names:
                        errors.append(f"{doc_id}: required Word document parts are missing.")
                    if archive.testzip() is not None:
                        errors.append(f"{doc_id}: a Word document part failed its integrity check.")
            except zipfile.BadZipFile:
                errors.append(f"{doc_id}: Word document archive is invalid.")
        else:
            errors.append(f"{doc_id}: unexpected document type.")

        aliases = document.get("aliases", [])
        if not aliases:
            errors.append(f"{doc_id}: source filename/alias record is missing.")
        alias_count += len(aliases)
        for alias in aliases:
            original = alias.get("original_filename", "")
            if not original or "/" in original or "\\" in original:
                errors.append(f"{doc_id}: alias must retain a filename, not a workstation path.")
            if alias.get("public_path") != public_path:
                errors.append(f"{doc_id}: alias points to a different public file.")
            if alias.get("availability") != "packaged_alias":
                errors.append(f"{doc_id}: alias availability is missing.")

    request_ids = set()
    unavailable = []
    for request in requests:
        request_id = request.get("id", "<missing ID>")
        if request_id in request_ids:
            errors.append(f"Duplicate request ID: {request_id}.")
        request_ids.add(request_id)
        if request.get("availability") != "packaged":
            unavailable.append(request_id)
            continue
        document = by_id.get(request.get("document_id"))
        if document is None:
            errors.append(f"{request_id}: packaged document reference is missing.")
        elif request.get("public_path") != document.get("public_path"):
            errors.append(f"{request_id}: public path differs from its document record.")
        elif request.get("sha256") != document.get("sha256"):
            errors.append(f"{request_id}: fingerprint differs from its document record.")
    if unavailable:
        errors.append("Requested documents awaiting packaging: " + ", ".join(unavailable))

    actual_paths = {
        path.relative_to(repo_root).as_posix()
        for path in package_root.rglob("*") if path.is_file()
    }
    for unlisted in sorted(actual_paths - public_paths):
        errors.append(f"Packaged file has no manifest record: {unlisted}.")
    summary = manifest.get("summary", {})
    if summary.get("unique_documents") != len(documents):
        errors.append("Summary document count differs from the records.")
    if summary.get("unique_bytes") != total_bytes:
        errors.append("Summary byte count differs from the packaged files.")
    if summary.get("user_supplied_requests") != len(requests):
        errors.append("Summary request count differs from the records.")
    result = {
        "ok": not errors,
        "unique_documents": len(documents),
        "user_supplied_requests": len(requests),
        "packaged_requests": len(requests) - len(unavailable),
        "source_aliases": alias_count,
        "unique_bytes": total_bytes,
        "page_counts_checked": check_pages and page_reader is not None,
        "errors": errors,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="Use another public document manifest.")
    parser.add_argument("--check-pages", action="store_true", help="Also verify PDF page counts with pypdf.")
    parser.add_argument("--json", action="store_true", help="Print the verification result as JSON.")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = args.manifest or repo_root / "data" / "document-manifest.json"
    try:
        result = check_manifest(repo_root, manifest_path, args.check_pages)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {"ok": False, "errors": [f"Manifest could not be checked: {type(exc).__name__}: {exc}"]}
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    elif result["ok"]:
        print(f"Verified {result['unique_documents']} documents, {result['packaged_requests']} requested originals, "
              f"{result['source_aliases']} source aliases and {result['unique_bytes']:,} bytes.")
    else:
        print("Document verification needs attention:")
        for error in result["errors"]:
            print("- " + error)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
