import os
import duckdb
import chromadb
from chromadb.utils import embedding_functions

# Path Konfigurasi
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DUCKDB_PATH = os.path.join(DATA_DIR, "marketplace.duckdb")
CHROMA_PATH = os.path.join(DATA_DIR, "chroma_db")

def run_sql_query(query: str):
    """Menjalankan query SQL di DuckDB secara aman dan mengembalikan hasil dalam format terstruktur."""
    conn = duckdb.connect(DUCKDB_PATH, read_only=True)
    try:
        df = conn.execute(query).df()
        conn.close()
        return {
            "success": True, 
            "data": df.to_dict(orient="records"), 
            "columns": list(df.columns),
            "row_count": len(df)
        }
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}

def init_and_index_vector_store():
    """Inisialisasi ChromaDB dan mengindeks teks ulasan pelanggan dari DuckDB."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name="marketplace_reviews", 
        embedding_function=default_ef
    )
    
    # Jika collection belum memiliki data, lakukan batch indexing
    if collection.count() == 0:
        print("[INFO] Mengindeks data ulasan pelanggan ke ChromaDB...")
        conn = duckdb.connect(DUCKDB_PATH, read_only=True)
        reviews_df = conn.execute("SELECT order_id, sku_code, product_name, review_score, review_text FROM reviews").df()
        conn.close()
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in reviews_df.iterrows():
            documents.append(str(row["review_text"]))
            metadatas.append({
                "order_id": str(row["order_id"]),
                "sku_code": str(row["sku_code"]),
                "product_name": str(row["product_name"]),
                "review_score": int(row["review_score"]) if row["review_score"] else 0
            })
            ids.append(f"rev_{idx}")
            
        # Indexing batch per 500 dokumen
        batch_size = 500
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )
        print(f"[SUCCESS] Berhasil mengindeks {collection.count()} review ke ChromaDB!")
        
    return collection

def query_vector_store(query_text: str, n_results=5):
    """Mencari ulasan/komplain pelanggan yang paling relevan secara kualitatif berbasis semantic search."""
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_or_create_collection(name="marketplace_reviews", embedding_function=default_ef)
        
        # Jika collection kosong, jalankan init
        if collection.count() == 0:
            collection = init_and_index_vector_store()
            
        results = collection.query(query_texts=[query_text], n_results=n_results)
        
        formatted_reviews = []
        if results and "documents" in results and results["documents"]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                formatted_reviews.append({
                    "review": doc,
                    "score": meta.get("review_score"),
                    "product": meta.get("product_name"),
                    "sku": meta.get("sku_code")
                })
        return formatted_reviews
    except Exception as e:
        print(f"[ERROR] ChromaDB query error: {e}")
        return []

if __name__ == "__main__":
    # Test sederhana
    print("[TEST] Memeriksa koneksi DuckDB & ChromaDB...")
    res = run_sql_query("SELECT COUNT(*) AS total_orders FROM orders")
    print(f"DuckDB Test: {res}")
    init_and_index_vector_store()
    reviews = query_vector_store("barang rusak pengiriman lambat", n_results=2)
    print(f"Vector Store Test: {reviews}")
