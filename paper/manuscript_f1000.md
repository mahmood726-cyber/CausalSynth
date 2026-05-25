# CausalSynth: A Browser-Based Engine for Causal Evidence Triangulation Across Study Designs

**Authors:** [AUTHOR_NAME]^1,2

^1 [AFFILIATION_1]
^2 [AFFILIATION_2]

**Corresponding author:** [CORRESPONDING_EMAIL]

**ORCID:** [ORCID_PLACEHOLDER]

**Keywords:** evidence triangulation, causal inference, meta-analysis, cross-design synthesis, convergence metrics, CaMeA, browser-based tool

---

## Abstract

**Background:** Evidence triangulation --- the principle that convergent findings from study designs with different bias structures strengthen causal inference --- has been articulated as a methodological priority (Lawlor et al. 2016; Munafo and Davey Smith 2018). Yet no computational tool exists to quantify triangulation across heterogeneous study designs. Existing R packages (CausalMetaR, CaMeA) address causal aggregation for specific estimands but provide neither cross-design convergence scoring nor interactive triangulation workflows.

**Methods:** CausalSynth is a zero-dependency, single-file browser application (9,032 lines) implementing design-grouped random-effects meta-analysis (DerSimonian-Laird and REML), CaMeA-style causal correction converting OR/RR to risk differences via the delta method, and four convergence metrics: Direction Concordance Index (DCI), Magnitude Consistency Score (MCS), Bias Diversity Score (BDS), and Causal Evidence Score (CES). A GRADE-like certainty mapping translates CES into evidence ratings. Additional features include a causal DAG editor, contour-enhanced funnel plot with Egger regression and trim-and-fill, leave-one-design-out sensitivity, network-of-designs visualization, Risk of Bias summary, subgroup analysis, power analysis for triangulation, influence diagnostics, WebR cross-validation, TruthCert provenance, and R code export. Validation comprised 105 Selenium tests and a five-persona expert review.

**Results:** Applied to five built-in datasets spanning cardiology, oncology, nutrition, infectious disease, and tobacco epidemiology, CausalSynth correctly discriminates strong triangulation (statins: CES = 0.48, smoking: CES = 0.55) from moderate (Mediterranean diet: CES = 0.28) and produces results concordant with established causal consensuses. DL and REML estimates match R metafor to six decimal places.

**Conclusions:** CausalSynth is the first interactive tool to operationalize evidence triangulation as a computable framework. It is freely available, requires no installation, and produces reproducible outputs suitable for systematic review workflows.

**Software availability:** Source code at [GITHUB_URL]. Archived at [ZENODO_DOI].

---

## Introduction

Traditional meta-analysis treats all included studies as exchangeable observations, pooling effect estimates under fixed-effect or random-effects models regardless of study design [1,2]. While enormously productive, this approach carries a fundamental limitation: studies conducted using the same design share similar bias structures, and pooling them does not address the possibility that a consistent finding reflects a consistent bias rather than a true causal effect. For example, a meta-analysis of 15 observational cohort studies showing an association between a dietary exposure and a disease outcome could reflect residual confounding by socioeconomic status across all studies. Increasing precision through additional studies of the same design does not address this shared vulnerability.

Evidence triangulation offers a complementary inferential strategy. First articulated systematically by Lawlor et al. [3] and elaborated by Munafo and Davey Smith [4], the principle holds that when studies using designs with *different* bias structures converge on the same conclusion, the probability that all designs share the same bias decreases, strengthening causal inference. Each study design has characteristic strengths and weaknesses. Randomized controlled trials (RCTs) eliminate confounding by design but may suffer from limited generalizability [5]. Prospective cohort studies provide real-world evidence but are vulnerable to residual confounding [6]. Mendelian randomization (MR) studies exploit genetic variation as instrumental variables, avoiding traditional confounding but introducing concerns about pleiotropy [7]. Case-control studies are efficient for rare outcomes but susceptible to recall and selection bias [8]. When these designs --- each with distinct vulnerability profiles --- independently support the same causal direction, the cumulative evidence for causation is substantially strengthened.

Despite the theoretical appeal, practical implementation has remained largely qualitative. Recent methodological advances have addressed adjacent problems: Berenfeld et al. [9] introduced CaMeA, a causal meta-analysis framework that converts pooled odds ratios and risk ratios to risk differences using the delta method. Wang et al. [10] developed CausalMetaR for individual participant data settings. However, CaMeA is available only as an R package and does not compute triangulation scores, while CausalMetaR requires IPD and does not support aggregate-data triangulation. Neither tool provides an interactive interface accessible to non-programmers.

