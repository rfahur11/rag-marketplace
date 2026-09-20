import os
import random
import datetime
import duckdb

# Path konfigurasi
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DUCKDB_PATH = os.path.join(DATA_DIR, "marketplace.duckdb")
RAW_CSV_PATH = os.path.join(DATA_DIR, "raw_marketplace.csv")

def ensure_data_dir():
    """Memastikan folder data tersedia."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def generate_mock_marketplace_data(num_rows=2500):
    """Menghasilkan dataset simulasi e-commerce multi-channel (Tokopedia, Shopee, TikTok Shop, Lazada)
    dengan variasi status (COMPLETED, CANCELLED, RETURNED) dan ulasan pelanggan."""
    
    platforms = ["Shopee", "Tokopedia", "TikTok Shop", "Lazada"]
    statuses = ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "RETURNED", "CANCELLED"]
    
    sku_list = [
        ("SKU-FSH-001", "Kaos Polos Cotton Combed 30s", "Fashion"),
        ("SKU-FSH-002", "Kemeja Flanel Kotak Lengan Panjang", "Fashion"),
        ("SKU-ELC-001", "Headset Bluetooth Wireless TWS", "Elektronik"),
        ("SKU-ELC-002", "Powerbank Fast Charging 10000mAh", "Elektronik"),
        ("SKU-KCT-001", "Serum Wajah Brightening Vitamin C", "Kecantikan"),
        ("SKU-KCT-002", "Sunscreen Gel SPF 50 PA++++", "Kecantikan"),
        ("SKU-PRM-001", "Wajan Anti Lengket Granite 24cm", "Perlengkapan Rumah"),
        ("SKU-KSH-001", "Minyak Angin Aromatheraphy 10ml", "Kesehatan")
    ]
    
    positive_reviews = [
        "Produk bagus banget, pengiriman cepat dan packing rapi!",
        "Kualitas ok sesuai harga, barang berfungsi dengan baik.",
        "Sangat puas belanja di toko ini, seller ramah dan responsif.",
        "Barang original 100%, mantap recommended seller!"
    ]
    
    negative_reviews = [
        "Ukuran baju terlalu kecil dan jahitan tidak rapi, kecewa.",
        "Barang mati total saat diterima, respon garansi lambat!",
        "Pengiriman lama sekali, kemasan penyok dan barang agak lecet.",
        "Bahan tipis tidak sesuai deskripsi produk, ajukan retur."
    ]

    start_date = datetime.date(2026, 1, 1)
    
    rows = []
    for i in range(1, num_rows + 1):
        order_id = f"ORD-{20260000 + i}"
        sku_info = random.choice(sku_list)
        sku_code, product_name, category = sku_info
        platform = random.choice(platforms)
        status = random.choice(statuses)
        
        # Tanggal transaksi
        random_days = random.randint(0, 250)
        trx_date = start_date + datetime.timedelta(days=random_days)
        trx_str = trx_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Nilai transaksi & biaya
        order_value = random.randint(35000, 750000)
        shipping_fee = random.randint(10000, 35000)
        seller_voucher = random.choice([0, 5000, 10000, 15000, 25000])
        platform_fee = int(order_value * 0.04) # 4% admin fee
        
        # Review
        if status == "COMPLETED":
            review_score = random.choice([4, 5, 5, 5, 3])
            review_text = random.choice(positive_reviews) if review_score >= 4 else "Biasa saja, pengiriman agak lama."
        elif status == "RETURNED":
            review_score = random.choice([1, 2])
            review_text = random.choice(negative_reviews)
        else:
            review_score = None
            review_text = None
            
        rows.append((
            order_id, platform, sku_code, product_name, category,
            order_value, shipping_fee, seller_voucher, platform_fee,
            status, trx_str, review_score, review_text
        ))

    # Tulis CSV
    import csv
    with open(RAW_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "order_id", "platform", "sku_code", "product_name", "category",
            "order_value", "shipping_fee", "seller_voucher", "platform_fee",
            "order_status", "transaction_date", "review_score", "review_text"
        ])
        writer.writerows(rows)
        
    print(f"[INFO] Generated {num_rows} raw marketplace transactions to: {RAW_CSV_PATH}")

def fetch_and_clean_data():
    """Menggunakan DuckDB Engine untuk memproses raw dataset & membuat tabel SQL bersih."""
    ensure_data_dir()
    
    # Generate data jika raw CSV belum ada
    if not os.path.exists(RAW_CSV_PATH):
        generate_mock_marketplace_data()
        
    print("[INFO] Memproses dataset marketplace via DuckDB Engine...")
    conn = duckdb.connect(DUCKDB_PATH)
    
    # Fix path untuk SQL string DuckDB
    csv_path_sql = RAW_CSV_PATH.replace("\\", "/")
    
    try:
        # 1. Tabel Utama Orders (Transaksi & Finansial)
        conn.execute(f"""
        CREATE OR REPLACE TABLE orders AS
        SELECT 
            order_id,
            platform,
            sku_code,
            product_name,
            category,
            CAST(order_value AS DOUBLE) AS order_value,
            CAST(shipping_fee AS DOUBLE) AS shipping_fee,
            CAST(seller_voucher AS DOUBLE) AS seller_voucher,
            CAST(platform_fee AS DOUBLE) AS platform_fee,
            order_status,
            CAST(transaction_date AS VARCHAR) AS transaction_date
        FROM read_csv_auto('{csv_path_sql}');
        """)
        
        # 2. Tabel Reviews (Data Ulasan Pelanggan untuk Vector Search)
        conn.execute(f"""
        CREATE OR REPLACE TABLE reviews AS
        SELECT 
            order_id,
            sku_code,
            product_name,
            CAST(review_score AS INTEGER) AS review_score,
            review_text
        FROM read_csv_auto('{csv_path_sql}')
        WHERE review_text IS NOT NULL AND TRIM(review_text) != '';
        """)
        
        orders_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        reviews_count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        
        print("\n==========================================")
        print("[SUCCESS] PIPELINE DATASET MARKETPLACE BERHASIL!")
        print(f"   Total Transaksi Dimuat: {orders_count:,} baris")
        print(f"   Total Review Dimuat   : {reviews_count:,} baris")
        print(f"   Database DuckDB       : {DUCKDB_PATH}")
        print("==========================================\n")
        
    except Exception as e:
        print(f"[ERROR] Gagal memproses pipeline data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_and_clean_data()
