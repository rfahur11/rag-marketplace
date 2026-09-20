import os
import sys
import re
import time

# Enforce root directory in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
from google import genai

from src.database import run_sql_query, query_vector_store

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
FALLBACK_MODELS = [PRIMARY_MODEL, "gemini-2.0-flash", "gemini-1.5-flash"]

def get_genai_client():
    """Mengembalikan client Gemini API yang valid."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        return None
    return genai.Client(api_key=GEMINI_API_KEY)

def safe_generate_content(client, prompt: str, max_retries=2):
    """Memanggil Gemini API dengan retry otomatis & fallback model jika terjadi lonjakan trafik (Error 503)."""
    for model_name in FALLBACK_MODELS:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                err_str = str(e)
                # Jika 503 (Server Busy) atau 429 (Rate Limit), tunggu sejenak lalu retry
                if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                else:
                    break
    raise RuntimeError("Server AI sedang mengalami beban trafik tinggi. Silakan coba kembali dalam beberapa saat.")

# 1. Intent Classifier Router
def classify_intent(query_text: str) -> str:
    """Mengklasifikasikan intent pertanyaan menjadi: METRICS, REVIEWS, atau HYBRID."""
    query_lower = query_text.lower()
    
    # Keyword penanda ulasan/komplain kualitatif (ID & EN)
    review_keywords = [
        "komplain", "ulasan", "review", "kecewa", "rusak", "cacat", "alasan", "masalah", "buruk", "retur kenapa",
        "complaint", "feedback", "broken", "damaged", "defective", "dissatisfied", "why return", "poor quality"
    ]
    # Keyword penanda metrik/angka (ID & EN)
    metric_keywords = [
        "gmv", "penjualan", "omset", "total", "berapa", "jumlah", "biaya", "aov", "margin", "voucher", "pendapatan",
        "sales", "revenue", "how much", "how many", "count", "amount", "return rate", "orders"
    ]
    
    has_review = any(k in query_lower for k in review_keywords)
    has_metric = any(k in query_lower for k in metric_keywords)
    
    if has_review and has_metric:
        return "HYBRID"
    elif has_review:
        return "REVIEWS"
    else:
        return "METRICS"

# 2. Text-to-SQL Generator dengan Metric Layer & Anti-Hallucination
SYSTEM_SQL_PROMPT = """
Anda adalah Senior Data Engineer & Business Analyst yang bertugas mengubah pertanyaan bisnis menjadi query SQL DuckDB yang 100% valid.

SCHEMA DATABASE DUCKDB:
Tabel `orders`:
- order_id (VARCHAR)
- platform (VARCHAR): 'Tokopedia', 'Shopee', 'TikTok Shop', 'Lazada'
- sku_code (VARCHAR): e.g., 'SKU-FSH-001', 'SKU-ELC-001'
- product_name (VARCHAR)
- category (VARCHAR): 'Fashion', 'Elektronik', 'Kecantikan', 'Perlengkapan Rumah', 'Kesehatan'
- order_value (DOUBLE): Harga barang kotor (IDR)
- shipping_fee (DOUBLE)
- seller_voucher (DOUBLE)
- platform_fee (DOUBLE)
- order_status (VARCHAR): 'COMPLETED', 'CANCELLED', 'RETURNED'
- transaction_date (VARCHAR): Format 'YYYY-MM-DD HH:mm:ss' (Bisa di-filter pakai string LIKE '2026-05%' atau STRFTIME/SUBSTR)

