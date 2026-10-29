# Layanan Keluhan Asrama

Aplikasi Streamlit untuk penghuni mengirim keluhan dan model NLP berbasis TF-IDF + ANN (MLP) untuk menyarankan kategori laporan. Laporan tetap diterima sebagai **Keluhan umum** jika model belum yakin.

## Menjalankan aplikasi

Di Windows, buka PowerShell pada folder proyek lalu jalankan:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python train.py
streamlit run app.py
```

Buka alamat lokal yang ditampilkan Streamlit. Untuk memperbaiki kategori, tambahkan contoh keluhan berlabel di `dataset.py`, kemudian jalankan ulang `python train.py`.

## Pemantauan dan berbagi laporan

Halaman **Laporan Asrama** menampilkan semua laporan, ringkasan status, filter kategori/status, dan unduhan CSV. Siapa pun yang memiliki tautan dapat melihat isi laporan sesuai permintaan. Perubahan status dan catatan tindak lanjut hanya tersedia setelah login pengelola.

Untuk membagikan data lintas perangkat, siapkan database Supabase bersama:

1. Jalankan `supabase_schema.sql` di SQL Editor proyek Supabase.
2. Salin `.streamlit/secrets.toml.example` menjadi `.streamlit/secrets.toml`, lalu isi URL dan secret key Supabase serta kredensial admin. Simpan key hanya pada konfigurasi server; jangan bagikan atau commit file rahasia tersebut.
3. Jalankan `python migrate_laporan.py` satu kali untuk menyalin laporan yang sudah ada dari `asrama.db` ke database bersama.
4. Deploy aplikasi Streamlit ke hosting agar mendapatkan tautan yang dapat dibuka seluruh SR dan pihak terkait. Tautan laporan bersifat terbuka untuk siapa pun yang memilikinya; untuk membatasi akses lebih lanjut, gunakan login akun untuk semua pembaca.

Sesudah impor, sinkronkan identity sequence di SQL Editor:

```sql
select setval(
  pg_get_serial_sequence('public.laporan', 'id'),
  coalesce((select max(id) from public.laporan), 1),
  exists(select 1 from public.laporan)
);
```

## Catatan model

Dataset saat ini berisi **720 contoh seimbang**: 80 untuk masing-masing dari 9 kategori. Contoh mencakup variasi bahasa formal dan percakapan. Setelah mengubah `dataset.py`, jalankan ulang `python train.py` agar model memakai data terbaru. Skor keyakinan bukan jaminan kebenaran; keluhan yang ragu-ragu tetap dicatat dan perlu ditinjau pengelola. Kumpulkan keluhan nyata yang sudah dianonimkan dan label yang benar sebelum mengandalkan klasifikasi otomatis.

Jangan gunakan aplikasi ini sebagai saluran darurat. Untuk bahaya yang sedang berlangsung, penghuni perlu menghubungi petugas secara langsung.
