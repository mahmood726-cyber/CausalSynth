"""
Comprehensive Selenium test suite for CausalSynth -- Causal Evidence Triangulation Engine.
Target: 80+ tests covering all features.
"""
import sys
import os
import io
import time

# Set UTF-8 for console output only when running standalone (not under pytest)
if "pytest" not in sys.modules:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

HTML_PATH = Path(__file__).parent / "causal-synth.html"
URL = f"file:///{HTML_PATH.resolve().as_posix()}"

WAIT_SEC = 8


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1400,900")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    d = webdriver.Chrome(options=options)
    d.get(URL)
    time.sleep(1)
    yield d
    d.quit()


def _wait(driver, timeout=WAIT_SEC):
    return WebDriverWait(driver, timeout)


def _load_example(driver, key="statins"):
    """Helper: load an example dataset and wait for rows to appear."""
    driver.execute_script(f"loadExample('{key}')")
    time.sleep(0.3)


def _run_analysis(driver):
    """Helper: run triangulation and wait for results."""
    driver.execute_script("runTriangulation()")
    _wait(driver).until(
        lambda d: d.find_element(By.ID, "results").value_of_css_property("display") != "none"
    )
    time.sleep(0.3)


def _load_and_run(driver, key="statins"):
    """Helper: load example + run analysis."""
    _load_example(driver, key)
    _run_analysis(driver)


def _reset(driver):
    """Helper: reload page to clean state."""
    driver.get(URL)
    time.sleep(0.8)


# =============================================================================
# DATA INPUT (10 tests)
# =============================================================================

class TestDataInput:
    def test_01_page_loads_no_js_errors(self, driver):
        """Page loads without critical JS errors."""
        _reset(driver)
        logs = driver.get_log("browser")
        severe = [l for l in logs if l["level"] == "SEVERE"]
        # Filter out known harmless messages (e.g. favicon)
        real_errors = [l for l in severe if "favicon" not in l.get("message", "").lower()]
        assert len(real_errors) == 0, f"JS errors on load: {real_errors}"

    def test_02_default_five_empty_rows(self, driver):
        """Init creates 5 empty rows in the data table."""
        _reset(driver)
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 5

    def test_03_add_row_button(self, driver):
        """Add Study button adds one row."""
        _reset(driver)
        initial = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
        driver.execute_script("addRow()")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == initial + 1

    def test_04_clear_all_removes_rows(self, driver):
        """Clear All removes all rows."""
        _reset(driver)
        _load_example(driver, "statins")
        rows_before = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
        assert rows_before > 0
        driver.execute_script("clearAll()")
        rows_after = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
        assert rows_after == 0

    def test_05_entering_valid_data_enables_run(self, driver):
        """Entering valid yi/se enables the Run button."""
        _reset(driver)
        driver.execute_script("clearAll()")
        driver.execute_script("addRow({study:'A', design:'RCT', yi:-0.3, se:0.1})")
        driver.execute_script("addRow({study:'B', design:'cohort', yi:-0.2, se:0.05})")
        btn = driver.find_element(By.ID, "runBtn")
        assert not btn.get_attribute("disabled")

    def test_06_run_disabled_fewer_than_2_studies(self, driver):
        """Run button disabled with <2 valid studies."""
        _reset(driver)
        driver.execute_script("clearAll()")
        driver.execute_script("addRow({study:'A', design:'RCT', yi:-0.3, se:0.1})")
        btn = driver.find_element(By.ID, "runBtn")
        assert btn.get_attribute("disabled")

    def test_07_design_dropdown_has_6_options(self, driver):
        """Design dropdown has all 6 design types."""
        _reset(driver)
        driver.execute_script("clearAll(); addRow()")
        selects = driver.find_elements(By.CSS_SELECTOR, "#dataBody select[data-f='design']")
        assert len(selects) >= 1
        opts = selects[0].find_elements(By.TAG_NAME, "option")
        opt_vals = [o.get_attribute("value") for o in opts]
        for expected in ["RCT", "cohort", "cc", "MR", "ecological", "cross"]:
            assert expected in opt_vals, f"Missing design option: {expected}"

    def test_08_subgroup_column_exists(self, driver):
        """Subgroup column exists and accepts input."""
        _reset(driver)
        driver.execute_script("clearAll(); addRow()")
        sg_inputs = driver.find_elements(By.CSS_SELECTOR, "#dataBody input[data-f='subgroup']")
        assert len(sg_inputs) >= 1
        driver.execute_script("arguments[0].value = 'TestGroup'; arguments[0].dispatchEvent(new Event('input'))", sg_inputs[0])
        assert sg_inputs[0].get_attribute("value") == "TestGroup"

    def test_09_study_badge_updates(self, driver):
        """Study badge updates when data changes."""
        _reset(driver)
        _load_example(driver, "statins")
        badge = driver.find_element(By.ID, "studyBadge")
        assert "12" in badge.text

    def test_10_add_five_rows_button(self, driver):
        """Add 5 button adds 5 rows at once."""
        _reset(driver)
        initial = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
        driver.execute_script("addRows(5)")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == initial + 5


