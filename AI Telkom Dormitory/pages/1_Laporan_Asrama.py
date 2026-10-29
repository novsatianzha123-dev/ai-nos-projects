"""Admin monitoring page for resident complaints."""
import os

import pandas as pd
import streamlit as st

from ai import CATEGORIES
from database import ambil_laporan, update_status


st.set_page_config(page_title="Laporan Asrama", page_icon="📋", layout="wide")

try:
    admin_secrets = st.secrets.get("admin", {})
except Exception:
    admin_secrets = {}
ADMIN_USERNAME = os.environ.get("ASRAMA_ADMIN_USERNAME") or admin_secrets.get("username")
ADMIN_PASSWORD = os.environ.get("ASRAMA_ADMIN_PASSWORD") or admin_secrets.get("password")
STATUSES = ["Menunggu", "Diproses", "Selesai"]
CATEGORY_LABELS = {key: value for key, value in CATEGORIES.items()}

st.markdown("""
<style>
  .block-container { max-width: 1500px; padding-top: 2rem; }
  [data-testid="stHeader"] { background: transparent; }
  [data-testid="stMetric"] { background: #f5f7fb; border: 1px solid #e5eaf2;
    padding: 1rem; border-radius: 14px; }
  [data-testid="stDataFrame"] { border: 1px solid #e5eaf2; border-radius: 12px; }
  .report-detail { background: #f5f7fb; border: 1px solid #e5eaf2;
    border-radius: 14px; padding: 1rem 1.2rem; }
</style>
""", unsafe_allow_html=True)

heading_col, access_col = st.columns([5, 2])
with heading_col:
    st.title("📋 Laporan Asrama")
    st.caption("Pemantauan bersama untuk SR dan pihak pengelola.")
with access_col:
    if st.session_state.get("admin_authenticated", False):
        st.success("Mode pengelola: dapat memperbarui tindak lanjut")
        if st.button("Keluar dari mode pengelola", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()
    else:
        with st.expander("Masuk sebagai pengelola untuk memperbarui status"):
            if not ADMIN_USERNAME or not ADMIN_PASSWORD:
                st.error("Login pengelola belum diatur. Isi username dan password rahasia pada konfigurasi aplikasi.")
            else:
                with st.form("admin_login"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    login = st.form_submit_button("Masuk", type="primary")
                if login:
                    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                        st.session_state.admin_authenticated = True
                        st.rerun()
                    st.error("Username atau password belum sesuai.")

st.warning("Halaman ini dapat dilihat oleh siapa pun yang memiliki tautan. Jangan membagikan tautannya di luar pihak asrama.")

rows = ambil_laporan()
if not rows:
    st.info("Belum ada laporan yang masuk.")
    st.stop()

columns = ["ID", "Tanggal", "Nama", "Kamar", "Isi laporan", "Kategori", "Prioritas", "Status", "Catatan"]
all_reports = pd.DataFrame(rows, columns=columns)

total = len(all_reports)
waiting = int((all_reports["Status"] == "Menunggu").sum())
processing = int((all_reports["Status"] == "Diproses").sum())
completed = int((all_reports["Status"] == "Selesai").sum())
metric_cols = st.columns(4)
for col, label, value in zip(metric_cols, ["Total laporan", "Menunggu", "Diproses", "Selesai"],
                             [total, waiting, processing, completed]):
    col.metric(label, value)

st.subheader("Daftar laporan")
filter_col, category_col = st.columns(2)
with filter_col:
    status_filter = st.selectbox("Filter status", ["Semua", *STATUSES])
with category_col:
    categories = ["Semua", *sorted(all_reports["Kategori"].dropna().unique().tolist())]
    category_filter = st.selectbox(
        "Filter kategori", categories,
        format_func=lambda value: "Semua kategori" if value == "Semua" else CATEGORY_LABELS.get(value, value.title()),
    )

filtered = all_reports.copy()
if status_filter != "Semua":
    filtered = filtered[filtered["Status"] == status_filter]
if category_filter != "Semua":
    filtered = filtered[filtered["Kategori"] == category_filter]

st.dataframe(filtered, hide_index=True, use_container_width=True)
csv_data = filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button("Unduh hasil filter (CSV)", csv_data, "laporan_asrama.csv", "text/csv")

if not filtered.empty:
    st.subheader("Tindak lanjut laporan")
    report_ids = filtered["ID"].astype(int).tolist()
    selected_id = st.selectbox(
        "Pilih laporan",
        report_ids,
        format_func=lambda report_id: next(
            f"ASR-{int(row['ID']):04d} · {row['Nama']} · {row['Kategori']} · {row['Status']}"
            for _, row in filtered.iterrows() if int(row["ID"]) == report_id
        ),
    )
    report = all_reports[all_reports["ID"] == selected_id].iloc[0]
    with st.container(border=True):
        st.markdown("**Isi laporan**")
        st.write(report["Isi laporan"])
        st.caption(f"Prioritas: {report['Prioritas']} · Kamar: {report['Kamar']}")
    if st.session_state.get("admin_authenticated", False):
        with st.form("update_report"):
            new_status = st.selectbox("Status tindak lanjut", STATUSES,
                                      index=STATUSES.index(report["Status"]) if report["Status"] in STATUSES else 0)
            note = st.text_area("Catatan tindak lanjut", value="" if report["Catatan"] == "-" else report["Catatan"],
                                placeholder="Contoh: Sudah diteruskan ke CME pada ...")
            save = st.form_submit_button("Simpan perubahan", type="primary")
        if save:
            update_status(int(selected_id), new_status, note.strip() or "-")
            st.success("Status dan catatan tindak lanjut berhasil diperbarui.")
            st.rerun()
    else:
        st.info("Masuk sebagai pengelola untuk mengubah status atau catatan tindak lanjut.")
