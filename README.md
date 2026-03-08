# HargaTaniCerdas — Sistem Prediksi Harga Bahan Pokok

Sistem berbasis AI untuk memprediksi tren harga bahan pokok (beras, minyak goreng, telur, dll) menggunakan data real dari SP2KP, BMKG, CNN Indonesia, dan BPS.

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Recharts |
| Backend | Python, FastAPI, SQLAlchemy, Prophet |
| Database | SQLite (development) |
| Data Sources | SP2KP, BMKG API, CNN Indonesia RSS, BPS Web API |
| NLP | VADER Sentiment Analysis |

## Architecture

```
SP2KP + BMKG + CNN + BPS → Database → AI Model (Prophet) → FastAPI → Next.js Dashboard
```

## Setup & Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- SP2KP API running locally on port 5500

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend akan berjalan di `http://localhost:8000`. Buka `http://localhost:8000/docs` untuk dokumentasi API interaktif.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend akan berjalan di `http://localhost:3000`.

### Pertama Kali Jalan

1. Pastikan SP2KP API (`http://127.0.0.1:5500`) sudah running
2. Jalankan backend
3. Klik tombol **"Refresh Data"** di dashboard atau POST ke `http://localhost:8000/api/collect` untuk mengumpulkan data dari semua sumber
4. Data akan tersimpan di SQLite dan dashboard akan menampilkan harga + prediksi

## API Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/dashboard` | GET | Aggregated data semua komoditas |
| `/api/predict?commodity=beras&days=7` | GET | Prediksi harga AI |
| `/api/prices?commodity=beras&days=30` | GET | Harga historis |
| `/api/commodities` | GET | Daftar komoditas tersedia |
| `/api/weather` | GET | Data cuaca BMKG |
| `/api/news` | GET | Berita ekonomi + sentimen |
| `/api/collect` | POST | Trigger data collection manual |

## Environment Variables

### Backend (`.env`)
```
DATABASE_URL=sqlite:///./hargatani.db
SP2KP_BASE_URL=http://127.0.0.1:5500
SP2KP_KODE_PROVINSI=33
SP2KP_KODE_KAB_KOTA=3315
BMKG_ADM4=33.15.00.0000
BPS_API_KEY=your_key_here
FRONTEND_URL=http://localhost:3000
```

### Frontend (`.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
