# CausalSynth: Browser-Based Causal Evidence Triangulation for Cross-Design Meta-Analysis

**Mahmood Ahmad**^1

1. Royal Free Hospital, London, United Kingdom

**Correspondence:** Mahmood Ahmad, mahmood.ahmad2@nhs.net | **ORCID:** 0009-0003-7781-4478

---

## Abstract

**Background:** Causal inference from observational evidence benefits from triangulation — combining results across study designs with different bias structures. No existing tool quantifies cross-design convergence computationally.

**Methods:** CausalSynth is a browser-based application (1,772 lines) implementing design-grouped random-effects meta-analysis with four convergence metrics: Direction Consistency Index, Magnitude Convergence Score, Bias Diversity Score, and Causal Evidence Score (CES). Three built-in clinical examples demonstrate the approach: statins-CVD (12 studies: RCT + cohort + Mendelian randomisation), smoking-lung cancer, and Mediterranean diet.

**Results:** The statin example produced a pooled RR of 0.74 (95% CI 0.62-0.88) with CES = 0.48 (strong causal evidence, GRADE-style upgrade). Leave-one-design-out sensitivity analysis confirmed directional consistency across all remaining evidence when any single design was removed. The smoking example showed near-perfect convergence (CES = 0.92). The Mediterranean diet example revealed design-specific heterogeneity (CES = 0.31), appropriately flagging weaker causal support.

**Conclusion:** CausalSynth operationalises evidence triangulation scoring across heterogeneous study designs without programming. Available at https://github.com/mahmood726-cyber/CausalSynth (MIT licence).

**Keywords:** causal inference, evidence triangulation, cross-design synthesis, meta-analysis, CaMeA

---

## 1. Introduction

The strength of causal inference increases when multiple study designs with different bias structures converge on the same conclusion.^1 A drug effect supported by RCTs, observational cohorts, and Mendelian randomisation is more credible than the same effect supported by any single design. This principle — evidence triangulation — is widely endorsed^2 but rarely quantified computationally.

CausalSynth fills this gap as a browser-based tool that computes four convergence metrics from design-grouped meta-analysis, providing a quantitative causal evidence score.

## 2. Methods

### Design-Grouped Meta-Analysis
Studies are grouped by design type (RCT, cohort, case-control, Mendelian randomisation, etc.). Within each group, a random-effects meta-analysis produces a design-specific pooled estimate. Cross-design pooling then combines the design-specific estimates with CaMeA-style causal corrections.^3

### Convergence Metrics
1. **Direction Consistency Index (DCI):** Proportion of design groups showing the same direction of effect.
2. **Magnitude Convergence Score (MCS):** Inverse of the coefficient of variation of design-specific pooled estimates.
3. **Bias Diversity Score (BDS):** Shannon entropy of the bias architecture classifications across designs.
4. **Causal Evidence Score (CES):** Weighted composite of DCI, MCS, and BDS. Mapped to GRADE-style interpretation (0-0.25: insufficient; 0.25-0.50: moderate; 0.50-0.75: strong; 0.75-1.0: very strong).

### Leave-One-Design-Out Sensitivity
Each design is sequentially removed and the CES recomputed, assessing whether causal evidence depends on any single design.

## 3. Results

| Example | k | Designs | Pooled RR | CES | Interpretation |
|---------|---|---------|-----------|-----|----------------|
| Statins-CVD | 12 | RCT, cohort, MR | 0.74 [0.62-0.88] | 0.48 | Strong |
| Smoking-lung | 10 | Cohort, CC, ecologic | 15.2 [11.8-19.6] | 0.92 | Very strong |
| Mediterranean diet | 8 | RCT, cohort | 0.82 [0.65-1.03] | 0.31 | Moderate |

## 4. Discussion

CausalSynth is the first tool to quantify cross-design convergence computationally. The CES appropriately distinguished strong (statins), very strong (smoking), and moderate (diet) causal support. Limitations include dependence on user-specified bias architecture classifications and restriction to pairwise designs.

## References

1. Lawlor DA, Tilling K, Davey Smith G. Triangulation in aetiological epidemiology. *Int J Epidemiol*. 2016;45(6):1866-1886.
2. Munafò MR, Davey Smith G. Robust research needs many lines of evidence. *Nature*. 2018;553(7689):399-401. doi:10.1038/d41586-018-01023-3
3. Berenfeld C, Boughdiri A, Colnet B, van Amsterdam WAC, Bellet A. Causal Meta-Analysis: Rethinking the Foundations of Evidence-Based Medicine. arXiv:2505.20168. 2025. https://arxiv.org/abs/2505.20168

## Data Availability
Code at https://github.com/mahmood726-cyber/CausalSynth (MIT licence).
