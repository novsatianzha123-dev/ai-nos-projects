"""Shared inference and report-priority rules for the ANN classifier."""
from pathlib import Path
import pickle

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "model" / "ai_model.pkl"

CATEGORIES = {
    "fasilitas": "Fasilitas", "jaringan": "Wi-Fi / jaringan",
    "kebersihan": "Kebersihan", "keamanan": "Keamanan",
    "perizinan": "Perizinan", "peraturan": "Informasi peraturan",
    "kehilangan": "Barang hilang", "administrasi": "Administrasi",
    "pengaduan": "Keluhan umum",
}
RESPONSES = {
    "fasilitas": "Terima kasih sudah memberi tahu kami. Laporan kerusakan fasilitas akan diteruskan kepada CME untuk ditindaklanjuti.",
    "jaringan": "Terima kasih sudah melaporkan kendala Wi-Fi. Laporanmu sudah dicatat untuk ditindaklanjuti.",
    "kebersihan": "Terima kasih sudah menyampaikan kondisi kebersihan. Laporanmu akan diteruskan kepada petugas terkait.",
    "keamanan": "Terima kasih sudah memberi tahu kami. Laporan keamanan akan ditindaklanjuti. Jika situasinya sedang berlangsung atau ada bahaya, segera hubungi satpam atau Senior Resident secara langsung.",
    "perizinan": "Terima kasih sudah bertanya tentang perizinan. Pertanyaanmu akan diteruskan kepada pengelola agar kamu mendapat arahan yang sesuai.",
    "peraturan": "Terima kasih sudah bertanya. Jika informasi aturan belum tersedia di sini, silakan konfirmasi kepada Senior Resident agar mendapat penjelasan yang tepat.",
    "kehilangan": "Turut prihatin barangmu hilang. Laporan ini akan dicatat; mohon sampaikan juga kepada satpam atau Senior Resident supaya dapat dibantu lebih lanjut.",
    "administrasi": "Terima kasih sudah menyampaikan kendala administrasi. Laporanmu akan diteruskan kepada pengelola untuk diperiksa.",
    "pengaduan": "Terima kasih sudah bercerita. Laporanmu sudah dicatat sebagai keluhan umum agar tetap dapat ditinjau pengelola.",
}


