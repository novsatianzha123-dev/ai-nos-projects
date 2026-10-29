"""Optional terminal interface; the primary resident interface is app.py."""
from ai import CATEGORIES, RESPONSES, classify, priority
from database import simpan_laporan


def main():
    print("Layanan Keluhan Asrama — ketik 'exit' untuk keluar")
    while True:
        text = input("\nKeluhan Anda: ").strip()
        if text.casefold() == "exit":
            print("Terima kasih.")
            break
        if len(text) < 8:
            print("AI: Mohon jelaskan keluhan sedikit lebih lengkap.")
            continue
        name = input("Nama: ").strip()
        room = input("Nomor kamar: ").strip()
        if not name or not room:
            print("Nama dan nomor kamar diperlukan untuk membuat laporan.")
            continue
        category, confidence, unsure = classify(text)
        report_id = simpan_laporan(name, room, text, category, priority(text))
        print(RESPONSES.get(category, RESPONSES["pengaduan"]))
        print(f"Nomor ASR-{report_id:04d} · {CATEGORIES.get(category, category)} · "
              f"{'Kategori umum' if unsure else f'keyakinan {confidence:.0%}'}")


if __name__ == "__main__":
    main()
