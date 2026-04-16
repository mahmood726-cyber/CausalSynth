"""
Selenium test suite for CausalSynth Phase 2 features:
- Design comparison cards & evidence weight bar
- Bias architecture heatmap (interactive)
- Evidence concordance matrix (4 tabs)
- Funnel plot (design-colored)
- New example datasets (alcohol, exercise)
- Accessibility (skip link, ARIA, keyboard nav)
- Auto-load demo data on startup

30 tests across 8 categories.
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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

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
    toggle = driver.find_element(By.CSS_SELECTOR, ".example-dropdown > button")
    toggle.click()
    time.sleep(0.3)
    buttons = driver.find_elements(By.CSS_SELECTOR, "#exampleDropdown button")
    for btn in buttons:
        if name.lower() in btn.text.lower():
            btn.click()
            break
    time.sleep(0.3)


def run_triangulation(driver):
    """Click the Run Triangulation button."""
    run_btn = driver.find_element(By.ID, "runBtn")
    driver.execute_script("arguments[0].scrollIntoView(true);", run_btn)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", run_btn)
    time.sleep(0.5)


def get_console_errors(driver):
    """Return list of SEVERE console log entries (excluding favicon 404s)."""
    logs = driver.get_log("browser")
    return [l for l in logs if l.get("level") == "SEVERE" and "favicon" not in l.get("message", "")]


# ================================================================
# Category 1: Auto-Load Demo Data on Startup (2 tests)
# ================================================================
def test_01_auto_load_on_startup(driver):
    """Statins dataset should be loaded automatically on page load."""
    driver.get(URL)
    time.sleep(1)
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    assert len(rows) >= 10, f"Expected >=10 rows auto-loaded, got {len(rows)}"
    badge = driver.find_element(By.ID, "studyBadge")
    text = badge.text
    assert "12" in text or "stud" in text.lower(), f"Badge should show 12 studies, got: {text}"
    return True


def test_02_run_button_enabled_on_load(driver):
    """Run button should be enabled immediately since demo data is loaded."""
    driver.get(URL)
    time.sleep(0.8)
    run_btn = driver.find_element(By.ID, "runBtn")
    assert not run_btn.get_attribute("disabled"), "Run button should be enabled on load with demo data"
    return True


# ================================================================
# Category 2: Design Comparison Cards (4 tests)
# ================================================================
def test_03_design_compare_grid_renders(driver):
    """Design comparison cards should render after triangulation."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    cards = driver.find_elements(By.CSS_SELECTOR, "#designCompareGrid .design-compare-card")
    assert len(cards) >= 3, f"Expected >=3 design cards (RCT,cohort,MR), got {len(cards)}"
    return True


def test_04_design_card_has_effect_and_ci(driver):
    """Each design card should show pooled effect and CI."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    cards = driver.find_elements(By.CSS_SELECTOR, "#designCompareGrid .design-compare-card")
    for card in cards:
        stats = card.find_elements(By.CSS_SELECTOR, ".dc-stat")
        labels = [s.find_element(By.CSS_SELECTOR, ".dc-label").text for s in stats]
        assert "Pooled Effect" in labels, f"Missing 'Pooled Effect' in card labels: {labels}"
        assert "95% CI" in labels, f"Missing '95% CI' in card labels: {labels}"
    return True


def test_05_evidence_weight_bar_renders(driver):
    """Evidence weight stacked bar should render with segments."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    segments = driver.find_elements(By.CSS_SELECTOR, "#evidenceWeightBar .evidence-weight-segment")
    assert len(segments) >= 3, f"Expected >=3 weight segments, got {len(segments)}"
    return True


def test_06_weight_percentages_sum_to_100(driver):
    """Evidence weight percentages should approximately sum to 100."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    cards = driver.find_elements(By.CSS_SELECTOR, "#designCompareGrid .design-compare-card")
    total_pct = 0.0
    for card in cards:
        stats = card.find_elements(By.CSS_SELECTOR, ".dc-stat")
        for s in stats:
            lbl = s.find_element(By.CSS_SELECTOR, ".dc-label").text
            if "Weight" in lbl:
                val_text = s.find_element(By.CSS_SELECTOR, ".dc-value").text.replace("%", "")
                total_pct += float(val_text)
    assert 99.0 <= total_pct <= 101.0, f"Weight pcts should sum to ~100%, got {total_pct:.1f}%"
    return True


# ================================================================
# Category 3: Bias Architecture Heatmap (4 tests)
# ================================================================
def test_07_bias_heatmap_svg_renders(driver):
    """Bias heatmap SVG should render with rect elements."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    rects = driver.find_elements(By.CSS_SELECTOR, "#biasHeatmapContainer svg rect[data-bias]")
    # 3 designs x 5 biases = 15 cells minimum
    assert len(rects) >= 15, f"Expected >=15 heatmap cells, got {len(rects)}"
    return True


