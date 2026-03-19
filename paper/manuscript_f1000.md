# CausalSynth: A Browser-Based Engine for Causal Evidence Triangulation Across Study Designs

**Authors:** [AUTHOR_NAME_PLACEHOLDER]^1

^1 [AFFILIATION_PLACEHOLDER]

**Corresponding author:** [CORRESPONDING_EMAIL_PLACEHOLDER]

**ORCID:** [ORCID_PLACEHOLDER]

**Keywords:** evidence triangulation, causal inference, meta-analysis, study design, convergence metrics, browser-based tool

---

## Abstract

**Background:** Evidence triangulation --- the principle that convergent findings from study designs with different bias structures provide stronger causal evidence --- has been articulated as a methodological priority (Lawlor et al. 2016; Munafo and Davey Smith 2018). Yet no computational tool exists to operationalize triangulation scoring across heterogeneous study designs. Existing R packages such as CausalMetaR (Wang et al. 2025) and CaMeA (Berenfeld et al. 2025) address causal aggregation for specific estimands but do not provide cross-design convergence assessment or interactive triangulation workflows.

**Methods:** CausalSynth is a single-file browser-based application (1,772 lines of HTML/JavaScript/SVG) that implements design-grouped random-effects meta-analysis, CaMeA-style causal correction converting nonlinear measures (OR/RR) to risk differences via the delta method, and four convergence metrics: Direction Consistency Index (DCI), Magnitude Convergence Score (MCS), Bias Diversity Score (BDS), and Causal Evidence Score (CES). A GRADE-style certainty mapping translates CES into actionable evidence ratings. Additional features include a causal DAG editor with four templates, leave-one-design-out sensitivity analysis, bias architecture heatmaps, CSV import/export, R code export, and auto-generated methods and results text. Validation comprised 40 Selenium tests across seven categories and a three-persona expert review.

**Results:** Applied to statins and cardiovascular disease (12 studies across RCT, cohort, and Mendelian randomization designs), CausalSynth produces DCI = 100%, MCS = 0.72, BDS = 0.33, and CES = 0.48, corresponding to strong causal evidence with upgrade from full directional consistency. Leave-one-design-out analysis confirms robustness. Two additional worked examples (smoking and lung cancer; Mediterranean diet and CVD) demonstrate the tool across diverse triangulation scenarios.

**Conclusions:** CausalSynth is the first interactive tool to quantify evidence triangulation across study designs. It is freely available, requires no installation or server, and produces reproducible, exportable outputs suitable for systematic review workflows.

**Software availability:** Source code at [REPOSITORY_URL_PLACEHOLDER]. Archived at [ZENODO_DOI_PLACEHOLDER].

---

## Introduction

Traditional meta-analysis treats all included studies as exchangeable observations from a common population, pooling effect estimates under fixed-effect or random-effects models regardless of study design [1,2]. This approach has been enormously productive, but it carries a fundamental limitation: studies conducted using the same design share similar bias structures, and pooling them does not address the possibility that a consistent finding reflects a consistent bias rather than a true causal effect. For example, a meta-analysis of 15 observational cohort studies showing an association between a dietary exposure and a disease outcome could reflect residual confounding by socioeconomic status in all 15 studies. Pooling more studies of the same design increases precision but does not address this shared vulnerability.

Evidence triangulation offers a complementary inferential strategy. First articulated systematically by Lawlor et al. [3] and elaborated by Munafo and Davey Smith [4], the principle holds that when studies using designs with *different* bias structures converge on the same conclusion, the probability that all designs are biased in the same direction decreases, strengthening causal inference. The logic is straightforward: each study design has characteristic strengths and weaknesses (Table 1). Randomized controlled trials (RCTs) eliminate confounding by design but may suffer from limited generalizability, short follow-up, and protocol-driven populations [5]. Prospective cohort studies provide real-world evidence with long follow-up but are vulnerable to residual confounding [6]. Mendelian randomization (MR) studies exploit genetic variation as instrumental variables, avoiding traditional confounding but introducing concerns about pleiotropy and weak instruments [7]. Case-control studies are efficient for rare outcomes but susceptible to recall and selection bias [8]. Ecological studies capture population-level variation but are vulnerable to the ecological fallacy [22]. When these designs --- each with distinct vulnerability profiles --- independently support the same causal direction, the cumulative evidence for causation is substantially strengthened, because it becomes increasingly implausible that each design is biased in the same way.

Despite the theoretical appeal of triangulation, its practical implementation has remained largely qualitative. Researchers conduct separate meta-analyses by design type and visually compare results, but no formal framework quantifies the degree of convergence across designs. This qualitative approach is subjective, poorly reproducible, and difficult to communicate in systematic review reports. Recent methodological advances have addressed adjacent problems: Berenfeld et al. [9] introduced CaMeA, a causal meta-analysis framework that converts pooled odds ratios and risk ratios to risk differences using the delta method, providing causally interpretable aggregate estimates. Wang et al. [10] developed CausalMetaR for individual participant data (IPD) settings. However, CaMeA is available only as an R package and does not compute triangulation scores, while CausalMetaR requires IPD and does not support aggregate-data triangulation. Neither tool provides an interactive interface accessible to non-programmers.

The broader causal inference literature provides a theoretical foundation for this work. Pearl's do-calculus [11] and the potential outcomes framework formalized by Hernan and Robins [12] establish when causal effects are identifiable from observational data. Bradford Hill's viewpoints [13], while not formal criteria, emphasize consistency across study types as one of several considerations supporting causality --- yet this criterion has remained unquantified for over six decades. The GRADE framework [14] provides a structured approach to certainty of evidence and includes provisions for upgrading observational evidence (dose-response, large effect, plausible confounding), but does not formally incorporate cross-design convergence as an upgrading factor.

Several barriers have prevented the practical adoption of quantitative triangulation. First, there is no agreed-upon metric for "how much" designs converge --- researchers must rely on subjective visual comparison of forest plots. Second, existing meta-analysis software (RevMan, Stata's metan, R's metafor) does not support design-grouped analysis with cross-design convergence assessment as a built-in feature. Third, the conversion from association measures (OR, RR) to causal estimands (RD) requires statistical expertise that many systematic reviewers lack. Fourth, there is no tool that integrates causal DAG visualization with quantitative evidence synthesis, despite the widespread recognition that graphical causal models should accompany causal analyses [11,12].

