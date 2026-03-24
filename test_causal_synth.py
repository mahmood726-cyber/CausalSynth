"""
Comprehensive Selenium test suite for CausalSynth — Causal Evidence Triangulation Engine.
40 tests across 7 categories.
"""

import sys
import io
import time
import traceback

# UTF-8 encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "http://localhost:8781/causal-synth.html"

def create_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,1000")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(2)
    return driver


def load_example(driver, name):
    """Load an example dataset by clicking the dropdown and the example button."""
    # Click the "Load Example" dropdown toggle
    toggle = driver.find_element(By.CSS_SELECTOR, ".example-dropdown > button")
    toggle.click()
    time.sleep(0.3)
    # Click the specific example button
    buttons = driver.find_elements(By.CSS_SELECTOR, "#exampleDropdown button")
    for btn in buttons:
        if name.lower() in btn.text.lower():
            btn.click()
            break
    time.sleep(0.3)


def run_analysis(driver):
    """Click Run Triangulation Analysis and wait for results."""
    run_btn = driver.find_element(By.ID, "runBtn")
    driver.execute_script("arguments[0].click();", run_btn)
    # Wait for results section to be visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "results"))
    )
    time.sleep(0.5)


def load_and_run_statins(driver):
    """Load statins example and run analysis."""
    load_example(driver, "statins")
    run_analysis(driver)


# ============================================================
# Category 1: Page Load & UI (5 tests)
# ============================================================

def test_01_page_title(driver):
    """Page loads with correct title containing 'CausalSynth'."""
    driver.get(URL)
    time.sleep(0.5)
    assert "CausalSynth" in driver.title, f"Title was: {driver.title}"


def test_02_design_legend_6_types(driver):
    """Design legend shows 6 design types."""
    driver.get(URL)
    time.sleep(0.5)
    items = driver.find_elements(By.CSS_SELECTOR, "#designLegend .leg-item")
    assert len(items) == 6, f"Expected 6 legend items, got {len(items)}"


def test_03_data_table_renders_empty_rows(driver):
    """Study data table renders with empty rows on load."""
    driver.get(URL)
    time.sleep(0.5)
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    assert len(rows) >= 1, f"Expected at least 1 empty row, got {len(rows)}"
    # Verify table headers
    headers = driver.find_elements(By.CSS_SELECTOR, "#dataTable thead th")
    assert len(headers) >= 7, f"Expected at least 7 headers, got {len(headers)}"


def test_04_design_dropdown_6_options(driver):
    """Design dropdown in table rows has 6 options (RCT, Cohort, Case-Ctrl, MR, Ecological, Cross-Sec)."""
    driver.get(URL)
    time.sleep(0.5)
    # Get the first design dropdown in the data table
    select = driver.find_element(By.CSS_SELECTOR, "#dataBody tr select[data-f='design']")
    options = select.find_elements(By.TAG_NAME, "option")
    assert len(options) == 6, f"Expected 6 design options, got {len(options)}"
    option_texts = [o.text for o in options]
    expected = ["RCT", "Cohort", "Case-Ctrl", "MR", "Ecological", "Cross-Sec"]
    for exp in expected:
        assert exp in option_texts, f"Missing option: {exp}. Found: {option_texts}"


def test_05_dark_mode_toggle(driver):
    """Dark mode toggle works."""
    driver.get(URL)
    time.sleep(0.5)
    body = driver.find_element(By.TAG_NAME, "body")
    assert "dark" not in body.get_attribute("class"), "Should start in light mode"
    btn = driver.find_element(By.ID, "themeBtn")
    btn.click()
    time.sleep(0.3)
    assert "dark" in body.get_attribute("class"), "Body should have 'dark' class after toggle"
    assert btn.text == "Light Mode", f"Button text should be 'Light Mode', got '{btn.text}'"
    # Toggle back
    btn.click()
    time.sleep(0.3)
    assert "dark" not in body.get_attribute("class"), "Should return to light mode"


# ============================================================
# Category 2: Data Input (5 tests)
# ============================================================

