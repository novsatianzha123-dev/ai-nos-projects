"""SQLite persistence for resident complaints."""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DB_PATH = Path(__file__).resolve().parent / "asrama.db"


def _remote_config():
    """Read server-side Supabase credentials from env or Streamlit secrets."""
    url = os.environ.get("SUPABASE_URL")
    key = (os.environ.get("SUPABASE_SECRET_KEY")
           or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
           or os.environ.get("SUPABASE_KEY"))
    if not url or not key:
        try:
            import streamlit as st
            config = st.secrets.get("supabase", {})
            url = url or config.get("url")
            key = key or config.get("secret_key") or config.get("service_role_key") or config.get("key")
        except Exception:
            pass
    if url and key:
        return url.rstrip("/"), key
    return None


def _remote_request(method, query="", payload=None, prefer=None):
    config = _remote_config()
    if config is None:
        raise RuntimeError("Konfigurasi database bersama belum lengkap.")
    url, key = config
    headers = {
        "apikey": key,
        "Content-Type": "application/json",
    }
    # New sb_secret keys are opaque API keys, not JWTs. Legacy service_role keys
    # are JWTs and still need the Authorization header for PostgREST role access.
    if not key.startswith("sb_secret_"):
        headers["Authorization"] = f"Bearer {key}"
    if prefer:
        headers["Prefer"] = prefer
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(f"{url}/rest/v1/laporan{query}", data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=20) as response:
            data = response.read()
            return json.loads(data.decode("utf-8")) if data else None
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Database bersama menolak permintaan ({exc.code}): {detail}") from exc
    except URLError as exc:
        raise RuntimeError("Database bersama tidak dapat dijangkau. Periksa koneksi dan URL database.") from exc


def _connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    if _remote_config():
        return
    with _connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS laporan (
            id INTEGER PRIMARY KEY AUTOINCREMENT, tanggal TEXT, nama TEXT,
            kamar TEXT, pesan TEXT, kategori TEXT, prioritas TEXT,
            status TEXT, catatan TEXT)""")


def simpan_laporan(nama, kamar, pesan, kategori, prioritas):
    waktu = datetime.now().strftime("%d-%m-%Y %H:%M")
    if _remote_config():
        result = _remote_request("POST", "?select=id", {
            "tanggal": waktu, "nama": nama, "kamar": kamar, "pesan": pesan,
            "kategori": kategori, "prioritas": prioritas, "status": "Menunggu", "catatan": "-",
        }, "return=representation")
        return int(result[0]["id"])
    with _connect() as conn:
        cur = conn.execute("""INSERT INTO laporan
            (tanggal,nama,kamar,pesan,kategori,prioritas,status,catatan)
            VALUES (?,?,?,?,?,?,?,?)""",
            (waktu, nama, kamar, pesan, kategori, prioritas, "Menunggu", "-"))
        return cur.lastrowid


def ambil_laporan():
    if _remote_config():
        records = []
        offset = 0
        while True:
            page = _remote_request("GET", f"?select=*&order=id.desc&limit=1000&offset={offset}") or []
            records.extend(page)
            if len(page) < 1000:
                break
            offset += len(page)
        fields = ("id", "tanggal", "nama", "kamar", "pesan", "kategori", "prioritas", "status", "catatan")
        return [tuple(record.get(field) for field in fields) for record in records]
    with _connect() as conn:
        return [tuple(row) for row in conn.execute("SELECT * FROM laporan ORDER BY id DESC")]


def update_status(id_laporan, status, catatan="-"):
    if _remote_config():
        _remote_request("PATCH", f"?id=eq.{int(id_laporan)}", {"status": status, "catatan": catatan}, "return=minimal")
        return
    with _connect() as conn:
        conn.execute("UPDATE laporan SET status=?, catatan=? WHERE id=?",
                     (status, catatan, id_laporan))


def hapus_laporan(id_laporan):
    if _remote_config():
        _remote_request("DELETE", f"?id=eq.{int(id_laporan)}", prefer="return=minimal")
        return
    with _connect() as conn:
        conn.execute("DELETE FROM laporan WHERE id=?", (id_laporan,))


def jumlah_laporan():
    if _remote_config():
        return len(ambil_laporan())
    with _connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM laporan").fetchone()[0]


_init_db()
