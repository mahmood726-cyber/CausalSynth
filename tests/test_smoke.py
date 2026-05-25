from pathlib import Path

REQUIRED_FILES = (
    'causal-synth.html',
    'index.html',
    'favicon.svg',
)

REQUIRED_HTML_SNIPPETS = (
    'id="dataBody"',
    'id="runBtn"',
    'id="results"',
    'function loadExample(',
    'renderTruthCert',
    'downloadTruthCertBundle',
)


def test_repository_smoke_contract():
    root = Path(__file__).resolve().parents[1]

    for name in REQUIRED_FILES:
        assert (root / name).exists(), name

    html = (root / 'causal-synth.html').read_text(encoding='utf-8')
    for snippet in REQUIRED_HTML_SNIPPETS:
        assert snippet in html, snippet
