import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_URL = 'http://127.0.0.1:8000/causal-synth.html'
EXAMPLE_COUNTS = {
    'statins': 12,
    'meddiet': 7,
    'smoking': 8,
    'hiv': 7,
    'immunotherapy': 7,
}
EXAMPLE_DESIGNS = {
    'statins': 3,
    'meddiet': 3,
    'smoking': 4,
    'hiv': 4,
    'immunotherapy': 3,
}


@pytest.fixture(scope='module')
def app_server():
    handler = partial(SimpleHTTPRequestHandler, directory=str(PROJECT_ROOT))
    server = ThreadingHTTPServer(('127.0.0.1', 8000), handler)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


@pytest.fixture(scope='module')
def driver(app_server):
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1400,1200')
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    try:
        drv = webdriver.Chrome(options=opts)
    except WebDriverException as exc:
        pytest.skip(f'Chrome webdriver unavailable: {exc}')
    drv.set_page_load_timeout(30)
    drv.implicitly_wait(2)
    try:
        yield drv
    finally:
        drv.quit()


def _load_page(driver):
    driver.get(APP_URL)
    driver.execute_script('window.confirm = function(){return true}; window.alert = function(){};')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'dataBody')))


def _clear_browser_logs(driver):
    try:
        driver.get_log('browser')
    except Exception:
        pass


def _js_click(driver, element):
    driver.execute_script('arguments[0].click()', element)


def _load_example(driver, key):
    driver.execute_script("loadExample(arguments[0])", key)
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, '#dataBody tr')) == EXAMPLE_COUNTS[key]
    )


def _run_analysis(driver):
    btn = driver.find_element(By.ID, 'runBtn')
    _js_click(driver, btn)
    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script("return document.getElementById('results').style.display") == 'block'
    )
    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script('return !!(window._truthCertBundle && triResults)')
    )


def _visible(driver, element_id):
    return driver.execute_script(
        "var el = document.getElementById(arguments[0]);"
        "return !!el && window.getComputedStyle(el).display !== 'none';",
        element_id,
    )


def _console_severe(driver):
    logs = driver.get_log('browser')
    return [
        entry for entry in logs
        if entry.get('level') == 'SEVERE'
        and 'favicon' not in entry.get('message', '').lower()
    ]


class TestPageLoad:
    def test_page_loads(self, driver):
        _load_page(driver)
        assert 'CausalSynth' in driver.title

    def test_header_brand_visible(self, driver):
        brand = driver.find_element(By.CSS_SELECTOR, 'header .brand')
        assert brand.text == 'CausalSynth'

    def test_data_table_headers_present(self, driver):
        headers = [h.text for h in driver.find_elements(By.CSS_SELECTOR, '#dataTable th')]
        assert headers[:5] == ['#', 'Study', 'Design', 'Effect (yi)', 'SE']

    def test_run_button_present(self, driver):
        btn = driver.find_element(By.ID, 'runBtn')
        assert 'Run Triangulation' in btn.text

    def test_example_button_present(self, driver):
        btn = driver.find_element(By.ID, 'exampleToggleBtn')
        assert 'Load Example' in btn.text

    def test_initial_state_has_no_rows(self, driver):
        assert len(driver.find_elements(By.CSS_SELECTOR, '#dataBody tr')) == 5
        assert driver.find_element(By.ID, 'studyBadge').text == '0 studies'
        assert driver.find_element(By.ID, 'runBtn').get_attribute('disabled')


class TestExamples:
    @pytest.mark.parametrize(
        ('dataset', 'expected_rows'),
        tuple(EXAMPLE_COUNTS.items()),
    )
    def test_example_dataset_loads(self, driver, dataset, expected_rows):
        _load_page(driver)
        _load_example(driver, dataset)
        assert len(driver.find_elements(By.CSS_SELECTOR, '#dataBody tr')) == expected_rows

    def test_study_badge_updates(self, driver):
        _load_page(driver)
        _load_example(driver, 'statins')
        assert '12' in driver.find_element(By.ID, 'studyBadge').text

    def test_example_keys_match_current_catalog(self, driver):
        _load_page(driver)
        keys = driver.execute_script('return Object.keys(EXAMPLE_DATASETS)')
        assert keys == ['statins', 'meddiet', 'smoking', 'hiv', 'immunotherapy']


