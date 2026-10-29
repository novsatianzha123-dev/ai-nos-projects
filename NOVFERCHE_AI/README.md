# NOVFERCHE AI

## Sistem Peringatan Dini Mastitis pada Sapi Perah Berbasis AI melalui Integrasi Sensor Suhu dan Analisis Perilaku, Terjangkau untuk Peternak Rakyat

NOVFERCHE AI dirancang untuk menggabungkan suhu tubuh dan fitur perilaku sapi (aktivitas, indeks gerakan, durasi istirahat) guna membantu memberi peringatan dini mastitis. Prototipe perangkat lunak menerima data secara manual atau melalui API lokal. Pada mode API, dashboard membandingkan data terbaru dengan riwayat sapi yang sama dan dapat menandai perubahan sensor besar setelah tersedia sedikitnya 10 pembacaan terdahulu. Ambang anomali masih sementara dan perubahan sensor tidak spesifik untuk mastitis. **Model klasifikasi AI yang tersedia masih belajar status pemantauan dari data simulasi; model belum dilatih atau divalidasi untuk mengenali mastitis.** Keluaran saat ini bukan deteksi atau diagnosis mastitis. Sensor fisik, gateway, data mastitis berlabel, dan validasi lapangan masih perlu disiapkan.

## Menjalankan di VS Code (Windows)

1. Buka folder proyek `NOVFERCHE_AI` di VS Code.
2. Pilih **Terminal → New Terminal**. Pastikan terminal berada di folder proyek.
3. Buat dan aktifkan virtual environment:

   ```powershell
   python -m venv .venv
   ```

   Jika `python` tidak dikenali, instal Python dari python.org, lalu buka ulang VS Code.

4. Instal dependensi proyek:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

5. Latih model klasifikasi pemantauan:

   ```powershell
   .\.venv\Scripts\python.exe src\train_monitoring_model.py
   ```

   Perintah ini membaca `dataset/raw/sensor_data_raw.csv`, lalu membuat `model/monitoring_model.pkl` dan `monitoring_evaluation.txt`.

6. Jalankan dashboard (terminal pertama):

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run dashboard\app.py
   ```

   Streamlit akan menampilkan alamat lokal di terminal dan biasanya membuka dashboard di browser.

7. Untuk menerima data dari perangkat/gateway, buka terminal VS Code kedua dan jalankan API:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn src.sensor_api:app --host 0.0.0.0 --port 8000
   ```

   Dokumentasi endpoint tersedia di `http://127.0.0.1:8000/docs`. Perangkat dan komputer harus berada di jaringan lokal yang sama; gunakan alamat IP komputer pada perangkat. Endpoint `POST /sensor-data` menerima JSON berikut:

   ```json
   {
     "cow_id": "COW-001",
     "temperature_celsius": 38.5,
     "activity_level": 72,
     "movement_index": 61,
     "rest_duration_hour": 6
   }
   ```

   Kolom aktivitas, gerakan, dan istirahat adalah fitur olahan. Firmware/gateway perlu menghitungnya dari pembacaan akselerometer sebelum mengirim. Data yang diterima disimpan di `dataset/processed/sensor_readings.csv`, lalu dashboard dapat menampilkan data terbaru melalui pilihan **Sensor via API**. Untuk uji koneksi tanpa perangkat, kirim contoh melalui dokumentasi `/docs` atau PowerShell:

   ```powershell
   $body = @{
     cow_id = "COW-001"
     temperature_celsius = 38.5
     activity_level = 72
     movement_index = 61
     rest_duration_hour = 6
   } | ConvertTo-Json
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/sensor-data" -Method Post -ContentType "application/json" -Body $body
   ```

8. Alternatif untuk mencoba prediksi satu contoh melalui terminal:

   ```powershell
   .\.venv\Scripts\python.exe src\prediction.py
   ```

## Kelas pemantauan

Model saat ini belajar dua kelas dari dataset simulasi: `0` untuk `NORMAL` dan `1` untuk `PERLU PEMANTAUAN`. Aplikasi mengubah probabilitas kelas kedua menjadi indikator 0–100 untuk mengelompokkan hasil menjadi `PEMANTAUAN RUTIN` (<30), `PERLU PEMANTAUAN` (30–<70), atau `PEMANTAUAN LEBIH INTENSIF` (≥70). Ini merupakan klasifikasi prioritas pemantauan, bukan pengenalan mastitis atau diagnosis medis.

Alur: `dataset/raw/sensor_data_raw.csv` → validasi kolom dan data → pembagian data latih/uji terstratifikasi → Random Forest → evaluasi pada data uji → model dan laporan evaluasi.

Dataset yang disediakan dibuat secara sintetis oleh `src/create_dataset.py`. Label mengikuti pola simulasi sensor, sehingga evaluasi hanya menunjukkan kemampuan model mempelajari simulasi tersebut. Untuk melatih model pengenalan mastitis, kumpulkan data sapi perah nyata dengan label mastitis yang ditetapkan melalui pemeriksaan rujukan oleh tenaga terlatih. Pisahkan data latih dan uji menurut individu atau periode, lalu evaluasi sensitivitas, precision, recall, F1, dan confusion matrix sebelum menyatakan kemampuan deteksi. Skrip pemantauan ini hanya menerima kolom `monitoring_status`; data berlabel mastitis memerlukan alur pelatihan dan evaluasi tersendiri.

## Persiapan model mastitis

Alur terpisah tersedia di `src/train_mastitis_model.py`. Alur ini membaca `dataset/raw/mastitis_labeled.csv` dengan kolom `cow_id`, empat fitur sensor di atas, dan `mastitis_status` (`0` = tidak mastitis, `1` = mastitis). Setiap label harus berasal dari pemeriksaan rujukan yang terdokumentasi; jangan menyalin label simulasi `monitoring_status` ke kolom mastitis. Pembagian uji memisahkan sapi berdasarkan `cow_id` untuk mengurangi kebocoran antar sampel individu. Setelah data berlabel tersedia, jalankan:

```powershell
.\.venv\Scripts\python.exe src\train_mastitis_model.py
```

Skrip menyimpan model dan laporan secara terpisah dari model pemantauan. Tanpa dataset tersebut, model mastitis tidak dapat dilatih. Hasil evaluasi internal juga belum menjadi validasi klinis; lakukan peninjauan bersama tenaga kesehatan hewan sebelum penggunaan lapangan.

API saat ini menerima fitur sensor yang sudah diolah, bukan aliran mentah akselerometer. Integrasi fisik memerlukan firmware yang sesuai dengan board dan sensor yang dipilih. API prototipe ditujukan untuk jaringan lokal.

## Model klasifikasi perilaku

`src/train_model.py` dan `model/behavior_model.pkl` merupakan alur terpisah untuk klasifikasi perilaku berdasarkan fitur akselerometer. Model perilaku itu bukan model yang dipakai dashboard pemantauan sensor.