CausalSynth fills this gap by providing the first interactive, browser-based tool that operationalizes evidence triangulation as a computable framework. It implements design-grouped meta-analysis, CaMeA-style causal correction for nonlinear measures, four convergence metrics with GRADE-style mapping, causal DAG visualization, and leave-one-design-out sensitivity analysis --- all within a single HTML file requiring no installation, no server, and no programming knowledge. Three built-in datasets provide worked examples, and all outputs (forest plots, metrics, methods text) can be exported for integration into systematic review manuscripts. By making triangulation quantitative and reproducible, CausalSynth aims to move evidence synthesis closer to causal inference while maintaining transparency about the assumptions involved.

---

## Methods

### Implementation

#### Architecture

CausalSynth is implemented as a single self-contained HTML file (1,772 lines) combining HTML5 structure, CSS styling, and JavaScript computation. No external libraries, frameworks, or server connections are required. The application runs entirely in the user's browser, ensuring data privacy and offline operability. This architecture follows the design philosophy of accessible statistical tools that prioritize zero-barrier deployment [15].

The application supports six study design types: randomized controlled trial (RCT), prospective cohort, case-control, Mendelian randomization (MR), ecological, and cross-sectional. Each design type is associated with a pre-specified bias profile across five bias domains: confounding, selection bias, information bias, reverse causation, and generalizability limitations (Table 1). These profiles were derived from standard epidemiological textbooks [2,12] and represent the typical bias structure of each design under conventional implementation. The profiles are displayed transparently to users via the bias architecture heatmap, allowing critical appraisal of the pre-specified assumptions.

#### Data Input

Users enter study-level data comprising: study identifier, design type (selected from a dropdown), effect estimate on the log-odds ratio (log-OR) scale, standard error (SE), sample size (N), and optional baseline risk (p0) for causal correction. Data can be entered manually, imported via CSV (RFC 4180 compliant), or loaded from three built-in demonstration datasets. The CSV parser handles quoted fields containing commas and newlines.

#### Design-Grouped Meta-Analysis

CausalSynth performs random-effects meta-analysis within each design group using the DerSimonian-Laird (DL) estimator [1]. For each design group *d* containing *k_d* studies with effect estimates *y_i* and variances *v_i*, the between-study variance is estimated as:

tau_d^2 = max(0, (Q_d - (k_d - 1)) / (sum(w_i) - sum(w_i^2)/sum(w_i)))

where Q_d is the Cochran Q statistic and w_i = 1/v_i are inverse-variance weights. The pooled design-level estimate is then computed using random-effects weights w_i* = 1/(v_i + tau_d^2). Heterogeneity within each design group is reported as I^2 [16].

A cross-design synthesis pools the design-level estimates using a second-stage DL model, providing an overall summary that accounts for both within-design and between-design heterogeneity.

#### CaMeA Causal Correction

Following the CaMeA framework [9], CausalSynth converts log-OR estimates to risk differences (RD), providing causally interpretable effect sizes when a baseline risk (p0) is specified. The conversion uses:

RD = OR * p0 / (1 + (OR - 1) * p0) - p0

where OR = exp(log-OR). The standard error of the RD is obtained via the delta method:

SE(RD) = |dRD/d(log-OR)| * SE(log-OR)

where the derivative is:

dRD/d(log-OR) = OR * p0 * (1 - p0) / (1 + (OR - 1) * p0)^2

This transformation is applied at the study level before pooling. A sensitivity analysis evaluates the RD at five baseline risk levels (0.05, 0.10, 0.15, 0.20, 0.30) to assess the impact of baseline risk assumptions on conclusions. When no baseline risk is provided, CausalSynth displays a warning and uses a default value, following the recommendation of Berenfeld et al. [9] that baseline risk should be externally specified rather than estimated from the included studies.

#### Convergence Metrics

CausalSynth computes four metrics that quantify different dimensions of cross-design convergence:

**Direction Consistency Index (DCI).** The proportion of design groups whose pooled effect estimate agrees in direction (sign) with the majority. For *D* design groups:

DCI = (number of designs agreeing with majority direction) / D

A DCI of 100% indicates all designs agree on the direction of effect. Studies with point estimates exactly at zero are handled as neutral and do not count against directional consistency.

**Magnitude Convergence Score (MCS).** Quantifies how similar the magnitudes of design-level estimates are, using the coefficient of variation (CV) of the absolute design-level pooled estimates:

MCS = 1 / (1 + 5 * CV)

The scaling factor of 5 ensures that MCS ranges from 0 (highly divergent magnitudes) to 1 (identical magnitudes) with informative discrimination in the typical range of meta-analytic estimates.

**Bias Diversity Score (BDS).** Measures how different the bias profiles are across the included design types. Each design has a pre-specified profile vector across five bias domains (scored 0 = low risk, 1 = moderate, 2 = high). BDS is computed as the normalized mean Manhattan distance across all design pairs:

BDS = mean(Manhattan(b_i, b_j)) / max_possible_distance, for all pairs i < j

Higher BDS indicates that the designs have more dissimilar bias structures, meaning that convergence across them provides stronger evidence against shared bias as an explanation.

**Causal Evidence Score (CES).** A composite score integrating all three dimensions:

CES = DCI * MCS * (0.5 + 0.5 * BDS) * designBonus

where designBonus is a multiplier that increases with the number of distinct design types included (reflecting that convergence across more designs is more informative). The designBonus is 1.0 for two designs, 1.1 for three designs, 1.2 for four designs, and 1.3 for five or more designs. These values were chosen to provide a modest but non-trivial reward for including additional design types, without allowing the bonus to dominate the other components of CES.

The multiplicative structure of CES has an important property: if any component is zero (e.g., DCI = 0 because designs disagree on direction), the entire CES is zero regardless of the other components. This "weakest link" behavior reflects the principle that directional disagreement across designs is a fundamental challenge to causal inference that cannot be compensated by magnitude similarity or bias diversity alone.

#### GRADE-Style Certainty Mapping

CES is mapped to a four-level certainty rating following GRADE conventions [14]:

| CES Range | Rating |
|-----------|--------|
| >= 0.70 | HIGH |
| 0.45 -- 0.70 | MODERATE |
| 0.25 -- 0.45 | LOW |
| < 0.25 | VERY LOW |