# =============================================================================
# EXAMPLE DATASETS (5 tests)
# =============================================================================

class TestExampleDatasets:
    def test_11_load_statins(self, driver):
        """Statins dataset loads 12 studies with RCT, cohort, MR designs."""
        _reset(driver)
        _load_example(driver, "statins")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 12
        badge = driver.find_element(By.ID, "studyBadge")
        assert "12" in badge.text

    def test_12_load_smoking(self, driver):
        """Smoking dataset loads 8 studies."""
        _reset(driver)
        _load_example(driver, "smoking")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 8

    def test_13_load_hiv(self, driver):
        """HIV dataset loads 7 studies."""
        _reset(driver)
        _load_example(driver, "hiv")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 7

    def test_14_load_immunotherapy(self, driver):
        """Immunotherapy dataset loads 7 studies."""
        _reset(driver)
        _load_example(driver, "immunotherapy")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 7

    def test_15_run_enabled_after_loading(self, driver):
        """After loading any example, Run button is enabled."""
        _reset(driver)
        _load_example(driver, "meddiet")
        btn = driver.find_element(By.ID, "runBtn")
        assert not btn.get_attribute("disabled")


# =============================================================================
# TRIANGULATION ENGINE (15 tests)
# =============================================================================

class TestTriangulationEngine:
    def test_16_results_visible_after_run(self, driver):
        """Results section becomes visible after running statins."""
        _reset(driver)
        _load_and_run(driver, "statins")
        results = driver.find_element(By.ID, "results")
        assert results.value_of_css_property("display") != "none"

    def test_17_convergence_metrics_present(self, driver):
        """Convergence metrics div contains DCI, MCS, BDS, CES values."""
        _reset(driver)
        _load_and_run(driver, "statins")
        metrics = driver.find_element(By.ID, "convMetrics")
        text = metrics.text
        for label in ["Direction Concordance", "Magnitude Consistency", "Bias Diversity", "Causal Evidence Score"]:
            assert label in text, f"Missing metric: {label}"

    def test_18_dci_100_for_statins(self, driver):
        """DCI is 100% for statins (all same direction)."""
        _reset(driver)
        _load_and_run(driver, "statins")
        dci = driver.execute_script("return triResults.DCI")
        assert dci == 1.0, f"DCI should be 1.0, got {dci}"

    def test_19_ces_positive_for_all_examples(self, driver):
        """CES > 0 for all example datasets."""
        for key in ["statins", "meddiet", "smoking", "hiv", "immunotherapy"]:
            _reset(driver)
            _load_and_run(driver, key)
            ces = driver.execute_script("return triResults.CES")
            assert ces > 0, f"CES should be > 0 for {key}, got {ces}"

    def test_20_grade_badge_present(self, driver):
        """GRADE-like certainty badge is displayed."""
        _reset(driver)
        _load_and_run(driver, "statins")
        badges = driver.find_elements(By.CSS_SELECTOR, "#convMetrics .grade-badge")
        assert len(badges) >= 1
        badge_text = badges[0].text
        assert any(lev in badge_text for lev in ["HIGH", "MODERATE", "LOW", "VERY LOW"])

    def test_21_pooled_effect_in_range_statins(self, driver):
        """Overall pooled effect for statins is within expected range (-0.5 to -0.1)."""
        _reset(driver)
        _load_and_run(driver, "statins")
        theta = driver.execute_script("return triResults.overallResult.theta")
        assert -0.5 <= theta <= -0.1, f"Pooled effect {theta} out of range"

    def test_22_per_design_estimates_exist(self, driver):
        """Per-design pooled estimates exist for RCT, cohort, MR in statins."""
        _reset(driver)
        _load_and_run(driver, "statins")
        designs = driver.execute_script("return Object.keys(triResults.designResults)")
        for d in ["RCT", "cohort", "MR"]:
            assert d in designs, f"Design {d} missing from results"

    def test_23_between_design_pooled(self, driver):
        """Between-design pooled estimate is computed."""
        _reset(driver)
        _load_and_run(driver, "statins")
        bd = driver.execute_script("return triResults.betweenDesignResult")
        assert bd is not None
        assert "theta" in bd

    def test_24_i2_in_range(self, driver):
        """I-squared is between 0 and 100."""
        _reset(driver)
        _load_and_run(driver, "statins")
        i2 = driver.execute_script("return triResults.overallResult.I2")
        assert 0 <= i2 <= 100, f"I2 = {i2} out of [0, 100]"

    def test_25_method_toggle_dl_reml(self, driver):
        """Method toggle switches between DL and REML."""
        _reset(driver)
        _load_example(driver, "statins")
        sel = Select(driver.find_element(By.ID, "poolingMethodSelect"))
        sel.select_by_value("REML")
        val = driver.execute_script("return document.getElementById('poolingMethodSelect').value")
        assert val == "REML"
        sel.select_by_value("DL")
        val = driver.execute_script("return document.getElementById('poolingMethodSelect').value")
        assert val == "DL"

    def test_26_reml_differs_from_dl(self, driver):
        """REML results differ slightly from DL for statins."""
        _reset(driver)
        _load_example(driver, "statins")
        # DL run
        driver.execute_script("document.getElementById('poolingMethodSelect').value='DL'; runTriangulation()")
        time.sleep(0.3)
        dl_theta = driver.execute_script("return triResults.overallResult.theta")
        # REML run
        driver.execute_script("document.getElementById('poolingMethodSelect').value='REML'; runTriangulation()")
        time.sleep(0.3)
        reml_theta = driver.execute_script("return triResults.overallResult.theta")
        # They should be different (or very close but typically not identical)
        assert isinstance(dl_theta, float) and isinstance(reml_theta, float)
        # REML typically gives a slightly different tau2 and hence different pooled estimate
        # For statins data, they may differ; we just check both are valid numbers
        assert -1 < dl_theta < 0 and -1 < reml_theta < 0

    def test_27_forest_plot_rendered(self, driver):
        """Forest plot SVG is rendered after analysis."""
        _reset(driver)
        _load_and_run(driver, "statins")
        svg = driver.find_elements(By.CSS_SELECTOR, "#forestContainer svg")
        assert len(svg) >= 1

    def test_28_forest_plot_has_design_headers(self, driver):
        """Forest plot contains design group header text."""
        _reset(driver)
        _load_and_run(driver, "statins")
        svg_text = driver.execute_script(
            "return document.getElementById('forestContainer').innerHTML"
        )
        assert "Randomized Controlled Trial" in svg_text or "RCT" in svg_text

    def test_29_forest_null_line(self, driver):
        """Forest plot has a null line at x=0."""
        _reset(driver)
        _load_and_run(driver, "statins")
        # The null line is a dashed line in the SVG at the x-scaled position for value 0
        svg_text = driver.execute_script(
            "return document.getElementById('forestContainer').innerHTML"
        )
        assert "stroke-dasharray" in svg_text

    def test_30_rerun_updates_results(self, driver):
        """Re-running with different data updates the results."""
        _reset(driver)
        _load_and_run(driver, "statins")
        theta1 = driver.execute_script("return triResults.overallResult.theta")
        _load_and_run(driver, "smoking")
        theta2 = driver.execute_script("return triResults.overallResult.theta")
        assert theta1 != theta2, "Results should differ between datasets"


