# DisasterWatch Pipeline Orchestrator: runs experiments 1 to 8 sequentially.
import subprocess, sys, time

EXPERIMENTS = [
    ("Exp 1: Static Scraping", "exp1_static.py"),
    ("Exp 2: Selectors Comparison", "exp2_selectors.py"),
    ("Exp 3: Dynamic Scraping (Selenium)", "exp3_dynamic.py"),
    ("Exp 4: Multi-page Scraping & Logging", "exp4_multipage.py"),
    ("Exp 5: JSON & XML APIs (USGS + GDACS)", "exp5_api_json_xml.py"),
    ("Exp 6: API Auth, Params & Pagination", "exp6_api_auth.py"),
    ("Exp 7: Clean, Validate & Store Master", "exp7_clean.py"),
    ("Exp 8: Mini Case Study & Timeline", "exp8_case_study.py"),
]

def run_pipeline():
    print("=" * 78)
    print("DISASTERWATCH: Executing End-to-End Pipeline (Experiments 1 to 8)")
    print("=" * 78)
    
    results = []
    for name, script in EXPERIMENTS:
        print(f"\n>> [RUNNING] {name} ({script})...")
        t0 = time.time()
        res = subprocess.run([sys.executable, script])
        elapsed = round(time.time() - t0, 2)
        if res.returncode == 0: status = "SUCCESS"
        elif res.returncode == 2: status = "BLOCKED (Key)"
        else: status = "FAILED"
        results.append((name, script, status, f"{elapsed}s"))
        print(f">> [{status}] {name} in {elapsed}s")
        
    print("\n" + "=" * 78)
    print("DISASTERWATCH PIPELINE EXECUTION SUMMARY")
    print("=" * 78)
    print(f"{'Experiment':<40} {'Script':<22} {'Status':<16} {'Time'}")
    print("-" * 78)
    for name, script, status, elapsed in results:
        print(f"{name:<40} {script:<22} {status:<16} {elapsed}")
    print("=" * 78)
    
if __name__ == "__main__":
    run_pipeline()