def test_06_load_statins_12_studies(driver):
    """Load Statins example -> 12 studies appear."""
    driver.get(URL)
    time.sleep(0.5)
    load_example(driver, "statins")
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    assert len(rows) == 12, f"Expected 12 studies, got {len(rows)}"
    badge = driver.find_element(By.ID, "studyBadge")
    assert "12" in badge.text, f"Badge should show 12 studies, got '{badge.text}'"


def test_07_load_meddiet_7_studies(driver):
    """Load Mediterranean Diet example -> 7 studies appear."""
    driver.get(URL)
    time.sleep(0.5)
    load_example(driver, "mediterranean")
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    assert len(rows) == 7, f"Expected 7 studies, got {len(rows)}"


def test_08_load_smoking_8_studies(driver):
    """Load Smoking example -> 8 studies appear."""
    driver.get(URL)
    time.sleep(0.5)
    load_example(driver, "smoking")
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    assert len(rows) == 8, f"Expected 8 studies, got {len(rows)}"


def test_09_dataset_dropdown_5_options(driver):
    """Dataset dropdown has 5 example options."""
    driver.get(URL)
    time.sleep(0.5)
    # Open the dropdown
    toggle = driver.find_element(By.CSS_SELECTOR, ".example-dropdown > button")
    toggle.click()
    time.sleep(0.3)
    buttons = driver.find_elements(By.CSS_SELECTOR, "#exampleDropdown button[role='menuitem']")
    assert len(buttons) == 5, f"Expected 5 example options, got {len(buttons)}"


def test_10_clear_all(driver):
    """Clear All empties table, disables run button."""
    driver.get(URL)
    time.sleep(0.5)
    load_example(driver, "statins")
    # Now clear
    clear_btn = driver.find_element(By.XPATH, "//button[text()='Clear All']")
    clear_btn.click()
    time.sleep(0.3)
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    assert len(rows) == 0, f"Expected 0 rows after clear, got {len(rows)}"
    run_btn = driver.find_element(By.ID, "runBtn")
    assert not run_btn.is_enabled(), "Run button should be disabled after Clear All"


# ============================================================
# Category 3: Core Triangulation Engine (10 tests)
# ============================================================

def test_11_statins_3_designs(driver):
    """Statins: 3 study designs detected."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    n_designs = driver.execute_script("return triResults.nDesigns")
    assert n_designs == 3, f"Expected 3 designs, got {n_designs}"


def test_12_direction_concordance_100(driver):
    """Direction concordance = 100% for statins."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    dci = driver.execute_script("return triResults.DCI")
    assert dci == 1.0, f"Expected DCI=1.0, got {dci}"


def test_13_ces_reasonable(driver):
    """CES >= 0.4 (should be 'Strong' or 'Moderate' with formula)."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    ces = driver.execute_script("return triResults.CES")
    assert ces >= 0.4, f"Expected CES >= 0.4, got {ces}"


def test_14_pooled_effect_negative(driver):
    """Overall pooled effect is negative (protective) for statins."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    theta = driver.execute_script("return triResults.overallResult.theta")
    assert theta < 0, f"Expected negative pooled effect, got {theta}"


def test_15_I2_reasonable(driver):
    """I-squared (overall) is reasonable (< 50%) for statins."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    i2 = driver.execute_script("return triResults.overallResult.I2")
    assert i2 < 50, f"Expected I2 < 50, got {i2}"


def test_16_forest_plot_renders(driver):
    """Design-grouped forest plot renders (SVG with study labels)."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    svg = driver.find_element(By.CSS_SELECTOR, "#forestContainer svg")
    assert svg is not None, "Forest plot SVG not found"
    # Check for study labels (text elements)
    texts = svg.find_elements(By.TAG_NAME, "text")
    assert len(texts) > 10, f"Expected >10 text elements in forest plot, got {len(texts)}"
    # Check for a known study label
    svg_html = driver.execute_script("return arguments[0].innerHTML", svg)
    assert "CTT 2010" in svg_html, "Expected 'CTT 2010' study label in forest plot"