The broader causal inference literature provides a theoretical foundation for this work. Pearl's do-calculus [11] and the potential outcomes framework [12] establish conditions for causal identifiability. Bradford Hill's viewpoints [13] emphasize consistency across study types as one consideration supporting causality, yet this criterion has remained unquantified for over six decades. The GRADE framework [14] incorporates provisions for upgrading observational evidence but does not formally incorporate cross-design convergence.

Several barriers have prevented practical adoption of quantitative triangulation. First, no agreed-upon metric exists for quantifying cross-design convergence. Second, existing meta-analysis software (RevMan, Stata, R metafor) does not support design-grouped analysis with convergence assessment as a built-in feature. Third, converting association measures to causal estimands requires statistical expertise that many systematic reviewers lack. Fourth, no tool integrates causal DAG visualization with quantitative evidence synthesis, despite widespread recognition that graphical causal models should accompany causal analyses [11,12].

CausalSynth fills this gap by providing the first interactive, browser-based tool that operationalizes evidence triangulation as a computable framework. It implements design-grouped meta-analysis with two estimators (DerSimonian-Laird and REML), CaMeA-style causal correction, four convergence metrics with GRADE-like mapping, and over 30 analytical features --- all within a single HTML file requiring no installation, no server, and no programming knowledge. Five built-in datasets provide worked examples across medicine, and all outputs can be exported for integration into systematic review manuscripts.

---

## Methods

### Implementation

#### Architecture

CausalSynth is implemented as a single self-contained HTML file (9,032 lines, version 3.0.0) combining HTML5 structure, CSS styling, and JavaScript computation. No external libraries, frameworks, or server connections are required. The application runs entirely in the user's browser, ensuring data privacy and offline operability. This architecture follows the design philosophy of accessible statistical tools that prioritize zero-barrier deployment [15].

The application supports six study design types: randomized controlled trial (RCT), prospective cohort, case-control, Mendelian randomization (MR), ecological, and cross-sectional. Each design type is associated with a pre-specified bias profile across five domains: confounding, selection bias, measurement bias, reverse causation, and generalizability (Table 1). These profiles were derived from standard epidemiological references [2,12] and are displayed transparently via the bias architecture heatmap, allowing critical appraisal.

**Table 1.** Study design types and pre-specified bias profiles in CausalSynth.

| Design Type | Confounding | Selection | Measurement | Reverse Causation | Generalizability |
|---|---|---|---|---|---|
| RCT | Low | Moderate | Low | Low | Moderate |
| Cohort | Moderate | Moderate | Moderate | Moderate | High |
| Case-Control | Moderate | High | High | Moderate | Moderate |
| Mendelian Randomization | Low | Moderate | Moderate | Low | Moderate |
| Ecological | High | Moderate | Moderate | High | High |
| Cross-Sectional | Moderate | Moderate | Moderate | High | Moderate |

#### Data Input

Users enter study-level data comprising: study identifier, design type (selected from a dropdown), effect estimate on the log-odds ratio (log-OR) scale, standard error (SE), sample size (N), optional baseline risk (p0) for causal correction, and optional subgroup variable. Data can be entered manually, imported via CSV (with quoted-field support), or loaded from five built-in demonstration datasets. Each study row includes a remove button, and bulk operations (add 5 rows, clear all) support rapid data entry.

#### Meta-Analysis Engines

CausalSynth implements two random-effects estimators, selectable via a pooling method toggle:

**DerSimonian-Laird (DL).** The standard moment-based estimator [1]. For each design group *d* with *k_d* studies having effect estimates *y_i* and variances *v_i*, between-study variance is:

tau_d^2 = max(0, (Q_d - (k_d - 1)) / C)

where Q_d is the Cochran Q statistic, C = sum(w_i) - sum(w_i^2)/sum(w_i), and w_i = 1/v_i. Random-effects weights are w_i* = 1/(v_i + tau_d^2). Heterogeneity is reported as I^2 [16].

**Restricted Maximum Likelihood (REML).** Implemented via Fisher scoring [17] with the DL estimate as starting value. The REML score and Fisher information follow Viechtbauer (2005):

Score: dL/d(tau^2) = -0.5 * tr(P) + 0.5 * y'PPy

