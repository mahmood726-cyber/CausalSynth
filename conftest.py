"""Pytest config for CausalSynth.

The browser-heavy Selenium suites in this repo require Chrome/chromedriver +
local HTTP server support. By default, pytest collection skips those suites
and leaves lightweight smoke tests enabled — set `RUN_BROWSER_TESTS=1` to
include the browser checks.

Rationale: these Selenium files also reassign `sys.stdout`/`sys.stderr` at
module level, which breaks pytest's terminal writer at session-finish
(ValueError: I/O operation on closed file). Excluding them from collection
avoids that teardown crash entirely and keeps `pytest` runnable in CI/triage
contexts without a browser while still preserving a default smoke contract.

To run browser tests manually:
    $Env:RUN_BROWSER_TESTS = "1"
    python -m pytest tests/test_causalsynth.py -v
"""
import os

if not os.environ.get("RUN_BROWSER_TESTS"):
    collect_ignore_glob = [
        "test_causal_synth.py",
        "test_causal_synth_selenium.py",
        "test_phase2.py",
        "test_phase3.py",
        "tests/test_causalsynth.py",
    ]