class TestAnalysis:
    def test_run_statins_analysis(self, driver):
        _load_page(driver)
        _clear_browser_logs(driver)
        _load_example(driver, 'statins')
        _run_analysis(driver)
        assert _visible(driver, 'results')

    def test_convergence_metrics_render(self, driver):
        text = driver.find_element(By.ID, 'convMetrics').text
        assert 'Causal Evidence Score' in text
        assert 'Direction Concordance' in text
        assert 'Magnitude Consistency' in text
        assert 'Bias Diversity' in text

    def test_convergence_values_are_numeric(self, driver):
        vals = driver.execute_script("""
            return Array.from(document.querySelectorAll('#convMetrics .conv-metric .val'))
              .map(node => node.textContent.trim());
        """)
        assert len(vals) >= 6
        assert '%' in vals[2]
        assert 0 <= float(vals[5]) <= 1

    def test_pooled_effect_and_grade_badge_render(self, driver):
        text = driver.find_element(By.ID, 'convMetrics').text
        assert 'Pooled Effect' in text
        assert driver.find_elements(By.CSS_SELECTOR, '.grade-badge')

    def test_forest_plot_renders(self, driver):
        assert driver.find_elements(By.CSS_SELECTOR, '#forestContainer svg')

    def test_forest_plot_has_study_labels(self, driver):
        labels = driver.execute_script("""
            return Array.from(document.querySelectorAll('#forestContainer svg text'))
              .map(node => node.textContent);
        """)
        combined = ' '.join(labels)
        assert 'CTT' in combined or 'JUPITER' in combined or 'Overall' in combined

    def test_theme_toggle_dark_and_back(self, driver):
        _load_page(driver)
        btn = driver.find_element(By.ID, 'themeBtn')
        _js_click(driver, btn)
        time.sleep(0.2)
        assert driver.execute_script("return document.body.classList.contains('dark')")
        assert 'Light' in btn.text
        _js_click(driver, btn)
        time.sleep(0.2)
        assert not driver.execute_script("return document.body.classList.contains('dark')")
        assert 'Dark' in btn.text


class TestExportAndReport:
    def test_export_csv_creates_blob_url(self, driver):
        _load_page(driver)
        _load_example(driver, 'statins')
        _run_analysis(driver)
        driver.execute_script("""
            window._lastBlobURL = null;
            const origCreate = document.createElement.bind(document);
            document.createElement = function(tag) {
              const el = origCreate(tag);
              if (tag === 'a') {
                el.click = function() { window._lastBlobURL = el.href; };
              }
              return el;
            };
        """)
        _js_click(driver, driver.find_element(By.XPATH, "//button[contains(text(),'Export CSV')]"))
        time.sleep(0.3)
        blob_url = driver.execute_script('return window._lastBlobURL')
        assert blob_url and blob_url.startswith('blob:')

    def test_report_text_contains_methods_and_results(self, driver):
        text = driver.find_element(By.ID, 'reportText').text
        assert 'METHODS' in text
        assert 'RESULTS' in text
        assert 'CausalSynth' in text
        assert 'DerSimonian-Laird' in text

    def test_r_code_block_contains_metafor(self, driver):
        text = driver.find_element(By.ID, 'rCodeBlock').text.lower()
        assert 'metafor' in text or 'rma' in text

    def test_export_pdf_calls_window_print(self, driver):
        _load_page(driver)
        _load_example(driver, 'statins')
        _run_analysis(driver)
        called = driver.execute_script("""
            window._printCalled = false;
            window.print = function(){ window._printCalled = true; };
            exportPDF();
            return window._printCalled;
        """)
        assert called