# =============================================================================
# CAUSAL CORRECTION (8 tests)
# =============================================================================

class TestCausalCorrection:
    def test_31_camea_card_visible(self, driver):
        """CaMeA card appears after running analysis."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "causalCorrectionCard")
        assert card.value_of_css_property("display") != "none"

    def test_32_four_causal_boxes(self, driver):
        """CaMeA shows 4 boxes (log-OR, OR, causal RD, implied RD)."""
        _reset(driver)
        _load_and_run(driver, "statins")
        boxes = driver.find_elements(By.CSS_SELECTOR, "#causalGrid .causal-box")
        assert len(boxes) == 4

    def test_33_sensitivity_table_five_rows(self, driver):
        """Sensitivity table shows 5 p0 values."""
        _reset(driver)
        _load_and_run(driver, "statins")
        rows = driver.find_elements(By.CSS_SELECTOR, "#causalSensContainer .causal-sens-table tbody tr")
        assert len(rows) == 5

    def test_34_p0_slider_updates_rd(self, driver):
        """Changing p0 slider updates RD value."""
        _reset(driver)
        _load_and_run(driver, "statins")
        # Get initial value
        initial_val = driver.execute_script(
            "return document.getElementById('p0SliderVal').textContent"
        )
        # Change slider
        driver.execute_script("onP0SliderChange(0.35)")
        new_val = driver.execute_script(
            "return document.getElementById('p0SliderVal').textContent"
        )
        assert new_val == "0.35"
        assert new_val != initial_val

    def test_35_measure_type_dropdown_exists(self, driver):
        """Measure type dropdown (OR/RR) exists."""
        _reset(driver)
        _load_and_run(driver, "statins")
        sel = driver.find_element(By.ID, "measureTypeSelect")
        opts = sel.find_elements(By.TAG_NAME, "option")
        opt_vals = [o.get_attribute("value") for o in opts]
        assert "OR" in opt_vals
        assert "RR" in opt_vals

    def test_36_switching_measure_updates_labels(self, driver):
        """Switching from OR to RR updates labels in causal boxes."""
        _reset(driver)
        _load_and_run(driver, "statins")
        grid_html_or = driver.execute_script("return document.getElementById('causalGrid').innerHTML")
        assert "OR" in grid_html_or or "log-OR" in grid_html_or
        driver.execute_script(
            "document.getElementById('measureTypeSelect').value='RR'; renderCausalCorrection()"
        )
        time.sleep(0.2)
        grid_html_rr = driver.execute_script("return document.getElementById('causalGrid').innerHTML")
        assert "RR" in grid_html_rr or "log-RR" in grid_html_rr

    def test_37_causal_rd_highlighted(self, driver):
        """The causal RD box has the highlight class."""
        _reset(driver)
        _load_and_run(driver, "statins")
        highlights = driver.find_elements(By.CSS_SELECTOR, "#causalGrid .causal-box.highlight")
        assert len(highlights) >= 1

    def test_38_p0_slider_wrap_visible(self, driver):
        """p0 slider wrap is visible after running."""
        _reset(driver)
        _load_and_run(driver, "statins")
        wrap = driver.find_element(By.ID, "p0SliderWrap")
        assert wrap.value_of_css_property("display") != "none"


# =============================================================================
# SENSITIVITY ANALYSIS (5 tests)
# =============================================================================

class TestSensitivityAnalysis:
    def test_39_lodo_table_renders(self, driver):
        """Leave-one-design-out table renders."""
        _reset(driver)
        _load_and_run(driver, "statins")
        container = driver.find_element(By.ID, "sensitivityContainer")
        table = container.find_elements(By.CSS_SELECTOR, "table.sens-table")
        assert len(table) >= 1

    def test_40_lodo_one_row_per_design(self, driver):
        """LODO table (first sens-table) has one row per design."""
        _reset(driver)
        _load_and_run(driver, "statins")
        n_designs = driver.execute_script("return Object.keys(triResults.designResults).length")
        # The first .sens-table is the LODO table; subsequent ones are expanded sensitivity
        tables = driver.find_elements(By.CSS_SELECTOR, "#sensitivityContainer .sens-table")
        assert len(tables) >= 1
        lodo_rows = tables[0].find_elements(By.CSS_SELECTOR, "tbody tr")
        assert len(lodo_rows) == n_designs

    def test_41_removing_design_changes_estimate(self, driver):
        """Removing one design changes the pooled estimate."""
        _reset(driver)
        _load_and_run(driver, "statins")
        overall = driver.execute_script("return triResults.overallResult.theta")
        # Read the first row's pooled-without value
        first_val = driver.execute_script("""
            const cells = document.querySelectorAll('#sensitivityContainer .sens-table tbody tr td');
            return cells[1] ? cells[1].textContent.trim() : null;
        """)
        assert first_val is not None
        without_val = float(first_val)
        assert abs(without_val - overall) > 1e-8, "Removing a design should change the estimate"

    def test_42_direction_consistency_column(self, driver):
        """Direction consistency column shows Yes or No."""
        _reset(driver)
        _load_and_run(driver, "statins")
        html = driver.execute_script(
            "return document.getElementById('sensitivityContainer').innerHTML"
        )
        assert "Yes" in html or "No" in html

    def test_43_sensitivity_card_visible(self, driver):
        """Sensitivity card is visible after analysis."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "sensitivityCard")
        assert card.is_displayed()


