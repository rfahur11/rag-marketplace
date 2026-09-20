import os
import sys

# Ensure root directory in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import run_sql_query, query_vector_store
from src.rag_engine import classify_intent

def run_evaluation_suite():
    """Menjalankan pengujian otomatis untuk mengukur keandalan sistem RAG & Data Engine."""
    print("==================================================")
    print("[EVALUATION] MEMULAI RAG & DATA ENGINE EVALUATION SUITE")
    print("==================================================\n")
    
    passed_tests = 0
    total_tests = 0
    
    # 1. Test Ingestion & DuckDB Connection
    total_tests += 1
    res = run_sql_query("SELECT COUNT(*) AS total FROM orders")
    if res["success"] and res["data"][0]["total"] > 0:
        print("[PASSED] Test 1: DuckDB Connection & Table Integrity OK")
        passed_tests += 1
    else:
        print("[FAILED] Test 1: DuckDB Table Integrity Failed")
        
    # 2. Test Net GMV Business Rule
    total_tests += 1
    res_gmv = run_sql_query("SELECT SUM(CASE WHEN order_status = 'COMPLETED' THEN order_value ELSE 0 END) AS net_gmv FROM orders")
    if res_gmv["success"] and res_gmv["data"][0]["net_gmv"] > 0:
        print("[PASSED] Test 2: Business Rule Metrics (Net GMV Calculation) OK")
        passed_tests += 1
    else:
        print("[FAILED] Test 2: Net GMV Calculation Failed")
        
    # 3. Test Vector Store Indexing & Retrieval
    total_tests += 1
    reviews = query_vector_store("barang rusak komplain", n_results=2)
    if len(reviews) > 0:
        print("[PASSED] Test 3: ChromaDB Vector Store Retrieval OK")
        passed_tests += 1
    else:
        print("[FAILED] Test 3: ChromaDB Vector Store Retrieval Failed")
        
    # 4. Test Intent Router Accuracy
    total_tests += 1
    intent1 = classify_intent("Berapa total GMV?")
    intent2 = classify_intent("Apa komplain pembeli?")
    intent3 = classify_intent("Berapa penjualan Tokopedia dan apa komplainnya?")
    
    if intent1 == "METRICS" and intent2 == "REVIEWS" and intent3 == "HYBRID":
        print("[PASSED] Test 4: Intent Classifier Router Accuracy 100%")
        passed_tests += 1
    else:
        print(f"[FAILED] Test 4: Intent Router Mismatch: {intent1}, {intent2}, {intent3}")
        
    print("\n==================================================")
    print(f"[SUMMARY] HASIL EVALUASI: {passed_tests}/{total_tests} TEST PASSED ({(passed_tests/total_tests)*100:.0f}%)")
    print("==================================================\n")

if __name__ == "__main__":
    run_evaluation_suite()
