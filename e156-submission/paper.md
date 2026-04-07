Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

CausalSynth: Browser-Based Causal Evidence Triangulation Engine

Can cross-design evidence triangulation be quantified computationally to strengthen causal inference beyond what any single study design provides? Five clinical examples spanning RCT, cohort, case-control, Mendelian randomization, and ecological designs were analyzed, including statins-CVD, smoking-lung cancer, and Mediterranean diet-mortality. CausalSynth, a browser-based application of 3,045 lines, implements design-grouped random-effects meta-analysis with CaMeA-style causal correction, bias direction modeling, and four convergence metrics: Direction Consistency Index, Magnitude Convergence Score, Bias Diversity Score, and Causal Evidence Score, with TruthCert SHA-256 provenance. The statin example produced a pooled RR of 0.74 (95% CI 0.62-0.88) with a Causal Evidence Score of 0.48, corresponding to strong causal evidence with GRADE-style certainty mapping. Leave-one-design-out sensitivity analysis confirmed directional consistency, and the bias direction model identified expected bias patterns per Phillips and Smith 2020. CausalSynth is the first interactive tool to operationalize evidence triangulation with causal correction and cryptographic audit trails. A limitation is that convergence metrics depend on user-specified bias classifications for each study design.

Outside Notes

Type: methods
Primary estimand: Causal Evidence Score
App: CausalSynth v2.0
Data: Statins-CVD, smoking-lung cancer, Mediterranean diet, alcohol-liver, exercise-depression (built-in)
Code: https://github.com/mahmood726-cyber/CausalSynth
Version: 2.0
Validation: PASS (60/60 tests, WebR, 3-round review clean)

References

1. Lawlor DA, Tilling K, Davey Smith G. Triangulation in aetiological epidemiology. Int J Epidemiol. 2016;45(6):1866-1886.
2. Munafo MR, Davey Smith G. Robust research needs many lines of evidence. Nature. 2018;553:399-401.
3. Greenland S. Quantitative methods in the review of epidemiologic literature. Epidemiol Rev. 1987;9:1-30.
