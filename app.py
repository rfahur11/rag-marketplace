import os
import sys
import pandas as pd
import gradio as gr

# Ensure root directory in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import run_sql_query, init_and_index_vector_store, DUCKDB_PATH
from src.data_pipeline import fetch_and_clean_data
from src.rag_engine import process_rag_query

# ZeroGPU compatibility for Hugging Face Spaces free tier
try:
    import spaces  # type: ignore
    @spaces.GPU(duration=1)  # type: ignore
    def dummy_gpu():
        return None
except (ImportError, ModuleNotFoundError):
    def dummy_gpu():
        return None

# Auto-initialize database & vector index if running on clean environment (e.g., Hugging Face Spaces)
if not os.path.exists(DUCKDB_PATH):
    print("[INIT] Database DuckDB tidak ditemukan. Menjalankan data pipeline & vector indexing...")
    fetch_and_clean_data()
    init_and_index_vector_store()

# Internationalization (i18n) Translations Dictionary
TRANSLATIONS = {
    "id": {
        "header_title": "# 🛒 Marketplace Intelligence System (Hybrid RAG)",
        "header_subtitle": "### Executive Dashboard & Anti-Hallucination AI Assistant untuk E-Commerce",
        "tab_dashboard": "📊 Executive Performance Dashboard",
        "tab_chat": "🤖 AI Assistant (Text-to-SQL + Vector RAG)",
        "kpi_section_title": "### 📈 Ringkasan Metrik Performa Multi-Channel",
        "kpi_gmv": "Net GMV (Bersih)",
        "kpi_completed": "Transaksi Selesai",
        "kpi_returned": "Transaksi Retur",
        "kpi_ret_rate": "Return Rate (%)",
        "btn_refresh": "🔄 Refresh Data Metrik",
        "table_section_title": "### 🛍️ Breakdown Performa per Marketplace",
        "chat_section_title": "### 💬 Tanya Jawab Performa & Komplain Pelanggan",
        "chat_subtitle": "Gunakan Bahasa Indonesia atau Inggris alami untuk menanyakan metrik penjualan atau ulasan produk.",
        "chatbot_label": "Executive AI Assistant",
        "msg_input_label": "Pertanyaan Anda",
        "msg_input_placeholder": "Contoh: Berapa total Net GMV Tokopedia dan kenapa banyak komplain?",
        "btn_send": "Kirim 🚀",
        "audit_label": "🔍 Audit Trail (Lihat Query SQL DuckDB yang Dieksekusi AI)",
        "sql_code_label": "Executed SQL Query",
        "no_sql_executed": "Tidak ada query SQL yang dieksekusi.",
        "vector_only": "Query ini menggunakan Vector Search / Kualitatif (Tanpa SQL).",
        "table_cols": ["Marketplace", "Total Transaksi", "Selesai", "Retur", "Net GMV (IDR)"],
        "examples_label": "💡 Contoh Pertanyaan Cepat:"
    },
    "en": {
        "header_title": "# 🛒 Marketplace Intelligence System (Hybrid RAG)",
        "header_subtitle": "### Executive Dashboard & Anti-Hallucination AI Assistant for E-Commerce",
        "tab_dashboard": "📊 Executive Performance Dashboard",
        "tab_chat": "🤖 AI Assistant (Text-to-SQL + Vector RAG)",
        "kpi_section_title": "### 📈 Multi-Channel Performance Metrics Summary",
        "kpi_gmv": "Net GMV (Clean)",
        "kpi_completed": "Completed Orders",
        "kpi_returned": "Returned Orders",
        "kpi_ret_rate": "Return Rate (%)",
        "btn_refresh": "🔄 Refresh Metrics",
        "table_section_title": "### 🛍️ Performance Breakdown by Marketplace",
        "chat_section_title": "### 💬 Q&A: Performance Metrics & Customer Complaints",
        "chat_subtitle": "Ask questions in natural English or Indonesian to analyze sales metrics or customer reviews.",
        "chatbot_label": "Executive AI Assistant",
        "msg_input_label": "Your Question",
        "msg_input_placeholder": "Example: What is the total Net GMV of Tokopedia and why are there complaints?",
        "btn_send": "Send 🚀",
        "audit_label": "🔍 Audit Trail (Inspect DuckDB SQL Query Executed by AI)",
        "sql_code_label": "Executed SQL Query",
        "no_sql_executed": "No SQL query was executed.",
        "vector_only": "This query used Vector Search / Qualitative Analysis (No SQL).",
        "table_cols": ["Marketplace", "Total Orders", "Completed", "Returned", "Net GMV (IDR)"],
        "examples_label": "💡 Quick Example Questions:"
    }
}

