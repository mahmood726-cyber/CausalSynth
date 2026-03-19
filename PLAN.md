# CausalSynth: Causal Evidence Triangulation Engine — Implementation Plan

## Vision
The world's first browser-based tool for **causally interpretable meta-analysis** with **cross-design evidence triangulation**. Traditional meta-analysis pools effect estimates (OR, RR) without causal interpretation — CausalSynth corrects this using the CaMeA framework (Berenfeld et al., 2025) and triangulates evidence across RCTs, cohort studies, case-control studies, and Mendelian randomization analyses to produce Convergence of Evidence scores.

**No browser tool exists.** R packages CausalMetaR and CaMeA shipped in early 2025. This would be a world first.

## Why This Is Transformational
- Addresses a fundamental flaw: pooled OR/RR from heterogeneous populations lack causal interpretation
- Evidence triangulation (Lawlor 2016, Munafò 2017) is theoretical — no computational tool implements it
- Integrates naturally with TruthCert (proof-carrying CAUSAL claims, not just statistical claims)
- Publishable in BMJ/Lancet-tier journals (methods + tool paper)
- Builds on user's existing MA engines, WebR, and TruthCert infrastructure

## Core Concepts

### 1. The Causal Meta-Analysis Problem
Traditional MA assumes: if Study A reports OR=1.5 and Study B reports OR=2.0, the pooled OR is ~1.7.

But Berenfeld et al. (2025) showed:
- For **nonlinear** measures (OR, RR), the pooled effect depends on the **distribution of covariates** in each study population
- Different study populations → different covariate distributions → the pooled OR is NOT a causal average treatment effect
- **CaMeA solution**: use causal aggregation formulas that account for population heterogeneity

### 2. Evidence Triangulation
Different study designs have different strengths/biases:
- **RCTs**: No confounding, but limited generalizability + selection bias
- **Cohort studies**: Better generalizability, but unmeasured confounding
- **Case-control**: Efficient for rare outcomes, but recall bias + selection bias
- **Mendelian randomization**: No traditional confounding, but pleiotropy + weak instruments
- **Ecological**: Population-level trends, but ecological fallacy

**Triangulation principle**: If multiple designs with DIFFERENT bias structures all point to the same conclusion → stronger causal evidence than any single design.

### 3. Convergence Scoring
Quantify how well evidence converges across designs:
- Direction agreement (all point same way?)
- Magnitude consistency (effects within plausible range?)
- Statistical significance pattern
- Bias-adjusted estimates

## Architecture

### Single-file HTML app (`causal-synth.html`)
- Target: ~20K-30K lines (mature)
- Seeded PRNG for reproducibility
- WebR for CaMeA/CausalMetaR cross-validation
- TruthCert integration

### Core Modules

#### 1. Multi-Design Data Input
For each study, capture:
- **Design type**: RCT, prospective cohort, retrospective cohort, case-control, MR, ecological, cross-sectional
- **Effect estimate**: OR, RR, HR, MD, SMD + CI/SE
- **Population characteristics**: age range, sex ratio, region, key covariates
- **Bias assessment**: Design-specific (RoB 2 for RCTs, ROBINS-I for observational, STROBE-MR for MR)
- **Sample size**: N, events

Import: CSV, manual entry, or paste from existing MetaSprint/TruthCert exports.

#### 2. Causal DAG Module
- Visual DAG editor (drag-and-drop nodes, edges)
- Pre-built templates for common causal structures:
  - Confounding (classic arrow pattern)
  - Mediation (A → M → Y)
  - Collider (A → C ← B)
  - Instrumental variable (MR: G → X → Y, G ⊥⊥ confounders)
- For each design, overlay which paths are blocked/unblocked
- Identify: which biases each design addresses, which remain
- **Output**: "bias signature" per design (vector of addressed/unaddressed bias types)

#### 3. Causal Aggregation Engine (CaMeA Implementation)
Implement Berenfeld et al. (2025) causal aggregation:

**For linear measures (MD, SMD)**:
- Standard random-effects is causally valid (causal effect = weighted average)
- Traditional DL/REML applies directly

**For nonlinear measures (OR, RR)**:
- Traditional pooled OR ≠ causal average treatment effect
- CaMeA correction:
  1. Estimate study-specific causal effects on probability scale
  2. Standardize to a common target population
  3. Re-aggregate on probability scale
  4. Convert back to OR/RR scale
- Requires: marginal baseline risks per study (or assumptions)
- Sensitivity analysis: range of plausible baseline risk distributions

**For HR**:
- Collapsibility issues similar to OR
- Marginal vs conditional hazard ratio distinction
- Apply CaMeA-style correction when covariate distributions available

**Output**: Traditional pooled effect vs Causally-corrected pooled effect, with discrepancy highlighted.

#### 4. Design-Specific Bias Models
For each study design, model the expected bias:

| Design | Primary Biases | Bias Direction Model |
|--------|---------------|---------------------|
| RCT | Selection, attrition | Typically away from null (inflate) |
| Cohort | Confounding, selection | Direction depends on confounders |
| Case-control | Recall, selection | Typically away from null |
| MR | Pleiotropy, weak instruments | Toward null (dilution) |
| Ecological | Ecological fallacy | Unpredictable |