def test_17_evidence_radar_renders(driver):
    """Evidence radar renders (SVG)."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    svg = driver.find_element(By.CSS_SELECTOR, "#radarContainer svg")
    assert svg is not None, "Radar SVG not found"
    # Check for polygon (triangulation shape) or lines
    svg_html = driver.execute_script("return arguments[0].innerHTML", svg)
    assert "polygon" in svg_html or "line" in svg_html, "Radar should contain polygon or line elements"


def test_18_bias_table_renders(driver):
    """Bias architecture table renders with 5 bias columns."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    table = driver.find_element(By.CSS_SELECTOR, "#biasContainer table.bias-table")
    assert table is not None, "Bias table not found"
    headers = table.find_elements(By.CSS_SELECTOR, "thead th")
    # Should be "Design" + 5 bias columns = 6 headers
    assert len(headers) == 6, f"Expected 6 headers (Design + 5 bias), got {len(headers)}"
    # Verify bias column names
    header_texts = [h.text for h in headers]
    assert "Confounding" in header_texts, f"Missing 'Confounding' in headers: {header_texts}"
    assert "Selection" in header_texts, f"Missing 'Selection' in headers: {header_texts}"


def test_19_between_design_diamond(driver):
    """Between-design pooled diamond appears in forest plot."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    svg_html = driver.execute_script(
        "return document.querySelector('#forestContainer svg').innerHTML"
    )
    # Check for "Between-Design Pooled" header and diamond (polygon)
    assert "Between-Design Pooled" in svg_html, "Expected 'Between-Design Pooled' label in forest"
    assert "<polygon" in svg_html, "Expected diamond (polygon) in forest plot"


def test_20_interpretation_causal_evidence(driver):
    """Interpretation panel contains 'Causal Evidence' text."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    panel = driver.find_element(By.ID, "interpPanel")
    text = panel.text
    assert "Causal Evidence" in text, f"Expected 'Causal Evidence' in interpretation, got: {text[:200]}"


# ============================================================
# Category 4: CaMeA Causal Correction (4 tests)
# ============================================================

def test_21_causal_correction_card_renders(driver):
    """Causal correction card renders."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    card = driver.find_element(By.ID, "causalCorrectionCard")
    # The card uses display:none when no p0 data - for statins without explicit p0 it uses defaultP0=0.2
    display = driver.execute_script("return getComputedStyle(arguments[0]).display", card)
    assert display != "none", f"Causal correction card should be visible, got display={display}"


def test_22_traditional_OR_and_causal_RD(driver):
    """Shows traditional OR and causal RD."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    grid = driver.find_element(By.ID, "causalGrid")
    boxes = grid.find_elements(By.CSS_SELECTOR, ".causal-box")
    assert len(boxes) >= 3, f"Expected at least 3 causal boxes, got {len(boxes)}"
    grid_text = grid.text
    assert "Traditional" in grid_text or "OR" in grid_text, f"Expected OR label, got: {grid_text[:200]}"
    assert "RD" in grid_text or "Causal" in grid_text, f"Expected RD label, got: {grid_text[:200]}"


def test_23_sensitivity_table_5_baselines(driver):
    """Sensitivity table has rows for 5 baseline risk levels."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    rows = driver.find_elements(By.CSS_SELECTOR, "#causalSensContainer table.causal-sens-table tbody tr")
    assert len(rows) == 5, f"Expected 5 sensitivity rows (p0=0.05,0.1,0.2,0.3,0.5), got {len(rows)}"


def test_24_rd_values_reasonable(driver):
    """RD values are in reasonable range (not NaN, not >100%)."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    # Read the causal RD value from JavaScript
    rd = driver.execute_script("""
        var defaultP0 = 0.2;
        var rdYi = [];
        var rdSei = [];
        for (var s of studies) {
            var p0 = s.p0 || defaultP0;
            var OR = Math.exp(s.yi);
            var denom = 1 + (OR - 1) * p0;
            if (denom <= 0) continue;
            var p1 = OR * p0 / denom;
            var rd = p1 - p0;
            var drdDlogOR = OR * p0 * (1 - p0) / (denom * denom);
            var rdSe = Math.abs(drdDlogOR) * s.se;
            if (rdSe > 0 && isFinite(rd) && isFinite(rdSe)) {
                rdYi.push(rd);
                rdSei.push(rdSe);
            }
        }
        var result = dlMeta(rdYi, rdSei);
        return result ? result.theta : null;
    """)
    assert rd is not None, "RD computation returned null"
    assert abs(rd) < 1.0, f"RD should be < 100% (i.e., < 1.0), got {rd}"
    assert rd == rd, "RD is NaN"  # NaN != NaN


