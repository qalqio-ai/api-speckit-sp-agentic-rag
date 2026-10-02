#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
python_bin="${CI_LOCAL_PYTHON:-$repo_root/.venv/bin/python}"

if [[ ! -x "$python_bin" ]]; then
    printf 'Create .venv and install the test extra: python3 -m venv .venv && .venv/bin/python -m pip install -e ".[test]"\n' >&2
    exit 1
fi

printf '\n[1/5] Ruff\n'
"$python_bin" -m ruff check .
printf '\n[2/5] Python tests\n'
"$python_bin" -m pytest -v

command -v docker >/dev/null
docker compose version >/dev/null
docker info >/dev/null

temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/ci-local.XXXXXX")"
project_name="ci-local-$(date +%s)-$$"
compose_file="$temp_dir/compose.yaml"
compose_attempted=false
export CI_LOCAL_CONTEXT="$repo_root"

compose() {
    docker compose --project-name "$project_name" --file "$compose_file" "$@"
}

cleanup() {
    local status=$?
    trap - EXIT INT TERM
    if [[ "$compose_attempted" == true ]]; then
        if [[ "$status" -ne 0 ]]; then
            compose logs --no-color api >&2 || true
        fi
        printf '\n[5/5] Remove test container and network (%s)\n' "$project_name"
        if ! compose down --timeout 10 --remove-orphans; then
            printf 'Container cleanup failed for project %s.\n' "$project_name" >&2
            [[ "$status" -ne 0 ]] || status=1
        fi
    fi
    rm -f "$compose_file"
    rmdir "$temp_dir"
    exit "$status"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Keep the container setup inside this single script; it is not a deployment stack.
cat > "$compose_file" <<'YAML'
services:
  api:
    build:
      context: ${CI_LOCAL_CONTEXT}
      dockerfile_inline: |
        FROM python:3.12-slim
        ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
        WORKDIR /app
        COPY pyproject.toml README.md ./
        COPY app ./app
        RUN python -m pip install --no-cache-dir .
        CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    init: true
    ports:
      - target: 8000
        host_ip: 127.0.0.1
        protocol: tcp
YAML

printf '\n[3/5] Build and start API (%s)\n' "$project_name"
compose_attempted=true
compose build api
compose up --detach --no-build api
address="$(compose port api 8000)"

printf '\n[4/5] Wait for /health and check API at http://%s\n' "$address"
"$python_bin" - "http://$address" <<'PY'
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, build_opener

base_url = sys.argv[1]
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
        raise SystemExit("API did not become healthy within 60 seconds")
    time.sleep(1)

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
    status, headers, body = request(path)
    if status != expected_status or body != expected_body:
        raise SystemExit(f"{path}: expected {expected_status} {expected_body}, got {status} {body}")
    if headers.get_content_type() != "application/json":
        raise SystemExit(f"{path}: expected JSON content type")
    print(f"PASS {path}: HTTP {status}")
PY

printf '\nAll local CI checks passed.\n'
