# 📱 Social Media & Portfolio Showcase Pack
## Marketplace Intelligence System (Hybrid RAG)

Dokumen ini berisi seluruh materi promosi profesional siap pakai untuk mempublikasikan proyek **Marketplace Intelligence System** ke LinkedIn, Twitter/X, resume/CV, dan portofolio web.

---

## 📑 1. LinkedIn Document Carousel (7 Slides PDF Plan)

Format Carousel dokumen PDF memiliki tingkat impresi dan *engagement* tertinggi di LinkedIn untuk konten rekayasa perangkat lunak (*software engineering*).

---

### **Slide 1: Cover Hook**
* **Visual:** Background gradien gelap elegan (Dark Slate `#0f172a` dengan aksen Blue/Cyan). Logo e-commerce (Tokopedia, Shopee, TikTok Shop, Lazada) dengan tanda silang merah pada grafik yang meleset.
* **Headline:** *"Kenapa Chatbot AI Biasa Pasti Gagal Mengelola Data Penjualan E-Commerce?"*
* **Sub-headline:** *Mengapa RAG biasa berhalusinasi saat menghitung GMV, dan bagaimana memecahkannya dengan arsitektur Hybrid RAG deterministik.*
* **Footer:** *Swipe for architecture deep-dive ➡️*

---

### **Slide 2: The Real Problem (The Trap of Vanilla RAG)**
* **Visual:** Ilustrasi perbandingan: Prompt ke LLM *"Berapa Net GMV Tokopedia bulan ini?"* $\rightarrow$ LLM mengira-ngira angka secara acak.
* **Poin Kunci:**
  * ❌ **Data Multi-Channel Berantakan:** Kolom status pesanan Shopee, Tokopedia, dan TikTok berbeda format.
  * ❌ **Halusinasi Angka:** Vector Database (Cosine Similarity) dirancang untuk mencari kemiripan makna teks, **bukan menjumlahkan angka finansial**.
  * 💥 **Risiko:** Keputusan bisnis salah fatal jika berbasis angka AI yang berhalusinasi.

---

### **Slide 3: The Solution (Hybrid Architecture)**
* **Visual:** Diagram arsitektur 2 jalur (*Two-Pronged Architecture*):
  * **Jalur Kiri (Biru):** DuckDB In-Memory OLAP $\rightarrow$ 100% Deterministik.
  * **Jalur Kanan (Ungu):** ChromaDB Vector Store $\rightarrow$ Semantic Review Retrieval.
  * **Di Tengah:** Router Agent cerdas yang memilah pertanyaan pengguna.
* **Tagline:** *"Jangan paksa Vector DB menghitung angka, dan jangan paksa SQL menganalisis emosi pembeli."*

---

### **Slide 4: The Live Experience (Gradio 6.x Dashboard)**
* **Visual:** Screenshot antarmuka dashboard:
  * 4 Kartu KPI: Net GMV, Transaksi Selesai, Retur, Return Rate.
  * Breakdown performa per platform (Shopee, Tokopedia, TikTok Shop, Lazada).
  * Chatbot interaktif dengan audit trail query SQL.
* **Fitur Unggulan:**
  * 🌐 **Bilingual Toggle (ID / EN):** Beradaptasi seketika untuk audiens lokal dan global.
  * 🔍 **Audit Trail:** Transparansi penuh—eksekutif bisa melihat query SQL asli yang dieksekusi DuckDB.

---

### **Slide 5: Engineering Depth & Under The Hood**
* **Visual:** Cuplikan kode estetik (*syntax-highlighted code block*) yang memperlihatkan *Self-Correction Loop*:
* **Penjelasan:**
  * 🔄 **Autonomous Self-Correction:** Jika LLM typo menghasilkan fungsi SQL yang tidak didukung, sistem menangkap *exception* DuckDB dan memerintahkan AI memperbaiki query-nya secara otomatis dalam hitungan milidetik.
  * 🛡️ **Model Cascade:** Fallback otomatis dari `Gemini 3.6 Flash` ke `2.0 Flash` dan `1.5 Flash` saat server mengalami beban trafik (Error 503 / 429).

---