# ============================================================
# Category 5: Phase 3 Features (10 tests)
# ============================================================

def test_25_dag_editor_exists(driver):
    """DAG editor card exists."""
    driver.get(URL)
    time.sleep(0.5)
    card = driver.find_element(By.ID, "dagCard")
    assert card is not None, "DAG card not found"
    heading = card.find_element(By.TAG_NAME, "h2")
    assert "DAG" in heading.text or "Causal" in heading.text, f"DAG card heading: {heading.text}"


def test_26_dag_template_4_options(driver):
    """DAG template dropdown has 4 options (plus placeholder)."""
    driver.get(URL)
    time.sleep(0.5)
    select = driver.find_element(By.ID, "dagTemplate")
    options = select.find_elements(By.TAG_NAME, "option")
    # 1 placeholder + 4 templates = 5 options; we check for 4 real ones
    real_options = [o for o in options if o.get_attribute("value")]
    assert len(real_options) == 4, f"Expected 4 DAG templates, got {len(real_options)}"
    vals = [o.get_attribute("value") for o in real_options]
    assert "confounding" in vals, f"Missing 'confounding' template: {vals}"
    assert "mediation" in vals, f"Missing 'mediation' template: {vals}"
    assert "iv" in vals, f"Missing 'iv' template: {vals}"
    assert "collider" in vals, f"Missing 'collider' template: {vals}"


def test_27_confounding_dag_renders_nodes(driver):
    """Selecting 'Simple Confounding' renders nodes in SVG."""
    driver.get(URL)
    time.sleep(0.5)
    select = driver.find_element(By.ID, "dagTemplate")
    # Use JS to set value and trigger change event
    driver.execute_script("""
        var sel = arguments[0];
        sel.value = 'confounding';
        sel.dispatchEvent(new Event('change'));
    """, select)
    time.sleep(0.5)
    svg = driver.find_element(By.ID, "dagSvg")
    svg_html = driver.execute_script("return arguments[0].innerHTML", svg)
    # Should have circle elements for nodes
    circles = svg.find_elements(By.TAG_NAME, "circle")
    assert len(circles) >= 3, f"Expected at least 3 node circles, got {len(circles)}"
    # Should have node labels
    assert "Exposure" in svg_html, "Missing 'Exposure' label in DAG"
    assert "Outcome" in svg_html, "Missing 'Outcome' label in DAG"
    assert "Confounder" in svg_html, "Missing 'Confounder' label in DAG"


def test_28_grade_badge_in_metrics(driver):
    """GRADE badge appears in convergence metrics."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    metrics = driver.find_element(By.ID, "convMetrics")
    badges = metrics.find_elements(By.CSS_SELECTOR, ".grade-badge")
    assert len(badges) >= 1, "Expected at least 1 GRADE badge in convergence metrics"
    badge_text = badges[0].text.strip()
    assert any(g in badge_text for g in ["HIGH", "MODERATE", "LOW", "VERY LOW"]), \
        f"GRADE badge text unexpected: '{badge_text}'"


def test_29_grade_level_reasonable_statins(driver):
    """GRADE level is reasonable for statins (MODERATE or HIGH)."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    grade = driver.execute_script("""
        return getGRADECertainty(triResults.CES, triResults.DCI, triResults.BDS, triResults.designResults).level;
    """)
    assert grade in ["HIGH", "MODERATE"], f"Expected MODERATE or HIGH for statins, got '{grade}'"


def test_30_methods_text_renders(driver):
    """Methods text card renders with copyable text."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    report_text = driver.find_element(By.ID, "reportText")
    text = report_text.text
    assert "METHODS" in text, f"Report should contain 'METHODS', got: {text[:200]}"
    assert "DerSimonian-Laird" in text, "Report should mention DerSimonian-Laird"


