"""
Predict Router — /api/predict
Menjalankan model AI dan mengembalikan prediksi harga.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.ai.predictor import predict_prices, store_predictions
from app.schemas import PredictionOut

router = APIRouter(prefix="/api", tags=["prediction"])


@router.get("/predict", response_model=list[PredictionOut])
async def get_prediction(
    commodity: str = Query("beras", description="Nama komoditas, e.g. beras, telur ayam"),
    days: int = Query(7, description="Jumlah hari prediksi ke depan", ge=1, le=30),
    kode_provinsi: str = Query(None, description="Kode Provinsi"),
    kode_kab_kota: str = Query(None, description="Kode Kab/Kota"),
    db: Session = Depends(get_db),
):
    """
    Prediksi harga bahan pokok menggunakan model AI.

    - **commodity**: Nama komoditas (beras, minyak goreng, telur ayam, dll)
    - **days**: Jumlah hari prediksi (1-30)

    Returns: List prediksi harga, tren, dan persentase perubahan per hari.
    """
    predictions = predict_prices(db, commodity, days, kode_provinsi=kode_provinsi, kode_kab_kota=kode_kab_kota)

    if not predictions:
        raise HTTPException(
            status_code=404,
            detail=f"Tidak cukup data untuk memprediksi harga '{commodity}'. "
                   f"Pastikan data historis sudah dikumpulkan.",
        )

    # Store predictions in DB
    store_predictions(db, predictions)

    return predictions
