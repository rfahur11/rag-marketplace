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

# Auto-initialize database & vector index if running on clean environment (e.g., Hugging Face Spaces)
if not os.path.exists(DUCKDB_PATH):
    print("[INIT] Database DuckDB tidak ditemukan. Menjalankan data pipeline & vector indexing...")
    fetch_and_clean_data()
    init_and_index_vector_store()

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

def load_platform_breakdown():
    """Mengambil performa per marketplace platform."""
    duck_query = """
    SELECT 
        platform AS "Marketplace",
        COUNT(*) AS "Total Transaksi",
        SUM(CASE WHEN order_status = 'COMPLETED' THEN 1 ELSE 0 END) AS "Selesai",
        SUM(CASE WHEN order_status = 'RETURNED' THEN 1 ELSE 0 END) AS "Retur",
        CAST(SUM(CASE WHEN order_status = 'COMPLETED' THEN order_value ELSE 0 END) AS BIGINT) AS "Net GMV (IDR)"
    FROM orders
    GROUP BY platform
    ORDER BY "Net GMV (IDR)" DESC;
    """
    res = run_sql_query(duck_query)
    if res["success"]:
        df = pd.DataFrame(res["data"])
        return df
    return pd.DataFrame()

def handle_chat_query(user_message, history):
    """Handler interaksi chatbot RAG (Gradio 6.x messages format)."""
    if not user_message.strip():
        return "", history, "Tidak ada query SQL yang dieksekusi."
    
    rag_result = process_rag_query(user_message)
    answer = rag_result["answer"]
    sql_used = rag_result["sql_query"] if rag_result["sql_query"] else "Query ini menggunakan Vector Search / Kualitatif (Tanpa SQL)."
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": answer})
    return "", history, sql_used

# Tampilan Gradio Interface (Clean theme setup)
with gr.Blocks(title="Marketplace Intelligence System RAG") as demo:
    gr.Markdown("""
    # 🛒 Marketplace Intelligence System (Hybrid RAG)
    ### Executive Dashboard & Anti-Hallucination AI Assistant untuk E-Commerce
    """)
    
    with gr.Tabs():
        # TAB 1: EXECUTIVE DASHBOARD
        with gr.TabItem("📊 Executive Performance Dashboard"):
            gr.Markdown("### 📈 Ringkasan Metrik Performa Multi-Channel")
            
            with gr.Row():
                kpi_gmv = gr.Textbox(label="Net GMV (Bersih)", interactive=False)
                kpi_completed = gr.Textbox(label="Transaksi Selesai", interactive=False)
                kpi_returned = gr.Textbox(label="Transaksi Retur", interactive=False)
                kpi_ret_rate = gr.Textbox(label="Return Rate (%)", interactive=False)
                
            btn_refresh = gr.Button("🔄 Refresh Data Metrik", variant="secondary")
            
            gr.Markdown("### 🛍️ Breakdown Performa per Marketplace")
            table_platform = gr.Dataframe(interactive=False)
            
            # Event handler dashboard
            def update_dashboard():
                gmv, comp, ret, rate = load_dashboard_kpis()
                df_plat = load_platform_breakdown()
                return gmv, comp, ret, rate, df_plat
                
            demo.load(update_dashboard, outputs=[kpi_gmv, kpi_completed, kpi_returned, kpi_ret_rate, table_platform])
            btn_refresh.click(update_dashboard, outputs=[kpi_gmv, kpi_completed, kpi_returned, kpi_ret_rate, table_platform])

        # TAB 2: AI ASSISTANT CHATBOT
        with gr.TabItem("🤖 AI Assistant (Text-to-SQL + Vector RAG)"):
            gr.Markdown("### 💬 Tanya Jawab Performa & Komplain Pelanggan")
            gr.Markdown("Gunakan Bahasa Indonesia alami untuk menanyakan metrik penjualan atau ulasan produk.")
            
            chatbot = gr.Chatbot(label="Executive AI Assistant", height=400)
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Contoh: Berapa total Net GMV Tokopedia dan kenapa banyak komplain?", 
                    label="Pertanyaan Anda",
                    scale=4
                )
                btn_send = gr.Button("Kirim 🚀", variant="primary", scale=1)
                
            with gr.Accordion("🔍 Audit Trail (Lihat Query SQL DuckDB yang Dieksekusi AI)", open=False):
                sql_inspector = gr.Code(label="Executed SQL Query", language="sql", interactive=False)
                
            # Sample quick questions
            gr.Examples(
                examples=[
                    "Berapa total Net GMV Tokopedia dibanding Shopee?",
                    "Apa komplain terbanyak pembeli untuk produk Headset Bluetooth?",
                    "Berapa jumlah transaksi retur di TikTok Shop?",
                    "Mengapa produk Kemeja Flanel banyak diajukan retur?"
                ],
                inputs=msg_input,
                label="💡 Contoh Pertanyaan Cepat:"
            )
            
            # Chat event handlers
            btn_send.click(
                handle_chat_query, 
                inputs=[msg_input, chatbot], 
                outputs=[msg_input, chatbot, sql_inspector]
            )
            msg_input.submit(
                handle_chat_query, 
                inputs=[msg_input, chatbot], 
                outputs=[msg_input, chatbot, sql_inspector]
            )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False)
