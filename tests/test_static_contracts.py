import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = REPO_ROOT / "causal-synth.html"
HTML = HTML_PATH.read_text(encoding="utf-8")
EXPECTED_DATASETS = ["statins", "meddiet", "smoking", "hiv", "immunotherapy"]
REQUIRED_IDS = [
    "dataBody",
    "runBtn",
    "results",
    "convMetrics",
    "forestContainer",
    "reportText",
    "rCodeBlock",
]


def test_example_menu_matches_expected_dataset_catalog():
    menu_keys = re.findall(r"loadExample\('([^']+)'\)", HTML)
    assert menu_keys == EXPECTED_DATASETS

    object_match = re.search(r"const EXAMPLE_DATASETS = \{(.*?)^\};", HTML, flags=re.MULTILINE | re.DOTALL)
    assert object_match is not None

    defined_in_object = re.findall(r"^\s{2}([a-zA-Z0-9_]+):\s*\{", object_match.group(1), flags=re.MULTILINE)
    extended_later = re.findall(r"^EXAMPLE_DATASETS\.([a-zA-Z0-9_]+)\s*=\s*\{", HTML, flags=re.MULTILINE)
    defined_keys = defined_in_object + extended_later
    assert defined_keys == EXPECTED_DATASETS


def test_core_dashboard_ids_and_hooks_are_present():
    for element_id in REQUIRED_IDS:
        assert f'id="{element_id}"' in HTML, element_id

    required_hooks = [
        "function loadExample(",
        "renderTruthCert",
        "function downloadTruthCertBundle()",
        "function exportResults()",
        "function exportPDF()",
    ]
    for hook in required_hooks:
        assert hook in HTML, hook


def test_truthcert_and_report_surface_are_wired():
    required_strings = [
        "Download TruthCert JSON",
        "METHODS",
        "RESULTS",
        "DerSimonian-Laird",
        "metafor",
        "Causal Evidence Score",
    ]
    for snippet in required_strings:
        assert snippet in HTML, snippet
