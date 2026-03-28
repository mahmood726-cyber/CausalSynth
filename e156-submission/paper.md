Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

CausalSynth: Browser-Based Causal Evidence Triangulation Engine

Can cross-design evidence triangulation be quantified computationally to strengthen causal inference beyond what any single study design provides? Twelve studies spanning RCT, cohort, and Mendelian randomization designs were analyzed for the statin-cardiovascular disease relationship using three built-in clinical examples. CausalSynth, a browser-based application of 1,772 lines, implements design-grouped random-effects meta-analysis with CaMeA-style causal correction and four convergence metrics: Direction Consistency Index, Magnitude Convergence Score, Bias Diversity Score, and Causal Evidence Score. The statin example produced a pooled RR of 0.74 (95% CI 0.62-0.88) with a Causal Evidence Score of 0.48, corresponding to strong causal evidence with GRADE-style upgrade. Leave-one-design-out sensitivity analysis confirmed that removing any single design preserved directional consistency across the remaining evidence base. CausalSynth is the first interactive tool to operationalize evidence triangulation scoring across heterogeneous study designs without requiring any programming expertise. A limitation is that the convergence metrics depend on the accuracy of user-specified bias architecture classifications for each included study design.

Outside Notes

Type: methods
Primary estimand: Causal Evidence Score
App: CausalSynth v1.0
Data: Statins-CVD, smoking-lung cancer, Mediterranean diet (built-in datasets)
Code: https://github.com/mahmood726-cyber/CausalSynth
Version: 1.0
Validation: DRAFT

References

1. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
2. Higgins JPT, Thompson SG, Deeks JJ, Altman DG. Measuring inconsistency in meta-analyses. BMJ. 2003;327(7414):557-560.
3. Cochrane Handbook for Systematic Reviews of Interventions. Version 6.4. Cochrane; 2023.

AI Disclosure

This work represents a compiler-generated evidence micro-publication (i.e., a structured, pipeline-based synthesis output). AI is used as a constrained synthesis engine operating on structured inputs and predefined rules, rather than as an autonomous author. Deterministic components of the pipeline, together with versioned, reproducible evidence capsules (TruthCert), are designed to support transparent and auditable outputs. All results and text were reviewed and verified by the author, who takes full responsibility for the content. The workflow operationalises key transparency and reporting principles consistent with CONSORT-AI/SPIRIT-AI, including explicit input specification, predefined schemas, logged human-AI interaction, and reproducible outputs.