def test_08_bias_heatmap_click_shows_detail(driver):
    """Clicking a heatmap cell should reveal the detail panel."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    rects = driver.find_elements(By.CSS_SELECTOR, "#biasHeatmapContainer svg rect[data-bias]")
    assert len(rects) > 0, "No heatmap cells found"
    # Click the first rect
    driver.execute_script("arguments[0].dispatchEvent(new Event('click'));", rects[0])
    time.sleep(0.3)
    panel = driver.find_element(By.ID, "biasDetailPanel")
    assert "visible" in panel.get_attribute("class"), "Detail panel should be visible after click"
    return True


def test_09_bias_detail_has_text_content(driver):
    """Bias detail panel should contain meaningful text."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    rects = driver.find_elements(By.CSS_SELECTOR, "#biasHeatmapContainer svg rect[data-bias]")
    driver.execute_script("arguments[0].dispatchEvent(new Event('click'));", rects[0])
    time.sleep(0.3)
    content = driver.find_element(By.ID, "biasDetailContent").text
    assert len(content) > 20, f"Detail content too short: '{content}'"
    return True


def test_10_bias_heatmap_has_high_risk_count(driver):
    """Heatmap should show high-risk count summary row."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    svg_text = driver.find_element(By.CSS_SELECTOR, "#biasHeatmapContainer svg").get_attribute("innerHTML")
    assert "High-risk count" in svg_text, "Should have 'High-risk count' summary row"
    return True


# ================================================================
# Category 4: Evidence Concordance Matrix (6 tests)
# ================================================================
def test_11_concordance_card_renders(driver):
    """Concordance card with tabs should render."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    tabs = driver.find_elements(By.CSS_SELECTOR, "#concordanceTabs button[role='tab']")
    assert len(tabs) == 4, f"Expected 4 concordance tabs, got {len(tabs)}"
    return True


def test_12_direction_matrix_has_agree_cells(driver):
    """Direction concordance matrix should have 'Agree' cells for statins data."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    cells = driver.find_elements(By.CSS_SELECTOR, "#concDirectionMatrix td.conc-agree")
    # All designs should agree for statins (all protective)
    assert len(cells) >= 3, f"Expected >=3 'Agree' cells, got {len(cells)}"
    return True


def test_13_ci_overlap_tab_renders(driver):
    """CI Overlap tab should render percentages."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    # Click CI Overlap tab
    overlap_tab = driver.find_element(By.ID, "concOverlapTab")
    overlap_tab.click()
    time.sleep(0.3)
    panel = driver.find_element(By.ID, "concOverlapPanel")
    assert "active" in panel.get_attribute("class"), "Overlap panel should be active"
    cells = panel.find_elements(By.CSS_SELECTOR, "td")
    non_na = [c for c in cells if c.text != "--"]
    assert len(non_na) >= 3, f"Expected >=3 non-NA overlap cells, got {len(non_na)}"
    return True


def test_14_significance_tab_renders(driver):
    """Significance concordance tab should render."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    sig_tab = driver.find_element(By.ID, "concSignifTab")
    sig_tab.click()
    time.sleep(0.3)
    panel = driver.find_element(By.ID, "concSignifPanel")
    assert "active" in panel.get_attribute("class"), "Signif panel should be active"
    return True


def test_15_composite_tab_renders(driver):
    """Composite concordance tab should render with numeric scores."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    comp_tab = driver.find_element(By.ID, "concCompositeTab")
    comp_tab.click()
    time.sleep(0.3)
    cells = driver.find_elements(By.CSS_SELECTOR, "#concCompositeMatrix td:not(.conc-na)")
    # Check that at least one cell has a numeric value
    has_numeric = False
    for c in cells:
        try:
            float(c.text)
            has_numeric = True
            break
        except ValueError:
            continue
    assert has_numeric, "Composite matrix should have numeric scores"
    return True


def test_16_concordance_summary_renders(driver):
    """Concordance summary panel should render with pairwise count."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    summary = driver.find_element(By.ID, "concordanceSummary")
    text = summary.text
    assert "Pairwise" in text or "pairs" in text.lower(), f"Summary should mention pairwise: {text}"
    return True


# ================================================================
# Category 5: Funnel Plot (3 tests)
# ================================================================
def test_17_funnel_plot_renders(driver):
    """Funnel plot SVG should render with circles."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    circles = driver.find_elements(By.CSS_SELECTOR, "#funnelContainer svg circle")
    assert len(circles) >= 10, f"Expected >=10 funnel circles, got {len(circles)}"
    return True