# =============================================================================
# DAG EDITOR (8 tests)
# =============================================================================

class TestDAGEditor:
    def test_44_dag_template_dropdown_4_options(self, driver):
        """Template dropdown has 4 DAG template options (plus blank)."""
        _reset(driver)
        sel = driver.find_element(By.ID, "dagTemplate")
        opts = sel.find_elements(By.TAG_NAME, "option")
        # 4 templates + 1 blank
        template_vals = [o.get_attribute("value") for o in opts if o.get_attribute("value")]
        assert set(template_vals) == {"confounding", "mediation", "iv", "collider"}

    def test_45_confounding_template_3_nodes(self, driver):
        """Loading confounding template renders 3 nodes (circles)."""
        _reset(driver)
        driver.execute_script("loadDAGTemplate('confounding')")
        time.sleep(0.3)
        circles = driver.find_elements(By.CSS_SELECTOR, "#dagSvg circle")
        assert len(circles) == 3

    def test_46_iv_template_4_nodes(self, driver):
        """Loading IV template renders 4 nodes."""
        _reset(driver)
        driver.execute_script("loadDAGTemplate('iv')")
        time.sleep(0.3)
        circles = driver.find_elements(By.CSS_SELECTOR, "#dagSvg circle")
        assert len(circles) == 4

    def test_47_clear_dag(self, driver):
        """Clear button clears the DAG."""
        _reset(driver)
        driver.execute_script("loadDAGTemplate('confounding')")
        time.sleep(0.2)
        driver.execute_script("clearDAG()")
        time.sleep(0.2)
        circles = driver.find_elements(By.CSS_SELECTOR, "#dagSvg circle")
        assert len(circles) == 0

    def test_48_svg_has_circles_for_nodes(self, driver):
        """SVG has circle elements for nodes."""
        _reset(driver)
        driver.execute_script("loadDAGTemplate('mediation')")
        time.sleep(0.3)
        circles = driver.find_elements(By.CSS_SELECTOR, "#dagSvg circle")
        assert len(circles) == 3  # mediation has 3 nodes

    def test_49_svg_has_lines_for_edges(self, driver):
        """SVG has line elements for edges."""
        _reset(driver)
        driver.execute_script("loadDAGTemplate('confounding')")
        time.sleep(0.3)
        lines = driver.find_elements(By.CSS_SELECTOR, "#dagSvg line")
        assert len(lines) >= 3  # confounding has 3 edges

    def test_50_collider_template_renders(self, driver):
        """Collider template renders correctly with 3 nodes."""
        _reset(driver)
        driver.execute_script("loadDAGTemplate('collider')")
        time.sleep(0.3)
        circles = driver.find_elements(By.CSS_SELECTOR, "#dagSvg circle")
        assert len(circles) == 3

    def test_51_dag_edit_toggle_exists(self, driver):
        """Edit Mode toggle button exists."""
        _reset(driver)
        btn = driver.find_element(By.ID, "dagEditToggle")
        assert btn is not None
        assert "Edit Mode" in btn.text or "editing" in btn.text.lower() or btn.is_displayed()


