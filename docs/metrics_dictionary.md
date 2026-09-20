# 📊 Business Metrics Dictionary - Marketplace Intelligence

Dokumen ini mendefinisikan rumus bisnis resmi yang digunakan oleh **Text-to-SQL Engine** untuk mencegah LLM mengarang logika perhitungan finansial.

---

## 1. Metrics Definition Matrix

| Nama Metrik | Formula SQL | Deskripsi Bisnis |
| :--- | :--- | :--- |
| **Gross Sales (GMV Kotor)** | `SUM(order_value)` | Total nilai transaksi kotor sebelum dikurangi retur/pembatalan. |
| **Net GMV (GMV Bersih)** | `SUM(CASE WHEN order_status = 'COMPLETED' THEN order_value ELSE 0 END)` | Total nilai transaksi bersih yang berhasil diselesaikan pelanggan. |
| **Net Revenue (Pendapatan Bersih)** | `SUM(CASE WHEN order_status = 'COMPLETED' THEN (order_value - seller_voucher - platform_fee) ELSE 0 END)` | Pendapatan bersih seller setelah dikurangi diskon seller & biaya admin platform. |
| **Return Rate (%)** | `(COUNT(CASE WHEN order_status = 'RETURNED' THEN 1 END) * 100.0) / COUNT(*)` | Persentase pesanan yang dikembalikan/retur oleh pembeli. |
| **Average Order Value (AOV)** | `AVG(CASE WHEN order_status = 'COMPLETED' THEN order_value END)` | Rata-rata nilai belanja per transaksi completed. |

---

## 2. Business Rules & Edge Cases
1. **Penyaringan Status Transaksi**:
   - `COMPLETED`: Transaksi selesai & diterima pembeli (Dihitung dalam Net GMV).
   - `CANCELLED`: Transaksi dibatalkan sebelum dikirim (Diabaikan dari Net GMV).
   - `RETURNED`: Transaksi dikembalikan karena komplain/cacat (Diabaikan dari Net GMV, dihitung dalam Return Rate).
2. **Standardisasi Platform**:
   - Platform valid: `Tokopedia`, `Shopee`, `TikTok Shop`, `Lazada`.