def jawab_pertanyaan(text):
    """Answer dormitory FAQs from confirmed local information; avoid guessing."""
    t = " ".join(text.casefold().replace("?", " ").replace("!", " ").split())

    if any(word in t for word in ("jam berapa", "pukul berapa", "jam malam", "tutup", "telat", "terlambat", "malam", "pulang", "kembali", "gerbang", "lewat 22", "22.00", "22:00")):
        return ("Asrama tutup pukul **22.00**. Kalau kamu memperkirakan akan terlambat, "
                "silakan hubungi **Senior Resident** agar mereka mengetahui kondisimu.")

    if any(word in t for word in ("satpam", "keamanan", "aman", "jaga", "penjaga", "darurat", "ancaman")):
        return ("Asrama dijaga oleh **satpam**. Ada juga **HD** dan **Senior Resident** di lingkungan asrama. "
                "Jika ada bahaya yang sedang berlangsung, segera hubungi satpam atau petugas asrama secara langsung.")

    if any(word in t for word in ("cme", "rusak", "kerusakan", "fasilitas", "perbaikan", "memperbaiki", "lampu", "air", "toilet", "kipas")):
        return ("Kalau ada fasilitas yang rusak, ceritakan bagian yang bermasalah dan lokasinya lewat formulir keluhan. "
                "Laporan kerusakan akan diteruskan kepada **CME** untuk ditindaklanjuti. Terima kasih sudah membantu menjaga fasilitas bersama.")

    if any(word in t for word in ("siapa yang mengelola", "pengelola", "dikelola", "kelola", "ditmawa", "asus", "pengurus")):
        return ("Pengelolaan asrama melibatkan **ASUS** dan **Ditmawa**. Untuk kebutuhan atau situasi sehari-hari, "
                "kamu juga bisa meminta arahan kepada **HD** atau **Senior Resident**. Sampaikan kebutuhanmu dengan jelas supaya mereka bisa mengarahkan ke pihak yang tepat.")

    if any(word in t for word in ("tujuan", "manfaat", "kenapa ada", "untuk apa", "asrama ini", "maba", "mahasiswa baru", "karakter")):
        return ("Asrama membantu mahasiswa baru membentuk karakter selama menjalani masa awal kuliah. "
                "Prosesnya dijalani bersama sebagai bagian dari kehidupan dan kegiatan di asrama. Saran kecil: ikuti kegiatan dengan terbuka, jaga tanggung jawab, dan saling menghormati agar pengalaman tinggal bersama terasa baik untuk semua.")

    if "hd" in t or "senior resident" in t:
        return ("Di asrama ada HD dan **Senior Resident** yang dapat menjadi tempat meminta arahan. "
                "Kalau ada keadaan darurat, segera hubungi satpam secara langsung.")

    category, confidence, unsure = classify(text)
    if not unsure:
        guidance = {
            "fasilitas": "Sampaikan nama fasilitas, lokasi, dan kondisi kerusakannya lewat formulir keluhan. Laporan akan diteruskan kepada CME.",
            "jaringan": "Coba sambungkan ulang Wi-Fi. Jika masih bermasalah, catat lokasi dan waktu kejadian lalu kirim laporan agar bisa diperiksa.",
            "kebersihan": "Sebutkan area yang perlu ditangani dan kapan kamu melihat kondisinya, lalu kirim laporan kepada pengelola.",
            "keamanan": "Jika ada bahaya sekarang, segera hubungi satpam. Untuk masalah yang tidak darurat, beri tahu Senior Resident atau kirim laporan.",
            "perizinan": "Sebelum pergi, hubungi Senior Resident. Sampaikan tujuan, waktu berangkat, perkiraan kembali, dan alasan izin agar mendapat arahan yang sesuai.",
            "peraturan": "Aturan bisa bergantung pada kondisi dan kebijakan yang berlaku. Konfirmasikan kepada HD atau Senior Resident sebelum mengambil tindakan.",
            "kehilangan": "Periksa kembali tempat terakhir barang terlihat, lalu segera beri tahu satpam atau Senior Resident. Sertakan ciri barang dan waktu/lokasi terakhir.",
            "administrasi": "Siapkan nomor kamar dan dokumen yang berkaitan, lalu tanyakan kepada pengelola administrasi atau Senior Resident tentang langkah berikutnya.",
            "pengaduan": "Agar bisa dibantu, jelaskan apa yang terjadi, kapan dan di mana, serta bantuan apa yang kamu perlukan. Kamu bisa mencatatnya lewat formulir keluhan.",
        }
        return ("Terima kasih sudah menjelaskan. "
                + guidance.get(category, "Sampaikan situasi dan bantuan yang kamu perlukan kepada Senior Resident atau pengelola."))

    return ("Terima kasih sudah bertanya. Aku belum memiliki aturan atau informasi yang cukup untuk memastikan jawabannya, "
            "jadi aku tidak ingin memberi informasi yang keliru. Langkah yang bisa kamu ambil: tanyakan kepada HD atau Senior Resident; "
            "jika menyangkut kerusakan, catat lokasi dan kondisi lalu kirim laporan; jika ada bahaya saat ini, hubungi satpam langsung.")


def load_model():
    if not MODEL_PATH.exists():
        return None
    with MODEL_PATH.open("rb") as f:
        model = pickle.load(f)
    if not hasattr(model, "predict_proba") or not hasattr(model, "named_steps"):
        return None
    return model


def classify(text, model=None):
    model = model if model is not None else load_model()
    if model is None:
        return "pengaduan", 0.0, True
    probabilities = model.predict_proba([text])[0]
    index = int(probabilities.argmax())
    confidence = float(probabilities[index])
    if confidence < 0.42:
        return "pengaduan", confidence, True
    return str(model.classes_[index]), confidence, False


def priority(text):
    t = text.casefold()
    urgent = ("kebakaran", "ada api", "diserang", "kekerasan", "ancaman", "orang asing masuk", "darurat")
    high = ("listrik", "korsleting", "pintu tidak bisa dikunci", "tidak aman", "dicuri", "hp hilang", "barang hilang")
    if any(term in t for term in urgent):
        return "Darurat"
    if any(term in t for term in high):
        return "Tinggi"
    return "Normal"