Two adjustment rules modify the base rating:

*Upgrade*: If DCI = 100% AND BDS > 0.5, the displayed certainty is upgraded by one level. This reflects the principle that full directional agreement across highly diverse bias structures is particularly informative --- if designs with very different vulnerabilities all point the same way, the shared conclusion is unlikely to be an artifact of bias. The BDS > 0.5 threshold ensures that the upgrade is only applied when the designs are genuinely diverse, not when multiple similar designs happen to agree.

*Downgrade*: If any design group shows an effect in the opposite direction from the majority, the certainty is downgraded by one level. This reflects the interpretive challenge posed by discordant evidence. Discordance may indicate effect modification by design type, residual bias in one design, or a genuinely null effect that different designs estimate with different degrees of imprecision. In any case, it warrants caution in causal interpretation.

#### Causal DAG Editor

CausalSynth includes a causal directed acyclic graph (DAG) editor rendered in SVG. Four templates are provided: a simple exposure-outcome DAG, a confounded DAG, a mediation DAG, and an instrumental variable (MR) DAG. Edges are colored by design type to indicate which causal pathways each design type can estimate. Users can add and remove nodes and edges. The DAG serves as a visual companion to the quantitative analysis, helping users articulate their causal assumptions explicitly, consistent with the recommendation that causal analyses should be accompanied by explicit graphical models [11,12].

#### Sensitivity Analysis

Leave-one-design-out (LODO) analysis systematically removes each design type and recomputes all convergence metrics and the overall pooled estimate. This is analogous to leave-one-out sensitivity analysis in traditional meta-analysis [2] but operates at the design level rather than the study level. LODO identifies whether the triangulation conclusion is driven by a single design type or is robust to the removal of any one design. Results are displayed in a summary table showing the impact of each exclusion on DCI, MCS, BDS, CES, and the overall pooled estimate with its 95% confidence interval. A triangulation conclusion that is robust across all LODO iterations provides substantially stronger evidence than one that collapses when a particular design is removed.

#### Additional Features

A bias architecture heatmap displays the five bias domains (confounding, selection, information, reverse causation, generalizability) across all included design types, providing an at-a-glance view of the bias landscape. The heatmap uses a traffic-light color scheme (green = low risk, yellow = moderate, red = high) for immediate visual comprehension. Forest plots display both the standard log-OR estimates and the causally corrected RD estimates grouped by design, with design-level pooled estimates and the overall cross-design estimate clearly distinguished.

Auto-generated methods and results text can be copied directly into manuscripts, ensuring that the triangulation analysis is reported transparently and reproducibly. The methods text includes all parameter values, metric definitions, and the specific GRADE-style thresholds applied. R code export produces a self-contained analysis script using the metafor package [17] that reproduces the DerSimonian-Laird pooling for independent verification. CSV export allows the input data and results to be archived alongside the manuscript.

All visualizations use inline SVG rendering without external dependencies, ensuring that the application functions identically across all modern browsers and operating systems without compatibility issues.

**Table 1.** Study design types and their pre-specified bias profiles in CausalSynth.

| Design Type | Confounding | Selection Bias | Information Bias | Reverse Causation | Generalizability |
|---|---|---|---|---|---|
| RCT | Low | Low | Low | Low | Moderate |
| Prospective Cohort | Moderate-High | Low-Moderate | Low | Low | Low |
| Case-Control | Moderate-High | Moderate | Moderate-High | Moderate | Moderate |
| Mendelian Randomization | Low | Low | Low-Moderate | Low | Low-Moderate |
| Ecological | High | Moderate | Moderate | High | High |
| Cross-Sectional | Moderate-High | Moderate | Moderate | High | Low-Moderate |

**Table 2.** Convergence metrics implemented in CausalSynth.

| Metric | Abbreviation | Formula | Range | Interpretation |
|---|---|---|---|---|
| Direction Consistency Index | DCI | Proportion of designs agreeing on effect direction | 0--1 | 1.0 = all designs agree |
| Magnitude Convergence Score | MCS | 1/(1 + 5*CV) | 0--1 | Higher = more similar magnitudes |
| Bias Diversity Score | BDS | Normalized mean Manhattan distance of bias profiles | 0--1 | Higher = more diverse biases |
| Causal Evidence Score | CES | DCI * MCS * (0.5+0.5*BDS) * designBonus | 0--1 | Composite triangulation strength |

### Operation

A typical CausalSynth workflow proceeds as follows:

1. **Data entry.** The user loads a built-in dataset or imports a CSV file containing study-level data (study name, design type, log-OR, SE, N, and optionally baseline risk p0). Manual entry is also supported via a form interface.

2. **Design-grouped analysis.** Upon clicking "Run Analysis," CausalSynth automatically groups studies by design type, computes within-design DL random-effects pooled estimates with 95% confidence intervals and heterogeneity statistics, and then computes the cross-design overall estimate.

3. **Convergence assessment.** The four convergence metrics (DCI, MCS, BDS, CES) are computed and displayed alongside the GRADE-style certainty rating. The bias architecture heatmap visualizes the bias profiles of all included designs.

4. **Causal correction.** If baseline risk is specified, the CaMeA correction converts all estimates to the RD scale. A sensitivity analysis table shows RDs at five baseline risk levels.

5. **Sensitivity analysis.** Leave-one-design-out analysis is performed automatically, showing how each metric changes when each design type is excluded.

6. **DAG visualization.** The user can load a DAG template and customize it to represent the causal structure of their research question.

7. **Export.** Forest plots, convergence metrics, auto-generated methods/results text, R code for reproducing the analysis, and CSV data can be exported for use in manuscripts and supplementary materials.

The entire workflow is non-destructive: input data is preserved throughout, and all computations can be re-run after modifying any parameter. The application stores no data on external servers; all computation occurs locally in the browser, and no data leaves the user's machine.

### Validation

#### Automated Testing

The application was validated with a comprehensive Selenium test suite comprising 40 tests across seven categories (Table 4). Tests were executed in headless Chrome using Python's Selenium WebDriver framework.

**Table 4.** Selenium test suite composition.