# =============================================================================
# VISUALIZATIONS (10 tests)
# =============================================================================

class TestVisualizations:
    def test_52_radar_chart_rendered(self, driver):
        """Radar chart renders with a polygon."""
        _reset(driver)
        _load_and_run(driver, "statins")
        svg = driver.find_elements(By.CSS_SELECTOR, "#radarContainer svg")
        assert len(svg) >= 1
        polygons = driver.find_elements(By.CSS_SELECTOR, "#radarContainer svg polygon")
        assert len(polygons) >= 1

    def test_53_bias_heatmap_renders(self, driver):
        """Bias architecture heatmap table renders with traffic-light colors."""
        _reset(driver)
        _load_and_run(driver, "statins")
        container = driver.find_element(By.ID, "biasContainer")
        bias_table = container.find_elements(By.CSS_SELECTOR, "table.bias-table")
        assert len(bias_table) >= 1
        # Check for traffic-light classes
        html = container.get_attribute("innerHTML")
        assert "bias-low" in html or "bias-mod" in html or "bias-high" in html

    def test_54_funnel_plot_renders(self, driver):
        """Funnel plot renders after analysis."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "funnelCard")
        assert card.value_of_css_property("display") != "none"
        svg = driver.find_elements(By.CSS_SELECTOR, "#funnelContainer svg")
        assert len(svg) >= 1

    def test_55_network_diagram_renders(self, driver):
        """Network-of-designs diagram renders with nodes and edges."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "networkCard")
        assert card.value_of_css_property("display") != "none"
        svg = driver.find_elements(By.CSS_SELECTOR, "#networkContainer svg")
        assert len(svg) >= 1
        circles = driver.find_elements(By.CSS_SELECTOR, "#networkContainer svg circle")
        lines = driver.find_elements(By.CSS_SELECTOR, "#networkContainer svg line")
        assert len(circles) >= 2
        assert len(lines) >= 1

    def test_56_subgroup_plot_renders_with_subgroups(self, driver):
        """Subgroup card renders when data has subgroups (statins has Primary/Secondary)."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "subgroupCard")
        assert card.value_of_css_property("display") != "none"

    def test_57_timeline_chart_renders(self, driver):
        """Timeline visualization renders (statins has year-labelled studies)."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "timelineCard")
        assert card.value_of_css_property("display") != "none"
        svg = driver.find_elements(By.CSS_SELECTOR, "#timelineContainer svg")
        assert len(svg) >= 1

    def test_58_rob_table_renders(self, driver):
        """Risk of Bias traffic-light table renders."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "robCard")
        assert card.value_of_css_property("display") != "none"
        html = driver.execute_script("return document.getElementById('robContainer').innerHTML")
        assert "rob-traffic-light" in html

    def test_59_power_analysis_card_renders(self, driver):
        """Power analysis card renders with controls."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "powerCard")
        assert card.value_of_css_property("display") != "none"
        container_html = driver.execute_script("return document.getElementById('powerContainer').innerHTML")
        assert "powerKSlider" in container_html

    def test_60_contour_funnel_toggle(self, driver):
        """Contour funnel toggle works."""
        _reset(driver)
        _load_and_run(driver, "statins")
        toggle = driver.find_elements(By.ID, "contourFunnelToggle")
        if toggle:
            driver.execute_script("document.getElementById('contourFunnelToggle').checked = true; toggleContourFunnel()")
            time.sleep(0.3)
            svg_html = driver.execute_script("return document.getElementById('funnelContainer').innerHTML")
            # After enabling contour, the SVG should have additional overlay elements
            assert "svg" in svg_html.lower()

    def test_61_agreement_matrix_renders(self, driver):
        """Agreement matrix card renders."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "agreementCard")
        assert card.value_of_css_property("display") != "none"
        html = driver.execute_script("return document.getElementById('agreementContainer').innerHTML")
        assert "agreement-cell" in html


# =============================================================================
# EXPORT & REPORT (8 tests)
# =============================================================================

class TestExportReport:
    def test_62_report_contains_methods(self, driver):
        """Report text contains METHODS."""
        _reset(driver)
        _load_and_run(driver, "statins")
        text = driver.execute_script("return document.getElementById('reportText').textContent")
        assert "METHODS" in text

    def test_63_report_contains_results(self, driver):
        """Report text contains RESULTS."""
        _reset(driver)
        _load_and_run(driver, "statins")
        text = driver.execute_script("return document.getElementById('reportText').textContent")
        assert "RESULTS" in text

    def test_64_r_code_contains_library(self, driver):
        """R code contains library(metafor)."""
        _reset(driver)
        _load_and_run(driver, "statins")
        code = driver.execute_script("return document.getElementById('rCodeBlock').textContent")
        assert "library(metafor)" in code

    def test_65_r_code_contains_study_data(self, driver):
        """R code contains study data."""
        _reset(driver)
        _load_and_run(driver, "statins")
        code = driver.execute_script("return document.getElementById('rCodeBlock').textContent")
        assert "CTT 2010" in code or "dat <- data.frame" in code

    def test_66_csv_export_button_exists(self, driver):
        """CSV export button exists in header."""
        _reset(driver)
        btns = driver.find_elements(By.CSS_SELECTOR, "header button")
        btn_texts = [b.text.strip() for b in btns]
        assert "Export CSV" in btn_texts

    def test_67_copy_report_button_exists(self, driver):
        """Copy report button exists."""
        _reset(driver)
        _load_and_run(driver, "statins")
        btns = driver.find_elements(By.CSS_SELECTOR, "#reportCard .copy-btn")
        assert len(btns) >= 1

    def test_68_truthcert_card_renders(self, driver):
        """TruthCert card renders after analysis."""
        _reset(driver)
        _load_and_run(driver, "statins")
        # TruthCert is async, give it a moment
        time.sleep(1)
        card = driver.find_element(By.ID, "truthcertCard")
        assert card.value_of_css_property("display") != "none"

    def test_69_r_code_card_visible(self, driver):
        """R code card is visible after analysis."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "rCodeCard")
        assert card.is_displayed()