ATURAN BISNIS METRIK (HARUS DIIKUTI):
1. Net GMV = SUM(CASE WHEN order_status = 'COMPLETED' THEN order_value ELSE 0 END)
2. Net Revenue = SUM(CASE WHEN order_status = 'COMPLETED' THEN (order_value - seller_voucher - platform_fee) ELSE 0 END)
3. Total Retur Count = COUNT(CASE WHEN order_status = 'RETURNED' THEN 1 END)
4. HANYA KEMBALIKAN QUERY SQL DALAM BLOK CODE ```sql ... ``` TANPA PENJELASAN LAIN.
"""

def generate_text_to_sql(client, query_text: str) -> str:
    """Menggunakan Gemini untuk menghasilkan query SQL berbasis schema & metrik bisnis."""
    prompt = f"{SYSTEM_SQL_PROMPT}\n\nPertanyaan Bisnis: {query_text}\nQuery SQL DuckDB:"
    sql_text = safe_generate_content(client, prompt)
    
    # Ekstrak SQL dari codeblock jika ada
    match = re.search(r"```sql\s*(.*?)\s*```", sql_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return sql_text.replace("```", "").strip()

def execute_sql_with_self_correction(client, query_text: str, max_retries=2):
    """Menjalankan query SQL dengan fitur Self-Correction (Auto-retry jika error SQL)."""
    current_sql = generate_text_to_sql(client, query_text)
    
    for attempt in range(max_retries + 1):
        result = run_sql_query(current_sql)
        if result["success"]:
            return current_sql, result
        
        # Self-correction loop: minta LLM perbaiki SQL yang error
        if attempt < max_retries:
            error_msg = result["error"]
            fix_prompt = f"{SYSTEM_SQL_PROMPT}\n\nQuery SQL Sebelumnya yang ERROR:\n{current_sql}\n\nPesan Error DuckDB:\n{error_msg}\n\nPerbaiki Query SQL DuckDB tersebut:"
            fixed_text = safe_generate_content(client, fix_prompt)
            current_sql = fixed_text.replace("```sql", "").replace("```", "").strip()
            
    return current_sql, result

# 3. Main RAG Pipeline Handler
def process_rag_query(query_text: str, language: str = "id") -> dict:
    """Fungsi utama pengolah RAG yang menggabungkan Intent Router, Text-to-SQL, Vector Search, dan Synthesis."""
    client = get_genai_client()
    if not client:
        err_msg = (
            "⚠️ **Gemini API Key Not Configured!**\nPlease configure your `GEMINI_API_KEY` in Hugging Face Space Secrets or `.env`."
            if language == "en"
            else "⚠️ **API Key Gemini Belum Dikonfigurasi!**\nSilakan isikan `GEMINI_API_KEY` Anda di file `.env` untuk mengaktifkan RAG Assistant."
        )
        return {
            "intent": "ERROR",
            "sql_query": None,
            "sql_data": None,
            "reviews_data": None,
            "answer": err_msg
        }
        
    intent = classify_intent(query_text)
    sql_query = None
    sql_result = None
    reviews_result = None
    
    try:
        # Path 1: Metrik / Angka (Text-to-SQL)
        if intent in ["METRICS", "HYBRID"]:
            sql_query, sql_result = execute_sql_with_self_correction(client, query_text)
            
        # Path 2: Ulasan / Kualitatif (Vector Search)
        if intent in ["REVIEWS", "HYBRID"]:
            reviews_result = query_vector_store(query_text, n_results=4)
            
        # Path 3: Synthesizer (Menyusun Jawaban Eksekutif Akhir)
        if language == "en":
            synthesis_prompt = f"""You are an Executive Assistant & E-Commerce Business Analyst.
Synthesize a professional, accurate, concise, and direct executive answer.

USER QUESTION: {query_text}
INTENT CATEGORY: {intent}

SQL QUERY RESULTS (If Any):
SQL Query Executed: `{sql_query}`
Data Result: {sql_result.get('data') if sql_result and sql_result.get('success') else 'No SQL Data / Not Applicable'}

CUSTOMER REVIEWS / FEEDBACK RESULTS (If Any):
Customer Reviews: {reviews_result if reviews_result else 'No Review Data / Not Applicable'}

RESPONSE GUIDELINES:
1. Provide the response entirely in professional Business English.
2. If SQL data exists, mention metric figures clearly formatted with IDR / Rupiah currency and percentages.
3. If review data exists, summarize customer complaints and feedback clearly.
4. Use executive-level bullet points with clean Markdown formatting.
"""
        else:
            synthesis_prompt = f"""Anda adalah Executive Assistant & Business Analyst ahli e-commerce.
Susun jawaban yang profesional, akurat, ringkas, dan langsung menjawab pertanyaan pengguna.

PERTANYAAN PENGGUNA: {query_text}
INTENT KATEGORI: {intent}

DATA HASIL QUERY SQL (Jika Ada):
SQL Query Executed: `{sql_query}`
Data Result: {sql_result.get('data') if sql_result and sql_result.get('success') else 'Tidak Ada Data SQL / Error'}

DATA HASIL ULASAN PELANGGAN (Jika Ada):
Review Pelanggan: {reviews_result if reviews_result else 'Tidak Ada Data Review'}

PETUNJUK RESPONS:
1. Jika ada data SQL, sebutkan angka-angka metrik dengan format Rupiah/Persentase yang jelas.
2. Jika ada data ulasan, rangkum poin komplain/umpan balik pelanggan.
3. Gunakan poin-poin Markdown agar mudah dibaca oleh eksekutif bisnis.
"""

        answer_text = safe_generate_content(client, synthesis_prompt)
        
        return {
            "intent": intent,
            "sql_query": sql_query,
            "sql_data": sql_result.get("data") if sql_result and sql_result.get("success") else None,
            "reviews_data": reviews_result,
            "answer": answer_text
        }
    except Exception as e:
        return {
            "intent": intent,
            "sql_query": sql_query,
            "sql_data": None,
            "reviews_data": reviews_result,
            "answer": f"⚠️ **Server Google AI Sedang Sibuk (Lonjakan Trafik):**\n*{str(e)}*\n\nSilakan coba klik tombol kirim kembali dalam beberapa detik."
        }

if __name__ == "__main__":
    # Smoke test intent classifier
    test_q = "Berapa total GMV Tokopedia dan kenapa banyak komplain?"
    print(f"[TEST] Intent Classification for '{test_q}': {classify_intent(test_q)}")