def test_18_funnel_plot_has_funnel_region(driver):
    """Funnel plot should have the pseudo-CI funnel polygon."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    polygons = driver.find_elements(By.CSS_SELECTOR, "#funnelContainer svg polygon")
    assert len(polygons) >= 1, "Funnel plot should have at least 1 polygon (funnel region)"
    return True


def test_19_funnel_has_axis_labels(driver):
    """Funnel plot should have axis labels."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    svg_text = driver.find_element(By.CSS_SELECTOR, "#funnelContainer svg").get_attribute("innerHTML")
    assert "Effect Size" in svg_text, "Funnel should have 'Effect Size' x-axis label"
    assert "Standard Error" in svg_text, "Funnel should have 'Standard Error' y-axis label"
    return True


# ================================================================
# Category 6: New Example Datasets (4 tests)
# ================================================================
def test_20_dropdown_has_5_examples(driver):
    """Example dropdown should have 5 options (statins, meddiet, smoking, alcohol, exercise)."""
    driver.get(URL)
    time.sleep(0.8)
    toggle = driver.find_element(By.CSS_SELECTOR, ".example-dropdown > button")
    toggle.click()
    time.sleep(0.3)
    buttons = driver.find_elements(By.CSS_SELECTOR, "#exampleDropdown button[role='menuitem']")
    assert len(buttons) == 5, f"Expected 5 example buttons, got {len(buttons)}"
    return True


def test_21_load_alcohol_dataset(driver):
    """Loading Alcohol dataset should populate 9 studies."""
    driver.get(URL)
    time.sleep(0.8)
    load_example(driver, "alcohol")
    badge = driver.find_element(By.ID, "studyBadge")
    assert "9" in badge.text, f"Alcohol dataset should have 9 studies, badge: {badge.text}"
    return True


def test_22_load_exercise_dataset(driver):
    """Loading Exercise dataset should populate 8 studies."""
    driver.get(URL)
    time.sleep(0.8)
    load_example(driver, "exercise")
    badge = driver.find_element(By.ID, "studyBadge")
    assert "8" in badge.text, f"Exercise dataset should have 8 studies, badge: {badge.text}"
    return True


def test_23_alcohol_runs_triangulation(driver):
    """Alcohol dataset should run triangulation with 5 designs."""
    driver.get(URL)
    time.sleep(0.8)
    load_example(driver, "alcohol")
    run_triangulation(driver)
    time.sleep(0.5)
    metrics = driver.find_elements(By.CSS_SELECTOR, "#convMetrics .conv-metric")
    # First metric should be number of designs
    first_val = metrics[0].find_element(By.CSS_SELECTOR, ".val").text
    assert first_val == "5", f"Alcohol should have 5 designs, got: {first_val}"
    return True


# ================================================================
# Category 7: Accessibility (4 tests)
# ================================================================
def test_24_skip_link_exists(driver):
    """Page should have a skip-to-content link."""
    driver.get(URL)
    time.sleep(0.5)
    skip = driver.find_elements(By.CSS_SELECTOR, "a.skip-link")
    assert len(skip) == 1, "Should have exactly 1 skip link"
    assert skip[0].get_attribute("href").endswith("#mainContent"), "Skip link should point to #mainContent"
    return True


def test_25_aria_labels_on_buttons(driver):
    """Header buttons should have aria-labels."""
    driver.get(URL)
    time.sleep(0.5)
    theme_btn = driver.find_element(By.ID, "themeBtn")
    assert theme_btn.get_attribute("aria-label"), "Theme button should have aria-label"
    example_btn = driver.find_element(By.ID, "exampleBtn")
    assert example_btn.get_attribute("aria-haspopup") == "true", "Example button should have aria-haspopup"
    return True


def test_26_tab_role_on_concordance(driver):
    """Concordance tabs should have proper ARIA tab roles."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    tabs = driver.find_elements(By.CSS_SELECTOR, "#concordanceTabs button[role='tab']")
    assert len(tabs) == 4, f"Expected 4 tabs with role=tab, got {len(tabs)}"
    # First tab should be selected
    assert tabs[0].get_attribute("aria-selected") == "true", "First tab should be aria-selected=true"
    assert tabs[1].get_attribute("aria-selected") == "false", "Second tab should be aria-selected=false"
    return True


def test_27_main_content_role(driver):
    """Container should have role=main and id=mainContent."""
    driver.get(URL)
    time.sleep(0.5)
    main = driver.find_elements(By.CSS_SELECTOR, "#mainContent[role='main']")
    assert len(main) == 1, "Should have #mainContent with role=main"
    return True


# ================================================================
# Category 8: Cross-feature integration (3 tests)
# ================================================================
def test_28_switching_datasets_rerenders(driver):
    """Switching from statins to smoking should update results."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    # Get initial design count
    metrics = driver.find_elements(By.CSS_SELECTOR, "#convMetrics .conv-metric")
    initial_designs = metrics[0].find_element(By.CSS_SELECTOR, ".val").text

    # Switch to smoking
    load_example(driver, "smoking")
    run_triangulation(driver)
    time.sleep(0.5)
    metrics2 = driver.find_elements(By.CSS_SELECTOR, "#convMetrics .conv-metric")
    new_designs = metrics2[0].find_element(By.CSS_SELECTOR, ".val").text
    # Smoking has 4 designs vs statins 3
    assert new_designs == "4", f"Smoking should have 4 designs, got: {new_designs}"
    return True


