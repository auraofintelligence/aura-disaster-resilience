#!/usr/bin/env python3
"""Check captured public page editions, or capture the supplied addresses.

Check:   python scripts/verify_web_pages.py
Capture: python scripts/verify_web_pages.py --capture
Retry network failures: python scripts/verify_web_pages.py --retry-network-errors

Only the unique public_urls in data/ecosystem.json are requested. Capture uses
ordinary HTTPS requests and redirects, with no cookies, authentication, browser
execution or crawl. Response-body bytes remain exactly as received.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "sources" / "web-pages"
MANIFEST = ROOT / "data" / "web-page-manifest.json"
MAX_BODY = 32 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + ".pending")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)


def supplied_urls():
    records = read_json(ROOT / "data" / "ecosystem.json")
    return list(dict.fromkeys(url for item in records for url in item.get("public_urls", [])))


def directory_name(number, url):
    parsed = urlsplit(url)
    label = parsed.path.strip("/").replace("/", "-") or parsed.hostname
    label = re.sub(r"[^A-Za-z0-9._-]+", "-", label)[:100]
    return f"{number:02d}-{label}"


def capture_one(number, url):
    record = {"id": f"WEB-{number:02d}", "url": url,
              "request_started_utc": now(), "final_url": None,
              "http_status": None, "status": "network_error"}
    request = Request(url, headers={
        "User-Agent": "AuraDisasterResilienceSourceCapture/1.0",
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
        "Accept-Encoding": "identity",
    })
    response = None
    try:
        try:
            response = build_opener().open(request, timeout=25)
        except HTTPError as error:
            # HTTPError is a real HTTP response. Keep its status and body, with
            # the same byte-preservation rule used for a successful response.
            response = error
        with response:
            record["final_url"] = response.geturl()
            record["http_status"] = response.status
            record["http_reason"] = str(response.reason)
            record["server_date"] = response.headers.get("Date")
            record["content_type"] = response.headers.get("Content-Type")
            record["content_encoding"] = response.headers.get("Content-Encoding")
            record["declared_content_length"] = response.headers.get("Content-Length")
            record["last_modified"] = response.headers.get("Last-Modified")
            record["etag"] = response.headers.get("ETag")
            body = response.read(MAX_BODY + 1)
            if len(body) > MAX_BODY:
                record["status"] = "response_too_large"
                record["reason"] = "Response exceeded the 32 MiB page-edition limit; no partial page is presented as complete."
            else:
                directory = WEB_ROOT / directory_name(number, url)
                directory.mkdir(parents=True, exist_ok=True)
                content_type = (record["content_type"] or "").lower()
                suffix = ".html" if "html" in content_type else ".bin"
                if record["content_encoding"] and record["content_encoding"].lower() != "identity":
                    suffix += ".encoded"
                body_path = directory / ("response" + suffix)
                body_path.write_bytes(body)
                record["bytes"] = len(body)
                record["sha256"] = hashlib.sha256(body).hexdigest()
                if 200 <= response.status < 300:
                    record["status"] = "captured"
                    record["public_path"] = body_path.relative_to(ROOT).as_posix()
                else:
                    record["status"] = "http_error"
                    record["reason"] = f"The server returned HTTP {response.status} {response.reason}."
                    record["error_body_path"] = body_path.relative_to(ROOT).as_posix()
    except (URLError, TimeoutError, OSError) as error:
        record["status"] = "network_error"
        # Keep the error class and public host, without proxy settings, local
        # workstation paths, credentials or values from the environment.
        reason = getattr(error, "reason", error)
        record["reason"] = f"{type(reason).__name__} while requesting the supplied public address."
        if isinstance(reason, OSError) and reason.errno is not None:
            record["network_error_code"] = reason.errno
    record["captured_utc"] = now()
    record["edition"] = "Exact received HTTP response-body bytes; page edition, with source/assets held separately."
    return record


def make_index(manifest):
    lines = [
        "# Captured public page editions", "",
        "These page editions preserve the HTTP response bodies received from the supplied public addresses. Each record gives its capture time, server date, final address, response type, status, size and SHA-256 content fingerprint. A matching fingerprint confirms the saved bytes.", "",
        "The website source packages in [the site library](../sites/README.md) carry the related code, documents and assets. These HTML captures add a dated view of the public addresses, including external canonical sites. Hosting configuration, external databases and any separate WordPress export have their own handover when supplied.", "",
        "Capture requested only the listed addresses and followed ordinary redirects. It used no cookies or authentication, ran no remote JavaScript and performed no wider crawl. A refusal or network failure is recorded as received.", "",
        f"Capture completed: {manifest['capture_completed_utc']}.", "",
        "| Public address | HTTP result | Saved edition | Bytes |",
        "| --- | --- | --- | --- |",
    ]
    for record in manifest["records"]:
        public_path = record.get("public_path") or record.get("error_body_path")
        if public_path:
            relative = Path(public_path).relative_to("sources/web-pages").as_posix()
            saved = f"[Response bytes]({relative})"
        else:
            saved = record.get("reason", "No response body received").replace("|", "\\|")
        result = str(record["http_status"]) if record["http_status"] is not None else record["status"]
        lines.append(f"| [{record['url']}]({record['url']}) | {result} | {saved} | {record.get('bytes', 0):,} |")
    lines.extend(["", "[Complete capture manifest](../../data/web-page-manifest.json)", "",
                  "Check the saved bytes from the repository top level:", "", "```text",
                  "python scripts/verify_web_pages.py", "```", ""])
    (WEB_ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def capture():
    if MANIFEST.exists() or (WEB_ROOT.exists() and any(WEB_ROOT.iterdir())):
        raise ValueError("A public page capture already exists. Preserve its recorded edition before creating another.")
    WEB_ROOT.mkdir(parents=True, exist_ok=True)
    urls = supplied_urls()
    manifest = {"schema_version": 1, "capture_status": "in_progress",
                "capture_started_utc": now(), "scope": "Only unique public_urls supplied in data/ecosystem.json.",
                "method": "Ordinary HTTPS GET, redirects enabled, Accept-Encoding identity, no cookies/authentication/browser execution/crawl. Exact received body bytes are saved without rewriting.",
                "response_header_scope": "Date, Content-Type, Content-Encoding, Content-Length, Last-Modified and ETag. Session-cookie headers are not retained.",
                "edition_boundary": "A dated response-body edition. Related repository source and assets are saved separately; external databases, hosting configuration and a separate WordPress installation remain distinct handovers.",
                "records": []}
    write_json(MANIFEST, manifest)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(capture_one, number, url) for number, url in enumerate(urls, 1)]
        for future in as_completed(futures):
            record = future.result()
            manifest["records"].append(record)
            manifest["records"].sort(key=lambda item: item["id"])
            write_json(MANIFEST, manifest)
            print(f"{record['id']}: {record['status']}; HTTP {record['http_status']}; {record['url']}", flush=True)
    return finish_capture(manifest)


def finish_capture(manifest):
    manifest["capture_completed_utc"] = now()
    manifest["capture_status"] = "complete"
    manifest["summary"] = {
        "supplied_unique_urls": len(supplied_urls()), "address_records": len(manifest["records"]),
        "attempts_recorded": sum(1 + len(record.get("previous_attempts", [])) for record in manifest["records"]),
        "successful_page_captures": sum(record["status"] == "captured" for record in manifest["records"]),
        "http_error_responses": sum(record["status"] == "http_error" for record in manifest["records"]),
        "network_or_size_failures": sum(record["status"] in {"network_error", "response_too_large"} for record in manifest["records"]),
        "saved_response_bytes": sum(record.get("bytes", 0) for record in manifest["records"]),
    }
    make_index(manifest)
    write_json(MANIFEST, manifest)
    return verify()


def retry_network_errors():
    manifest = read_json(MANIFEST)
    targets = [record for record in manifest["records"] if record["status"] == "network_error"]
    manifest["capture_status"] = "in_progress"
    write_json(MANIFEST, manifest)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(capture_one, int(record["id"].split("-")[1]), record["url"]): record
                   for record in targets}
        for future in as_completed(futures):
            earlier = futures[future]
            record = future.result()
            previous = list(earlier.get("previous_attempts", []))
            previous.append({key: value for key, value in earlier.items() if key != "previous_attempts"})
            record["previous_attempts"] = previous
            manifest["records"] = [record if item["id"] == record["id"] else item for item in manifest["records"]]
            write_json(MANIFEST, manifest)
            print(f"{record['id']}: {record['status']}; HTTP {record['http_status']}; {record['url']}", flush=True)
    return finish_capture(manifest)


def verify():
    manifest = read_json(MANIFEST)
    if manifest["capture_status"] != "complete":
        raise ValueError("Page capture is still in progress")
    records = manifest["records"]
    if len(records) != len(supplied_urls()) or {record["url"] for record in records} != set(supplied_urls()):
        raise ValueError("Capture attempts and supplied public addresses differ")
    count = 0
    for record in records:
        public_path = record.get("public_path") or record.get("error_body_path")
        if not public_path:
            if record["status"] not in {"network_error", "response_too_large"}:
                raise ValueError("A response record has neither saved bytes nor a recorded failure")
            continue
        relative = PurePosixPath(public_path)
        if relative.is_absolute() or ".." in relative.parts or "\\" in public_path or ":" in public_path:
            raise ValueError("Saved page path must be a public relative path")
        path = ROOT.joinpath(*relative.parts)
        if path.is_symlink() or not path.resolve().is_relative_to(WEB_ROOT.resolve()):
            raise ValueError("Saved page path leaves the public page folder")
        body = path.read_bytes()
        if len(body) != record["bytes"] or hashlib.sha256(body).hexdigest() != record["sha256"]:
            raise ValueError(f"Saved response fingerprint differs: {record['id']}")
        count += 1
    print(f"Checked {len(records)} supplied addresses and all {count} saved response bodies.")
    print(json.dumps(manifest["summary"], indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--capture", action="store_true", help="Capture the supplied public addresses into a new edition")
    mode.add_argument("--retry-network-errors", action="store_true", help="Retry network failures while retaining the earlier attempt records")
    args = parser.parse_args()
    try:
        if args.capture:
            return capture()
        return retry_network_errors() if args.retry_network_errors else verify()
    except (OSError, ValueError) as error:
        print(f"Public page check: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
