"""Copy local SQLite reports to the configured shared Supabase database."""
import sqlite3
from pathlib import Path

from database import DB_PATH, _remote_config, _remote_request


def main():
    if not _remote_config():
        raise SystemExit("Atur SUPABASE_URL dan SUPABASE_SERVICE_ROLE_KEY terlebih dahulu.")

    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM laporan ORDER BY id").fetchall()

    fields = ("id", "tanggal", "nama", "kamar", "pesan", "kategori", "prioritas", "status", "catatan")
    records = [{field: row[field] for field in fields} for row in rows]
    for start in range(0, len(records), 100):
        batch = records[start:start + 100]
        _remote_request(
            "POST",
            "?on_conflict=id",
            batch,
            "resolution=merge-duplicates,return=minimal",
        )

    print(f"Berhasil menyalin {len(records)} laporan ke database bersama.")
    print("Setelah impor, jalankan SQL reset sequence yang ada di README.md.")


if __name__ == "__main__":
    main()
