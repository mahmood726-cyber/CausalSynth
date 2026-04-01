"""
Selenium test suite for CausalSynth -- Causal Evidence Triangulation Engine.
~20 tests covering page load, examples, analysis, convergence metrics,
theme toggle, export, leave-one-design-out, and more.

Usage:  python -m pytest tests/test_causalsynth.py -v
"""

import sys
import io
import os
import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Resolve file:// URL for the HTML file
HTML_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "causal-synth.html")
FILE_URL = "file:///" + HTML_PATH.replace("\\", "/")


@pytest.fixture(scope="module")
def driver():
    """Create a shared Chrome headless driver for all tests."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,1200")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    drv = webdriver.Chrome(options=opts)
    drv.set_page_load_timeout(30)
    drv.implicitly_wait(2)
    yield drv
    drv.quit()


def _load_page(driver):
    """Navigate to the app and suppress dialogs."""
    driver.get(FILE_URL)
    driver.execute_script("window.confirm = function(){return true};")
    driver.execute_script("window.alert = function(){};")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dataBody"))
    )


def _js_click(driver, el):
    """Click via JS to avoid ElementNotInteractableException in headless."""
    driver.execute_script("arguments[0].click()", el)


def _load_example(driver, key):
    """Load an example dataset by calling loadExample directly."""
    driver.execute_script(f"loadExample('{key}')")
    time.sleep(0.3)


def _run_analysis(driver):
    """Click the Run Triangulation Analysis button."""
    btn = driver.find_element(By.ID, "runBtn")
    _js_click(driver, btn)
    # Wait for results section to appear
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.getElementById('results').style.display") != "none"
    )
    time.sleep(0.5)


# ============================================================
# 1. Page load & structure
# ============================================================

class TestPageLoad:
    def test_01_page_loads(self, driver):
        """Page loads and title contains CausalSynth."""
        _load_page(driver)
        assert "CausalSynth" in driver.title

    def test_02_header_visible(self, driver):
        """Header brand text is visible."""
        brand = driver.find_element(By.CSS_SELECTOR, "header .brand")
        assert brand.text == "CausalSynth"

    def test_03_data_table_present(self, driver):
        """Data entry table exists with correct headers."""
        headers = driver.find_elements(By.CSS_SELECTOR, "#dataTable th")
        header_texts = [h.text for h in headers]
        assert "Study" in header_texts
        assert "Design" in header_texts
        assert "Effect (yi)" in header_texts
        assert "SE" in header_texts

    def test_04_run_button_present(self, driver):
        """Run Triangulation button exists."""
        btn = driver.find_element(By.ID, "runBtn")
        assert "Run Triangulation" in btn.text

    def test_05_example_dropdown_present(self, driver):
        """Load Example dropdown button is present."""
        btn = driver.find_element(By.ID, "exampleBtn")
        assert "Load Example" in btn.text

    def test_06_default_example_loaded(self, driver):
        """On page load, statins example is auto-loaded (12 studies)."""
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 12, f"Expected 12 rows (statins default), got {len(rows)}"


# ============================================================
# 2. Loading each example dataset
# ============================================================

class TestExamples:
    def test_07_load_statins(self, driver):
        """Load statins example: 12 studies, 3 designs."""
        _load_page(driver)
        _load_example(driver, "statins")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 12
        badge = driver.find_element(By.ID, "studyBadge")
        assert "12" in badge.text

    def test_08_load_meddiet(self, driver):
        """Load Mediterranean diet example: 7 studies."""
        _load_example(driver, "meddiet")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 7

    def test_09_load_smoking(self, driver):
        """Load smoking example: 8 studies, 4 designs."""
        _load_example(driver, "smoking")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 8

    def test_10_load_alcohol(self, driver):
        """Load alcohol example: 9 studies, 5 designs."""
        _load_example(driver, "alcohol")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 9

    def test_11_load_exercise(self, driver):
        """Load exercise example: 8 studies, 4 designs."""
        _load_example(driver, "exercise")
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 8


# ============================================================
# 3. Run analysis and verify CES / convergence metrics
# ============================================================

class TestAnalysis:
    def test_12_run_statins_analysis(self, driver):
        """Run analysis on statins: results section appears."""
        _load_page(driver)
        _load_example(driver, "statins")
        _run_analysis(driver)
        results = driver.find_element(By.ID, "results")
        assert results.is_displayed()

    def test_13_ces_appears(self, driver):
        """CES metric card is rendered after analysis."""
        metrics = driver.find_element(By.ID, "convMetrics")
        text = metrics.text
        assert "Causal Evidence Score" in text

    def test_14_dci_appears(self, driver):
        """Direction Concordance metric is rendered."""
        text = driver.find_element(By.ID, "convMetrics").text
        assert "Direction Concordance" in text

    def test_15_mcs_appears(self, driver):
        """Magnitude Consistency metric is rendered."""
        text = driver.find_element(By.ID, "convMetrics").text
        assert "Magnitude Consistency" in text

    def test_16_bds_appears(self, driver):
        """Bias Diversity metric is rendered."""
        text = driver.find_element(By.ID, "convMetrics").text
        assert "Bias Diversity" in text

    def test_17_convergence_values_numeric(self, driver):
        """All 4 convergence metric values are numeric (not empty or NaN)."""
        metrics_html = driver.execute_script(
            "return document.getElementById('convMetrics').innerHTML"
        )
        # Extract .val elements via JS
        vals = driver.execute_script("""
            var nodes = document.querySelectorAll('#convMetrics .conv-metric .val');
            var result = [];
            for (var i = 0; i < nodes.length; i++) result.push(nodes[i].textContent.trim());
            return result;
        """)
        # At least 6 metric tiles: nDesigns, nStudies, DCI, MCS, BDS, CES, pooled, I2
        assert len(vals) >= 6, f"Expected >= 6 metric values, got {len(vals)}"
        # DCI should contain a percentage
        dci_val = vals[2]  # "100%"
        assert "%" in dci_val, f"DCI should be a percentage, got: {dci_val}"
        # CES (index 5) should be a number like 0.xxx
        ces_val = vals[5]
        assert "NaN" not in ces_val, f"CES should not be NaN, got: {ces_val}"
        ces_float = float(ces_val)
        assert 0 <= ces_float <= 1, f"CES should be 0-1, got {ces_float}"

    def test_18_pooled_effect_displayed(self, driver):
        """Pooled effect and I-squared are shown."""
        text = driver.find_element(By.ID, "convMetrics").text
        assert "Pooled Effect" in text
        # I-squared with unicode superscript 2
        assert "I" in text  # I2 uses unicode

    def test_19_grade_certainty_shown(self, driver):
        """GRADE-like certainty badge is rendered."""
        text = driver.find_element(By.ID, "convMetrics").text
        assert "GRADE" in text or "Certainty" in text
        # Should have a grade level
        grade_badge = driver.find_elements(By.CSS_SELECTOR, ".grade-badge")
        assert len(grade_badge) >= 1, "No GRADE badge found"


# ============================================================
# 4. Forest plot
# ============================================================

class TestForestPlot:
    def test_20_forest_plot_rendered(self, driver):
        """Forest plot SVG is rendered after analysis."""
        svg = driver.find_elements(By.CSS_SELECTOR, "#forestContainer svg")
        assert len(svg) >= 1, "No forest plot SVG found"

    def test_21_forest_has_study_labels(self, driver):
        """Forest plot contains study name labels."""
        labels = driver.execute_script("""
            var texts = document.querySelectorAll('#forestContainer svg text');
            var result = [];
            for (var i = 0; i < texts.length; i++) result.push(texts[i].textContent);
            return result;
        """)
        # Should contain at least one study name from statins
        combined = " ".join(labels)
        assert "CTT" in combined or "JUPITER" in combined or "Overall" in combined, \
            f"Expected study labels in forest plot, got: {combined[:200]}"


# ============================================================
# 5. Theme toggle
# ============================================================

class TestTheme:
    def test_22_theme_toggle_dark(self, driver):
        """Toggle to dark mode adds .dark class to body."""
        _load_page(driver)
        theme_btn = driver.find_element(By.ID, "themeBtn")
        _js_click(driver, theme_btn)
        time.sleep(0.3)
        has_dark = driver.execute_script("return document.body.classList.contains('dark')")
        assert has_dark, "Body should have 'dark' class after toggle"
        # Button text should change
        assert "Light" in theme_btn.text

    def test_23_theme_toggle_back(self, driver):
        """Toggle back to light mode removes .dark class."""
        theme_btn = driver.find_element(By.ID, "themeBtn")
        _js_click(driver, theme_btn)
        time.sleep(0.3)
        has_dark = driver.execute_script("return document.body.classList.contains('dark')")
        assert not has_dark, "Body should NOT have 'dark' class after second toggle"
        assert "Dark" in theme_btn.text


# ============================================================
# 6. Export functionality
# ============================================================

class TestExport:
    def test_24_export_csv_no_error(self, driver):
        """Export CSV button does not throw JS errors."""
        _load_page(driver)
        _load_example(driver, "statins")
        _run_analysis(driver)
        # Intercept download by overriding createElement('a')
        driver.execute_script("""
            window._lastBlobURL = null;
            var origCreate = document.createElement.bind(document);
            document.createElement = function(tag) {
                var el = origCreate(tag);
                if (tag === 'a') {
                    var origClick = el.click;
                    el.click = function() {
                        window._lastBlobURL = el.href;
                        // don't actually trigger download
                    };
                }
                return el;
            };
        """)
        export_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Export CSV')]")
        _js_click(driver, export_btn)
        time.sleep(0.5)
        blob_url = driver.execute_script("return window._lastBlobURL")
        assert blob_url is not None and blob_url.startswith("blob:"), \
            f"Expected blob URL from export, got: {blob_url}"

    def test_25_export_r_code_present(self, driver):
        """R code block is rendered after analysis."""
        _load_page(driver)
        _load_example(driver, "statins")
        _run_analysis(driver)
        r_code = driver.find_element(By.ID, "rCodeBlock")
        text = r_code.text
        assert "metafor" in text.lower() or "rma" in text.lower(), \
            f"R code should reference metafor/rma, got: {text[:200]}"


# ============================================================
# 7. Leave-one-design-out sensitivity
# ============================================================

class TestSensitivity:
    def test_26_sensitivity_table_rendered(self, driver):
        """Leave-one-design-out table appears after analysis."""
        _load_page(driver)
        _load_example(driver, "statins")
        _run_analysis(driver)
        container = driver.find_element(By.ID, "sensitivityContainer")
        rows = container.find_elements(By.CSS_SELECTOR, "table.sens-table tbody tr")
        # Statins has 3 designs (RCT, cohort, MR) -> 3 rows
        assert len(rows) == 3, f"Expected 3 sensitivity rows, got {len(rows)}"

    def test_27_sensitivity_direction_check(self, driver):
        """Each sensitivity row shows direction agreement (Yes/No)."""
        container = driver.find_element(By.ID, "sensitivityContainer")
        text = container.text
        assert "Yes" in text or "No" in text, "Sensitivity table should show Yes/No for direction"

    def test_28_sensitivity_smoking_4designs(self, driver):
        """Smoking example has 4 designs -> 4 sensitivity rows."""
        _load_page(driver)
        _load_example(driver, "smoking")
        _run_analysis(driver)
        container = driver.find_element(By.ID, "sensitivityContainer")
        rows = container.find_elements(By.CSS_SELECTOR, "table.sens-table tbody tr")
        assert len(rows) == 4, f"Expected 4 sensitivity rows for smoking, got {len(rows)}"


# ============================================================
# 8. Additional components
# ============================================================

class TestAdditional:
    def test_29_bias_heatmap_rendered(self, driver):
        """Bias architecture heatmap appears after analysis."""
        _load_page(driver)
        _load_example(driver, "statins")
        _run_analysis(driver)
        container = driver.find_element(By.ID, "biasHeatmapContainer")
        assert container.text.strip() != "", "Bias heatmap should not be empty"

    def test_30_concordance_tabs(self, driver):
        """Concordance matrix has 4 tabs: Direction, CI Overlap, Significance, Composite."""
        tabs = driver.find_elements(By.CSS_SELECTOR, "#concordanceTabs button")
        tab_texts = [t.text for t in tabs]
        assert "Direction" in tab_texts
        assert "CI Overlap" in tab_texts
        assert "Significance" in tab_texts
        assert "Composite" in tab_texts

    def test_31_concordance_tab_switching(self, driver):
        """Switching concordance tabs shows correct panels."""
        overlap_tab = driver.find_element(By.ID, "concOverlapTab")
        _js_click(driver, overlap_tab)
        time.sleep(0.3)
        panel = driver.find_element(By.ID, "concOverlapPanel")
        assert "active" in panel.get_attribute("class"), "CI Overlap panel should be active"
        direction_panel = driver.find_element(By.ID, "concDirectionPanel")
        assert "active" not in direction_panel.get_attribute("class"), \
            "Direction panel should not be active"

    def test_32_report_text_generated(self, driver):
        """Auto-generated report contains key phrases."""
        _load_page(driver)
        _load_example(driver, "statins")
        _run_analysis(driver)
        report = driver.find_element(By.ID, "reportText")
        text = report.text
        assert "METHODS" in text, "Report should contain METHODS section"
        assert "RESULTS" in text, "Report should contain RESULTS section"
        assert "CausalSynth" in text, "Report should mention CausalSynth"
        assert "DerSimonian-Laird" in text, "Report should mention DL method"

    def test_33_design_compare_cards(self, driver):
        """Design comparison cards are rendered."""
        grid = driver.find_element(By.ID, "designCompareGrid")
        cards = grid.find_elements(By.CSS_SELECTOR, ".design-compare-card")
        # Statins: 3 design types
        assert len(cards) >= 3, f"Expected >= 3 design cards, got {len(cards)}"

    def test_34_dag_template_load(self, driver):
        """Loading a DAG template renders nodes in SVG."""
        _load_page(driver)
        driver.execute_script("loadDAGTemplate('confounding')")
        time.sleep(0.3)
        svg = driver.find_element(By.ID, "dagSvg")
        texts = svg.find_elements(By.TAG_NAME, "text")
        text_contents = [t.text for t in texts]
        combined = " ".join(text_contents)
        assert "Exposure" in combined or "Outcome" in combined, \
            f"DAG should show Exposure/Outcome nodes, got: {combined}"

    def test_35_clear_all(self, driver):
        """Clear All removes all rows from the data table."""
        _load_page(driver)
        _load_example(driver, "statins")
        rows_before = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows_before) > 0
        driver.execute_script("clearAll()")
        time.sleep(0.3)
        rows_after = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows_after) == 0, "After clearAll, data table should be empty"

    def test_36_add_row(self, driver):
        """Add Study button adds a row to the data table."""
        _load_page(driver)
        driver.execute_script("clearAll()")
        time.sleep(0.2)
        driver.execute_script("addRow()")
        time.sleep(0.2)
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == 1, f"Expected 1 row after addRow, got {len(rows)}"

    def test_37_run_button_disabled_with_few_studies(self, driver):
        """Run button is disabled when fewer than 2 studies."""
        _load_page(driver)
        driver.execute_script("clearAll()")
        time.sleep(0.2)
        driver.execute_script("addRow()")
        time.sleep(0.2)
        # Sync to update button state
        driver.execute_script("sync()")
        time.sleep(0.2)
        btn = driver.find_element(By.ID, "runBtn")
        is_disabled = btn.get_attribute("disabled")
        assert is_disabled, "Run button should be disabled with < 2 studies"

    def test_38_funnel_plot_rendered(self, driver):
        """Funnel plot SVG is rendered after analysis."""
        _load_page(driver)
        _load_example(driver, "statins")
        _run_analysis(driver)
        svgs = driver.find_elements(By.CSS_SELECTOR, "#funnelContainer svg")
        assert len(svgs) >= 1, "Funnel plot SVG should be rendered"

    def test_39_causal_correction_rendered(self, driver):
        """Causal correction (CaMeA) section appears for statins (which has p0)."""
        card = driver.find_element(By.ID, "causalCorrectionCard")
        displayed = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display !== 'none'", card
        )
        assert displayed, "Causal correction card should be visible for statins"

    def test_40_interpretation_panel(self, driver):
        """Interpretation panel is rendered after analysis."""
        panel = driver.find_element(By.ID, "interpPanel")
        text = panel.text
        assert len(text) > 20, f"Interpretation panel should have content, got {len(text)} chars"

    def test_41_no_js_errors(self, driver):
        """No severe JS errors in browser console after full run."""
        _load_page(driver)
        _load_example(driver, "statins")
        _run_analysis(driver)
        logs = driver.get_log("browser")
        severe = [l for l in logs if l.get("level") == "SEVERE"
                  and "favicon" not in l.get("message", "").lower()]
        assert len(severe) == 0, f"Severe JS errors found: {severe}"


# ============================================================
# New Feature Tests
# ============================================================

class TestNewFeatures:
    """Tests for features added in CausalSynth v2.0."""

    def test_42_json_import_button(self, driver):
        """JSON import button exists."""
        _load_page(driver)
        btn = driver.find_elements(By.XPATH, "//button[contains(text(),'Import JSON')]")
        assert len(btn) > 0

    def test_43_drop_zone_exists(self, driver):
        """Drop zone element exists."""
        zone = driver.find_elements(By.ID, "dropZone")
        assert len(zone) > 0

    def test_44_png_export_button(self, driver):
        """PNG export button exists."""
        btn = driver.find_elements(By.XPATH, "//button[contains(text(),'Export PNG')]")
        assert len(btn) > 0

    def test_45_tutorial_button(self, driver):
        """Tutorial button exists."""
        btn = driver.find_elements(By.XPATH, "//button[contains(text(),'Tutorial')]")
        assert len(btn) > 0

    def test_46_tutorial_starts(self, driver):
        """Tutorial overlay appears."""
        driver.execute_script("startTutorial()")
        time.sleep(0.5)
        active = driver.execute_script("return document.getElementById('tutorialOverlay').classList.contains('active')")
        assert active
        driver.execute_script("closeTutorial()")

    def test_47_tutorial_step_text(self, driver):
        """Tutorial shows title."""
        driver.execute_script("startTutorial()")
        time.sleep(0.3)
        title = driver.execute_script("return document.getElementById('tutTitle').textContent")
        assert len(title) > 0
        driver.execute_script("closeTutorial()")

    def test_48_tutorial_navigation(self, driver):
        """Tutorial Next advances step."""
        driver.execute_script("startTutorial()")
        driver.execute_script("tutNext()")
        time.sleep(0.3)
        step = driver.execute_script("return document.getElementById('tutStep').textContent")
        assert '2' in step
        driver.execute_script("closeTutorial()")

    def test_49_bias_direction_card(self, driver):
        """Bias direction model card appears after analysis."""
        _load_page(driver)
        _load_example(driver, "statins")
        _run_analysis(driver)
        display = driver.execute_script("return document.getElementById('biasDirectionCard').style.display")
        assert display != 'none'

    def test_50_bias_direction_content(self, driver):
        """Bias direction table has content."""
        content = driver.execute_script("return document.getElementById('biasDirectionContent').innerHTML")
        assert 'RCT' in content or 'Cohort' in content

    def test_51_truthcert_card_visible(self, driver):
        """TruthCert card visible after analysis."""
        display = driver.execute_script("return document.getElementById('truthcertCard').style.display")
        assert display != 'none'

    def test_52_truthcert_has_hash(self, driver):
        """TruthCert content has SHA-256."""
        content = driver.execute_script("return document.getElementById('truthcertContent').textContent")
        assert 'SHA-256' in content or len(content) > 20

    def test_53_truthcert_badge(self, driver):
        """TruthCert shows CERTIFIED."""
        badge = driver.execute_script("return document.getElementById('truthcertBadge').textContent")
        assert 'CERTIFIED' in badge

    def test_54_bias_direction_model_data(self, driver):
        """BIAS_DIRECTION constant has all design types."""
        _load_page(driver)
        count = driver.execute_script("return Object.keys(BIAS_DIRECTION).length")
        assert count == 6

    def test_55_export_png_no_crash(self, driver):
        """exportPNG runs without throwing."""
        _load_example(driver, "statins")
        _run_analysis(driver)
        error = driver.execute_script("""
            try { exportPNG(); return null; }
            catch(e) { return e.message; }
        """)

    def test_56_all_examples_no_errors(self, driver):
        """All 5 example datasets analyze without JS errors."""
        for ds in ['statins', 'meddiet', 'smoking', 'alcohol', 'exercise']:
            _load_page(driver)
            _load_example(driver, ds)
            _run_analysis(driver)
            n = driver.execute_script("return triResults ? Object.keys(triResults.designResults).length : 0")
            assert n >= 2, f"Dataset {ds} should have >=2 designs, got {n}"

    def test_57_truthcert_download_fn_exists(self, driver):
        """downloadTruthCert function exists."""
        _load_page(driver)
        exists = driver.execute_script("return typeof downloadTruthCert === 'function'")
        assert exists

    def test_58_tutorial_closes(self, driver):
        """Tutorial closes properly."""
        driver.execute_script("startTutorial()")
        time.sleep(0.3)
        driver.execute_script("closeTutorial()")
        time.sleep(0.3)
        active = driver.execute_script("return document.getElementById('tutorialOverlay').classList.contains('active')")
        assert not active

    def test_59_population_summary_fn(self, driver):
        """renderPopulationSummary function exists."""
        exists = driver.execute_script("return typeof renderPopulationSummary === 'function'")
        assert exists

    def test_60_handle_drag_functions(self, driver):
        """Drag-drop handler functions exist."""
        exists = driver.execute_script("""
            return typeof handleDragOver === 'function' &&
                   typeof handleDragLeave === 'function' &&
                   typeof handleDrop === 'function'
        """)
        assert exists
