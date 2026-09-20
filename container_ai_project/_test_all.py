r"""
Comprehensive test script -- validates every module in the project.
Run from: d:\Mersa_pfe
  .\mersa_pfe\Scripts\python.exe container_ai_project\_test_all.py
"""
import sys, os, traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "model"))
sys.path.insert(0, os.path.join(ROOT, "llm"))

PASS = "\033[92m  PASS\033[0m"
FAIL = "\033[91m  FAIL\033[0m"
results = []

def run(label, fn):
    try:
        fn()
        print(f"{PASS}  {label}")
        results.append((label, True))
    except Exception as e:
        print(f"{FAIL}  {label}")
        traceback.print_exc()
        results.append((label, False))

# == Test 1: config =============================================================
def test_config():
    from config import DATABASE_URL, YOLO_MODEL_PATH, LLM_BACKEND, UPLOAD_FOLDER
    assert "marsa_maroc" in DATABASE_URL, f"Bad DB URL: {DATABASE_URL}"
    print(f"       DB={DATABASE_URL}")
    print(f"       YOLO={YOLO_MODEL_PATH}")
    print(f"       LLM={LLM_BACKEND}")
run("config.py", test_config)

# == Test 2: db_manager ========================================================
def test_db_manager():
    from services.db_manager import init_db, get_stats, get_all_containers, save_container
    init_db()
    stats = get_stats()
    containers = get_all_containers()
    print(f"       stats={stats}")
    print(f"       containers_count={len(containers)}")
run("db_manager.py - init + query", test_db_manager)

# == Test 3: db insert =========================================================
def test_db_insert():
    from services.db_manager import save_container, get_stats
    before = get_stats()["total"]
    r = save_container({
        "container_id": "MSCU1234567",
        "confidence_score": 0.92,
        "ship_name": "MSC_Test",
        "dock_name": "Quai1",
        "sts_operator": "Ahmed",
        "status": "detecte",
        "ocr_text": "MSCU1234567",
        "ocr_confidence": 0.88,
        "processing_time": 1.1,
    })
    after = get_stats()["total"]
    assert after == before + 1, f"Expected {before+1}, got {after}"
    print(f"       inserted id={r.id}, total now={after}")
run("db_manager.py - insert", test_db_insert)

# == Test 4: LLM report ========================================================
def test_llm():
    from llm_report import generate_summary
    s = generate_summary({
        "total_containers": 5, "unloaded": 4, "ocr_errors": 1,
        "dock_name": "Quai 1", "sts_operator": "Ahmed", "ship_name": "Ship1",
        "anomalies": [], "avg_processing_time": 1.2, "ocr_success_rate": 80.0,
    })
    assert len(s) > 20, "Summary too short"
    print(f"       summary preview: {s[:80]} ...")
run("llm_report.py - template backend", test_llm)

# == Test 5: PDF generation ====================================================
def test_pdf():
    from services.report_gen import generate_pdf
    data = {
        "ship_name": "MSC Test", "dock_name": "Quai 1",
        "sts_operator": "Ahmed",
        "total": 3, "unloaded": 2, "ocr_errors": 1,
        "ocr_success_rate": 66.7, "avg_confidence": 88.0,
        "avg_processing_time": 1.5,
        "containers": [
            {"container_id": "MSCU1234567", "confidence_score": 0.92,
             "status": "detecte", "date_detection": "2024-01-15 09:30"},
            {"container_id": None, "confidence_score": 0.45,
             "status": "erreur OCR", "date_detection": "2024-01-15 09:31"},
        ],
    }
    pdf_bytes = generate_pdf(data, llm_summary="Test summary.")
    assert len(pdf_bytes) > 1000, "PDF too small"
    print(f"       PDF size={len(pdf_bytes)} bytes")
run("report_gen.py - PDF output", test_pdf)

# == Test 6: Flask app import ==================================================
def test_flask():
    from services.db_manager import init_db
    init_db()
    from app import create_app
    app = create_app()
    assert app is not None
    with app.test_client() as c:
        r = c.get("/health")
        assert r.status_code == 200
        j = r.get_json()
        assert j["status"] == "ok"
        print(f"       /health => {j}")
        r2 = c.get("/stats")
        assert r2.status_code == 200
        print(f"       /stats  => {r2.get_json()}")
        r3 = c.get("/containers")
        assert r3.status_code == 200
        print(f"       /containers => {r3.get_json()['count']} items")
run("app.py - Flask routes", test_flask)

# == Test 7: OCR reader import =================================================
def test_ocr_import():
    from services.ocr_reader import OCRReader, CONTAINER_ID_PATTERN
    # Test regex only (no GPU/model load)
    ids = ["MSCU1234567", "CMAU9876543", "TGHU4567890", "NOTANID"]
    for text in ids:
        m = CONTAINER_ID_PATTERN.search(text)
        print(f"       OCR regex '{text}' => {m.group(0) if m else 'no match'}")
    assert CONTAINER_ID_PATTERN.search("MSCU1234567") is not None
run("ocr_reader.py - regex pattern", test_ocr_import)

# == Summary ===================================================================
print("\n" + "="*50)
passed = sum(1 for _, ok in results if ok)
failed = sum(1 for _, ok in results if not ok)
print(f"  Results: {passed} passed, {failed} failed out of {len(results)}")
if failed:
    print("\n  FAILED tests:")
    for label, ok in results:
        if not ok:
            print(f"    [FAIL] {label}")
    sys.exit(1)
else:
    print("  ALL TESTS PASSED")