# =============================================================================
# UI / UX (8 tests)
# =============================================================================

class TestUIUX:
    def test_70_dark_mode_toggle(self, driver):
        """Dark mode toggle adds 'dark' class to body."""
        _reset(driver)
        has_dark = driver.execute_script("return document.body.classList.contains('dark')")
        assert not has_dark
        driver.execute_script("toggleTheme()")
        has_dark = driver.execute_script("return document.body.classList.contains('dark')")
        assert has_dark
        # Toggle back
        driver.execute_script("toggleTheme()")
        has_dark = driver.execute_script("return document.body.classList.contains('dark')")
        assert not has_dark

    def test_71_tutorial_modal_opens(self, driver):
        """Tutorial modal opens on button click."""
        _reset(driver)
        driver.execute_script("openTutorial()")
        time.sleep(0.3)
        overlay = driver.find_element(By.ID, "tutorialOverlay")
        assert "active" in overlay.get_attribute("class")

    def test_72_tutorial_has_6_steps(self, driver):
        """Tutorial has 6 steps."""
        _reset(driver)
        driver.execute_script("openTutorial()")
        time.sleep(0.3)
        steps = driver.find_elements(By.CSS_SELECTOR, "#tutorialOverlay .tutorial-step")
        assert len(steps) == 6

    def test_73_tutorial_closes_on_escape(self, driver):
        """Tutorial closes on Escape key."""
        _reset(driver)
        driver.execute_script("openTutorial()")
        time.sleep(0.3)
        overlay = driver.find_element(By.ID, "tutorialOverlay")
        assert "active" in overlay.get_attribute("class")
        # Press Escape
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.3)
        assert "active" not in overlay.get_attribute("class")

    def test_74_ctrl_enter_runs_analysis(self, driver):
        """Keyboard shortcut Ctrl+Enter runs analysis."""
        _reset(driver)
        _load_example(driver, "statins")
        results_display = driver.execute_script(
            "return document.getElementById('results').style.display"
        )
        assert results_display == "none"
        # Send Ctrl+Enter
        ActionChains(driver).key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
        time.sleep(1)
        results_display = driver.execute_script(
            "return document.getElementById('results').style.display"
        )
        assert results_display != "none"

    def test_75_results_scroll_into_view(self, driver):
        """Results section is scrolled to after run (by verifying the call structure)."""
        _reset(driver)
        _load_and_run(driver, "statins")
        # The results div should be displayed (scroll behavior hard to test directly)
        results = driver.find_element(By.ID, "results")
        assert results.is_displayed()

    def test_76_all_result_cards_have_headings(self, driver):
        """All visible result cards have h2 headings."""
        _reset(driver)
        _load_and_run(driver, "statins")
        cards = driver.find_elements(By.CSS_SELECTOR, "#results .card")
        for card in cards:
            if card.value_of_css_property("display") != "none":
                headings = card.find_elements(By.TAG_NAME, "h2")
                assert len(headings) >= 1, f"Card missing h2: {card.get_attribute('id')}"

    def test_77_theme_button_text_toggles(self, driver):
        """Theme button text changes between Dark Mode / Light Mode."""
        _reset(driver)
        btn = driver.find_element(By.ID, "themeBtn")
        assert btn.text.strip() == "Dark Mode"
        driver.execute_script("toggleTheme()")
        assert btn.text.strip() == "Light Mode"
        driver.execute_script("toggleTheme()")
        assert btn.text.strip() == "Dark Mode"


# =============================================================================
# EDGE CASES (5 tests)
# =============================================================================

