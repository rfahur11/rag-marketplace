# 🧭 System State & Living Context: Marketplace RAG Intelligence

> **Terakhir Diperbarui**: 2026-09-20 18:36 WIB  
> **Status Build**: Passing (100% Complete + Git Ready)  
> **Root Workspace**: `d:\porto\rag-marketplace`  

---

## 🏗️ 1. Matriks Arsitektur & Tech Stack
- **Data Engine**: DuckDB Native Engine (`data/marketplace.duckdb`) - 2,500 Transaksi & 2,048 Review
- **Vector Engine**: ChromaDB Persistent Store (`data/chroma_db`) - 2,048 Embedded Customer Reviews
- **LLM Engine**: Google Gemini API (`gemini-2.5-flash`) untuk Text-to-SQL & Synthesis
- **UI Framework**: Gradio 4.x (`app.py`) - Executive Dashboard & Chatbot UI
- **Testing**: Automated Evaluation Suite (`evaluate.py`) - 4/4 Tests Passed (100%)

---

## 🌟 2. Status Fitur & Checklist Proyek
- [x] **Tahap 1: Fondasi Proyek & Dokumentasi Context** (`SYSTEM_STATE.md`, `metrics_dictionary.md`, `requirements.txt`)
- [x] **Tahap 2: Dataset Marketplace & Ingestion Pipeline** (`data/raw_marketplace.csv` & `src/data_pipeline.py`)
- [x] **Tahap 3 & 4: Database Access Layer & Otak RAG** (`src/database.py` & `src/rag_engine.py`)
- [x] **Tahap 5: Antarmuka UI Gradio** (`app.py`)
- [x] **Tahap 6: Evaluasi Akurasi RAG & README Portal** (`evaluate.py` & `README.md`)
- [x] **Git Readiness**: File `.gitignore` terkonfigurasi untuk keamanan API Key & kebersihan repo.

---

## ⚙️ 3. Environment & Secret Management Matrix
| File Konfigurasi | Kebutuhan Secret / Key | Keterangan |
| :--- | :--- | :--- |
| `.env.example` | Template | Disimpan di Git |
| `.env` | `GEMINI_API_KEY` | **Diabaikan Git via `.gitignore`** |
| `.gitignore` | Standard Exclusion | Mengabaikan `.env`, `.venv/`, `*.duckdb`, `chroma_db/` |

---

## ⚠️ 4. Catatan Penting & Best Practices
- **Text-to-SQL Anti-Hallucination**: SQL query didasarkan pada `docs/metrics_dictionary.md`.
- **DuckDB Engine**: Ingestion & cleaning menggunakan DuckDB Native Engine untuk performa maksimal.
- **Windows UTF-8 Console Safety**: Log print disesuaikan agar berjalan tanpa error encoding di sebarang terminal Windows.

---

## 🚀 5. Quick Runbook Pindah Device / Setup Baru
```bash
git clone <url-repo-anda>
cd rag-marketplace
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/data_pipeline.py
.\.venv\Scripts\python.exe evaluate.py
.\.venv\Scripts\python.exe app.py
```