class TestResultsCards:
    def test_sensitivity_table_for_statins_has_three_rows(self, driver):
        count = driver.execute_script("""
            const table = document.querySelector('#sensitivityContainer table.sens-table');
            return table ? table.querySelectorAll('tbody tr').length : 0;
        """)
        assert count == 3

    def test_bias_table_renders(self, driver):
        text = driver.find_element(By.ID, 'biasContainer').text
        assert 'RCT' in text
        assert 'Confounding' in text

    def test_interpretation_panel_has_content(self, driver):
        assert len(driver.find_element(By.ID, 'interpPanel').text) > 40

    def test_funnel_plot_renders(self, driver):
        assert driver.find_elements(By.CSS_SELECTOR, '#funnelContainer svg')

    def test_subgroup_network_rob_and_timeline_cards_show(self, driver):
        for element_id in ('subgroupCard', 'networkCard', 'robCard', 'timelineCard', 'webrCard'):
            assert _visible(driver, element_id), element_id

    def test_all_examples_analyze_with_expected_design_counts(self, driver):
        for dataset, expected_designs in EXAMPLE_DESIGNS.items():
            _load_page(driver)
            _clear_browser_logs(driver)
            _load_example(driver, dataset)
            _run_analysis(driver)
            observed = driver.execute_script('return Object.keys(triResults.designResults).length')
            assert observed == expected_designs, (dataset, observed, expected_designs)
            assert not _console_severe(driver), dataset


class TestTutorialAndTruthCert:
    def test_json_import_button_exists(self, driver):
        _load_page(driver)
        assert driver.find_elements(By.XPATH, "//button[contains(text(),'Import JSON')]")

    def test_export_pdf_button_exists(self, driver):
        assert driver.find_elements(By.XPATH, "//button[contains(text(),'Export PDF')]")

    def test_tutorial_button_exists(self, driver):
        assert driver.find_elements(By.XPATH, "//button[contains(text(),'Tutorial')]")

    def test_open_and_close_tutorial(self, driver):
        driver.execute_script('openTutorial()')
        time.sleep(0.2)
        assert driver.execute_script("return document.getElementById('tutorialOverlay').classList.contains('active')")
        driver.execute_script('closeTutorial()')
        time.sleep(0.2)
        assert not driver.execute_script("return document.getElementById('tutorialOverlay').classList.contains('active')")

    def test_tutorial_contains_six_steps(self, driver):
        driver.execute_script('openTutorial()')
        steps = driver.find_elements(By.CSS_SELECTOR, '#tutorialOverlay .tutorial-step')
        assert len(steps) == 6
        driver.execute_script('closeTutorial()')

    def test_tutorial_highlight_marks_target(self, driver):
        driver.execute_script('openTutorial()')
        driver.execute_script("tutorialHighlight('dataCard')")
        time.sleep(0.3)
        active = driver.execute_script("return document.getElementById('dataCard').classList.contains('pulse-highlight')")
        assert active

    def test_truthcert_card_is_visible_after_analysis(self, driver):
        _load_page(driver)
        _load_example(driver, 'statins')
        _run_analysis(driver)
        assert _visible(driver, 'truthcertCard')

    def test_truthcert_chain_has_four_steps(self, driver):
        steps = driver.find_elements(By.CSS_SELECTOR, '#truthcertChain .tc-step')
        assert len(steps) == 4

    def test_truthcert_seal_badge_is_present(self, driver):
        assert 'SEALED' in driver.find_element(By.ID, 'truthcertSealBadge').text

    def test_truthcert_bundle_contains_certification_hash(self, driver):
        bundle = driver.execute_script('return window._truthCertBundle')
        assert bundle['certification']['status'] == 'SEALED'
        assert len(bundle['certification']['hash']) == 64

    def test_download_truthcert_bundle_function_exists(self, driver):
        assert driver.execute_script("return typeof downloadTruthCertBundle === 'function'")


class TestRuntimeContract:
    def test_bias_profile_and_design_constants_exist(self, driver):
        counts = driver.execute_script("""
            return {
              designs: Object.keys(DESIGNS).length,
              biasProfiles: Object.keys(BIAS_PROFILE).length,
              biasNames: BIAS_NAMES.length
            };
        """)
        assert counts == {'designs': 6, 'biasProfiles': 6, 'biasNames': 5}

    def test_risk_of_bias_modal_open_and_close(self, driver):
        _load_page(driver)
        _load_example(driver, 'statins')
        _run_analysis(driver)
        driver.execute_script('openRoBModal()')
        time.sleep(0.2)
        assert _visible(driver, 'robModalOverlay')
        driver.execute_script('closeRoBModal()')
        time.sleep(0.2)
        assert not _visible(driver, 'robModalOverlay')

    def test_no_severe_js_errors_for_statins_run(self, driver):
        _load_page(driver)
        _clear_browser_logs(driver)
        _load_example(driver, 'statins')
        _run_analysis(driver)
        assert not _console_severe(driver)
