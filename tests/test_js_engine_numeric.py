"""Headless numerical regression tests for the CausalSynth JS engine.

The default pytest suite only greps for strings/IDs in causal-synth.html; the
40 numeric checks live in the Chrome-gated Selenium suite that conftest.py
excludes. This module closes that gap: it drives the pure statistical core
(dlMeta, remlMeta, computeEggerTest) via a Node harness and INDEPENDENTLY
re-derives the expected values in pure-Python (stdlib math only, so it runs in
CI without numpy/scipy/Chrome). If `node` is unavailable the test skips.

It also serves as the regression guard for the renderPredictionIntervals()
duplicate-declaration fix (see test_no_duplicate_toplevel_js_function_decls).
"""
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS = REPO_ROOT / "tests" / "js_engine_harness.js"
HTML_PATH = REPO_ROOT / "causal-synth.html"

TOL = 1e-6


def _norm_ppf(p):
    """Acklam's inverse-normal CDF — matches the app's normalQuantile."""
    a = [-3.969683028665376e1, 2.209460984245205e2, -2.759285104469687e2,
         1.383577518672690e2, -3.066479806614716e1, 2.506628277459239e0]
    b = [-5.447609879822406e1, 1.615858368580409e2, -1.556989798598866e2,
         6.680131188771972e1, -1.328068155288572e1]
    c = [-7.784894002430293e-3, -3.223964580411365e-1, -2.400758277161838e0,
         -2.549732539343734e0, 4.374664141464968e0, 2.938163982698783e0]
    d = [7.784695709041462e-3, 3.224671290700398e-1, 2.445134137142996e0,
         3.754408661907416e0]
    pL = 0.02425
    if p < pL:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p <= 1 - pL:
        q = p - 0.5
        r = q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
            ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


def _dl_reference(yi, sei):
    """Independent DerSimonian-Laird reimplementation (stdlib only)."""
    k = len(yi)
    vi = [s * s for s in sei]
    wi = [1.0 / v for v in vi]
    sumW = sum(wi)
    theta_fe = sum(w * y for w, y in zip(wi, yi)) / sumW
    Q = sum(w * (y - theta_fe) ** 2 for w, y in zip(wi, yi))
    C = sumW - sum(w * w for w in wi) / sumW
    tau2 = max(0.0, (Q - (k - 1)) / C)
    wi2 = [1.0 / (v + tau2) for v in vi]
    sumW2 = sum(wi2)
    theta = sum(w * y for w, y in zip(wi2, yi)) / sumW2
    se = math.sqrt(1.0 / sumW2)
    I2 = max(0.0, (Q - (k - 1)) / Q * 100) if Q > (k - 1) else 0.0
    return {"theta": theta, "se": se, "tau2": tau2, "Q": Q, "I2": I2}


