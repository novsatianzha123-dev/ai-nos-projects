"""Local HTTP receiver for wearable/gateway sensor readings."""

import csv
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parents[1]
READINGS_PATH = BASE_DIR / "dataset" / "processed" / "sensor_readings.csv"
CSV_FIELDS = [
    "cow_id",
    "timestamp",
    "temperature_celsius",
    "activity_level",
    "movement_index",
    "rest_duration_hour",
]
write_lock = threading.Lock()

app = FastAPI(
    title="NOVFERCHE AI — Penerima Data Sensor",
    description=(
        "API ini menjadi jembatan antara perangkat/gateway sensor dan dashboard NOVFERCHE AI. "
        "Kirim satu pembacaan untuk menyimpannya dan menampilkannya di dashboard. "
        "Nilai aktivitas, gerakan, dan istirahat harus sudah diolah oleh perangkat/gateway. "
        "Model yang aktif belum dilatih untuk mendeteksi mastitis."
    ),
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Panduan",
            "description": "Periksa apakah layanan API sedang aktif.",
        },
        {
            "name": "Data Sensor",
            "description": (
                "Kirim pembacaan sensor sapi dan lihat data terbaru yang tersimpan. "
                "Semua data disimpan lokal di komputer yang menjalankan API."
            ),
        },
    ],
)


class SensorReading(BaseModel):
    cow_id: str = Field(
        min_length=1,
        max_length=40,
        description="ID unik sapi, misalnya COW-001.",
        examples=["COW-001"],
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Waktu pembacaan sensor. Jika dikosongkan, waktu saat ini digunakan.",
        examples=["2026-10-20T09:30:00Z"],
    )
    temperature_celsius: float = Field(
        ge=35,
        le=42,
        description="Suhu tubuh dalam derajat Celsius (rentang input 35–42).",
        examples=[38.5],
    )
    activity_level: float = Field(
        ge=0,
        le=100,
        description="Indeks aktivitas hasil olahan perangkat/gateway (0–100).",
        examples=[72],
    )
    movement_index: float = Field(
        ge=0,
        le=100,
        description="Indeks gerakan hasil olahan perangkat/gateway (0–100).",
        examples=[61],
    )
    rest_duration_hour: float = Field(
        ge=0,
        le=24,
        description="Durasi istirahat dalam jam (0–24).",
        examples=[6],
    )


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
def api_home():
    return """<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NOVFERCHE AI — Panduan Data Sensor</title>
  <style>
    :root { color-scheme: light; font-family: "Segoe UI", Arial, sans-serif; color: #18324b; background: #f4f7fb; }
    body { margin: 0; padding: 32px 18px; }
    main { max-width: 860px; margin: auto; }
    .card { background: white; border: 1px solid #dce5ef; border-radius: 16px; padding: 26px; margin: 16px 0; box-shadow: 0 5px 18px #18324b0d; }
    h1 { margin: 0 0 8px; font-size: 30px; } h2 { margin-top: 0; font-size: 21px; }
    p, li { line-height: 1.6; } .muted { color: #536579; }
    .flow { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align: center; }
    .step { background: #f1f6fc; border-radius: 12px; padding: 15px 10px; font-weight: 600; }
    .url, code { font-family: Consolas, monospace; overflow-wrap: anywhere; }
    .url { padding: 12px; border-radius: 8px; background: #f1f6fc; }
    table { width: 100%; border-collapse: collapse; } th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid #e5ebf2; }
    th { color: #38536e; }
    .actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 18px; }
    a.button { display: inline-block; border-radius: 9px; padding: 11px 16px; background: #1769aa; color: white; text-decoration: none; font-weight: 600; }
    a.secondary { background: #e8f0f8; color: #184d79; }
    .note { border-left: 4px solid #e8a328; padding: 10px 14px; background: #fff8e8; border-radius: 6px; }
    @media (max-width: 620px) { .flow { grid-template-columns: 1fr; } .card { padding: 19px; } }
  </style>
</head>
<body>
<main>
  <section class="card">
    <h1>🐄 NOVFERCHE AI</h1>
    <p class="muted">Panduan singkat pengiriman data sensor sapi ke dashboard.</p>
    <div class="flow">
      <div class="step">1. Sensor / gateway<br>membaca data</div>
      <div class="step">2. API menerima<br>dan menyimpan data</div>
      <div class="step">3. Dashboard<br>menampilkan data</div>
    </div>
  </section>
  <section class="card">
    <h2>Alamat penerima data</h2>
    <p>Kirim data dari perangkat atau gateway ke alamat ini menggunakan metode <strong>POST</strong>:</p>
    <div class="url">http://127.0.0.1:8000/sensor-data</div>
    <p class="muted">Jika mengirim dari perangkat lain di jaringan lokal, ganti <code>127.0.0.1</code> dengan alamat IP komputer yang menjalankan API.</p>
  </section>
  <section class="card">
    <h2>Data yang perlu dikirim</h2>
    <table>
      <thead><tr><th>Nama data</th><th>Arti</th><th>Contoh</th></tr></thead>
      <tbody>
        <tr><td><code>cow_id</code></td><td>ID sapi</td><td>COW-001</td></tr>
        <tr><td><code>temperature_celsius</code></td><td>Suhu tubuh (°C)</td><td>38.5</td></tr>
        <tr><td><code>activity_level</code></td><td>Indeks aktivitas (0–100)</td><td>72</td></tr>
        <tr><td><code>movement_index</code></td><td>Indeks gerakan (0–100)</td><td>61</td></tr>
        <tr><td><code>rest_duration_hour</code></td><td>Durasi istirahat (jam)</td><td>6</td></tr>
        <tr><td><code>timestamp</code></td><td>Waktu pencatatan (opsional)</td><td>2026-10-20T09:30:00Z</td></tr>
      </tbody>
    </table>
    <p>Aktivitas, gerakan, dan durasi istirahat harus dihitung lebih dulu oleh perangkat atau gateway. Jika waktu tidak dikirim, API memakai waktu saat data diterima.</p>
    <div class="actions">
      <a class="button" href="/docs">Buka panduan teknis API</a>
      <a class="button secondary" href="http://127.0.0.1:8501">Buka dashboard</a>
    </div>
  </section>
  <section class="card note">
    <strong>Status prototipe</strong>
    <p>Data disimpan lokal di komputer ini. Model yang aktif belum dilatih menggunakan label mastitis, jadi indikator dashboard bukan hasil deteksi mastitis.</p>
  </section>
</main>
</body>
</html>"""