def load_dashboard_kpis():
    """Mengambil data KPI utama untuk ditampilkan di Dashboard Executive."""
    gmv_query = """
    SELECT 
        SUM(CASE WHEN order_status = 'COMPLETED' THEN order_value ELSE 0 END) AS net_gmv,
        COUNT(CASE WHEN order_status = 'COMPLETED' THEN 1 END) AS total_completed_orders,
        COUNT(CASE WHEN order_status = 'RETURNED' THEN 1 END) AS total_returned_orders,
        ROUND((COUNT(CASE WHEN order_status = 'RETURNED' THEN 1 END) * 100.0) / COUNT(*), 2) AS return_rate
    FROM orders;
    """
    res = run_sql_query(gmv_query)
    if res["success"] and res["data"]:
        row = res["data"][0]
        net_gmv = f"Rp {row['net_gmv']:,.0f}".replace(",", ".")
        completed = f"{row['total_completed_orders']:,}"
        returned = f"{row['total_returned_orders']:,}"
        ret_rate = f"{row['return_rate']}%"
        return net_gmv, completed, returned, ret_rate
    return "Rp 0", "0", "0", "0%"

def load_platform_breakdown(lang_key="id"):
    """Mengambil performa per marketplace platform dengan kolom multibahasa."""
    cols = TRANSLATIONS[lang_key]["table_cols"]
    duck_query = f"""
    SELECT 
        platform AS "{cols[0]}",
        COUNT(*) AS "{cols[1]}",
        SUM(CASE WHEN order_status = 'COMPLETED' THEN 1 ELSE 0 END) AS "{cols[2]}",
        SUM(CASE WHEN order_status = 'RETURNED' THEN 1 ELSE 0 END) AS "{cols[3]}",
        CAST(SUM(CASE WHEN order_status = 'COMPLETED' THEN order_value ELSE 0 END) AS BIGINT) AS "{cols[4]}"
    FROM orders
    GROUP BY platform
    ORDER BY "{cols[4]}" DESC;
    """
    res = run_sql_query(duck_query)
    if res["success"]:
        return pd.DataFrame(res["data"])
    return pd.DataFrame()

def handle_chat_query(user_message, history, lang_choice):
    """Handler interaksi chatbot RAG multibahasa (Gradio 6.x messages format)."""
    lang_key = "en" if "en" in str(lang_choice).lower() else "id"
    t = TRANSLATIONS[lang_key]
    
    if not user_message.strip():
        return "", history, t["no_sql_executed"]
    
    rag_result = process_rag_query(user_message, language=lang_key)
    answer = rag_result["answer"]
    sql_used = rag_result["sql_query"] if rag_result["sql_query"] else t["vector_only"]
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": answer})
    return "", history, sql_used