### **Slide 6: Proven Impact & Reliability Metrics**
* **Visual:** Infografis kartu metrik hasil evaluasi sistem:
  * 🎯 **0% Finansial Hallucination:** Metrik dihitung langsung oleh DuckDB OLAP Engine.
  * ⚡ **100% Test Pass Rate:** 4/4 automated tests passing di `evaluate.py`.
  * ☁️ **Cloud Native & ZeroGPU Ready:** Live deploy di Hugging Face Spaces dengan auto-healing ingestion.

---

### **Slide 7: Conclusion & Call To Action (CTA)**
* **Visual:** Foto profil profesional Anda + Link QR Code ke Live Demo & GitHub.
* **Teks:**
  * *"Ingin mencoba langsung live demo atau menginspeksi kodenya?"*
  * 🚀 **Live Demo:** [huggingface.co/spaces/rfahrur6045/rag-marketplace-intelligence](https://huggingface.co/spaces/rfahrur6045/rag-marketplace-intelligence)
  * 💻 **GitHub Repo:** [github.com/rfahur11/rag-marketplace](https://github.com/rfahur11/rag-marketplace)
  * *Mari berdiskusi di kolom komentar: Bagaimana arsitektur RAG tim Anda saat ini menangani data numerik tabular?*

---

## 🎬 2. Video Demo Singkat (25 Detik Screen Recording Script)

*Rasio Rekomendasi:* 16:9 untuk LinkedIn / Desktop atau 9:16 untuk Instagram Reels / YouTube Shorts.

| Detik | Visual Layar (Screen Action) | On-Screen Text Overlay | Voiceover (Bahasa Indonesia / English) |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:05** | Layar Dashboard terbuka. Sorot 4 kartu KPI Net GMV dan tabel perbandingan Tokopedia vs Shopee. | *Stop asking LLMs to do math! 🛑* | *"Banyak chatbot AI gagal saat ditanya angka penjualan karena vector database tidak bisa menghitung agregasi finansial."* |
| **00:05 - 00:13** | Buka tab Chatbot. Ketik pertanyaan: *"Berapa total Net GMV Tokopedia dan kenapa banyak ulasan retur?"* lalu klik **Kirim 🚀**. | *Hybrid RAG: Text-to-SQL + Vector Search ⚡* | *"Di sini saya membangun Hybrid RAG: pertanyaan angka otomatis diarahkan ke DuckDB OLAP..."* |
| **00:13 - 00:19** | Jawaban muncul secara rapi dalam bullet points. Buka accordion **Audit Trail SQL Inspector** untuk memperlihatkan query SQL DuckDB yang dieksekusi. | *100% Deterministic & Anti-Hallucination 🔍* | *"...sementara akar masalah komplain dicari via ChromaDB Vector Search. Angka 100% akurat tanpa halusinasi."* |
| **00:19 - 00:25** | Klik tombol ganti bahasa ke **EN (English)**. Seluruh dashboard dan kartu berubah ke Bahasa Inggris. | *Bilingual (ID/EN) • Live on Hugging Face 🌐* | *"Lengkap dengan switch bahasa dinamis dan sudah live di Hugging Face Spaces. Cek link di deskripsi!"* |

---

## ✍️ 3. Draf Copywriting Media Sosial

### Versi LinkedIn (Formula PAS + High-Impact Narrative)

```markdown
Berapa kali Anda melihat AI Chatbot dengan percaya diri mengarang angka penjualan saat ditanya metrik bisnis? 🤦‍♂️

Masalah fundamental dari "Vanilla RAG" (Vector Database biasa) adalah:
Vector embeddings dirancang untuk mencari kemiripan teks, BUKAN untuk menghitung agregasi matematika seperti SUM, COUNT, atau Margin.

Ketika seorang eksekutif bertanya:
"Berapa Net GMV Tokopedia kuartal ini dan mengapa terjadi lonjakan retur?"
RAG biasa pasti berhalusinasi atau memberikan angka yang salah.

Untuk memecahkan masalah ini, saya merancang:
🛒 Marketplace Intelligence System (Hybrid RAG for Multi-Channel E-Commerce)

Solusinya bukan memilih antara SQL atau Vector, melainkan menggabungkan keduanya:

1. ⚡ Deterministik Path (Text-to-SQL + DuckDB OLAP):
Setiap pertanyaan kuantitatif otomatis diubah menjadi query SQL DuckDB yang mematuhi kamus metrik akuntansi e-commerce. Dilengkapi autonomous self-correction loop jika terjadi syntax error.

2. 🔍 Kualitatif Path (ChromaDB Vector Store):
Secara paralel, keluhan pembeli dari ribuan ulasan dianalisis menggunakan semantic search untuk menemukan akar masalah (misal: barang cacat, salah ukuran, pengiriman lambat).

3. 🌐 Dynamic Bilingual (ID & EN):
Antarmuka eksekutif (Gradio 6.x) dan sintesis LLM mendukung pergantian bahasa instan antara Bahasa Indonesia dan English.

4. 🛡️ Production Resilience:
Dilengkapi model fallback cascade (Gemini 3.6 -> 2.0 -> 1.5 Flash) dan container cold-start auto-healing untuk cloud deployment.

Hasil evaluasi:
✅ 0% Halusinasi Finansial
✅ 100% Automated Test Suite Passing
✅ Siap dicoba langsung di browser tanpa instalasi!

🔗 Live Demo (Hugging Face Spaces):
https://huggingface.co/spaces/rfahrur6045/rag-marketplace-intelligence

💻 GitHub Repository & Source Code:
https://github.com/rfahur11/rag-marketplace

Bagaimana pendekatan tim Anda saat ini dalam menghubungkan LLM dengan structured analytical database? Mari berdiskusi di kolom komentar! 👇

#ArtificialIntelligence #MachineLearning #RAG #DuckDB #Python #DataEngineering #GenerativeAI #Portfolio
```

---

### Versi Twitter / X Thread (Ringkas & Punchy)

```markdown
1/5 Jangan pernah biarkan LLM menghitung angka finansial bisnis Anda sendirian. 🛑

RAG berbasis Vector Database biasa PASTI berhalusinasi saat disuruh hitung Net GMV atau Return Rate e-commerce.

Inilah cara saya mengatasinya dengan Hybrid RAG: 🧵👇

2/5 I built "Marketplace Intelligence System":
AI Assistant multi-channel (Shopee, Tokopedia, TikTok Shop, Lazada) dengan arsitektur 2 jalur:
🔹 Angka/Metrik -> DuckDB OLAP (Text-to-SQL + Self-Correction)
🔹 Ulasan/Komplain -> ChromaDB Vector Store

3/5 Fitur kunci:
• Zero-hallucination metric calculations
• Audit Trail SQL Inspector (transparan 100%)
• Bilingual toggle dinamis: ID (Bahasa) & EN (English)
• Resilient Gemini Model Cascade (3.6 -> 2.0 -> 1.5 Flash)

4/5 Seluruh automated test suite (4/4) passing 100%.
Kombinasi OLAP in-process + Vector Retrieval membuktikan bahwa AI enterprise harus deterministik untuk angka dan semantik untuk teks.

5/5 🚀 Coba langsung Live Demo (Free on Hugging Face Spaces):
https://huggingface.co/spaces/rfahrur6045/rag-marketplace-intelligence

💻 Kode lengkap & arsitektur di GitHub:
https://github.com/rfahur11/rag-marketplace
```

---

## 🎯 4. Cheat Sheet Wawancara Kerja (CAR / STAR Framework)

Gunakan poin-poin ini saat interviewer menanyakan tentang proyek ini:

* **Context (Situasi):**
  *"Di e-commerce multi-channel, eksekutif kesulitan menggabungkan analisis angka penjualan (kuantitatif) dengan alasan keluhan pelanggan (kualitatif). Solusi chatbot biasa yang menggunakan Vanilla RAG selalu berhalusinasi saat menghitung angka agregasi."*

* **Action (Tindakan):**
  *"Saya merancang sistem Hybrid RAG modular. Saya memisahkan jalur analitik menggunakan DuckDB in-process OLAP dengan Semantic Metric Layer untuk Text-to-SQL anti-halusinasi, serta jalur kualitatif menggunakan ChromaDB untuk ulasan pelanggan. Saya juga mengimplementasikan autonomous self-correction pada SQL generator, cascade model fallback untuk mencegah error 503, dan dynamic bilingual switch (ID/EN) di UI Gradio 6.x."*

* **Result (Hasil):**
  *"Sistem berhasil mencapai 0% halusinasi finansial karena perhitungan dilakukan secara deterministik oleh engine database, lulus 100% pada automated test evaluation suite, dan telah ter-deploy live di Hugging Face Spaces dengan zero-cost cloud architecture."*
