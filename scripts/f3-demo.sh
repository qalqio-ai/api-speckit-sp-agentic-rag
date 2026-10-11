#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
exec "${F3_PYTHON:-$project_dir/.venv/bin/python}" -B -m app.answer.demo "$@"