@app.get(
    "/health",
    tags=["Panduan"],
    summary="Periksa koneksi API",
    description="Gunakan endpoint ini untuk memastikan API aktif dan mengetahui lokasi penyimpanan data.",
)
def health():
    return {"status": "ok", "readings_file": str(READINGS_PATH)}


@app.post(
    "/sensor-data",
    status_code=201,
    tags=["Data Sensor"],
    summary="Kirim pembacaan sensor sapi",
    description=(
        "Kirim satu pembacaan sensor. Isi ID sapi, suhu, aktivitas, gerakan, dan durasi istirahat. "
        "Timestamp boleh dihilangkan. Setelah berhasil, buka dashboard dan pilih Sensor via API."
    ),
    response_description="Data berhasil diterima dan disimpan secara lokal.",
)
def receive_sensor_data(reading: SensorReading):
    """Store one complete feature sample from a device or gateway."""
    row = reading.model_dump() if hasattr(reading, "model_dump") else reading.dict()
    row["timestamp"] = reading.timestamp.isoformat()
    READINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        with write_lock:
            write_header = not READINGS_PATH.exists() or READINGS_PATH.stat().st_size == 0
            with READINGS_PATH.open("a", newline="", encoding="utf-8") as output:
                writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
                if write_header:
                    writer.writeheader()
                writer.writerow(row)
    except OSError as error:
        raise HTTPException(status_code=500, detail="Gagal menyimpan data sensor lokal.") from error

    return {"accepted": True, "cow_id": reading.cow_id, "timestamp": row["timestamp"]}


@app.get(
    "/sensor-data/latest",
    tags=["Data Sensor"],
    summary="Lihat pembacaan sensor terbaru",
    description="Menampilkan hingga 100 pembacaan terakhir yang tersimpan secara lokal.",
)
def latest_sensor_data():
    if not READINGS_PATH.is_file():
        return {"readings": []}
    try:
        with READINGS_PATH.open("r", newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
    except OSError as error:
        raise HTTPException(status_code=500, detail="Gagal membaca data sensor lokal.") from error
    if not rows:
        return {"readings": []}
    return {"readings": rows[-100:]}