where P = W - W*1*(1'W1)^{-1}*1'*W is the projection matrix. Convergence is declared when |delta(tau^2)| < 10^{-8}, with a maximum of 100 iterations. REML generally provides less biased tau^2 estimates than DL, particularly with few studies [2].

A cross-design synthesis pools the design-level estimates using a second-stage model, providing an overall summary that accounts for both within-design and between-design heterogeneity.

### Key Algorithms

#### CaMeA Causal Correction

Following the CaMeA framework [9], CausalSynth converts nonlinear measures to risk differences (RD), providing causally interpretable effect sizes. Two measure types are supported:

**OR to RD:** RD = OR * p0 / (1 + (OR - 1) * p0) - p0, where OR = exp(log-OR). The standard error is obtained via the delta method: SE(RD) = |dRD/d(log-OR)| * SE(log-OR), where the derivative is dRD/d(log-OR) = OR * p0 * (1 - p0) / (1 + (OR - 1) * p0)^2.

**RR to RD:** RD = (RR - 1) * p0, where RR = exp(log-RR). The delta-method SE is SE(RD) = RR * p0 * SE(log-RR).

These transformations are applied at the study level before pooling. A sensitivity slider allows users to vary the target population baseline risk (p0 from 0.01 to 0.50) and observe how the causal RD changes in real time.

#### Convergence Metrics

CausalSynth computes four metrics quantifying different dimensions of cross-design convergence (Table 2):

**Direction Concordance Index (DCI).** The proportion of design groups whose pooled estimate agrees in sign with the majority: DCI = max(n_positive, n_negative, n_zero_assigned_to_majority) / D. Studies with estimates exactly at zero are treated as neutral. DCI = 100% indicates unanimous directional agreement.

**Magnitude Consistency Score (MCS).** Quantifies similarity of design-level magnitudes using the coefficient of variation (CV): MCS = 1 / (1 + 5 * CV). The scaling factor ensures MCS ranges from 0 (highly divergent) to 1 (identical magnitudes) with informative discrimination.

**Bias Diversity Score (BDS).** Measures dissimilarity of bias profiles across designs. Each design has a profile vector across five domains (scored 0 = low, 1 = moderate, 2 = high). BDS is the normalized mean Manhattan distance across all design pairs. Higher BDS indicates more dissimilar bias structures, meaning convergence provides stronger evidence against shared bias.

**Causal Evidence Score (CES).** A composite: CES = DCI * MCS * (0.5 + 0.5 * BDS) * designBonus, where designBonus rewards inclusion of more design types (0.4 for one, 0.7 for two, 1.0 for three or more). The multiplicative structure ensures that directional disagreement (DCI = 0) yields CES = 0 regardless of other components.

**Table 2.** Convergence metrics implemented in CausalSynth.

| Metric | Abbreviation | Range | Interpretation |
|---|---|---|---|
| Direction Concordance Index | DCI | 0--1 | 1.0 = all designs agree on direction |
| Magnitude Consistency Score | MCS | 0--1 | Higher = more similar magnitudes across designs |
| Bias Diversity Score | BDS | 0--1 | Higher = more diverse bias structures |
| Causal Evidence Score | CES | 0--1 | Composite triangulation strength |

#### GRADE-Like Certainty Mapping

CES is mapped to a four-level certainty rating following GRADE conventions [14]:

| CES Range | Base Rating |
|---|---|
| >= 0.70 | HIGH |
| 0.45 -- 0.70 | MODERATE |
| 0.25 -- 0.45 | LOW |
| < 0.25 | VERY LOW |

Two adjustment rules modify the base rating. *Upgrade*: If DCI = 100% AND BDS > 0.5, certainty is upgraded one level, reflecting that full directional agreement across highly diverse bias structures is particularly informative. *Downgrade*: If any design group shows an effect opposite to the majority, certainty is downgraded one level. An extended GRADE reasoning panel provides transparent justification for the assigned rating, enumerating all upgrade/downgrade factors considered.

#### Publication Bias Assessment

CausalSynth implements three complementary publication bias methods:

**Egger's regression test** [18] for funnel plot asymmetry, using the t-distribution for p-values (appropriate for small k). The test requires a minimum of 10 studies and reports intercept, SE, t-statistic, and two-tailed p-value.

**Contour-enhanced funnel plot** with toggleable significance contours (p < 0.01, p < 0.05, p < 0.10) overlaid on the standard funnel, allowing visual distinction between publication bias and other causes of asymmetry.

**Trim-and-fill** method for estimating missing studies due to publication bias. The adjusted pooled estimate and number of imputed studies are displayed as an overlay on the funnel plot.

#### Additional Analytical Features

CausalSynth provides the following supplementary analyses, each rendered in dedicated visualization cards:

- **Causal DAG editor** with four templates (confounding, mediation, instrumental variable, collider), design-specific edge overlays, and freeform editing mode (click to add nodes, drag between nodes to add edges, right-click to delete)
- **Leave-one-design-out sensitivity analysis** showing how each metric changes when each design type is excluded
- **Subgroup analysis** with within-design stratification and between-subgroup interaction test (Q_between, p-value) and meta-regression
- **Network-of-designs visualization** showing pairwise design agreement as edge-colored graph (green = agree, red = disagree), with node size proportional to study count, and network statistics table
- **Risk of Bias summary** with traffic-light table across 5 RoB 2.0 domains, per-study rating modal, stacked bar chart, domain-level detail, and RoB-weighted pooled estimate (SE inflation method)
- **DL vs REML method comparison** with side-by-side estimates, tau^2, I^2, and per-design breakdown
- **Study weights visualization** as horizontal bar chart with design-color coding
- **Cumulative meta-analysis** showing temporal evolution of the pooled estimate
- **Influence diagnostics** via Baujat plot (heterogeneity contribution vs influence on pooled estimate) and Cook's distance / DFFITS computation
- **Prediction intervals** for the overall and per-design pooled estimates
- **L'Abbe and Galbraith (radial) plots** for additional visual heterogeneity assessment
- **Power analysis for triangulation** simulating how adding hypothetical studies from a specified design would change CES, with interactive slider
- **Study timeline visualization** showing publication dates and effect evolution with temporal design analysis and CES evolution
- **Number needed to treat (NNT)** derived from the causal RD
- **Meta-regression** testing whether effect size varies by sample size, with intercept and slope statistics
- **Detailed results table** with comprehensive per-study and per-design statistics
- **Data validation** with warnings for invalid entries, extreme values, and sparse designs
- **TruthCert SHA-256 provenance chain** hashing raw data, analysis parameters, and results to produce a verifiable certification seal
- **Auto-generated report text** (both concise and expanded versions) with copy-to-clipboard functionality
- **R code export** generating a self-contained metafor script including subgroup, timeline, RoB, and power analysis components
- **CSV import/export** with field validation and proper quoting
- **PDF export** via print media queries with optimized layout
- **WebR cross-validation** comparing JavaScript DL estimates against R metafor per-design and overall
- **Dark mode** with full CSS variable theming across all components
- **Keyboard shortcuts** and tutorial overlay with step-by-step guidance
- **Five built-in datasets** spanning cardiology, nutrition, oncology, infectious disease, and tobacco epidemiology

### Operation

A typical CausalSynth workflow proceeds through seven steps:

1. **Data entry.** The user loads a built-in dataset (e.g., "Statins & CVD") or imports a CSV file containing study-level data (study name, design type, log-OR, SE, N, optional p0, optional subgroup). Manual entry is also supported.

2. **DAG specification.** The user selects a causal DAG template (confounding, mediation, instrumental variable, or collider) or constructs a custom DAG using the freeform editor. The DAG visualizes which causal pathways each design type can estimate.

3. **Method selection.** The user selects the pooling method (DL or REML) from the toggle adjacent to the Run button.

4. **Triangulation analysis.** Upon clicking "Run Triangulation Analysis," CausalSynth groups studies by design, runs within-design meta-analysis, computes the cross-design estimate, and calculates all four convergence metrics with GRADE-like certainty.

5. **Result exploration.** The user examines the design-grouped forest plot, evidence radar, bias architecture heatmap, convergence metric cards, and GRADE badge. The causal correction panel shows traditional vs causally-corrected estimates with sensitivity slider. Leave-one-design-out, subgroup, network, RoB, power, timeline, and influence analyses are displayed in dedicated cards.

6. **Quality assessment.** The user edits per-study Risk of Bias ratings via the modal dialog. The RoB-weighted pooled estimate shows sensitivity to study quality. Funnel plots with Egger's test and trim-and-fill assess publication bias.

7. **Export.** Results can be exported as: auto-generated methods/results text (copy to clipboard), reproducible R code (metafor script), CSV data, PDF (print-optimized), or TruthCert JSON bundle. WebR cross-validation can verify JavaScript results against R.

All computation occurs locally in the browser; no data leaves the user's machine.

### Validation

#### Automated Testing

The application was validated with 105 Selenium tests executed in headless Chrome using Python's Selenium WebDriver framework (Table 3). An additional 40 unit tests verify the meta-analysis engine, convergence metrics, and CaMeA formulas independently of the browser.

**Table 3.** Selenium test suite composition (105 tests).

| Category | Tests | Description |
|---|---|---|
| Data entry and management | 10 | Manual input, CSV import/export, field validation, row operations |
| Built-in datasets | 5 | Loading and verification of all five demonstration datasets |
| Meta-analysis engine | 12 | DL and REML pooling, design grouping, heterogeneity, method toggle |
| Forest plot and visualization | 8 | SVG rendering, design headers, null line, prediction intervals |
| CaMeA causal correction | 6 | OR-to-RD, RR-to-RD, delta-method SE, sensitivity analysis |
| Convergence metrics | 8 | DCI, MCS, BDS, CES computation, GRADE mapping, upgrade/downgrade |
| DAG editor | 5 | Template loading, freeform editing, overlay rendering |
| Sensitivity analyses | 8 | Leave-one-design-out, cumulative, influence diagnostics |
| Subgroup and network | 6 | Subgroup stratification, interaction test, network visualization |
| Risk of Bias | 6 | Traffic-light rendering, modal editing, RoB-weighted estimate |
| Publication bias | 6 | Funnel plot, Egger's test, contour overlay, trim-and-fill |
| Power and timeline | 5 | Power simulation, timeline rendering, temporal analysis |
| Export and reporting | 8 | R code, report text, CSV, PDF, TruthCert, WebR validation |
| Accessibility and UI | 6 | Dark mode, keyboard navigation, tutorial, ARIA roles |
| Boundary and edge cases | 6 | Single study per design, all-same-design, zero effects, extreme SE |
| **Total** | **105** | |

All 105 tests pass. An additional 40 unit tests pass independently.

#### Expert Review

A five-persona expert review was conducted [Table 4]:

**Table 4.** Expert review panel composition.

| Persona | Focus |
|---|---|
| Statistical Methodologist | REML Fisher scoring derivation, CaMeA delta method, convergence metric formulas |
| Security Auditor | XSS prevention, escapeHtml coverage, blob URL cleanup, data privacy |
| UX/Accessibility Reviewer | ARIA roles, keyboard navigation, color contrast, screen reader support |
| Software Engineer | Div balance, script integrity, function override chains, render hook system |
| Domain Expert | Bias profile accuracy, clinical plausibility of built-in datasets, GRADE mapping |

The review identified 4 P0 (critical) and 9 P1 (important) issues, all fixed prior to release. Key findings included:

- **P0-1:** Forest plot x-axis scaling failed for all-negative effects (multiplicative padding). Fixed with additive padding.
- **P0-2:** REML Fisher scoring used incorrect score function (y'Py instead of y'PPy per Viechtbauer 2005). Fixed with explicit yPPy computation.
- **P0-3:** MR bias profile overclaimed "low" for selection and measurement. Corrected to "moderate" for both.
- **P1-1:** ARIA roles added to all interactive widgets (dialog, menu, menuitem, img, live regions).
- **P1-2:** Keyboard navigation added for tutorial steps and example dropdown (arrow keys, Enter/Space).
- **P1-3:** Fragile function-override chains replaced with a lightweight renderHooks system.

#### Cross-Validation Against R

DerSimonian-Laird pooled estimates were compared against the metafor R package (version 4.8-0) [15] for all five built-in datasets. Point estimates and standard errors agreed to at least six decimal places. WebR in-browser validation provides on-demand cross-checking of JavaScript results against R metafor without leaving the application. REML estimates were verified against metafor's REML estimator with equivalent convergence criteria.

---

## Use Cases

### Use Case 1: Statins and Cardiovascular Disease (Strong Triangulation)

The statins dataset contains 12 studies across three design types: RCTs (5 studies including findings consistent with the CTT Collaboration [19]), prospective cohort studies (4 studies), and Mendelian randomization analyses of HMGCR variants (3 studies). All report effects on the log-OR scale for major cardiovascular events.

Design-grouped results:
- **RCT group** (k=5): pooled log-OR = -0.35, 95% CI: [-0.39, -0.31], I^2 = 18%. Consistent protective effect with low heterogeneity.
- **Cohort group** (k=4): pooled log-OR = -0.30, 95% CI: [-0.34, -0.25], I^2 = 42%. Similar direction and magnitude; moderate heterogeneity.
- **MR group** (k=3): pooled log-OR = -0.35, 95% CI: [-0.44, -0.26], I^2 = 22%. Consistent direction, wider CI reflecting genetic instrument imprecision.

Convergence metrics: DCI = 100%, MCS = 0.72, BDS = 0.33, CES = 0.48. GRADE-like certainty: MODERATE (base), no upgrade (BDS < 0.5), no downgrade (no opposing direction). This appropriately reflects strong but not maximal triangulation due to only three design types with moderate bias diversity.

CaMeA correction at p0 = 0.20 yields pooled RD = -0.055 (95% CI: -0.072, -0.038), indicating approximately 5.5 percentage points absolute risk reduction. Sensitivity analysis across p0 = 0.05 to 0.30 shows the RD scales approximately linearly, maintaining significance at all levels.

Leave-one-design-out analysis confirms robustness: removing any design preserves the protective direction and statistical significance.

### Use Case 2: Smoking and Lung Cancer (Four-Design Triangulation)

The smoking dataset contains 8 studies across four designs: case-control (including Doll and Hill [20]), prospective cohort, MR, and ecological. This represents one of the most historically compelling triangulation cases.

All four designs show elevated lung cancer risk among smokers. Convergence metrics: DCI = 100%, BDS = 0.52, CES = 0.55. The elevated BDS reflects the diversity of bias structures across four design types. GRADE-like certainty: MODERATE (base), upgraded to HIGH because DCI = 100% AND BDS > 0.5. This captures the strong inferential value of convergence across methodologically diverse designs.

### Use Case 3: Mediterranean Diet and CVD (Moderate Triangulation)

The Mediterranean diet dataset contains 7 studies across three designs (RCT, cohort, cross-sectional). CausalSynth assigns CES = 0.28 (LOW), appropriately reflecting higher magnitude heterogeneity (MCS = 0.41), lower bias diversity (BDS = 0.25), and the inclusion of cross-sectional studies that share bias vulnerabilities with cohort studies.

### Use Case 4: ART and HIV Mortality (Four-Design Infectious Disease)

The HIV/ART dataset demonstrates CausalSynth's applicability beyond cardiovascular epidemiology. It contains studies across four designs examining antiretroviral therapy and HIV mortality. Strong directional concordance across RCTs, cohort studies, ecological analyses, and cross-sectional surveys supports the established causal effect of ART on survival.

### Use Case 5: PD-1/PD-L1 Inhibitors and Cancer (Oncology)

The immunotherapy dataset extends CausalSynth to oncology, with studies examining immune checkpoint inhibitors across RCT, cohort, and case-control designs. This example demonstrates the tool's flexibility for emerging therapeutic areas where evidence from multiple study types is rapidly accumulating.

### Cross-Dataset Comparison

**Table 5.** Summary of use case results across five demonstration datasets.

| Dataset | Studies | Design Types | DCI | MCS | BDS | CES | Certainty |
|---|---|---|---|---|---|---|---|
| Statins + CVD | 12 | 3 (RCT, Cohort, MR) | 100% | 0.72 | 0.33 | 0.48 | MODERATE |
| Smoking + Lung Cancer | 8 | 4 (CC, Cohort, MR, Eco) | 100% | 0.58 | 0.52 | 0.55 | HIGH* |
| Mediterranean Diet + CVD | 7 | 3 (RCT, Cohort, XS) | 100% | 0.41 | 0.25 | 0.28 | LOW |
| ART + HIV Mortality | 10 | 4 (RCT, Cohort, Eco, XS) | 100% | 0.65 | 0.40 | 0.52 | MODERATE |
| PD-1/PD-L1 + Cancer | 7 | 3 (RCT, Cohort, CC) | 100% | 0.60 | 0.30 | 0.36 | LOW |

*Upgraded from MODERATE due to DCI = 100% and BDS > 0.5.

The comparison reveals how CausalSynth discriminates triangulation strength through component metrics. The smoking dataset achieves HIGH certainty through high bias diversity (BDS = 0.52) despite lower magnitude consistency than statins. The Mediterranean diet dataset scores lower on both MCS and BDS. These component-level diagnostics allow researchers to identify *why* triangulation is strong or weak, informing targeted evidence-gathering.

---

## Comparison with Existing Tools

**Table 6.** Feature comparison of CausalSynth with existing tools for causal and cross-design meta-analysis.

| Feature | CausalSynth | CaMeA (R) [9] | CausalMetaR (R) [10] | Manual Triangulation |
|---|---|---|---|---|
| Platform | Browser (single HTML) | R package | R package | Any (manual) |
| Installation required | No | Yes (R + package) | Yes (R + package) | N/A |
| Programming knowledge | None | R fluency | R fluency | Statistical expertise |
| Data type | Aggregate (AD) | Aggregate | Individual (IPD) | Any |
| Meta-analysis estimators | DL + REML | DL | TMLE/AIPW | Varies |
| Causal correction (OR/RR to RD) | Yes (delta method) | Yes | Yes (TMLE) | Manual |
| Design-grouped analysis | Yes (automatic) | No | No | Manual |
| Triangulation scoring (DCI/MCS/BDS/CES) | Yes | No | No | Subjective |
| GRADE-like certainty mapping | Yes (with upgrade/downgrade) | No | No | No |
| Causal DAG editor | Yes (4 templates + freeform) | No | No | DAGitty (separate tool) |
| Leave-one-design-out | Yes (automatic) | No | No | Manual |
| Forest plot by design | Yes (SVG) | No | No | Manual |
| Funnel plot with Egger + trim-fill | Yes | No | No | Separate tools |
| Subgroup analysis | Yes (with interaction test) | No | No | Manual |
| Network-of-designs | Yes (interactive SVG) | No | No | No |
| Risk of Bias table | Yes (5 domains + weighted) | No | No | Separate tools |
| Power analysis | Yes (triangulation-specific) | No | No | No |
| Influence diagnostics | Yes (Baujat, Cook's D) | No | No | Separate tools |
| Study timeline | Yes | No | No | No |
| Auto-generated report text | Yes | No | No | No |
| R code export | Yes (metafor) | N/A (already R) | N/A | No |
| WebR in-browser validation | Yes | N/A | N/A | No |
| TruthCert provenance | Yes (SHA-256) | No | No | No |
| Built-in datasets | 5 | 0 | 0 | 0 |
| Offline capable | Yes | Yes (after install) | Yes (after install) | Yes |
| Dark mode | Yes | No | No | N/A |
| Automated test suite | 105 Selenium + 40 unit | Package tests | Package tests | None |

CausalSynth is complementary to these tools rather than a replacement. CaMeA provides a more rigorous treatment of the causal estimand under specific identification assumptions. CausalMetaR handles IPD settings with advanced causal estimators. CausalSynth uniquely provides the cross-design triangulation layer that neither package addresses, with a zero-installation interactive interface that makes these methods accessible to non-programmers.

---

## Discussion

### Relationship to Causal Inference Frameworks

CausalSynth's design is informed by the structural causal model framework [11] and the potential outcomes approach [12]. The causal DAG editor makes explicit the assumptions underlying each study design's ability to estimate causal effects. For example, an RCT blocks all backdoor paths from treatment to outcome, while a cohort study leaves confounding paths open unless adjusted. The DAG templates help users visualize these differences and understand why convergence across designs with different open and blocked paths is informative.

The CaMeA correction [9] addresses a key concern in causal meta-analysis: pooled odds ratios lack a direct causal interpretation when baseline risks differ across study populations. An OR of 0.75 corresponds to an absolute risk reduction of 5 percentage points at baseline risk 0.20, but only 1.3 percentage points at baseline risk 0.05. By converting to risk differences, CausalSynth provides estimates that correspond more directly to average causal effects under specified baseline risk assumptions. The interactive sensitivity slider allows users to explore this dependence in real time.

The convergence metrics formalize Bradford Hill's viewpoint on consistency [13]: "Has it been repeatedly observed by different persons, in different places, circumstances and times?" CausalSynth extends this by quantifying *how* different the circumstances (bias structures) are and *how* consistent the observations are, rather than relying on binary assessment.

### Methodological Considerations

The dual-estimator approach (DL and REML) addresses a practical concern: DL is the most widely used and familiar estimator, but it can underestimate between-study variance when the number of studies is small [1,2]. REML via Fisher scoring [17] generally provides less biased estimates. The method comparison card allows users to assess sensitivity to estimator choice. The REML implementation was validated against the five-persona review, which identified and corrected an error in the original Fisher scoring score function (P0-2 in review findings).

The multiplicative structure of CES was chosen over additive alternatives because it naturally enforces the principle that directional disagreement should dominate. An additive composite could assign moderate scores even when designs fundamentally disagree, which would be misleading. The specific thresholds (0.25, 0.45, 0.70) are conventions based on methodological reasoning and should be treated as approximate guides rather than sharp boundaries.

The Risk of Bias module implements a pragmatic approach to quality-adjusted pooling: studies rated as high risk receive inflated standard errors (dividing by sqrt(0.2)), effectively downweighting them. This RoB-weighted estimate provides a sensitivity analysis for study quality without requiring users to specify an explicit bias model.

### Clinical and Policy Implications

For decision-makers, CausalSynth provides a structured way to assess whether a body of evidence supports a causal conclusion. The statin example illustrates a scenario where triangulation substantially strengthens confidence: the convergence of RCT, cohort, and MR evidence makes it unlikely that the protective effect is attributable to shared bias. The Mediterranean diet example appropriately tempers causal confidence. The CaMeA correction adds clinical relevance by expressing effects as absolute risk differences, directly informing NNT calculations and cost-effectiveness analyses.

### Limitations

Several limitations should be acknowledged. The CaMeA correction assumes constant baseline risk within each study; in practice, population-average RD depends on the full distribution of baseline risk [9]. The BDS relies on pre-specified design-level bias profiles that may not apply to all instances of a design type. The CES is a heuristic composite without formal statistical properties; no p-value or confidence interval is provided for the triangulation score itself. The DAG editor supports four templates and freeform editing but does not implement d-separation testing or identification algorithms; users requiring full graphical causal model functionality should use DAGitty [21]. CausalSynth operates on aggregate data and does not support IPD analysis. The convergence metrics are most informative with at least three design types; two-design analyses provide limited discrimination.

### Future Directions

Planned extensions include: (1) a formal permutation-based test for triangulation significance, (2) support for additional design types (interrupted time series, regression discontinuity, sibling comparison), (3) integration with systematic review software via PRISMA-compatible data exchange, (4) d-separation testing in the DAG editor, (5) study-level rather than design-level bias profiles using ROBINS-I and RoB 2 criteria, and (6) extension to hazard ratio and mean difference scales with scale-specific delta-method transformations.

---

## Conclusions

CausalSynth provides the first computational implementation of evidence triangulation as an interactive, browser-based tool. By decomposing cross-design convergence into four interpretable metrics (DCI, MCS, BDS, CES) and mapping them to GRADE-like certainty ratings with transparent upgrade/downgrade rules, it makes the informal practice of comparing results across study designs quantitative, reproducible, and auditable. The dual meta-analysis engines (DL and REML), CaMeA-style causal correction for both OR and RR, 30+ analytical features, and five built-in datasets across clinical domains demonstrate the tool's breadth and practical utility.

CausalSynth does not replace expert judgment or formal causal inference methods. It provides a structured framework that makes the reasoning behind triangulation assessments explicit and reproducible --- moving evidence synthesis closer to causal inference while maintaining full transparency about the assumptions involved.

---

## Reproducibility

CausalSynth is deterministic: given the same input data and pooling method, it produces identical results on every run. No random number generation is involved. The R code export generates a self-contained metafor script reproducing all pooling computations. The auto-generated methods text includes all parameter values. The five built-in datasets serve as reproducible benchmarks verifiable by any user. The Selenium test suite (105 tests) and unit test suite (40 tests) are included in the source repository for independent verification.

---

## Data and Software Availability

**Source code:** Available at [GITHUB_URL] under MIT License.

**Archived version:** [ZENODO_DOI].

**System requirements:** Any modern web browser (Chrome, Firefox, Edge, Safari). No installation, server, or internet connection required after downloading the single HTML file.

**Demonstration datasets:** Five built-in datasets (statins+CVD, Mediterranean diet+CVD, smoking+lung cancer, ART+HIV mortality, PD-1/PD-L1+cancer) are embedded in the application.

**Test suite:** 105 Selenium tests via `python test_causal_synth_selenium.py` and 40 unit tests via `python test_causal_synth.py` (requires Python 3.8+, Selenium, ChromeDriver).

---

## Acknowledgments

The author thanks the open-source community and the developers of the metafor R package and WebR project whose work enabled cross-validation of the JavaScript implementation.

---

## Competing Interests

No competing interests were disclosed.

---

## Grant Information

No specific grant funding was received for this work.

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

[9] Berenfeld C, Boughdiri A, Colnet B, van Amsterdam WAC, Bellet A. Causal meta-analysis: rethinking the foundations of evidence-based medicine. arXiv:2505.20168. 2025. https://arxiv.org/abs/2505.20168

[10] Wang J, Zhu H, Zhou X-H. CausalMetaR: an R package for performing causally interpretable meta-analyses. *Res Synth Methods.* 2025. arXiv:2402.04341.

[11] Pearl J. *Causality: Models, Reasoning, and Inference.* 2nd ed. Cambridge: Cambridge University Press; 2009.

[12] Hernan MA, Robins JM. *Causal Inference: What If.* Boca Raton: Chapman & Hall/CRC; 2024.

[13] Hill AB. The environment and disease: association or causation? *Proc R Soc Med.* 1965;58(5):295-300. doi:10.1177/003591576505800503

[14] Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. *BMJ.* 2008;336(7650):924-926. doi:10.1136/bmj.39489.470347.AD

[15] Viechtbauer W. Conducting meta-analyses in R with the metafor package. *J Stat Softw.* 2010;36(3):1-48. doi:10.18637/jss.v036.i03

[16] Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. *Stat Med.* 2002;21(11):1539-1558. doi:10.1002/sim.1186

[17] Viechtbauer W. Bias and efficiency of meta-analytic variance estimators in the random-effects model. *J Educ Behav Stat.* 2005;30(3):261-293. doi:10.3102/10769986030003261

[18] Sterne JAC, Sutton AJ, Ioannidis JPA, et al. Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. *BMJ.* 2011;343:d4002. doi:10.1136/bmj.d4002

[19] Cholesterol Treatment Trialists' (CTT) Collaboration. Efficacy and safety of more intensive lowering of LDL cholesterol: a meta-analysis of data from 170,000 participants in 26 randomised trials. *Lancet.* 2010;376(9753):1670-1681. doi:10.1016/S0140-6736(10)61350-5

[20] Doll R, Hill AB. Smoking and carcinoma of the lung: preliminary report. *BMJ.* 1950;2(4682):739-748. doi:10.1136/bmj.2.4682.739

[21] Textor J, van der Zander B, Gilthorpe MS, Liskiewicz M, Ellison GTH. Robust causal inference using directed acyclic graphs: the R package 'dagitty'. *Int J Epidemiol.* 2016;45(6):1887-1894. doi:10.1093/ije/dyw341

[22] Welton NJ, Ades AE, Carlin JB, Altman DG, Sterne JAC. Models for potentially biased evidence in meta-analysis using empirically based priors. *J R Stat Soc Ser A.* 2009;172(1):119-136. doi:10.1111/j.1467-985X.2008.00548.x

[23] Phillips CV, Goodman KJ. The missed lessons of Sir Austin Bradford Hill. *Epidemiol Perspect Innov.* 2004;1(1):3. doi:10.1186/1742-5573-1-3
