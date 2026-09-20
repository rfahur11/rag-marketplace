# 🏗️ System Architecture & Data Flow

## System Overview Diagram

```mermaid
flowchart TD
    User([User / Decision Maker]) --> UI[Gradio Interface app.py]
    UI --> Router[Intent Router src/rag_engine.py]
    
    subgraph Analytics Path [Determinisik / Angka]
        Router -->|Tabular / Metrics Query| Text2SQL[Text-to-SQL Engine]
        Text2SQL -->|Exec SQL| DuckDB[(DuckDB OLAP Engine)]
        DuckDB -->|Raw SQL Results| Synthesizer[LLM Synthesizer]
    end
    
    subgraph Qualitative Path [Kualitatif / Sentiment]
        Router -->|Ulasan / Komplain Query| VectorSearch[ChromaDB Hybrid Search]
        VectorSearch -->|Relevant Reviews| Synthesizer
    end
    
    Synthesizer --> UI
```

## Architectural Rationale
1. **Mengapa DuckDB?** DuckDB adalah OLAP in-process database yang memproses jutaan baris data agregasi (SUM, AVG, GROUP BY) dalam hitungan milidetik secara lokal tanpa overhead server DB.
2. **Mengapa Text-to-SQL + Metrics Layer?** RAG berbasis vector embedding biasa **pasti halusinasi** saat ditanya total nilai penjualan. Text-to-SQL memastikan perhitungan matematika 100% tepat.
3. **Mengapa ChromaDB?** Ringan, file-based, gratis, dan mendukung vector similarity search untuk ulasan pelanggan secara lokal.
