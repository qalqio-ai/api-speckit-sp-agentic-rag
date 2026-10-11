# Launch guard regression verification

Command: `.venv/bin/python -m pytest -q tests/test_seda_launch.py`.
Initial stub: three behavioral failures (changed host accepted, wrong image accepted, escaped path accepted), one positive pass. Implemented guard:4/4passed. Full suite397passed/1existing warning. The separately versioned guard preserves measured wrappers. Guarded live rehearsal exit0.