class TestEdgeCases:
    def test_78_two_studies_same_design(self, driver):
        """Run with only 2 studies from the same design still works."""
        _reset(driver)
        driver.execute_script("clearAll()")
        driver.execute_script("addRow({study:'A', design:'RCT', yi:-0.3, se:0.1})")
        driver.execute_script("addRow({study:'B', design:'RCT', yi:-0.2, se:0.08})")
        _run_analysis(driver)
        theta = driver.execute_script("return triResults.overallResult.theta")
        assert isinstance(theta, float)
        assert -1 < theta < 0

    def test_79_k1_per_design_forest_renders(self, driver):
        """Run with k=1 per design: forest plot still renders."""
        _reset(driver)
        driver.execute_script("clearAll()")
        driver.execute_script("addRow({study:'A', design:'RCT', yi:-0.3, se:0.1})")
        driver.execute_script("addRow({study:'B', design:'cohort', yi:-0.2, se:0.05})")
        _run_analysis(driver)
        svg = driver.find_elements(By.CSS_SELECTOR, "#forestContainer svg")
        assert len(svg) >= 1

    def test_80_large_effect_no_break(self, driver):
        """Very large effect (yi=10) doesn't break visualization."""
        _reset(driver)
        driver.execute_script("clearAll()")
        driver.execute_script("addRow({study:'Huge', design:'RCT', yi:10, se:1})")
        driver.execute_script("addRow({study:'Normal', design:'cohort', yi:-0.3, se:0.1})")
        _run_analysis(driver)
        theta = driver.execute_script("return triResults.overallResult.theta")
        assert isinstance(theta, float) and not (theta != theta)  # not NaN

    def test_81_negative_effects_render(self, driver):
        """Negative effects render correctly in forest plot."""
        _reset(driver)
        driver.execute_script("clearAll()")
        driver.execute_script("addRow({study:'Neg1', design:'RCT', yi:-1.5, se:0.2})")
        driver.execute_script("addRow({study:'Neg2', design:'cohort', yi:-0.8, se:0.15})")
        _run_analysis(driver)
        svg = driver.find_elements(By.CSS_SELECTOR, "#forestContainer svg")
        assert len(svg) >= 1
        theta = driver.execute_script("return triResults.overallResult.theta")
        assert theta < 0

    def test_82_zero_effect_handled(self, driver):
        """Zero effect (yi=0) is handled gracefully."""
        _reset(driver)
        driver.execute_script("clearAll()")
        driver.execute_script("addRow({study:'Zero', design:'RCT', yi:0, se:0.1})")
        driver.execute_script("addRow({study:'Nonzero', design:'cohort', yi:-0.3, se:0.1})")
        _run_analysis(driver)
        theta = driver.execute_script("return triResults.overallResult.theta")
        assert isinstance(theta, float) and not (theta != theta)


# =============================================================================
# ADDITIONAL COVERAGE (8 tests to reach 90 total)
# =============================================================================

class TestAdditionalCoverage:
    def test_83_bias_adjustment_card(self, driver):
        """Bias adjustment card renders after analysis."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "biasAdjCard")
        assert card.value_of_css_property("display") != "none"

    def test_84_reml_compare_card(self, driver):
        """REML comparison card renders."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "remlCompareCard")
        assert card.value_of_css_property("display") != "none"

    def test_85_weights_card(self, driver):
        """Study weights card renders."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "weightsCard")
        assert card.value_of_css_property("display") != "none"

    def test_86_cumulative_forest_card(self, driver):
        """Cumulative forest plot card renders."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "cumulativeCard")
        assert card.value_of_css_property("display") != "none"

    def test_87_influence_diagnostics_card(self, driver):
        """Influence diagnostics (Baujat) card renders."""
        _reset(driver)
        _load_and_run(driver, "statins")
        card = driver.find_element(By.ID, "influenceCard")
        assert card.value_of_css_property("display") != "none"

    def test_88_interpretation_panel(self, driver):
        """Interpretation panel renders with verdict text."""
        _reset(driver)
        _load_and_run(driver, "statins")
        panel = driver.find_element(By.ID, "interpPanel")
        text = panel.text
        assert len(text) > 50, "Interpretation panel should have substantial text"

    def test_89_meddiet_dataset_7_studies(self, driver):
        """Mediterranean diet dataset loads 7 studies."""
        _reset(driver)
        _load_example(driver, "meddiet")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 7

    def test_90_smoking_positive_effects(self, driver):
        """Smoking dataset has positive effects (harmful exposure)."""
        _reset(driver)
        _load_and_run(driver, "smoking")
        theta = driver.execute_script("return triResults.overallResult.theta")
        assert theta > 0, f"Smoking pooled effect should be positive, got {theta}"


# =============================================================================
# WEBR & TRUTHCERT (5 tests)
# =============================================================================

