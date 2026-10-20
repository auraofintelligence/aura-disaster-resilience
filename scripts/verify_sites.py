#!/usr/bin/env python3
"""Capture and check the source packages used by the disaster-resilience library.

A source package keeps the selected working files, their original licences and a
file-by-file fingerprint list. SHA-256 fingerprints let a later reader check
that the saved bytes are the same. Python's standard library is sufficient.

Check packages:       python scripts/verify_sites.py --deep
List capture sizes:  python scripts/verify_sites.py --preflight --source-root ..
Make packages:       python scripts/verify_sites.py --capture --source-root ..

Capture reads neighbouring repositories. It writes only sources/sites/ and
data/site-manifest.json in this destination repository. The destination keeps
its own version history and is never packaged inside itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
import zipfile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "site-manifest.json"
SITE_ROOT = ROOT / "sources" / "sites"
DESTINATION = "aura-disaster-resilience"
EMBEDDED_MANIFEST = "__snapshot_manifest__.json"
CHUNK = 1024 * 1024
PART_BYTES = 32 * 1024 * 1024
SPLIT_ABOVE = 90 * 1024 * 1024
EXCLUDED_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".cache",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".next", ".nuxt",
    ".turbo", ".parcel-cache", "coverage", "test-results",
    "playwright-report", "tmp", "temp", ".tmp", ".ssh", ".aws",
}
KEY_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".keystore", ".jks", ".kdbx"}
CREDENTIAL_NAMES = {
    ".npmrc", ".pypirc", ".netrc", "credentials.json", "service-account.json",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
}
# Detect concrete secret formats, rather than ordinary words such as API_KEY in
# examples. Matched contents are never logged or included in the package.
SECRET_MARKERS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"),
    re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{40,255}\b"),
    re.compile(rb"\bAKIA[A-Z0-9]{16}\b"),
)
RULES = {
    "selection": "Git tracked working files and untracked files not ignored by Git; current working contents, rather than only HEAD contents.",
    "preserved": "Original code, static assets, documents, licences and notices remain unchanged inside each package.",
    "excluded": "Git history, dependency folders, caches, temporary build output, credential/environment/key files, detected concrete secret formats, symlinks and unavailable working files.",
    "working_changes": "Source repositories are read only. Each package records its own capture time, HEAD, branch, start/end working status and file fingerprints.",
    "scope": "A repository snapshot preserves source artefacts. Live hosting configuration, external databases, unpublished records, ignored dependencies and an external WordPress installation require their own authorised handover.",
    "licences": "Each source retains its own licence and notices. Inclusion here does not replace those terms or grant additional rights.",
    "parts": "ZIP files over 90 MiB are divided into 32 MiB parts, with a fingerprint for every part and for the complete ZIP.",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonical_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + ".pending")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)


def git(source, *args):
    result = subprocess.run(["git", "-C", str(source), *args], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise RuntimeError(f"Git could not read {source.name}: {args[0]}")
    return result.stdout


def source_repositories():
    records = read_json(ROOT / "data" / "ecosystem.json")
    return sorted({url.removesuffix(".git").rstrip("/") for record in records
                   for url in record["repositories"]})


def safe_relative(value):
    # ZIP paths use forward slashes on all platforms. Reject Windows paths too.
    if not value or "\\" in value or "\x00" in value or ":" in value:
        raise ValueError("Package has an unsafe relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("Package has an unsafe relative path")
    return path


def excluded_reason(relative):
    path = PurePosixPath(relative)
    lower_parts = [part.lower() for part in path.parts]
    if any(part in EXCLUDED_DIRS for part in lower_parts):
        return "history, dependency, cache or temporary directory"
    name = path.name.lower()
    if name.startswith(".env") or name in CREDENTIAL_NAMES or path.suffix.lower() in KEY_SUFFIXES:
        return "credential, environment or key file"
    if re.fullmatch(r"(?:service[-_]?account|credentials?)[-.].*\.json", name):
        return "credential file name"
    return None


def selected_paths(source):
    raw = git(source, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    selected, excluded = [], []
    for relative in sorted(set(raw.decode("utf-8").split("\0")) - {""}):
        safe_relative(relative)
        reason = excluded_reason(relative)
        path = source.joinpath(*PurePosixPath(relative).parts)
        if not reason:
            if path.is_symlink():
                reason = "symbolic link; restore through its source project when needed"
            elif not path.is_file():
                reason = "working file unavailable or Git submodule directory"
        if reason:
            excluded.append({"path": relative, "reason": reason})
        else:
            selected.append((relative, path))
    return selected, excluded


def working_status(source):
    raw = git(source, "status", "--porcelain=v1", "--untracked-files=all", "-z")
    parts = raw.decode("utf-8").split("\0")
    records, index = [], 0
    while index < len(parts) and parts[index]:
        entry = parts[index]
        item = {"path": entry[3:], "index_status": entry[0], "working_status": entry[1]}
        if "R" in entry[:2] or "C" in entry[:2]:
            index += 1
            item["original_path"] = parts[index]
        records.append(item)
        index += 1
    return records


def source_version(source):
    return {
        "head": git(source, "rev-parse", "HEAD").decode().strip(),
        "branch": git(source, "rev-parse", "--abbrev-ref", "HEAD").decode().strip(),
        "working_status": working_status(source),
    }


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def file_descriptor(path):
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": file_sha256(path)}


def secret_marker(path):
    # Chunk overlap detects markers spanning a read boundary, including in large
    # documents. No extracted content or matched value is returned.
    previous = b""
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            content = previous + block
            if any(pattern.search(content) for pattern in SECRET_MARKERS):
                return True
            previous = content[-512:]
    return False


def external_site_records():
    result = []
    for item in read_json(ROOT / "data" / "ecosystem.json"):
        for url in item.get("public_urls", []):
            if "qld.gov.au/" in url:
                result.append({"url": url, "relationship": "official external reference",
                               "capture": "Reference only; its owner publishes the authoritative site."})
            elif "auraofintelligence.com" in url:
                result.append({"url": url, "source_repositories": ["auraofintelligence.github.io"],
                               "relationship": "external canonical address with related public repository source",
                               "capture": "The public repository source is packaged. A separate WordPress or hosting export remains a handover item when supplied."})
            elif "p4a.xyz" in url:
                result.append({"url": url, "source_repositories": ["p4a-xyz-cinema"],
                               "relationship": "external canonical address with mapped public source",
                               "capture": "The current local public source tree is packaged; live host configuration and external records have their own handover."})
            elif "auraofintelligence.github.io" in url:
                remainder = url.split("auraofintelligence.github.io", 1)[1].strip("/")
                slug = remainder.split("/", 1)[0] if remainder else "auraofintelligence.github.io"
                result.append({"url": url, "source_repositories": [slug],
                               "relationship": "GitHub Pages address mapped to repository source",
                               "capture": "The selected local source files are packaged with their recorded edition."})
            else:
                result.append({"url": url, "relationship": "external address awaiting a source mapping",
                               "capture": "Source export or mapping remains a handover item."})
    return result


def preflight(source_root):
    records = []
    for url in source_repositories():
        slug = url.rsplit("/", 1)[1]
        if slug == DESTINATION:
            records.append({"slug": slug, "state": "versioned_destination", "source_bytes": 0, "files": 0})
            continue
        source = source_root / slug
        if not source.is_dir():
            records.append({"slug": slug, "state": "local_source_missing", "source_bytes": 0, "files": 0})
            continue
        selected, excluded = selected_paths(source)
        records.append({"slug": slug, "state": "ready", "source_bytes": sum(p.stat().st_size for _, p in selected),
                        "files": len(selected), "excluded_paths": len(excluded)})
    return {"source_bytes": sum(r["source_bytes"] for r in records),
            "files": sum(r["files"] for r in records), "records": records}


def capture_one(url, source_root):
    slug = url.rsplit("/", 1)[1]
    if slug == DESTINATION:
        return {"slug": slug, "repository": url, "state": "versioned_destination",
                "capture": "This destination repository preserves its own complete files and version history. It is excluded from source archives to prevent recursion."}
    source = source_root / slug
    if not source.is_dir():
        return {"slug": slug, "repository": url, "state": "local_source_missing"}
    directory = SITE_ROOT / slug
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise RuntimeError(f"Package directory already has files: {slug}; keep that edition or choose a new capture destination")
    selected, exclusions = selected_paths(source)
    version_start = source_version(source)
    started = utc_now()
    zip_path = directory / "source.zip"
    files, observed = [], []
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as archive:
        for relative, path in selected:
            if relative == EMBEDDED_MANIFEST:
                raise RuntimeError(f"Reserved package manifest path exists in {slug}")
            if secret_marker(path):
                exclusions.append({"path": relative, "reason": "concrete credential or private-key format detected; source remains unchanged"})
                continue
            before = path.stat()
            info = zipfile.ZipInfo.from_file(path, arcname=relative, strict_timestamps=False)
            info.compress_type = zipfile.ZIP_DEFLATED
            info._compresslevel = 1
            digest = hashlib.sha256()
            count = 0
            with path.open("rb") as original, archive.open(info, "w", force_zip64=True) as saved:
                for block in iter(lambda: original.read(CHUNK), b""):
                    digest.update(block)
                    saved.write(block)
                    count += len(block)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or count != before.st_size:
                raise RuntimeError(f"Source file changed during capture: {slug}/{relative}; capture a new consistent edition")
            files.append({"path": relative, "bytes": count, "sha256": digest.hexdigest()})
            observed.append((relative, path, after.st_size, after.st_mtime_ns))
        changed = [relative for relative, path, size, mtime in observed
                   if not path.exists() or (path.stat().st_size, path.stat().st_mtime_ns) != (size, mtime)]
        if changed:
            raise RuntimeError(f"Source files changed before capture completed in {slug}; capture a new consistent edition")
        version_end = source_version(source)
        snapshot = {
            "schema_version": 1, "repository": url, "slug": slug,
            "capture_started_utc": started, "capture_completed_utc": utc_now(),
            "source_version_start": version_start, "source_version_end": version_end,
            "source_git_status_unchanged": version_start == version_end,
            "selection_rules": RULES, "files": files,
            "files_sha256": hashlib.sha256(canonical_bytes(files)).hexdigest(),
            "file_count": len(files), "source_bytes": sum(f["bytes"] for f in files),
            "excluded": sorted(exclusions, key=lambda item: item["path"]),
        }
        manifest_bytes = (json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        archive.writestr(EMBEDDED_MANIFEST, manifest_bytes)
    tree_path = directory / "source-manifest.json"
    tree_path.write_bytes(manifest_bytes)
    zip_size, zip_digest = zip_path.stat().st_size, file_sha256(zip_path)
    parts = []
    if zip_size > SPLIT_ABOVE:
        with zip_path.open("rb") as stream:
            number = 1
            while block := stream.read(PART_BYTES):
                part_path = directory / f"source.zip.part-{number:03d}"
                part_path.write_bytes(block)
                parts.append(file_descriptor(part_path))
                number += 1
        # Only this freshly created, fully fingerprinted file is removed.
        zip_path.unlink()
    else:
        parts.append(file_descriptor(zip_path))
    return {
        "slug": slug, "repository": url, "state": "source_packaged",
        "head": version_start["head"], "branch": version_start["branch"],
        "working_tree_changed_from_head": bool(version_start["working_status"]),
        "source_git_status_unchanged": snapshot["source_git_status_unchanged"],
        "file_count": len(files), "source_bytes": snapshot["source_bytes"],
        "excluded_count": len(exclusions), "tree_manifest": file_descriptor(tree_path),
        "files_sha256": snapshot["files_sha256"],
        "archive": {"format": "zip", "bytes": zip_size, "sha256": zip_digest,
                    "multipart": len(parts) > 1, "parts": parts},
        "capture_completed_utc": snapshot["capture_completed_utc"],
    }


def capture(source_root):
    if MANIFEST.exists():
        raise RuntimeError("A site manifest already exists. Preserve this captured edition before making another.")
    SITE_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "purpose": "Portable source packages for the kiosk planning library and connected ecosystem.",
                "capture_started_utc": utc_now(), "capture_status": "in_progress",
                "selection_rules": RULES, "external_sites": external_site_records(), "records": []}
    write_json(MANIFEST, manifest)
    for url in source_repositories():
        record = capture_one(url, source_root)
        manifest["records"].append(record)
        write_json(MANIFEST, manifest)
        archive_bytes = record.get("archive", {}).get("bytes", 0)
        print(f"{record['slug']}: {record['state']}; {record.get('file_count', 0)} files; {archive_bytes:,} archive bytes", flush=True)
    packaged = [r for r in manifest["records"] if r["state"] == "source_packaged"]
    manifest["summary"] = {
        "repository_destinations": len(manifest["records"]), "source_packages": len(packaged),
        "versioned_destinations": sum(r["state"] == "versioned_destination" for r in manifest["records"]),
        "missing_sources": [r["slug"] for r in manifest["records"] if r["state"] == "local_source_missing"],
        "source_files": sum(r["file_count"] for r in packaged),
        "source_bytes": sum(r["source_bytes"] for r in packaged),
        "archive_bytes": sum(r["archive"]["bytes"] for r in packaged),
        "archive_parts": sum(len(r["archive"]["parts"]) for r in packaged),
        "excluded_files": sum(r["excluded_count"] for r in packaged),
    }
    manifest["capture_completed_utc"] = utc_now()
    manifest["capture_status"] = "complete"
    write_json(MANIFEST, manifest)
    print(json.dumps(manifest["summary"], indent=2), flush=True)


def checked_path(descriptor):
    path = ROOT.joinpath(*safe_relative(descriptor["path"]).parts)
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Package file is unavailable: {descriptor['path']}")
    if path.stat().st_size != descriptor["bytes"] or file_sha256(path) != descriptor["sha256"]:
        raise ValueError(f"Package fingerprint differs: {descriptor['path']}")
    return path


def open_archive(record):
    """Return a checked complete ZIP stream; caller closes the returned stream."""
    parts = record["archive"]["parts"]
    if not parts:
        raise ValueError("Package has no archive parts")
    stream = tempfile.TemporaryFile() if record["archive"]["multipart"] else None
    digest, count = hashlib.sha256(), 0
    try:
        for descriptor in parts:
            path = ROOT.joinpath(*safe_relative(descriptor["path"]).parts)
            if not path.is_file() or path.is_symlink() or path.stat().st_size != descriptor["bytes"]:
                raise ValueError(f"Package part is unavailable or has a different size: {descriptor['path']}")
            part_digest = hashlib.sha256()
            with path.open("rb") as part:
                for block in iter(lambda: part.read(CHUNK), b""):
                    part_digest.update(block)
                    digest.update(block)
                    count += len(block)
                    if stream is not None:
                        stream.write(block)
            if part_digest.hexdigest() != descriptor["sha256"]:
                raise ValueError(f"Package part fingerprint differs: {descriptor['path']}")
        if count != record["archive"]["bytes"] or digest.hexdigest() != record["archive"]["sha256"]:
            raise ValueError(f"Complete ZIP fingerprint differs: {record['slug']}")
        if stream is None:
            stream = ROOT.joinpath(*safe_relative(parts[0]["path"]).parts).open("rb")
        stream.seek(0)
        return stream
    except Exception:
        if stream is not None:
            stream.close()
        raise


def inspect_archive(record, stream, deep=False):
    tree_path = checked_path(record["tree_manifest"])
    tree = read_json(tree_path)
    list_digest = hashlib.sha256(canonical_bytes(tree["files"])).hexdigest()
    if list_digest != record["files_sha256"] or list_digest != tree["files_sha256"]:
        raise ValueError(f"Source file list fingerprint differs: {record['slug']}")
    if (tree["file_count"] != record["file_count"] or tree["source_bytes"] != record["source_bytes"]
            or len(tree["files"]) != tree["file_count"]
            or sum(item["bytes"] for item in tree["files"]) != tree["source_bytes"]):
        raise ValueError(f"Source file totals differ: {record['slug']}")
    expected = {f["path"]: f for f in tree["files"]}
    if len(expected) != len(tree["files"]):
        raise ValueError("Source file list contains duplicate paths")
    with zipfile.ZipFile(stream) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected) | {EMBEDDED_MANIFEST}:
            raise ValueError(f"ZIP entries differ from the source file list: {record['slug']}")
        if archive.read(EMBEDDED_MANIFEST) != tree_path.read_bytes():
            raise ValueError(f"Embedded source manifest differs: {record['slug']}")
        for info in archive.infolist():
            safe_relative(info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("ZIP contains a symbolic link")
            if info.filename == EMBEDDED_MANIFEST:
                continue
            descriptor = expected[info.filename]
            if info.file_size != descriptor["bytes"]:
                raise ValueError(f"ZIP entry size differs: {record['slug']}/{info.filename}")
            if deep:
                digest, count = hashlib.sha256(), 0
                with archive.open(info) as saved:
                    for block in iter(lambda: saved.read(CHUNK), b""):
                        digest.update(block)
                        count += len(block)
                if count != descriptor["bytes"] or digest.hexdigest() != descriptor["sha256"]:
                    raise ValueError(f"ZIP entry fingerprint differs: {record['slug']}/{info.filename}")
    return tree


def verify(deep=False):
    manifest = read_json(MANIFEST)
    if manifest["capture_status"] != "complete":
        raise ValueError("Source capture is still in progress")
    recorded = {r["repository"] for r in manifest["records"]}
    if recorded != set(source_repositories()) or len(recorded) != len(manifest["records"]):
        raise ValueError("Site manifest and ecosystem repository list differ")
    count = 0
    for record in manifest["records"]:
        if record["state"] == "versioned_destination":
            if record["slug"] != DESTINATION:
                raise ValueError("Unexpected versioned destination")
            continue
        if record["state"] != "source_packaged":
            raise ValueError(f"Source package awaits capture: {record['slug']}")
        with open_archive(record) as stream:
            inspect_archive(record, stream, deep=deep)
        count += 1
        print(f"Checked {record['slug']}: {record['file_count']} files", flush=True)
    print(f"Verified {count} source packages and the versioned destination" +
          (", including every saved file fingerprint." if deep else "."), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--preflight", action="store_true", help="Show source sizes without creating packages")
    actions.add_argument("--capture", action="store_true", help="Capture the selected local source editions")
    parser.add_argument("--source-root", type=Path, default=ROOT.parent, help="Directory holding source repositories")
    parser.add_argument("--deep", action="store_true", help="Also read and fingerprint every saved source file")
    args = parser.parse_args()
    try:
        if args.preflight:
            print(json.dumps(preflight(args.source_root.resolve()), indent=2))
        elif args.capture:
            capture(args.source_root.resolve())
        else:
            verify(deep=args.deep)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print(f"Source package check: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
