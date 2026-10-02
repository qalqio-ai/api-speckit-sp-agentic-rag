#!/usr/bin/env python3
"""Check a running API using only the Python standard library."""

import argparse
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, build_opener


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", nargs="?", default="http://127.0.0.1:8000")
    base_url = parser.parse_args().base_url.rstrip("/")
    opener = build_opener(ProxyHandler({}))

    def request(path):
        try:
            response = opener.open(base_url + path, timeout=2)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.headers, json.load(response)

    deadline = time.monotonic() + 60
    while True:
        try:
            status, _, body = request("/health")
            if status == 200 and body == {"status": "ok"}:
                break
        except (URLError, TimeoutError, OSError, ValueError):
            pass
        if time.monotonic() >= deadline:
            raise SystemExit(f"API at {base_url} did not become healthy within 60 seconds")
        time.sleep(1)
    print("PASS /health: HTTP 200")

    checks = [
        (
            "/v1/use-cases/sample-use-case/sources",
            200,
            {
                "use_case_id": "sample-use-case",
                "sources": [{"source_id": "sample-source-1", "title": "Sample source"}],
            },
        ),
        (
            "/v1/use-cases/missing-use-case/sources",
            404,
            {"detail": {"code": "unknown_use_case"}},
        ),
    ]
    for path, expected_status, expected_body in checks:
        try:
            status, headers, body = request(path)
        except (URLError, TimeoutError, OSError, ValueError) as error:
            raise SystemExit(f"{path}: request failed: {error}") from error
        if status != expected_status or body != expected_body:
            raise SystemExit(
                f"{path}: expected {expected_status} {expected_body}, got {status} {body}"
            )
        if headers.get_content_type() != "application/json":
            raise SystemExit(f"{path}: expected JSON content type")
        print(f"PASS {path}: HTTP {status}")


if __name__ == "__main__":
    main()
