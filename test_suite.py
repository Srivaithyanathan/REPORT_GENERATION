"""
AluSense AI — Automated Quality Assurance & Demo Validation Suite
Executes all 8 QA test requirements with timing benchmarks, edge-case analysis, and report validation.
Windows-safe encoding version.
"""

import sys
import time
import urllib.request
import traceback

def run_qa_suite():
    results = {}
    timings = {}
    
    print("=" * 70)
    print("ALUSENSE AI -- SENIOR QA & PRODUCT VALIDATION SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # TEST 1: APPLICATION STARTUP & MODULE IMPORT TEST
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Application Startup & Module Imports...")
    t0 = time.perf_counter()
    try:
        import dataset.standards as ds
        import analysis.engine as ae
        import utils.report_generator as rg
        import app
        timings["module_import_ms"] = (time.perf_counter() - t0) * 1000.0
        results["Startup & Imports"] = ("PASS", f"All modules loaded successfully in {timings['module_import_ms']:.1f} ms")
        print(f"  [PASS] Module imports verified ({timings['module_import_ms']:.1f} ms)")
    except Exception as e:
        results["Startup & Imports"] = ("FAIL", f"Import Error: {e}")
        print(f"  [FAIL] Module import failed: {e}")
        traceback.print_exc()

    # -------------------------------------------------------------
    # TEST 2: BACKEND FUNCTION TESTING (SCENARIOS A, B, C, D)
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Backend Functional Scenarios...")
    
    # Scenario A: Optimal Manufacturing
    t0 = time.perf_counter()
    res_a = ae.analyze_manufacturing_process(
        alloy_key="AlSi10Mg",
        process_name="Laser Powder Bed Fusion (LPBF)",
        temperature=200.0,
        energy_density=62.0,
        scan_speed=1300.0,
        oxygen_concentration=45.0
    )
    timings["analysis_engine_ms"] = (time.perf_counter() - t0) * 1000.0
    
    base_ox_risk = res_a.defect_risks["oxidation"].probability
    base_lof_risk = res_a.defect_risks["lack_of_fusion"].probability
    base_kh_risk = res_a.defect_risks["keyholing"].probability

    check_a = (
        res_a.quality_score >= 90.0 and
        res_a.compliance_status == "FULL COMPLIANCE (IN-SPEC)" and
        all(r.probability < 25.0 for r in res_a.defect_risks.values())
    )
    if check_a:
        results["Scenario A: Optimal"] = ("PASS", f"Score: {res_a.quality_score}%, Status: {res_a.compliance_status}, Peak Risk: {res_a.peak_risk.name} ({res_a.peak_risk.probability:.1f}%)")
        print(f"  [PASS] Scenario A (Optimal): Quality Score = {res_a.quality_score}%, Status = {res_a.compliance_status}")
    else:
        results["Scenario A: Optimal"] = ("FAIL", f"Unexpected score {res_a.quality_score}% or status {res_a.compliance_status}")
        print(f"  [FAIL] Scenario A failed")

    # Scenario B: High Oxygen Condition (> 120 ppm)
    # Verify: Oxidation risk increases, warning recommendation appears
    res_b = ae.analyze_manufacturing_process(
        alloy_key="AlSi10Mg",
        process_name="Laser Powder Bed Fusion (LPBF)",
        temperature=200.0,
        energy_density=62.0,
        scan_speed=1300.0,
        oxygen_concentration=250.0  # High O2
    )
    ox_increased = res_b.defect_risks["oxidation"].probability > base_ox_risk * 5
    has_o2_warning = any(
        "oxygen" in rec["detail"].lower() or "o2" in rec["action"].lower() or "atmosphere" in rec["category"].lower()
        for rec in res_b.recommendations
    )
    check_b = ox_increased and has_o2_warning
    if check_b:
        results["Scenario B: High O2"] = ("PASS", f"Oxidation Risk increased from {base_ox_risk:.1f}% to {res_b.defect_risks['oxidation'].probability:.1f}%; corrective warning active")
        print(f"  [PASS] Scenario B (High O2): Oxidation Risk increased to {res_b.defect_risks['oxidation'].probability:.1f}%, Warning directive generated")
    else:
        results["Scenario B: High O2"] = ("FAIL", f"Oxidation Risk: {res_b.defect_risks['oxidation'].probability:.1f}%")
        print(f"  [FAIL] Scenario B failed")

    # Scenario C: Low Energy Density (< 48 J/mm³)
    # Verify: Lack of Fusion risk increases
    res_c = ae.analyze_manufacturing_process(
        alloy_key="AlSi10Mg",
        process_name="Laser Powder Bed Fusion (LPBF)",
        temperature=200.0,
        energy_density=38.0,  # Low VED
        scan_speed=1500.0,
        oxygen_concentration=45.0
    )
    lof_increased = res_c.defect_risks["lack_of_fusion"].probability > base_lof_risk * 5
    check_c = lof_increased and res_c.peak_risk.name.startswith("Lack of Fusion")
    if check_c:
        results["Scenario C: Low VED"] = ("PASS", f"Lack of Fusion Risk increased from {base_lof_risk:.1f}% to {res_c.defect_risks['lack_of_fusion'].probability:.1f}% (Dominant Risk)")
        print(f"  [PASS] Scenario C (Low VED): Lack of Fusion Risk increased to {res_c.defect_risks['lack_of_fusion'].probability:.1f}% (Dominant)")
    else:
        results["Scenario C: Low VED"] = ("FAIL", f"LoF Risk: {res_c.defect_risks['lack_of_fusion'].probability:.1f}%")
        print(f"  [FAIL] Scenario C failed")

    # Scenario D: High Energy Density (> 75 J/mm³)
    # Verify: Keyholing risk increases
    res_d = ae.analyze_manufacturing_process(
        alloy_key="AlSi10Mg",
        process_name="Laser Powder Bed Fusion (LPBF)",
        temperature=200.0,
        energy_density=88.0,  # High VED
        scan_speed=800.0,
        oxygen_concentration=45.0
    )
    kh_increased = res_d.defect_risks["keyholing"].probability > base_kh_risk * 5
    check_d = kh_increased and res_d.peak_risk.name.startswith("Keyholing")
    if check_d:
        results["Scenario D: High VED"] = ("PASS", f"Keyholing Risk increased from {base_kh_risk:.1f}% to {res_d.defect_risks['keyholing'].probability:.1f}% (Dominant Risk)")
        print(f"  [PASS] Scenario D (High VED): Keyholing Risk increased to {res_d.defect_risks['keyholing'].probability:.1f}% (Dominant)")
    else:
        results["Scenario D: High VED"] = ("FAIL", f"Keyholing Risk: {res_d.defect_risks['keyholing'].probability:.1f}%")
        print(f"  [FAIL] Scenario D failed")

    # -------------------------------------------------------------
    # TEST 3: DATABASE VALIDATION
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing Database & Standards Connectivity...")
    db_pass = True
    db_notes = []
    
    # Check all alloys
    for alloy_key in ds.ALLOY_STANDARDS:
        info = ds.get_alloy_details(alloy_key)
        if not info.get("name") or not info.get("nominal_mechanical"):
            db_pass = False
            db_notes.append(f"Missing info for alloy {alloy_key}")

    # Check all processes
    for proc_name in ds.MANUFACTURING_PROCESSES:
        lim = ds.get_process_limits(proc_name)
        req_keys = ["temperature", "energy_density", "scan_speed", "oxygen_concentration"]
        if not all(k in lim for k in req_keys):
            db_pass = False
            db_notes.append(f"Missing limit keys in process {proc_name}")

    # Check all presets
    presets = ds.get_presets()
    if len(presets) < 4:
        db_pass = False
        db_notes.append(f"Fewer than 4 presets: {len(presets)}")

    if db_pass:
        results["Database Validation"] = ("PASS", f"{len(ds.ALLOY_STANDARDS)} alloys, {len(ds.MANUFACTURING_PROCESSES)} processes, {len(presets)} presets verified")
        print(f"  [PASS] Database verified: {len(ds.ALLOY_STANDARDS)} alloys, {len(ds.MANUFACTURING_PROCESSES)} processes, {len(presets)} presets")
    else:
        results["Database Validation"] = ("FAIL", "; ".join(db_notes))
        print(f"  [FAIL] Database check failed: {db_notes}")

    # -------------------------------------------------------------
    # TEST 4: REPORT GENERATION TEST
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing Report Generation Module...")
    t0 = time.perf_counter()
    md_out = rg.generate_markdown_report(res_a, batch_id="AL-DEMO-01", operator_id="OP-QA-CHIEF")
    html_out = rg.generate_html_report(res_a, batch_id="AL-DEMO-01", operator_id="OP-QA-CHIEF")
    timings["report_generation_ms"] = (time.perf_counter() - t0) * 1000.0

    req_report_fields = [
        res_a.alloy_info["name"],
        res_a.process_name,
        f"{res_a.quality_score:.1f}%",
        "Keyholing",
        "Lack of Fusion",
        "Atmospheric Oxidation",
        "Residual Stress"
    ]
    
    md_valid = all(f in md_out for f in req_report_fields)
    html_valid = all(f in html_out for f in req_report_fields) and "<html" in html_out and "</html>" in html_out

    if md_valid and html_valid:
        results["Report Generation"] = ("PASS", f"Markdown ({len(md_out)} chars) & HTML ({len(html_out)} chars) generated in {timings['report_generation_ms']:.1f} ms")
        print(f"  [PASS] Report generation verified ({timings['report_generation_ms']:.1f} ms)")
    else:
        results["Report Generation"] = ("FAIL", "Missing required fields in generated reports")
        print("  [FAIL] Report generation failed")

    # -------------------------------------------------------------
    # TEST 5: ERROR HANDLING & EDGE BOUNDARY TESTING
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing Error Handling & Boundary Stress...")
    boundary_pass = True
    boundary_notes = []

    test_boundaries = [
        {"temperature": -100.0, "energy_density": 0.0, "scan_speed": 10.0, "oxygen_concentration": 0.0},
        {"temperature": 1500.0, "energy_density": 500.0, "scan_speed": 20000.0, "oxygen_concentration": 5000.0},
        {"temperature": 0.0, "energy_density": -10.0, "scan_speed": 0.0, "oxygen_concentration": -5.0},
    ]

    for i, b_input in enumerate(test_boundaries):
        try:
            res_edge = ae.analyze_manufacturing_process(
                alloy_key="AlSi10Mg",
                process_name="Laser Powder Bed Fusion (LPBF)",
                **b_input
            )
            if not (0.0 <= res_edge.quality_score <= 100.0):
                boundary_pass = False
                boundary_notes.append(f"Boundary {i}: Score {res_edge.quality_score} out of bounds")
            for rk, rv in res_edge.defect_risks.items():
                if not (0.0 <= rv.probability <= 100.0):
                    boundary_pass = False
                    boundary_notes.append(f"Boundary {i}: Risk {rk} {rv.probability} out of bounds")
        except Exception as e:
            boundary_pass = False
            boundary_notes.append(f"Boundary {i} threw unhandled exception: {e}")

    try:
        opt_zero = ae.calculate_ved_from_optics(power_w=0.0, speed_mms=0.0, layer_um=0.0, hatch_spacing_mm=0.0)
        if opt_zero != 0.0:
            boundary_pass = False
            boundary_notes.append(f"Optics zero check failed: {opt_zero}")
    except Exception as e:
        boundary_pass = False
        boundary_notes.append(f"calculate_ved_from_optics exception: {e}")

    if boundary_pass:
        results["Error Handling"] = ("PASS", "All extreme edge-cases & zero-divisions handled safely")
        print("  [PASS] Error handling verified: Safe limits enforced, zero division handled")
    else:
        results["Error Handling"] = ("FAIL", "; ".join(boundary_notes))
        print(f"  [FAIL] Error handling failed: {boundary_notes}")

    # -------------------------------------------------------------
    # TEST 6: LIVE HTTP SERVER & RESPONSE TESTING
    # -------------------------------------------------------------
    print("\n[TEST 6] Testing Live Streamlit Server Connection...")
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request("http://localhost:8501/", headers={"User-Agent": "AluSense-QA-Bot"})
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.status
            html_body = response.read().decode('utf-8')
            timings["http_ping_ms"] = (time.perf_counter() - t0) * 1000.0
            
            if status_code == 200 and len(html_body) > 1000:
                results["Live HTTP Server"] = ("PASS", f"HTTP 200 OK, {len(html_body)} bytes served in {timings['http_ping_ms']:.1f} ms")
                print(f"  [PASS] Live HTTP Server verified: HTTP {status_code} ({timings['http_ping_ms']:.1f} ms)")
            else:
                results["Live HTTP Server"] = ("FAIL", f"HTTP status {status_code}, response size {len(html_body)}")
                print(f"  [FAIL] HTTP status {status_code}")
    except Exception as e:
        results["Live HTTP Server"] = ("FAIL", f"Connection error: {e}")
        print(f"  [FAIL] Server connection error: {e}")

    # -------------------------------------------------------------
    # TEST 7: DEMO USER JOURNEY SIMULATION
    # -------------------------------------------------------------
    print("\n[TEST 7] Simulating Complete User Journey...")
    journey_steps = []
    try:
        journey_steps.append("Step 1: Selected material AlSi10Mg")
        alloy_j = ds.get_alloy_details("AlSi10Mg")
        
        journey_steps.append("Step 2: Selected process Laser Powder Bed Fusion (LPBF)")
        limits_j = ds.get_process_limits("Laser Powder Bed Fusion (LPBF)")
        
        params_j = {
            "temperature": 200.0,
            "energy_density": 62.5,
            "scan_speed": 1300.0,
            "oxygen_concentration": 45.0,
            "laser_power": 370.0,
            "layer_thickness": 30.0
        }
        journey_steps.append(f"Step 3: Entered parameters {params_j}")
        
        t0 = time.perf_counter()
        res_j = ae.analyze_manufacturing_process("AlSi10Mg", "Laser Powder Bed Fusion (LPBF)", **params_j)
        timings["journey_analysis_ms"] = (time.perf_counter() - t0) * 1000.0
        journey_steps.append(f"Step 4: Ran analysis ({timings['journey_analysis_ms']:.2f} ms)")
        
        score_j = res_j.quality_score
        journey_steps.append(f"Step 5: Evaluated Quality Score: {score_j:.1f}%")
        
        peak_j = res_j.peak_risk
        journey_steps.append(f"Step 6: Evaluated Defect Risks (Peak: {peak_j.name} at {peak_j.probability:.1f}%)")
        
        t0 = time.perf_counter()
        md_j = rg.generate_markdown_report(res_j)
        html_j = rg.generate_html_report(res_j)
        timings["journey_report_ms"] = (time.perf_counter() - t0) * 1000.0
        journey_steps.append(f"Step 7: Generated Inspection Reports ({timings['journey_report_ms']:.2f} ms)")
        
        results["Demo User Journey"] = ("PASS", "All 7 steps completed flawlessly")
        print("  [PASS] Full user journey simulation PASSED")
    except Exception as e:
        results["Demo User Journey"] = ("FAIL", f"Failed at step: {journey_steps[-1] if journey_steps else 'start'}: {e}")
        print(f"  [FAIL] User journey simulation failed: {e}")

    # -------------------------------------------------------------
    # PRINT SUMMARY TABLE
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("FINAL QA VALIDATION SUMMARY TABLE")
    print("=" * 70)
    print(f"{'Component / Test':<28} | {'Status':<8} | {'Notes'}")
    print("-" * 70)
    all_passed = True
    for comp, (status, note) in results.items():
        if status != "PASS":
            all_passed = False
        print(f"{comp:<28} | {status:<8} | {note}")
    print("=" * 70)
    print(f"OVERALL VALIDATION STATUS: {'READY FOR BUSINESS DEMO (100% PASS)' if all_passed else 'ACTION REQUIRED'}\n")

    return all_passed, results, timings

if __name__ == "__main__":
    success, _, _ = run_qa_suite()
    sys.exit(0 if success else 1)
