"""CausalSynth Phase 3 Selenium Tests"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-gpu')
opts.add_argument('--window-size=1400,900')
opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(options=opts)
driver.set_page_load_timeout(15)
passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}" + (f" -- {detail}" if detail else ""))
    else:
        failed += 1
        print(f"  [FAIL] {name}" + (f" -- {detail}" if detail else ""))

try:
    driver.get("http://localhost:8766/causal-synth.html")
    time.sleep(1)

    # Check for JS errors on load (ignore favicon 404)
    logs = driver.get_log("browser")
    errors = [l for l in logs if l["level"] == "SEVERE" and "favicon" not in l["message"]]
    check("No JS errors on load", len(errors) == 0,
          "; ".join(e["message"] for e in errors) if errors else "clean")

    # Check basic elements exist
    for eid, label in [
        ("dagCard", "DAG card"),
        ("dagTemplate", "DAG template dropdown"),
        ("dagSvg", "DAG SVG canvas"),
        ("exampleDropdown", "Example dataset dropdown"),
        ("reportCard", "Report card"),
        ("rCodeCard", "R code card"),
        ("rCodeBlock", "R code block"),
        ("reportText", "Report text area"),
    ]:
        el = driver.find_elements(By.ID, eid)
        check(f"Element exists: {label}", len(el) > 0)

    # Test 1: Load Statins example
    print("\nTEST 1: Load Statins dataset")
    driver.execute_script('loadExample("statins")')
    time.sleep(0.5)
    count = driver.execute_script("return studies.length")
    check("Statins: 12 studies loaded", count == 12, f"got {count}")

    # Test 2: Load Med Diet example
    print("\nTEST 2: Load Med Diet dataset")
    driver.execute_script('loadExample("meddiet")')
    time.sleep(0.5)
    count = driver.execute_script("return studies.length")
    check("MedDiet: 7 studies loaded", count == 7, f"got {count}")

    # Test 3: Load Smoking example (4 designs)
    print("\nTEST 3: Load Smoking dataset")
    driver.execute_script('loadExample("smoking")')
    time.sleep(0.5)
    count = driver.execute_script("return studies.length")
    designs = driver.execute_script("return [...new Set(studies.map(s=>s.design))]")
    check("Smoking: 8 studies loaded", count == 8, f"got {count}")
    check("Smoking: 4 designs", len(designs) == 4, f"got {designs}")

    # Test 4: Run triangulation on Statins
    print("\nTEST 4: Run triangulation on Statins")
    driver.execute_script('loadExample("statins")')
    time.sleep(0.3)
    driver.execute_script("runTriangulation()")
    time.sleep(0.5)
    results_visible = driver.execute_script(
        'return document.getElementById("results").style.display !== "none"'
    )
    check("Results section visible", results_visible)
    ces = driver.execute_script("return triResults.CES")
    dci = driver.execute_script("return triResults.DCI")
    mcs = driver.execute_script("return triResults.MCS")
    bds = driver.execute_script("return triResults.BDS")
    theta = driver.execute_script("return triResults.overallResult.theta")
    check("CES computed", ces > 0 and ces <= 1, f"CES={ces:.3f}")
    check("DCI=100% (all agree)", dci == 1.0, f"DCI={dci}")
    check("MCS computed", mcs > 0, f"MCS={mcs:.3f}")
    check("BDS computed", bds > 0, f"BDS={bds:.3f}")
    check("Pooled effect negative", theta < 0, f"theta={theta:.4f}")

    # Test 5: GRADE certainty mapping
    print("\nTEST 5: GRADE certainty")
    grade = driver.execute_script(
        "return getGRADECertainty(triResults.CES, triResults.DCI, triResults.BDS, triResults.designResults)"
    )
    check("GRADE level assigned", grade["level"] in ["HIGH","MODERATE","LOW","VERY LOW"], grade["level"])
    check("GRADE symbol assigned", len(grade["symbol"]) >= 1, grade["symbol"])
    badge_text = driver.execute_script(
        'return document.querySelector(".grade-badge")?.textContent'
    )
    check("GRADE badge in convergence metrics", badge_text is not None and len(badge_text) > 0, badge_text)
    # BDS for statins is 0.333 (< 0.5), so upgrade should NOT trigger
    # Upgrade requires DCI=1 AND BDS>0.5
    check("No upgrade (BDS=0.333 < 0.5)", grade["upgraded"] == False, f"BDS={bds:.3f}, reasons={grade['reasons']}")

    # Test 6: Report text
    print("\nTEST 6: Report text generation")
    report = driver.execute_script(
        'return document.getElementById("reportText").textContent'
    )
    check("Report not empty", len(report) > 100, f"{len(report)} chars")
    check("Report has METHODS", "METHODS" in report)
    check("Report has RESULTS", "RESULTS" in report)
    check("Report mentions DerSimonian-Laird", "DerSimonian-Laird" in report)
    check("Report mentions 3 designs", "3 designs" in report)
    check("Report mentions CES", "Causal Evidence Score" in report)
    check("Report mentions GRADE level", grade["level"] in report)

    # Test 7: R code
    print("\nTEST 7: R code generation")
    rcode = driver.execute_script(
        'return document.getElementById("rCodeBlock").textContent'
    )
    check("R code not empty", len(rcode) > 100, f"{len(rcode)} chars")
    check("R code has library(metafor)", "library(metafor)" in rcode)
    check("R code has rma()", "rma(" in rcode)
    check("R code has data.frame", "dat <- data.frame" in rcode)
    check("R code has per-design MA", "res_rct" in rcode.lower() or "res_RCT" in rcode)
    check("R code has DCI calculation", "DCI" in rcode)

    # Test 8: DAG templates
    print("\nTEST 8: DAG templates")
    for tpl, min_nodes, min_edges in [
        ("confounding", 3, 3),
        ("mediation", 3, 3),
        ("iv", 4, 4),
        ("collider", 3, 2),
    ]:
        driver.execute_script(f'loadDAGTemplate("{tpl}")')
        time.sleep(0.2)
        svg = driver.execute_script('return document.getElementById("dagSvg").innerHTML')
        circles = svg.count("<circle")
        lines = svg.count("<line")
        check(f"DAG {tpl}: nodes>={min_nodes}", circles >= min_nodes, f"{circles} nodes")
        check(f"DAG {tpl}: edges>={min_edges}", lines >= min_edges, f"{lines} edges")

    # Test 9: DAG overlays
    print("\nTEST 9: DAG overlays with loaded data")
    driver.execute_script('loadDAGTemplate("confounding")')
    driver.execute_script('loadExample("statins")')
    time.sleep(0.3)
    legend = driver.execute_script(
        'return document.getElementById("dagOverlayLegend").innerHTML'
    )
    check("DAG overlay legend populated", len(legend) > 10)
    svg = driver.execute_script('return document.getElementById("dagSvg").innerHTML')
    has_green = "var(--success)" in svg
    check("DAG has green (blocked) paths for RCT", has_green)

    # Test 10: Smoking dataset (4 designs)
    print("\nTEST 10: Smoking dataset triangulation")
    driver.execute_script('loadExample("smoking")')
    time.sleep(0.3)
    driver.execute_script("runTriangulation()")
    time.sleep(0.5)
    nDesigns = driver.execute_script("return triResults.nDesigns")
    check("4 designs detected", nDesigns == 4, f"got {nDesigns}")
    grade2 = driver.execute_script(
        "return getGRADECertainty(triResults.CES, triResults.DCI, triResults.BDS, triResults.designResults)"
    )
    check("Smoking: GRADE assigned", grade2["level"] in ["HIGH","MODERATE","LOW","VERY LOW"], grade2["level"])
    report2 = driver.execute_script(
        'return document.getElementById("reportText").textContent'
    )
    check("Report mentions 4 designs", "4 designs" in report2)
    # Smoking has ecological design
    check("Report mentions Ecological", "Ecological" in report2)

    # Test 11: Med Diet dataset
    print("\nTEST 11: Med Diet dataset triangulation")
    driver.execute_script('loadExample("meddiet")')
    time.sleep(0.3)
    driver.execute_script("runTriangulation()")
    time.sleep(0.5)
    nDesigns = driver.execute_script("return triResults.nDesigns")
    check("3 designs detected", nDesigns == 3, f"got {nDesigns}")
    pooled = driver.execute_script("return triResults.overallResult.theta")
    check("Med diet pooled effect negative", pooled < 0, f"theta={pooled:.4f}")

    # Test 12: Dark mode
    print("\nTEST 12: Dark mode")
    driver.execute_script("toggleTheme()")
    is_dark = driver.execute_script('return document.body.classList.contains("dark")')
    check("Dark mode activated", is_dark)
    badge_vis = driver.execute_script(
        'return document.querySelector(".grade-badge")?.offsetHeight > 0'
    )
    check("GRADE badge visible in dark mode", badge_vis)
    driver.execute_script("toggleTheme()")

    # Test 13: GRADE downgrade test
    print("\nTEST 13: GRADE downgrade (opposite direction)")
    # Manually test with fabricated data where one design opposes
    dg_result = driver.execute_script("""
        var fakeDesigns = {
            RCT: {theta: -0.3, se: 0.05, lower: -0.4, upper: -0.2, k: 3, I2: 10, tau2: 0.01},
            cohort: {theta: 0.1, se: 0.08, lower: -0.06, upper: 0.26, k: 2, I2: 0, tau2: 0}
        };
        return getGRADECertainty(0.5, 0.5, 0.6, fakeDesigns);
    """)
    check("Downgrade when opposite direction present", dg_result["downgraded"] == True, str(dg_result["reasons"]))

    # Test 14: Export R Code button exists
    print("\nTEST 14: Export R Code button")
    btns = driver.find_elements(By.XPATH, "//button[contains(text(),'Export R Code')]")
    check("Export R Code button exists", len(btns) > 0)

    # Test 15: Clear DAG
    print("\nTEST 15: Clear DAG")
    driver.execute_script('loadDAGTemplate("confounding")')
    time.sleep(0.2)
    driver.execute_script("clearDAG()")
    time.sleep(0.2)
    svg = driver.execute_script('return document.getElementById("dagSvg").innerHTML')
    check("DAG cleared (no circles)", "<circle" not in svg)
    tpl_val = driver.execute_script('return document.getElementById("dagTemplate").value')
    check("Template dropdown reset", tpl_val == "")

    # Final JS error check
    logs = driver.get_log("browser")
    errors = [l for l in logs if l["level"] == "SEVERE"]
    check("\nNo JS errors throughout tests", len(errors) == 0,
          "; ".join(e["message"] for e in errors) if errors else "clean")

    print("\n" + "=" * 55)
    print(f"  RESULTS: {passed} passed, {failed} failed")
    print("=" * 55)

except Exception as ex:
    print(f"\nFATAL: {ex}")
    import traceback
    traceback.print_exc()
    try:
        logs = driver.get_log("browser")
        for l in logs:
            if l["level"] == "SEVERE":
                print(f"JS ERROR: {l['message']}")
    except:
        pass
finally:
    driver.quit()

sys.exit(1 if failed > 0 else 0)
