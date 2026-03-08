# HargaTaniCerdas — Sistem Prediksi Harga Bahan Pokok 🌾📈

HargaTaniCerdas adalah sebuah platform berbasis web cerdas yang mengintegrasikan Data Science dan Web Development untuk memonitoring serta memprediksi tren harga bahan pokok pangan di Indonesia secara *real-time*. Proyek ini bertujuan untuk membantu masyarakat, petani, dan pemangku kebijakan dalam mengamati fluktuasi harga komoditas penting (seperti beras, minyak goreng, telur, dll).

Sistem ini didukung oleh kecerdasan buatan (model peramalan Prophet) serta proses pengumpulan data (*web scraping* & API Integration) otomatis dari berbagai sumber terpercaya di Indonesia.

## 🌟 Fitur Utama

- **Dashboard Market**: Pantauan interaktif harga pangan secara *real-time*.
- **AI Price Prediction**: Prediksi tren harga komoditas per 7 hari ke depan menggunakan Algoritma **Prophet**.
- **Analisis Sentimen Berita**: Penilaian sentimen berita ekonomi (positif/negatif/netral) menggunakan pemrosesan bahasa alami (NLP) VADER.
- **Cuaca Agrikultur**: Informasi status cuaca terkini untuk membantu memprediksi gagal panen atau gangguan logistik.

## 🛠️ Tech Stack & Framework

| Layer | Teknologi & Dependensi |
|-------|-----------|
| **Frontend** | **Next.js 15** (App Router), TypeScript, Tailwind CSS, Recharts (Visualisasi Data), Lucide React (Ikon) |
| **Backend** | **Python**, **FastAPI** (Web Framework), SQLAlchemy (ORM), Uvicorn |
| **Machine Learning** | **Prophet** (Time-Series Forecasting), VADER (Sentiment Analysis), Pandas |
| **Database** | **SQLite** (Cocok untuk versi Lite/Development) |
| **Alur Data & Kolektor** | HTTPX, BeautifulSoup4, Feedparser |

## 📡 Sumber Data (Integration)

Aplikasi ini menarik data dari empat (4) pilar sumber utama:
1. **SP2KP Kemendag**: Data harga bahan pokok harian di berbagai pasar seluruh Indonesia.
2. **BMKG**: Data keadaan cuaca ekstrem/terkini.
3. **Local News API (ex CNN Indonesia RSS)**: Artikel web seputar ekonomi untuk diekstrak menjadi analisis sentimen.
4. **BPS Web API**: Data tingkat inflasi makro ekonomi.

---

## 🚀 Tutorial Instalasi & Pemasangan

Proyek ini terbagi menjadi dua *service*: Frontend dan Backend. Anda harus menjalankan keduanya.

### Prasyarat (*Prerequisites*)
Pastikan hal-hal berikut telah ter-instal di sistem Anda:
- **Python 3.10** atau lebih baru.
- **Node.js 18** atau lebih baru.
- (Opsional) Git untuk melakukan *cloning* repositori.

### 1. Menjalankan Backend (FastAPI + AI)

Buka terminal (*Command Prompt / PowerShell*) dan ikuti langkah berikut:

```bash
# 1. Pindah ke direktori backend
cd backend

# 2. (Sangat Disarankan) Buat Virtual Environment Python
python -m venv venv

# Aktifkan Virtual Environment 
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Instal semua dependensi yang dibutuhkan
pip install -r requirements.txt

# 4. Buat file .env dari template
# Ubah isi .env sesuai kunci API yang Anda miliki jika perlu
cp .env.example .env

# 5. Jalankan server backend Uvicorn
uvicorn app.main:app --reload --port 8000
```
*Backend akan berjalan di `http://localhost:8000`. Cek dokumentasi API interaktif pada `http://localhost:8000/docs`.*

### 2. Menjalankan Frontend (Next.js)

Buka terminal/jendela baru, lalu masuk ke folder Frontend:

```bash
# 1. Pindah ke direktori frontend
cd frontend

# 2. Instal semua dependensi Node.js
npm install 
# atau gunakan yarn/pnpm (misal: yarn install)

# 3. Jalankan server pengembangan mode dev
npm run dev
```
*Frontend akan otomatis terbuka atau dapat diakses melalui `http://localhost:3000`.*

---

## ⚙️ Skema Operasional (Pertama Kali Jalan)

Karena *database* SQLite masih kosong saat Anda pertama kali mengunduh repositori ini, Anda perlu memicu sistem untuk "membaca" dari API luar:

1. Pastikan kedua *server* (Frontend & Backend) sudah berjalan.
2. Buka aplikasi di Browser (`http://localhost:3000`).
3. Pada halaman *Dashboard*, klik logo putar/tulisan **"Refresh Data"** di bagian navigasi atas.
4. *Backend server* proses berjalan: Sistem akan mengunduh ratusan data dari SP2KP, memanggil data iklim dari BMKG, membaca berita ekonomi, dan melakukan latih (*training*) ke model prediksi AI di belakang layar.
5. Tunggu notifikasi **"Sukses"** di layar (*Progress indicator* akan muncul).
6. Halaman akan dimuat ulang, seluruh grafik dan analisis prediksi AI sekarang akan tampil!

## 📄 Struktur API

Beberapa Endpoint utama yang bisa diakses untuk integrasi sistem ganda:
- `GET /api/dashboard` : Agregat data komoditas penuh, cuaca, dan makro data.
- `GET /api/predict?commodity={nama}&days=7` : RAMALAN Harga Prophet untuk komoditas tertentu.
- `GET /api/prices?commodity={nama}` : Grafik harga historikal.
- `GET /api/news` : Feed Berita yang telah melewati penilaian NLP.

### Pengembangan Masa Depan
Sistem dirancang dengan arsitektur modular yang memisahkan antara bagian *scrapper/collector* (`app/collectors`), jalur rute komunikasi (`app/routers`), dan Model ML (`app/ai`). Pendekatan ini memudahkan perluasan fungsi (*scalabiltiy*).

*(Projek Web Skripsi & AI Development 2026)*