@pytest.fixture(scope="module")
def engine():
    if shutil.which("node") is None:
        pytest.skip("node not available; JS engine numeric checks require Node")
    proc = subprocess.run(
        ["node", str(HARNESS)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, f"harness failed:\n{proc.stderr}"
    return json.loads(proc.stdout)


def test_dl_meta_matches_independent_reference(engine):
    yi = engine["inputs"]["yi"]
    sei = engine["inputs"]["sei"]
    ref = _dl_reference(yi, sei)
    dl = engine["dl"]
    # Sanity: this fixture must exercise the heterogeneity branch.
    assert ref["tau2"] > 0
    assert dl["Q"] > len(yi) - 1
    for key in ("theta", "se", "tau2", "Q", "I2"):
        assert abs(dl[key] - ref[key]) < TOL, f"{key}: {dl[key]} vs {ref[key]}"
    z95 = _norm_ppf(0.975)
    assert abs(dl["lower"] - (ref["theta"] - z95 * ref["se"])) < TOL
    assert abs(dl["upper"] - (ref["theta"] + z95 * ref["se"])) < TOL


def test_dl_meta_k1_edge_case(engine):
    dl1 = engine["dl_k1"]
    assert dl1["k"] == 1
    assert abs(dl1["theta"] - 0.42) < TOL
    assert abs(dl1["se"] - 0.13) < TOL
    assert dl1["tau2"] == 0
    assert dl1["I2"] == 0


def test_dl_meta_empty_returns_null(engine):
    assert engine["dl_empty"] is None


def test_reml_solution_satisfies_reml_score_equation(engine):
    """At the REML MLE, the score -0.5*tr(P) + 0.5*y'PPy must be ~0.

    This validates the returned tau2 as a genuine REML fixed point,
    independent of the JS Fisher-scoring iteration internals.
    """
    yi = engine["inputs"]["yi"]
    sei = engine["inputs"]["sei"]
    reml = engine["reml"]
    tau2 = reml["tau2"]
    assert reml["converged"] is True
    assert tau2 > 0  # fixture is heterogeneous
    v = [s * s for s in sei]
    w = [1.0 / (vi + tau2) for vi in v]
    sw = sum(w)
    mu = sum(wi * yi_ for wi, yi_ in zip(w, yi)) / sw
    traceP = sum(wi - wi * wi / sw for wi in w)
    yPPy = sum(wi * wi * (yi_ - mu) ** 2 for wi, yi_ in zip(w, yi))
    score = -0.5 * traceP + 0.5 * yPPy
    assert abs(score) < 1e-6, f"REML score not ~0 at returned tau2: {score}"
    # theta and se must be the RE-weighted mean / sqrt(1/sumW) at that tau2.
    assert abs(reml["theta"] - mu) < TOL
    assert abs(reml["se"] - math.sqrt(1.0 / sw)) < TOL


def test_egger_regression_matches_independent_ols(engine):
    """Egger = OLS of (yi/sei) on (1/sei); verify intercept/slope/se/t."""
    yi = engine["inputs"]["eyi"]
    sei = engine["inputs"]["esei"]
    n = len(yi)
    x = [1.0 / s for s in sei]
    z = [y / s for y, s in zip(yi, sei)]
    xbar = sum(x) / n
    zbar = sum(z) / n
    Sxx = sum((xi - xbar) ** 2 for xi in x)
    Sxy = sum((xi - xbar) * (zi - zbar) for xi, zi in zip(x, z))
    slope = Sxy / Sxx
    intercept = zbar - slope * xbar
    rss = sum((zi - (intercept + slope * xi)) ** 2 for xi, zi in zip(x, z))
    rse = math.sqrt(rss / (n - 2))
    se_int = rse * math.sqrt(1.0 / n + xbar ** 2 / Sxx)
    tstat = intercept / se_int

    eg = engine["egger"]
    assert eg["k"] == n
    assert eg["df"] == n - 2
    assert abs(eg["intercept"] - intercept) < TOL
    assert abs(eg["slope"] - slope) < TOL
    assert abs(eg["seIntercept"] - se_int) < TOL
    assert abs(eg["tStat"] - tstat) < TOL
    # p-value uses the app's t-CDF approximation; bound it and check the flag.
    assert 0.0 < eg["pValue"] < 1.0
    assert eg["significant"] == (eg["pValue"] < 0.1)


def test_egger_returns_null_below_ten_studies(engine):
    assert engine["egger_too_few"] is None


def test_no_duplicate_toplevel_js_function_decls():
    """Regression guard for the renderPredictionIntervals() collision (F1).

    Two identical top-level `function NAME()` declarations let the later one
    silently win at every call site (hoisting), which injected a literal
    'undefined' into the Sensitivity panel. Assert no top-level function name
    is declared more than once.
    """
    html = HTML_PATH.read_text(encoding="utf-8")
    names = re.findall(r"^function ([A-Za-z_$][\w$]*)\s*\(", html, flags=re.MULTILINE)
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert not dupes, f"duplicate top-level function declarations: {dupes}"
    # And the sensitivity-panel PI card must call the uniquely-named function.
    assert "renderOverallPredictionInterval()" in html