def test_29_report_includes_concordance(driver):
    """Generated report text should include pairwise concordance info."""
    driver.get(URL)
    time.sleep(0.8)
    run_triangulation(driver)
    time.sleep(0.5)
    report_text = driver.find_element(By.ID, "reportText").text
    assert "Pairwise concordance" in report_text or "pairwise" in report_text.lower() or "pairs" in report_text.lower(), \
        "Report should mention pairwise concordance"
    return True


def test_30_no_console_errors_after_full_run(driver):
    """Running all features should produce no SEVERE console errors."""
    driver.get(URL)
    time.sleep(0.8)
    # Load statins (default), run, then switch
    run_triangulation(driver)
    time.sleep(0.5)
    # Click through concordance tabs
    for tab_id in ["concOverlapTab", "concSignifTab", "concCompositeTab", "concDirectionTab"]:
        try:
            driver.find_element(By.ID, tab_id).click()
            time.sleep(0.2)
        except Exception:
            pass
    # Click a bias heatmap cell
    rects = driver.find_elements(By.CSS_SELECTOR, "#biasHeatmapContainer svg rect[data-bias]")
    if rects:
        driver.execute_script("arguments[0].dispatchEvent(new Event('click'));", rects[0])
        time.sleep(0.2)
    # Switch to exercise dataset
    load_example(driver, "exercise")
    run_triangulation(driver)
    time.sleep(0.5)
    # Check console
    errors = get_console_errors(driver)
    assert len(errors) == 0, f"Console errors: {[e['message'] for e in errors]}"
    return True


# ================================================================
# Test Runner
# ================================================================
ALL_TESTS = [
    test_01_auto_load_on_startup,
    test_02_run_button_enabled_on_load,
    test_03_design_compare_grid_renders,
    test_04_design_card_has_effect_and_ci,
    test_05_evidence_weight_bar_renders,
    test_06_weight_percentages_sum_to_100,
    test_07_bias_heatmap_svg_renders,
    test_08_bias_heatmap_click_shows_detail,
    test_09_bias_detail_has_text_content,
    test_10_bias_heatmap_has_high_risk_count,
    test_11_concordance_card_renders,
    test_12_direction_matrix_has_agree_cells,
    test_13_ci_overlap_tab_renders,
    test_14_significance_tab_renders,
    test_15_composite_tab_renders,
    test_16_concordance_summary_renders,
    test_17_funnel_plot_renders,
    test_18_funnel_plot_has_funnel_region,
    test_19_funnel_has_axis_labels,
    test_20_dropdown_has_5_examples,
    test_21_load_alcohol_dataset,
    test_22_load_exercise_dataset,
    test_23_alcohol_runs_triangulation,
    test_24_skip_link_exists,
    test_25_aria_labels_on_buttons,
    test_26_tab_role_on_concordance,
    test_27_main_content_role,
    test_28_switching_datasets_rerenders,
    test_29_report_includes_concordance,
    test_30_no_console_errors_after_full_run,
]


def main():
    print("=" * 70)
    print("CausalSynth Phase 2 Test Suite")
    print("=" * 70)

    passed = 0
    failed = 0
    errors = []

    driver = None
    try:
        driver = create_driver()
        for test_fn in ALL_TESTS:
            name = test_fn.__name__
            try:
                result = test_fn(driver)
                if result:
                    print(f"  PASS  {name}")
                    passed += 1
                else:
                    print(f"  FAIL  {name} (returned False)")
                    failed += 1
                    errors.append(name)
            except AssertionError as e:
                print(f"  FAIL  {name}: {e}")
                failed += 1
                errors.append(f"{name}: {e}")
            except Exception as e:
                print(f"  ERROR {name}: {e}")
                traceback.print_exc()
                failed += 1
                errors.append(f"{name}: {e}")
    finally:
        if driver:
            driver.quit()

    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    print("=" * 70)
    if errors:
        print("\nFailed tests:")
        for e in errors:
            print(f"  - {e}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