def test_31_results_text_with_study_count(driver):
    """Results text card renders with study count."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    report_text = driver.find_element(By.ID, "reportText")
    text = report_text.text
    assert "RESULTS" in text, f"Report should contain 'RESULTS', got: {text[:200]}"
    assert "12 studies" in text, f"Report should mention '12 studies', got: {text[:400]}"


def test_32_copy_button_exists(driver):
    """Copy button exists and is clickable."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    copy_btn = driver.find_element(By.CSS_SELECTOR, "#reportCard .copy-btn")
    assert copy_btn is not None, "Copy button not found"
    assert copy_btn.text.strip() in ["Copy to Clipboard", "Copied!"], \
        f"Copy button text unexpected: '{copy_btn.text}'"
    assert copy_btn.is_displayed(), "Copy button should be visible"


def test_33_r_code_export_button(driver):
    """R code export button exists in header."""
    driver.get(URL)
    time.sleep(0.5)
    # Find the Export R Code button in header
    header_btns = driver.find_elements(By.CSS_SELECTOR, "header .hdr-btns button")
    r_btn = None
    for btn in header_btns:
        if "R Code" in btn.text:
            r_btn = btn
            break
    assert r_btn is not None, "Export R Code button not found in header"
    assert r_btn.is_displayed(), "Export R Code button should be visible"


def test_34_leave_one_design_out_table(driver):
    """Leave-one-design-out sensitivity table renders."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    container = driver.find_element(By.ID, "sensitivityContainer")
    table = container.find_element(By.CSS_SELECTOR, "table.sens-table")
    assert table is not None, "Sensitivity table not found"
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    assert len(rows) >= 1, f"Expected at least 1 sensitivity row, got {len(rows)}"


# ============================================================
# Category 6: Sensitivity Analysis (3 tests)
# ============================================================

def test_35_sens_one_row_per_design(driver):
    """Sensitivity table shows one row per design."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    rows = driver.find_elements(By.CSS_SELECTOR, "#sensitivityContainer table.sens-table tbody tr")
    # Statins has 3 designs: RCT, cohort, MR
    assert len(rows) == 3, f"Expected 3 rows (one per design), got {len(rows)}"


def test_36_direction_same_column(driver):
    """'Direction Same?' column shows Yes/No with colors."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    rows = driver.find_elements(By.CSS_SELECTOR, "#sensitivityContainer table.sens-table tbody tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        # Direction Same? is the 5th column (index 4)
        dir_cell = cells[4]
        text = dir_cell.text.strip()
        assert text in ["Yes", "No"], f"Direction Same? should be Yes/No, got '{text}'"
        color = dir_cell.value_of_css_property("color")
        assert color is not None, "Direction cell should have a color"


def test_37_no_direction_reversal_statins(driver):
    """Removing any single design doesn't reverse direction for statins."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    rows = driver.find_elements(By.CSS_SELECTOR, "#sensitivityContainer table.sens-table tbody tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        design_removed = cells[0].text.strip()
        dir_same = cells[4].text.strip()
        assert dir_same == "Yes", f"Removing {design_removed} reverses direction (expected 'Yes', got '{dir_same}')"


# ============================================================
# Category 7: CSV Import & Export (3 tests)
# ============================================================

def test_38_import_csv_button(driver):
    """Import CSV button exists."""
    driver.get(URL)
    time.sleep(0.5)
    import_area = driver.find_element(By.CSS_SELECTOR, ".import-area")
    assert import_area is not None, "Import area not found"
    import_btn = import_area.find_element(By.TAG_NAME, "button")
    assert "Import" in import_btn.text, f"Expected 'Import' in button text, got '{import_btn.text}'"
    file_input = import_area.find_element(By.CSS_SELECTOR, "input[type='file']")
    assert file_input is not None, "File input for CSV import not found"


