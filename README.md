# CausalSynth

[![ci](https://github.com/mahmood726-cyber/CausalSynth/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/mahmood726-cyber/CausalSynth/actions/workflows/ci.yml) [![codeql](https://github.com/mahmood726-cyber/CausalSynth/actions/workflows/codeql.yml/badge.svg?branch=master)](https://github.com/mahmood726-cyber/CausalSynth/actions/workflows/codeql.yml) [![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

Browser-based causal evidence triangulation engine: pools studies grouped by design type and computes a convergence score across heterogeneous designs (RCTs, cohorts, case-control, Mendelian randomization).

**Live dashboard:** <https://mahmood726-cyber.github.io/causalsynth/>

## What it does

- Design-grouped random-effects meta-analysis with CaMeA-style causal correction (see Berenfeld et al. 2025 arXiv:2505.20168).
- Four convergence metrics:
  - **DCI** Direction Consistency Index
  - **MCS** Magnitude Convergence Score
  - **BDS** Bias Diversity Score (Manhattan distance across 5 RoB domains per design)
  - **CES** Causal Evidence Score (composite)
- GRADE-style certainty mapping with upgrade for high diversity + full direction agreement.
- Leave-one-design-out sensitivity, RoB-weighted pooling, funnel plot + Egger / trim-and-fill.
- Three built-in datasets: statins-CVD, smoking-lung cancer, Mediterranean diet.

## Run

Open `causal-synth.html` (or `index.html`) in any modern browser. No build step, fully offline.

For local development:

```bash
python -m http.server 8000
# then open http://localhost:8000/
```

## Test

```bash
python -m pytest -q                                  # smoke + unit tests
python selenium_causal_synth_legacy.py               # full Selenium E2E (requires Chrome)
```

## Repo layout

| Path | Purpose |
|---|---|
| `causal-synth.html` | the dashboard (main artifact, ~1800 lines) |
| `index.html` | landing page |
| `tests/`, `conftest.py` | unit + Selenium tests |
| `paper/manuscript.md`, `paper/manuscript_f1000.md` | submission manuscripts |
| `PLAN.md` | architecture + phasing notes |
| `e156-submission/` | E156 micro-paper bundle |
| `E156-PROTOCOL.md` | project metadata (E156 entry #17) |

## Key references

- CaMeA framework: Berenfeld C, Boughdiri A, Colnet B, van Amsterdam WAC, Bellet A. *Causal Meta-Analysis: Rethinking the Foundations of Evidence-Based Medicine.* arXiv:2505.20168 (2025).
- Triangulation framework: Lawlor DA, Tilling K, Davey Smith G. *Triangulation in aetiological epidemiology.* Int J Epidemiol 2016;45(6):1866-1886. `doi:10.1093/ije/dyw314`
- Empirical bias priors: Welton NJ et al. *Models for potentially biased evidence in meta-analysis using empirically based priors.* J R Stat Soc Ser A 2009;172(1):119-136.

## License

See `LICENSE` (MIT).