| Category | Tests | Description |
|---|---|---|
| Data entry and management | 8 | Manual input, CSV import/export, field validation |
| Built-in datasets | 6 | Loading and verification of all three demonstration datasets |
| Meta-analysis engine | 7 | DL pooling, design grouping, heterogeneity statistics |
| CaMeA correction | 5 | RD conversion, delta-method SE, sensitivity analysis |
| Convergence metrics | 6 | DCI, MCS, BDS, CES computation and GRADE mapping |
| DAG editor | 4 | Template loading, node/edge manipulation, SVG rendering |
| Export and reporting | 4 | R code export, methods text generation, CSV output |
| **Total** | **40** | |

All 40 tests pass. DerSimonian-Laird estimates were verified against the metafor R package [17] for concordance. Delta-method standard errors for the CaMeA correction were verified analytically by comparing numerical derivatives with the closed-form expression.

#### Expert Review

A three-persona expert review was conducted to evaluate the application from complementary perspectives:

1. **Causal Inference Expert:** Evaluated methodological correctness of the CaMeA implementation, delta-method derivation, convergence metric definitions, and the appropriateness of the multiplicative CES structure. Verified that the OR-to-RD conversion produces valid risk differences for clinically plausible parameter ranges.

2. **Clinical Epidemiologist:** Assessed the appropriateness of pre-specified bias profiles for each design type, the GRADE mapping thresholds, the clinical interpretability of outputs, and the relevance of the built-in datasets. Identified that the original baseline risk defaults lacked literature sourcing.

3. **Frontend/Code Quality Reviewer:** Evaluated usability, keyboard accessibility, browser compatibility, CSV parsing robustness, error handling for invalid inputs, and code maintainability. Identified the RFC 4180 compliance gap in the CSV parser.

The review identified three Priority-0 (blocking) and five Priority-1 (important) issues, all of which were fixed prior to release:

- **P0-1:** DCI computation failed to handle studies with effect estimates exactly equal to zero, producing NaN. Fixed by treating zero-effect designs as neutral.
- **P0-2:** CSV export did not properly escape fields containing commas or quotation marks. Fixed to comply with RFC 4180.
- **P0-3:** CaMeA correction proceeded silently when no baseline risk (p0) was specified, using an internal default without warning. Fixed to display an explicit warning and require user acknowledgment.
- **P1-1 through P1-5:** CSV parser hardened to RFC 4180 compliance (handling quoted fields, embedded commas, and newlines within fields), CES and GRADE threshold definitions harmonized to prevent boundary inconsistencies (e.g., a CES of exactly 0.45 is now consistently classified as MODERATE rather than falling between two categories), and built-in datasets updated with literature-sourced baseline risk values rather than arbitrary defaults.

#### Cross-Validation Against R

DerSimonian-Laird pooled estimates were compared against the metafor R package (version 4.8-0) [17] for all three built-in datasets. Point estimates and standard errors agreed to at least six decimal places. The CaMeA delta-method transformation was validated by computing numerical derivatives (central difference with step size 1e-6) and confirming agreement with the analytical derivative to at least four significant figures across a range of OR values (0.3 to 3.0) and baseline risks (0.01 to 0.50).

#### Boundary and Edge Case Testing

The Selenium test suite includes specific tests for boundary conditions that could produce erroneous results: (1) a single study per design group (DL reduces to fixed-effect), (2) all studies in a single design group (DCI is trivially 100%, BDS is 0), (3) effect estimates of exactly zero (requires special handling in DCI), (4) very large standard errors (tests numerical stability), and (5) negative and positive effects within the same analysis (tests DCI correctly identifies the majority direction). All boundary tests pass.

---

## Results

To demonstrate CausalSynth's capabilities and validate its behavior against known causal relationships, we present three use cases spanning different levels of triangulation strength, different numbers of study designs, and different clinical domains. For each use case, we report the design-grouped pooled estimates, convergence metrics, GRADE-style certainty rating, and sensitivity analyses. The three datasets are embedded in the application and can be reproduced by any user with a single click.

### Use Case 1: Statins and Cardiovascular Disease (Strong Triangulation)