def test_39_export_csv_button(driver):
    """Export CSV button exists."""
    driver.get(URL)
    time.sleep(0.5)
    header_btns = driver.find_elements(By.CSS_SELECTOR, "header .hdr-btns button")
    export_btn = None
    for btn in header_btns:
        if "Export CSV" in btn.text:
            export_btn = btn
            break
    assert export_btn is not None, "Export CSV button not found"
    assert export_btn.is_displayed(), "Export CSV button should be visible"


def test_40_export_no_console_errors(driver):
    """Export doesn't produce console errors."""
    driver.get(URL)
    time.sleep(0.5)
    load_and_run_statins(driver)
    # Clear any existing logs
    driver.get_log("browser")
    # Attempt export via JS (direct call avoids file dialog)
    driver.execute_script("exportResults()")
    time.sleep(0.5)
    logs = driver.get_log("browser")
    errors = [l for l in logs if l.get("level") == "SEVERE"]
    assert len(errors) == 0, f"Console errors during export: {errors}"


# ============================================================
# Test Runner
# ============================================================

ALL_TESTS = [
    # Category 1: Page Load & UI
    test_01_page_title,
    test_02_design_legend_6_types,
    test_03_data_table_renders_empty_rows,
    test_04_design_dropdown_6_options,
    test_05_dark_mode_toggle,
    # Category 2: Data Input
    test_06_load_statins_12_studies,
    test_07_load_meddiet_7_studies,
    test_08_load_smoking_8_studies,
    test_09_dataset_dropdown_5_options,
    test_10_clear_all,
    # Category 3: Core Triangulation Engine
    test_11_statins_3_designs,
    test_12_direction_concordance_100,
    test_13_ces_reasonable,
    test_14_pooled_effect_negative,
    test_15_I2_reasonable,
    test_16_forest_plot_renders,
    test_17_evidence_radar_renders,
    test_18_bias_table_renders,
    test_19_between_design_diamond,
    test_20_interpretation_causal_evidence,
    # Category 4: CaMeA Causal Correction
    test_21_causal_correction_card_renders,
    test_22_traditional_OR_and_causal_RD,
    test_23_sensitivity_table_5_baselines,
    test_24_rd_values_reasonable,
    # Category 5: Phase 3 Features
    test_25_dag_editor_exists,
    test_26_dag_template_4_options,
    test_27_confounding_dag_renders_nodes,
    test_28_grade_badge_in_metrics,
    test_29_grade_level_reasonable_statins,
    test_30_methods_text_renders,
    test_31_results_text_with_study_count,
    test_32_copy_button_exists,
    test_33_r_code_export_button,
    test_34_leave_one_design_out_table,
    # Category 6: Sensitivity Analysis
    test_35_sens_one_row_per_design,
    test_36_direction_same_column,
    test_37_no_direction_reversal_statins,
    # Category 7: CSV Import & Export
    test_38_import_csv_button,
    test_39_export_csv_button,
    test_40_export_no_console_errors,
]

def main():
    print("=" * 70)
    print("CausalSynth Selenium Test Suite")
    print("=" * 70)

    driver = create_driver()
    passed = 0
    failed = 0
    failures = []

    try:
        for i, test_fn in enumerate(ALL_TESTS, 1):
            name = test_fn.__doc__ or test_fn.__name__
            try:
                test_fn(driver)
                print(f"  PASS  [{i:2d}/40] {name}")
                passed += 1
            except Exception as e:
                print(f"  FAIL  [{i:2d}/40] {name}")
                print(f"          -> {e}")
                traceback.print_exc(limit=2)
                failed += 1
                failures.append((i, name, str(e)))
    finally:
        # Capture final console logs
        try:
            logs = driver.get_log("browser")
            severe = [l for l in logs if l.get("level") == "SEVERE"]
            if severe:
                print(f"\n--- Browser Console Errors ({len(severe)}) ---")
                for log in severe[:10]:
                    print(f"  {log['message'][:200]}")
        except:
            pass
        driver.quit()

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} PASSED, {failed} FAILED out of {passed + failed} tests")
    print("=" * 70)

    if failures:
        print("\nFailed tests:")
        for num, name, err in failures:
            print(f"  [{num:2d}] {name}")
            print(f"       {err}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