- Phillips & Smith (2020) cross-design bias framework
- Turner et al. (2009) predictive distributions for bias
- Welton et al. (2009) bias-adjusted synthesis

#### 5. Triangulation Engine
**Step 1**: Group studies by design type
**Step 2**: Run design-specific meta-analyses (standard RE model per design)
**Step 3**: Apply CaMeA causal correction within each design group
**Step 4**: Compute convergence metrics:

- **Direction Concordance Index (DCI)**: proportion of design groups agreeing on direction
  - DCI = 1.0 → all designs agree
  - DCI < 0.5 → concerning discordance
- **Magnitude Consistency Score (MCS)**: Cochran's Q across design-group estimates
  - Low Q → magnitude consistent across designs
  - High Q → designs disagree on effect size
- **Bias-Diversity Score (BDS)**: How different are the bias signatures across concordant designs?
  - High BDS + high DCI → strong triangulation (different biases, same answer)
  - Low BDS + high DCI → weak triangulation (same biases, same answer — could be same bias driving all)
- **Overall Causal Evidence Score (CES)**: Composite of DCI × BDS × precision weight
  - CES ∈ [0, 1]: 0 = no causal evidence, 1 = strong convergent causal evidence

**Step 5**: Sensitivity analysis on bias assumptions

#### 6. Visualization Suite

**A. Triangulation Map** (Primary visualization)
- Radial/spoke diagram: each spoke = one study design
- Spoke length = effect magnitude
- Spoke color = significance
- Center region = convergence zone
- If all spokes point same direction with similar magnitude → visual convergence

**B. Evidence Stream Forest Plot**
- Grouped forest plot: one section per design type
- Design-specific pooled estimates
- Cross-design pooled estimate (traditional vs causal)
- Discrepancy highlight (traditional ≠ causal)

**C. Bias Architecture Heatmap**
- Rows = studies, Columns = bias types
- Color = bias risk (green/yellow/red)
- Shows which biases each design addresses

**D. Convergence Dashboard**
- DCI, MCS, BDS, CES gauges
- Traffic-light summary
- Natural language interpretation

**E. Causal DAG Viewer**
- Interactive DAG with overlay per design
- Shows which causal paths each design blocks

#### 7. Reporting & Export
- Cross-design evidence summary (auto-generated text)
- Triangulation figure (SVG/PNG)
- R code export (CaMeA + CausalMetaR replication)
- TruthCert bundle: causal claims with evidence provenance
- GRADE-CERQual style assessment mapped to CES

## Implementation Phases

### Phase 1: Foundation + Traditional Cross-Design MA (MVP)
- Multi-design data input (3 designs: RCT, cohort, MR)
- Design-grouped forest plot
- Standard RE pooling within and across designs
- Direction concordance index
- 1 built-in dataset (e.g., statins + CVD: RCT + cohort + MR evidence)
- **Target: ~6K lines**

### Phase 2: Causal Aggregation
- CaMeA implementation for OR/RR
- Traditional vs causal pooled effect comparison
- Sensitivity analysis for baseline risk assumptions
- Bias model framework (3 bias types per design)
- Magnitude consistency score
- **Target: ~14K lines**

### Phase 3: Full Triangulation
- All 7 design types supported
- Causal DAG editor
- Bias-Diversity Score + Causal Evidence Score
- Triangulation map visualization
- Bias architecture heatmap
- Convergence dashboard
- **Target: ~22K lines**

### Phase 4: Publication-Ready
- Auto-generated reporting text
- WebR validation (CaMeA + CausalMetaR parity)
- TruthCert integration
- 3+ built-in datasets
- Tutorial walkthrough
- Dark mode, accessibility, PDF export
- Multi-persona review + manuscript
- **Target: ~28K lines**

## Testing Strategy
- Unit: CaMeA formulas reproduce R package results (tolerance 1e-6)
- Integration: multi-design input → triangulation output pipeline
- Property: adding a concordant design → CES increases
- Property: adding a discordant design → CES decreases
- Edge cases: single-design (degenerates to standard MA), all-RCT (triangulation = weak)
- WebR: CausalMetaR cross-validation for causal estimates
- Selenium: 200+ tests across all modules

## Key References
- Berenfeld et al. (2025) Causal meta-analysis. arXiv 2505.20168.
- Wang et al. (2025) CausalMetaR. Research Synthesis Methods.
- Lawlor et al. (2016) Triangulation in aetiological epidemiology. IJE.
- Munafò & Davey Smith (2018) Robust research via triangulation. Nature.
- Phillips & Smith (2020) Bayesian cross-design synthesis.
- Welton et al. (2009) Mixed treatment comparisons with design adjustment.
- Turner et al. (2009) Predictive distributions for bias.
- Hernán & Robins (2024) Target trial emulation. NEJM.

## Success Criteria
- [ ] CaMeA causal aggregation matches R package within 1e-6
- [ ] Triangulation map correctly visualizes convergence/divergence
- [ ] CES score responds correctly to adding concordant/discordant evidence
- [ ] Causal DAG editor functional with 3+ templates
- [ ] 200+ Selenium tests pass
- [ ] TruthCert bundle validates causal claims
- [ ] Publishable paper demonstrating causal correction changes pooled estimate by >10% in real data