# Tampilan Gradio Interface (Clean theme setup)
with gr.Blocks(title="Marketplace Intelligence System RAG") as demo:
    # Invisible button to ensure ZeroGPU event scanner registers the function
    _dummy_btn = gr.Button(visible=False)
    _dummy_btn.click(dummy_gpu)
    
    with gr.Row():
        with gr.Column(scale=4):
            header_md = gr.Markdown("""
            # 🛒 Marketplace Intelligence System (Hybrid RAG)
            ### Executive Dashboard & Anti-Hallucination AI Assistant untuk E-Commerce
            """)
        with gr.Column(scale=1):
            lang_selector = gr.Radio(
                choices=["ID (Bahasa)", "EN (English)"],
                value="ID (Bahasa)",
                label="🌐 Language / Bahasa",
                interactive=True
            )
    
    with gr.Tabs():
        # TAB 1: EXECUTIVE DASHBOARD
        with gr.TabItem("📊 Executive Performance Dashboard") as tab_dash:
            kpi_title_md = gr.Markdown("### 📈 Ringkasan Metrik Performa Multi-Channel")
            
            with gr.Row():
                kpi_gmv = gr.Textbox(label="Net GMV (Bersih)", interactive=False)
                kpi_completed = gr.Textbox(label="Transaksi Selesai", interactive=False)
                kpi_returned = gr.Textbox(label="Transaksi Retur", interactive=False)
                kpi_ret_rate = gr.Textbox(label="Return Rate (%)", interactive=False)
                
            btn_refresh = gr.Button("🔄 Refresh Data Metrik", variant="secondary")
            
            table_title_md = gr.Markdown("### 🛍️ Breakdown Performa per Marketplace")
            table_platform = gr.Dataframe(interactive=False)
            
            # Event handler dashboard refresh
            def update_dashboard(lang_choice):
                lang_key = "en" if "en" in str(lang_choice).lower() else "id"
                gmv, comp, ret, rate = load_dashboard_kpis()
                df_plat = load_platform_breakdown(lang_key)
                return gmv, comp, ret, rate, df_plat
                
            demo.load(
                update_dashboard, 
                inputs=[lang_selector], 
                outputs=[kpi_gmv, kpi_completed, kpi_returned, kpi_ret_rate, table_platform]
            )
            btn_refresh.click(
                update_dashboard, 
                inputs=[lang_selector], 
                outputs=[kpi_gmv, kpi_completed, kpi_returned, kpi_ret_rate, table_platform]
            )

        # TAB 2: AI ASSISTANT CHATBOT
        with gr.TabItem("🤖 AI Assistant (Text-to-SQL + Vector RAG)") as tab_chat:
            chat_title_md = gr.Markdown("### 💬 Tanya Jawab Performa & Komplain Pelanggan")
            chat_sub_md = gr.Markdown("Gunakan Bahasa Indonesia atau Inggris alami untuk menanyakan metrik penjualan atau ulasan produk.")
            
            chatbot = gr.Chatbot(label="Executive AI Assistant", height=400)
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Contoh: Berapa total Net GMV Tokopedia dan kenapa banyak komplain?", 
                    label="Pertanyaan Anda",
                    scale=4
                )
                btn_send = gr.Button("Kirim 🚀", variant="primary", scale=1)
                
            with gr.Accordion("🔍 Audit Trail (Lihat Query SQL DuckDB yang Dieksekusi AI)", open=False) as sql_accordion:
                sql_inspector = gr.Code(label="Executed SQL Query", language="sql", interactive=False)
                
            # Sample quick questions in both Indonesian & English
            gr.Examples(
                examples=[
                    "Berapa total Net GMV Tokopedia dibanding Shopee?",
                    "What is the total Net GMV of Tokopedia compared to Shopee?",
                    "Apa komplain terbanyak pembeli untuk produk Headset Bluetooth?",
                    "What are the top customer complaints for Bluetooth Headset?",
                    "Berapa jumlah transaksi retur di TikTok Shop?",
                    "Why are Flannel Shirts being returned?"
                ],
                inputs=msg_input,
                label="💡 Quick Example Questions / Contoh Pertanyaan Cepat:"
            )
            
            # Chat event handlers
            btn_send.click(
                handle_chat_query, 
                inputs=[msg_input, chatbot, lang_selector], 
                outputs=[msg_input, chatbot, sql_inspector]
            )
            msg_input.submit(
                handle_chat_query, 
                inputs=[msg_input, chatbot, lang_selector], 
                outputs=[msg_input, chatbot, sql_inspector]
            )

    # Dynamic language switch event handler
    def switch_language(lang_choice):
        lang_key = "en" if "en" in str(lang_choice).lower() else "id"
        t = TRANSLATIONS[lang_key]
        df_plat = load_platform_breakdown(lang_key)
        
        return (
            f"{t['header_title']}\n{t['header_subtitle']}", # header_md
            t["kpi_section_title"], # kpi_title_md
            gr.update(label=t["kpi_gmv"]), # kpi_gmv
            gr.update(label=t["kpi_completed"]), # kpi_completed
            gr.update(label=t["kpi_returned"]), # kpi_returned
            gr.update(label=t["kpi_ret_rate"]), # kpi_ret_rate
            gr.update(value=t["btn_refresh"]), # btn_refresh
            t["table_section_title"], # table_title_md
            df_plat, # table_platform
            t["chat_section_title"], # chat_title_md
            t["chat_sub_md" if "chat_sub_md" in t else "chat_subtitle"], # chat_sub_md
            gr.update(label=t["chatbot_label"]), # chatbot
            gr.update(label=t["msg_input_label"], placeholder=t["msg_input_placeholder"]), # msg_input
            gr.update(value=t["btn_send"]), # btn_send
            gr.update(label=t["audit_label"]), # sql_accordion
            gr.update(label=t["sql_code_label"]), # sql_inspector
        )

    lang_selector.change(
        switch_language,
        inputs=[lang_selector],
        outputs=[
            header_md,
            kpi_title_md,
            kpi_gmv,
            kpi_completed,
            kpi_returned,
            kpi_ret_rate,
            btn_refresh,
            table_title_md,
            table_platform,
            chat_title_md,
            chat_sub_md,
            chatbot,
            msg_input,
            btn_send,
            sql_accordion,
            sql_inspector
        ]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False)