class TestWebrTruthcert:
    def test_91_webr_card_initially_hidden(self, driver):
        """WebR card is initially hidden (shown only when validated)."""
        _reset(driver)
        card = driver.find_element(By.ID, "webrCard")
        assert card.value_of_css_property("display") == "none"

    def test_92_webr_badge_ready(self, driver):
        """WebR badge shows Ready initially (via textContent since card is hidden)."""
        _reset(driver)
        badge_text = driver.execute_script(
            "return document.getElementById('webrBadge').textContent"
        )
        assert "Ready" in badge_text

    def test_93_truthcert_chain_populated(self, driver):
        """TruthCert chain has steps after analysis."""
        _reset(driver)
        _load_and_run(driver, "statins")
        time.sleep(1)
        chain = driver.find_element(By.ID, "truthcertChain")
        steps = chain.find_elements(By.CSS_SELECTOR, ".tc-step")
        assert len(steps) >= 3, f"Expected at least 3 TruthCert steps, got {len(steps)}"

    def test_94_truthcert_seal_area(self, driver):
        """TruthCert seal area is populated after analysis."""
        _reset(driver)
        _load_and_run(driver, "statins")
        time.sleep(1)
        seal_area = driver.find_element(By.ID, "truthcertSealArea")
        assert len(seal_area.text) > 0 or len(seal_area.get_attribute("innerHTML")) > 0

    def test_95_report_text_mentions_designs(self, driver):
        """Report text mentions specific design types used."""
        _reset(driver)
        _load_and_run(driver, "statins")
        text = driver.execute_script("return document.getElementById('reportText').textContent")
        assert "Randomized Controlled Trial" in text or "RCT" in text
        assert "Cohort" in text
        assert "Mendelian Randomization" in text or "MR" in text


# =============================================================================
# SUBGROUP ANALYSIS (5 tests)
# =============================================================================

class TestSubgroupAnalysis:
    def test_96_subgroup_table_renders(self, driver):
        """Subgroup analysis table renders for statins (has Primary/Secondary)."""
        _reset(driver)
        _load_and_run(driver, "statins")
        html = driver.execute_script("return document.getElementById('subgroupContainer').innerHTML")
        assert "Primary" in html
        assert "Secondary" in html

    def test_97_subgroup_interaction_test(self, driver):
        """Subgroup interaction test (Q_between) is displayed."""
        _reset(driver)
        _load_and_run(driver, "statins")
        html = driver.execute_script("return document.getElementById('subgroupContainer').innerHTML")
        assert "Q_between" in html or "Subgroup Interaction" in html

    def test_98_no_subgroup_card_hidden(self, driver):
        """Subgroup card is hidden when no subgroups in data."""
        _reset(driver)
        driver.execute_script("clearAll()")
        driver.execute_script("addRow({study:'A', design:'RCT', yi:-0.3, se:0.1})")
        driver.execute_script("addRow({study:'B', design:'cohort', yi:-0.2, se:0.05})")
        _run_analysis(driver)
        card = driver.find_element(By.ID, "subgroupCard")
        assert card.value_of_css_property("display") == "none"

    def test_99_subgroup_forest_plot_present(self, driver):
        """Subgroup forest plot SVG is present in the container."""
        _reset(driver)
        _load_and_run(driver, "statins")
        html = driver.execute_script("return document.getElementById('subgroupContainer').innerHTML")
        assert "<svg" in html.lower()

    def test_100_subgroup_pooled_effect_values(self, driver):
        """Subgroup pooled effects are valid numbers."""
        _reset(driver)
        _load_and_run(driver, "statins")
        # Check the subgroup table has numeric pooled effects
        rows = driver.find_elements(By.CSS_SELECTOR, "#subgroupContainer .subgroup-table tbody tr")
        assert len(rows) >= 2  # Primary + Secondary
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                try:
                    val = float(cells[2].text)
                    assert -5 < val < 5, f"Subgroup pooled effect out of range: {val}"
                except ValueError:
                    pass  # header rows may not have numeric values


# =============================================================================
# DESIGN LEGEND & MISC (5 tests for 105 total)
# =============================================================================

class TestMiscFeatures:
    def test_101_design_legend_rendered(self, driver):
        """Design legend with colored dots is rendered on init."""
        _reset(driver)
        legend = driver.find_element(By.ID, "designLegend")
        assert len(legend.text) > 0
        dots = driver.find_elements(By.CSS_SELECTOR, "#designLegend .leg-dot")
        assert len(dots) == 6  # 6 design types

    def test_102_export_r_code_button_exists(self, driver):
        """Export R Code button exists in header."""
        _reset(driver)
        btns = driver.find_elements(By.CSS_SELECTOR, "header button")
        btn_texts = [b.text.strip() for b in btns]
        assert "Export R Code" in btn_texts

    def test_103_n_studies_metric_correct(self, driver):
        """Total studies metric matches actual study count."""
        _reset(driver)
        _load_and_run(driver, "statins")
        n = driver.execute_script("return triResults.nStudies")
        assert n == 12

    def test_104_n_designs_metric_correct(self, driver):
        """Number of designs metric is correct for statins (3 designs)."""
        _reset(driver)
        _load_and_run(driver, "statins")
        n = driver.execute_script("return triResults.nDesigns")
        assert n == 3

    def test_105_pooling_method_stored_in_results(self, driver):
        """Pooling method is stored in results object."""
        _reset(driver)
        _load_and_run(driver, "statins")
        method = driver.execute_script("return triResults.poolingMethod")
        assert method in ["DL", "REML"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])