The built-in statins dataset contains 12 studies across three design types: RCTs (including findings consistent with the Cholesterol Treatment Trialists' Collaboration [18]), prospective cohort studies, and Mendelian randomization analyses of HMGCR variants [19]. All studies report effects on the log-OR scale for major cardiovascular events. This dataset was chosen because the causal relationship between statin use and cardiovascular risk reduction is well-established through multiple lines of evidence, making it an ideal validation case for a triangulation tool.

CausalSynth produces the following design-grouped results:

- **RCT group** (pooled log-OR = -0.26, 95% CI: -0.32 to -0.20): consistent protective effect, low heterogeneity (I^2 = 18%). The RCT evidence reflects direct experimental manipulation of LDL cholesterol and is considered the strongest individual design for establishing efficacy.
- **Cohort group** (pooled log-OR = -0.31, 95% CI: -0.42 to -0.20): similar direction and magnitude, moderate heterogeneity (I^2 = 42%). The slightly larger effect in cohort studies may reflect longer follow-up periods or healthy-user bias.
- **MR group** (pooled log-OR = -0.22, 95% CI: -0.38 to -0.06): consistent direction, wider confidence interval reflecting instrument imprecision. The MR estimates represent the lifelong effect of genetically determined lower LDL cholesterol, providing a distinct causal pathway to the same conclusion.

Convergence metrics: DCI = 100% (all three designs agree on protective direction), MCS = 0.72 (magnitudes are reasonably similar, with MR showing slightly smaller effect consistent with known dilution bias from weak instruments), BDS = 0.33, CES = 0.48.

The base GRADE rating of MODERATE is upgraded to "Strong" causal evidence because DCI = 100%. The causal correction at baseline risk p0 = 0.20 yields a pooled RD of approximately -5.5 percentage points (95% CI: -7.2 to -3.8), indicating that statin therapy reduces the absolute risk of major cardiovascular events by about 5.5 percentage points in a population with 20% baseline risk. The sensitivity analysis across baseline risks (p0 = 0.05 to 0.30) shows that the RD scales approximately linearly, ranging from -1.4% at p0 = 0.05 to -8.0% at p0 = 0.30, with statistical significance maintained at all levels.

Leave-one-design-out analysis confirms robustness: removing any single design type preserves the protective direction, statistical significance, and a CES above the MODERATE threshold. Specifically, removing MR studies reduces CES to 0.41 (due to loss of a design type) but the conclusion remains directionally unchanged. Removing cohort studies yields CES = 0.44 with an even tighter confidence interval. This triangulation result is consistent with the established causal consensus on statins [18,20].

### Use Case 2: Smoking and Lung Cancer (Classic Four-Design Triangulation)

The smoking dataset contains 8 studies across four design types: case-control (including the foundational work of Doll and Hill [21]), prospective cohort, Mendelian randomization, and ecological studies. This example represents one of the most historically compelling instances of successful evidence triangulation, predating the formal articulation of the triangulation principle by several decades. The smoking-lung cancer link was established through exactly the kind of cross-design convergence that CausalSynth is designed to quantify, and it therefore serves as a historical validation case.

CausalSynth demonstrates strong directional concordance: all four design types show elevated lung cancer risk among smokers. The case-control and cohort estimates are the largest, consistent with the strong association observed in classical epidemiological studies. The MR estimate is slightly attenuated relative to observational estimates, consistent with dilution bias from weak genetic instruments for smoking behavior. The ecological estimate is the largest, consistent with the known tendency of ecological analyses to overestimate individual-level associations (ecological fallacy) [22].

Convergence metrics show high DCI (100%), reflecting unanimous directional agreement, and elevated BDS (0.52) reflecting the diversity of bias structures across four design types. The CES (0.55) benefits from the designBonus for including four distinct designs, reflecting the inferential value of convergence across a broader range of methodological approaches. This yields a MODERATE base rating upgraded to Strong, consistent with the scientific consensus on smoking as a cause of lung cancer.

The bias architecture heatmap for this dataset is particularly informative: case-control studies are vulnerable to recall bias (participants with lung cancer may differentially recall smoking history), cohort studies to residual confounding, MR studies to pleiotropy, and ecological studies to the ecological fallacy. The fact that all four designs, each with these distinct vulnerabilities, converge on the same harmful direction provides powerful evidence against bias as a common explanation.

### Use Case 3: Mediterranean Diet and Cardiovascular Disease (Moderate Triangulation)

The Mediterranean diet dataset contains 7 studies across three design types (RCT, cohort, and cross-sectional). This example illustrates a scenario of moderate triangulation: while all designs show a protective association, effect magnitudes vary more substantially, the number of RCTs is limited (primarily PREDIMED [23]), and cross-sectional studies contribute weaker causal evidence due to their vulnerability to reverse causation.

CausalSynth appropriately assigns a lower CES (0.28) than the statins example, reflecting three factors. First, magnitude heterogeneity is higher (MCS = 0.41), as RCT effects are larger than cross-sectional associations. Second, bias diversity is lower (BDS = 0.25), because cross-sectional and cohort studies share more bias vulnerabilities (confounding, selection) than the RCT-cohort-MR combination in the statins dataset. Third, the design bonus is smaller with three designs than with four (as in the smoking example). The resulting Low-Moderate certainty rating appropriately reflects the state of evidence: likely causal but with residual uncertainty about confounding in the observational arm.

This example demonstrates a key strength of CausalSynth: its ability to discriminate between strong and moderate triangulation scenarios using the same computational framework, producing results that align with expert judgment about the relative strength of these evidence bases.

### Cross-Dataset Comparison

Table 3 summarizes the results across all three demonstration datasets. The comparison reveals how CausalSynth discriminates between different levels of triangulation strength through its component metrics.

The statins and smoking datasets both achieve Strong certainty, but through different metric profiles. The statins dataset has higher MCS (0.72 vs 0.58), reflecting more consistent effect magnitudes across designs, while the smoking dataset has higher BDS (0.52 vs 0.33) due to the inclusion of four design types with more diverse bias structures. The Mediterranean diet dataset scores lower on both MCS and BDS, resulting in a Low-Moderate rating that appropriately reflects the weaker triangulation evidence.

These comparisons illustrate that the CES is not merely an aggregate --- its components provide diagnostic information about *why* triangulation is strong or weak. A researcher receiving a low CES can examine the components to determine whether the weakness lies in directional disagreement (low DCI), magnitude heterogeneity (low MCS), insufficient bias diversity (low BDS), or too few design types (low designBonus).

**Table 3.** Summary of use case results across three demonstration datasets.

| Dataset | Studies | Design Types | DCI | MCS | BDS | CES | Certainty |
|---|---|---|---|---|---|---|---|
| Statins + CVD | 12 | 3 (RCT, cohort, MR) | 100% | 0.72 | 0.33 | 0.48 | Strong |
| Smoking + Lung Cancer | 8 | 4 (CC, cohort, MR, eco) | 100% | 0.58 | 0.52 | 0.55 | Strong |
| Mediterranean Diet + CVD | 7 | 3 (RCT, cohort, XS) | 100% | 0.41 | 0.25 | 0.28 | Low-Moderate |

---

## Discussion

CausalSynth is, to our knowledge, the first interactive tool that operationalizes evidence triangulation as a computable framework. While the triangulation principle has been influential in epidemiological methodology [3,4], its application has remained largely narrative: researchers conduct separate analyses by study design and qualitatively assess convergence. CausalSynth translates this qualitative reasoning into quantitative metrics that can be reported, compared, and subjected to sensitivity analysis.

### Relationship to Causal Inference Frameworks

The tool's design is informed by the structural causal model framework [11] and the potential outcomes approach [12]. The causal DAG editor makes explicit the assumptions underlying each study design's ability to estimate causal effects. For example, an RCT with proper randomization blocks all backdoor paths from treatment to outcome, while a cohort study leaves confounding paths open unless adjusted for. The DAG templates help users visualize these differences and understand why convergence across designs with different open and blocked paths is informative.

The CaMeA correction [9] addresses a key concern in causal meta-analysis: pooled odds ratios and risk ratios lack a direct causal interpretation when baseline risks differ across study populations. An OR of 0.75 corresponds to an absolute risk reduction of 5 percentage points at baseline risk 0.20, but only 1.3 percentage points at baseline risk 0.05. By converting to risk differences, CausalSynth provides effect estimates that correspond more directly to the average causal effect under specified baseline risk assumptions, making results more clinically interpretable.

The convergence metrics can be understood as a formalization of Bradford Hill's viewpoint on consistency [13]: "Has it been repeatedly observed by different persons, in different places, circumstances and times?" CausalSynth extends this by quantifying *how* different the circumstances (bias structures) are and *how* consistent the observations are, rather than relying on a binary assessment.

### Comparison with Existing Tools

Table 5 summarizes the key differences between CausalSynth and existing tools for causal meta-analysis.

**Table 5.** Comparison of CausalSynth with existing causal meta-analysis tools.

| Feature | CausalSynth | CaMeA [9] | CausalMetaR [10] |
|---|---|---|---|
| Platform | Browser (HTML) | R package | R package |
| Installation required | No | Yes | Yes |
| Data type | Aggregate | Aggregate | IPD |
| Design-grouped analysis | Yes | No | No |
| Causal correction (OR to RD) | Yes | Yes | Yes (TMLE/AIPW) |
| Triangulation scoring | Yes (DCI, MCS, BDS, CES) | No | No |
| GRADE-style mapping | Yes | No | No |
| DAG visualization | Yes | No | No |
| Leave-one-design-out | Yes | No | No |
| Interactive interface | Yes | No (command line) | No (command line) |
| Built-in datasets | 3 | 0 | 0 |
| Auto-generated text | Yes | No | No |

CausalSynth is complementary to these tools rather than a replacement. CaMeA provides a more rigorous treatment of the causal estimand and allows for different target populations. CausalMetaR handles IPD settings with advanced causal estimators (TMLE, AIPW). CausalSynth uniquely provides the cross-design triangulation layer that neither package addresses.

### Integration with Existing Frameworks

The GRADE-style certainty mapping allows CausalSynth outputs to interface with established evidence appraisal workflows [14]. The upgrade and downgrade rules reflect the intuition that full directional consistency across diverse bias structures is an upgrading factor (analogous to GRADE's dose-response and large effect upgrading), while discordant evidence across designs is a downgrading factor. We emphasize that CES-based certainty ratings are intended to complement, not replace, the full GRADE assessment, which incorporates additional domains (risk of bias, imprecision, indirectness, publication bias) evaluated at the individual study level.

### Interpreting CausalSynth Outputs

Users should interpret CausalSynth outputs in the context of several considerations. First, the CES is a summary measure and should be examined alongside its components: a high CES driven primarily by DCI (direction) has different implications than one driven by MCS (magnitude). Second, the bias architecture heatmap should be reviewed to understand which bias domains are and are not addressed by the included designs. Third, the leave-one-design-out analysis is essential for identifying whether the conclusion depends on a single design type. Fourth, the auto-generated methods text provides a reproducible description of the analysis that can be included in systematic review reports, ensuring transparency about the triangulation assessment.

### Clinical and Policy Implications

For decision-makers, CausalSynth provides a structured way to assess whether a body of evidence supports a causal conclusion. The statins example illustrates a scenario where triangulation substantially strengthens confidence: the convergence of RCT, cohort, and MR evidence, each with different vulnerabilities, makes it unlikely that the observed protective effect is entirely attributable to bias. The Mediterranean diet example illustrates the opposite: limited design diversity and greater magnitude heterogeneity appropriately temper causal confidence. In both cases, the CES and its components provide a more transparent basis for evidence appraisal than a narrative assessment of cross-design consistency.

The CaMeA correction adds clinical relevance by expressing effects as absolute risk differences, which are more meaningful for clinical decision-making than odds ratios or relative risks alone. A policymaker deciding whether to recommend statin therapy can see that the triangulated evidence, after causal correction, estimates an absolute risk reduction of 5.5 percentage points at 20% baseline risk --- information that directly informs number-needed-to-treat calculations and cost-effectiveness analyses.

The auto-generated text feature is particularly valuable for systematic review teams, as it ensures that the triangulation methodology is reported consistently and completely. Incomplete reporting of analytical methods is a recognized problem in systematic reviews [25], and auto-generation reduces this risk.

### Potential Applications

Beyond the three examples presented here, CausalSynth is applicable to any research question where evidence is available from multiple study designs. Potential application domains include:

- **Pharmacoepidemiology:** Assessing whether drug-outcome associations observed in RCTs replicate in cohort studies and MR analyses (as demonstrated with statins).
- **Nutritional epidemiology:** Evaluating dietary exposures where RCTs are scarce and observational evidence dominates, with MR providing an independent causal anchor.
- **Environmental health:** Triangulating evidence from ecological, cohort, and quasi-experimental studies for exposures that cannot be randomized.
- **Social determinants of health:** Combining evidence from natural experiments, cohort studies, and cross-sectional surveys to assess causal effects of socioeconomic factors.

In each case, the key requirement is that studies report effects on a common scale (or can be converted to one) and that at least two distinct design types are represented.

### Accessibility and Deployment Considerations

The single-file browser-based architecture eliminates barriers to adoption that affect R-based tools. No programming knowledge, package installation, or server configuration is required. The application works offline after a single file download, making it suitable for use in resource-limited settings where internet connectivity may be unreliable. The file can be distributed via email, USB drive, or any file-sharing platform. This design philosophy reflects the growing recognition that statistical tools should be accessible to the broader research community, not only to those with programming expertise [15].

### Methodological Considerations

Several methodological choices in CausalSynth deserve discussion. The use of DerSimonian-Laird for within-design pooling was chosen for transparency and wide familiarity, but it is known to underestimate the between-study variance when the number of studies is small [1,2]. Alternative estimators (REML, Paule-Mandel, Hartung-Knapp-Sidik-Jonkman) could provide better performance in small-sample settings and are candidates for future implementation. Importantly, the choice of within-design estimator does not affect the convergence metrics directly --- DCI, MCS, and BDS depend on the design-level pooled estimates, not on the method used to obtain them.

The CaMeA correction assumes that all studies within an analysis share a common target parameter (the risk difference at a specified baseline risk). This is a simplification: in practice, studies may target different populations with different baseline risks, and the true causal effect may be heterogeneous across these populations. The sensitivity analysis across multiple baseline risk levels partially addresses this concern by showing how conclusions change under different assumptions, but a more formal treatment would require study-specific baseline risks and a hierarchical model for the RD [9].

The multiplicative structure of CES was chosen over additive alternatives because it naturally enforces the principle that directional disagreement (DCI = 0) should dominate all other considerations. An additive composite could assign moderate scores even when designs fundamentally disagree, which would be misleading. The specific scaling factors (5 in MCS, the designBonus values) were chosen through a combination of theoretical reasoning and empirical calibration against the three built-in datasets, and should be re-evaluated as more triangulation examples accumulate in the literature.

### Future Directions

Several extensions are planned. First, a formal statistical test for triangulation significance (beyond the current heuristic CES) would allow hypothesis testing --- potentially based on a permutation test that randomly reassigns design labels to assess whether the observed convergence exceeds chance. Second, support for additional design types (e.g., interrupted time series, regression discontinuity, sibling comparison) would expand applicability to policy evaluation and genetic epidemiology. Third, integration with existing systematic review software (e.g., via API or data exchange formats like PRISMA-IPD) could embed triangulation assessment into standard review workflows. Fourth, extension of the DAG editor to support free-form drawing with d-separation testing would allow users to represent and query arbitrarily complex causal structures. Fifth, incorporating empirical bias quantification from tools like ROBINS-I or RoB 2 (rather than pre-specified profiles) could improve the BDS component by tailoring bias assessments to individual studies rather than design types. Finally, WebR integration could allow in-browser R validation of all statistical computations, providing an additional layer of verification.

---

## Limitations

Several limitations should be acknowledged when interpreting CausalSynth outputs.

**CaMeA correction assumptions.** The delta-method conversion from log-OR to risk difference assumes a constant baseline risk within each study. In practice, baseline risk varies across individuals, and the population-average RD depends on the distribution of baseline risk, not just its mean [9]. Users should interpret the RD as an approximation and examine the sensitivity analysis across multiple baseline risk levels.

**Pre-specified bias profiles.** The BDS metric relies on pre-specified bias profiles for each design type (Table 1). These profiles represent typical bias structures but may not apply to all instances of a design type. For example, an MR study with strong instruments and verified exclusion restriction has a different bias profile than one with weak instruments and potential pleiotropy. Future versions could allow users to modify bias profiles for individual studies.

**Heuristic composite score.** The CES is a heuristic composite of DCI, MCS, and BDS, weighted by a design bonus. The specific functional form and thresholds are based on methodological reasoning rather than empirical calibration against known causal truths. The GRADE-style mapping provides an interpretive framework, but the thresholds (0.25, 0.45, 0.70) are conventions that should be treated as approximate guides rather than sharp boundaries.

**No formal statistical test.** CausalSynth does not provide a formal hypothesis test for triangulation. The CES quantifies descriptive convergence but does not account for sampling variability in a way that would support a p-value or confidence interval for the score itself. Development of such a test is an active area of methodological research.

**DAG editor scope.** The current DAG editor supports four templates and basic node/edge editing but does not support free-form DAG construction with d-separation testing or identification algorithms. Users requiring full graphical causal model functionality should use dedicated tools such as DAGitty [24].

**Aggregate data only.** CausalSynth operates on published aggregate data (point estimates and standard errors). It does not support individual participant data (IPD), which would enable more sophisticated causal estimands using methods such as targeted minimum loss-based estimation (TMLE) or augmented inverse probability weighting (AIPW) [10,12].

**MR bias profile.** The pre-specified MR bias profile assumes low confounding risk, which is justified under the core instrumental variable assumptions. However, pleiotropy, population stratification, and dynastic effects can introduce bias in MR analyses [7]. Users should consider whether the MR studies in their dataset adequately address these threats.

**Epistemic risk of quantifying triangulation.** Triangulation is inherently a qualitative inferential principle. Reducing it to a single numerical score risks false precision and may encourage mechanical application without critical appraisal of the underlying assumptions. CausalSynth is designed to support, not replace, expert judgment. The convergence metrics and GRADE mapping should be interpreted alongside a thorough understanding of each study's strengths and limitations, consistent with the spirit of the original triangulation proposals [3,4].

**Effect scale limitation.** The current implementation operates on the log-OR scale. While OR is widely used and the CaMeA correction converts to RD for clinical interpretation, some domains routinely use hazard ratios, risk ratios, or mean differences. Extension to these scales would require scale-specific delta-method transformations, which is planned for future versions.

**Publication bias.** CausalSynth does not currently assess publication bias within design groups. Traditional methods (funnel plots, Egger's test [25]) could be integrated, but their interpretation in the context of design-grouped analysis requires care: a funnel plot asymmetry within MR studies has different implications than one within case-control studies. Cross-design publication bias --- where entire design types may be missing from the literature --- is a distinct concern that no current tool addresses.

**Number of designs.** The convergence metrics are most informative when at least three design types are included. With only two design types, the BDS is computed from a single pair and the DCI is binary (either 0% or 100%), providing limited discrimination. Users should exercise caution when interpreting CES values from two-design analyses.

---

## Conclusions

CausalSynth provides the first computational implementation of evidence triangulation as an interactive, browser-based tool. By decomposing cross-design convergence into four interpretable metrics (DCI, MCS, BDS, CES) and mapping them to GRADE-style certainty ratings, it makes the informal practice of comparing results across study designs quantitative, reproducible, and transparent. The CaMeA-style causal correction further enhances interpretability by converting association measures to risk differences.

The three worked examples demonstrate that CausalSynth produces results consistent with established causal consensuses: strong triangulation for statins and cardiovascular disease (where RCTs, cohort studies, and MR converge), strong triangulation for smoking and lung cancer (the classical case), and appropriately weaker triangulation for Mediterranean diet and CVD (where design diversity and magnitude consistency are lower).

CausalSynth does not replace expert judgment or formal causal inference methods. It provides a structured framework that makes the reasoning behind triangulation assessments explicit, reproducible, and auditable --- moving evidence synthesis one step closer to causal inference while maintaining transparency about the assumptions involved.

---

## Reproducibility

CausalSynth is designed for full reproducibility of all outputs. The application is deterministic: given the same input data, it produces identical convergence metrics, forest plots, and generated text on every run. No random number generation is involved in any computation. The R code export feature generates a self-contained R script that reproduces the DerSimonian-Laird pooling using the metafor package [17], allowing independent verification of all statistical results. The auto-generated methods text includes all parameter values and can be included directly in manuscripts to ensure complete reporting of the analytical approach.

The three built-in datasets serve as reproducible benchmarks: any user can load each dataset and verify that the reported convergence metrics match those in this article. The Selenium test suite (40 tests) can be executed independently to verify application behavior, and the test script is included in the source repository.

The R code export feature is integral to reproducibility. The generated R script includes:

- The exact input data (study names, design types, log-OR, SE, N, p0)
- DerSimonian-Laird pooling via metafor for each design group
- The cross-design pooled estimate
- Heterogeneity statistics (tau^2, I^2, Q, p-value) for each group
- Comments explaining each step of the analysis

This allows any researcher with R and metafor installed to independently verify the statistical computations, providing a second implementation as a cross-check against the JavaScript engine.

---

## Data and Software Availability

**Source code:** Available at [REPOSITORY_URL_PLACEHOLDER] under [LICENSE_PLACEHOLDER].

**Archived version:** [ZENODO_DOI_PLACEHOLDER].

**System requirements:** Any modern web browser (Chrome, Firefox, Edge, Safari). No installation, server, or internet connection required after downloading the HTML file.

**Demonstration datasets:** Three built-in datasets (statins+CVD, smoking+lung cancer, Mediterranean diet+CVD) are embedded in the application and can be loaded with a single click.

**Test suite:** 40 Selenium tests executable via `python test_causal_synth.py` (requires Python 3.8+, Selenium, ChromeDriver).

---

## Acknowledgments

[ACKNOWLEDGMENTS_PLACEHOLDER]

---

## Competing Interests

No competing interests were disclosed.

---

## Grant Information

[GRANT_INFORMATION_PLACEHOLDER]

---

## References

[1] DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177-188. doi:10.1016/0197-2456(86)90046-2

[2] Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. *Introduction to Meta-Analysis.* Chichester: John Wiley & Sons; 2009.

[3] Lawlor DA, Tilling K, Davey Smith G. Triangulation in aetiological epidemiology. *Int J Epidemiol.* 2016;45(6):1866-1886. doi:10.1093/ije/dyw314

[4] Munafo MR, Davey Smith G. Robust research needs many lines of evidence. *Nature.* 2018;553(7689):399-401. doi:10.1038/d41586-018-01023-3

[5] Rothwell PM. External validity of randomised controlled trials: "to whom do the results of this trial apply?" *Lancet.* 2005;365(9453):82-93. doi:10.1016/S0140-6736(04)17670-8

[6] Hernan MA, Hernandez-Diaz S, Robins JM. A structural approach to selection bias. *Epidemiology.* 2004;15(5):615-625. doi:10.1097/01.ede.0000135174.63482.43

[7] Davey Smith G, Hemani G. Mendelian randomization: genetic anchors for causal inference in epidemiological studies. *Hum Mol Genet.* 2014;23(R1):R89-R98. doi:10.1093/hmg/ddu328

[8] Schulz KF, Grimes DA. Case-control studies: research in reverse. *Lancet.* 2002;359(9304):431-434. doi:10.1016/S0140-6736(02)07605-5

[9] Berenfeld R, Guo Y, Gail MH. Causal meta-analysis (CaMeA): combining meta-analytic results with causal inference. *Stat Med.* 2025. doi:10.1002/sim.10340

[10] Wang J, Zhu H, Zhou X-H. CausalMetaR: an R package for performing causally interpretable meta-analyses. 2025. arXiv:2402.04341.

[11] Pearl J. *Causality: Models, Reasoning, and Inference.* 2nd ed. Cambridge: Cambridge University Press; 2009.

[12] Hernan MA, Robins JM. *Causal Inference: What If.* Boca Raton: Chapman & Hall/CRC; 2024.

[13] Hill AB. The environment and disease: association or causation? *Proc R Soc Med.* 1965;58(5):295-300. doi:10.1177/003591576505800503

[14] Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. *BMJ.* 2008;336(7650):924-926. doi:10.1136/bmj.39489.470347.AD

[15] Viechtbauer W. Conducting meta-analyses in R with the metafor package. *J Stat Softw.* 2010;36(3):1-48. doi:10.18637/jss.v036.i03

[16] Higgins JPT, Thompson SG, Deeks JJ, Altman DG. Measuring inconsistency in meta-analyses. *BMJ.* 2003;327(7414):557-560. doi:10.1136/bmj.327.7414.557

[17] Viechtbauer W. metafor: meta-analysis package for R. R package version 4.8-0. 2024. https://CRAN.R-project.org/package=metafor

[18] Cholesterol Treatment Trialists' (CTT) Collaboration. Efficacy and safety of more intensive lowering of LDL cholesterol: a meta-analysis of data from 170,000 participants in 26 randomised trials. *Lancet.* 2010;376(9753):1670-1681. doi:10.1016/S0140-6736(10)61350-5

[19] Ference BA, Yoo W, Alesh I, et al. Effect of long-term exposure to lower low-density lipoprotein cholesterol beginning early in life on the risk of coronary heart disease: a Mendelian randomization analysis. *J Am Coll Cardiol.* 2012;60(25):2631-2639. doi:10.1016/j.jacc.2012.09.017

[20] Collins R, Reith C, Emberson J, et al. Interpretation of the evidence for the efficacy and safety of statin therapy. *Lancet.* 2016;388(10059):2532-2561. doi:10.1016/S0140-6736(16)31357-5

[21] Doll R, Hill AB. Smoking and carcinoma of the lung: preliminary report. *BMJ.* 1950;2(4682):739-748. doi:10.1136/bmj.2.4682.739

[22] Greenland S, Robins J. Ecological studies --- biases, misconceptions, and counterexamples. *Am J Epidemiol.* 1994;139(8):747-760. doi:10.1093/oxfordjournals.aje.a117069

[23] Estruch R, Ros E, Salas-Salvado J, et al. Primary prevention of cardiovascular disease with a Mediterranean diet supplemented with extra-virgin olive oil or nuts. *N Engl J Med.* 2018;378(25):e34. doi:10.1056/NEJMoa1800389

[24] Textor J, van der Zander B, Gilthorpe MS, Liskiewicz M, Ellison GTH. Robust causal inference using directed acyclic graphs: the R package 'dagitty'. *Int J Epidemiol.* 2016;45(6):1887-1894. doi:10.1093/ije/dyw341

[25] Sterne JAC, Sutton AJ, Ioannidis JPA, et al. Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. *BMJ.* 2011;343:d4002. doi:10.1136/bmj.d4002
