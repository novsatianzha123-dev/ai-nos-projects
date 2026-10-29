"""Web form for submitting and tracking dormitory complaints."""
import base64
from pathlib import Path

import streamlit as st
from database import simpan_laporan
from ai import CATEGORIES, RESPONSES, classify, priority, jawab_pertanyaan


@st.cache_resource
def get_model():
    from ai import load_model
    return load_model()


st.set_page_config(page_title="Aduan Asrama", page_icon="🏠", layout="centered")
assets_path = Path(__file__).parent / "assets"
background_data = base64.b64encode((assets_path / "dormitory-photo.png").read_bytes()).decode("ascii")
logo_data = base64.b64encode((assets_path / "dormitory-logo.png").read_bytes()).decode("ascii")
st.markdown(f"""
<style>
 .stApp {{
   background-image: linear-gradient(135deg, rgba(8, 25, 43, .64), rgba(13, 39, 60, .46)),
     url("data:image/png;base64,{background_data}");
   background-size: cover;
   background-position: center;
   background-attachment: fixed;
 }}
 .block-container {{ max-width: 860px; padding-top: 2.4rem; padding-bottom: 2.4rem; }}
 [data-testid="stHeader"] {{ background: transparent; }}
 html, body, [class*="st-"] {{ font-family: "Segoe UI", Arial, sans-serif; }}
 .hero {{ display: flex; align-items: center; gap: 1.15rem; margin: .2rem 0 1.2rem; }}
 .hero-logo {{ width: 90px; height: 90px; object-fit: contain; border-radius: 18px; background: #fff;
   padding: 5px; box-shadow: 0 8px 26px rgba(0,0,0,.22); flex: 0 0 auto; }}
 .hero-title {{ color: #ffffff !important; font-size: clamp(1.8rem, 4vw, 2.55rem); line-height: 1.12;
   font-weight: 750; letter-spacing: -.035em; text-shadow: 0 2px 14px rgba(0,0,0,.34); margin: 0; }}
 .hero-subtitle {{ color: #f4f8fc; font-size: 1.08rem; line-height: 1.6; margin: .5rem 0 0;
   text-shadow: 0 1px 8px rgba(0,0,0,.35); }}
 [data-testid="stForm"] {{ background: #fff; padding: 1.55rem 1.65rem; border-radius: 20px;
   border: 1px solid rgba(255, 255, 255, .85); box-shadow: 0 20px 55px rgba(0, 0, 0, .28); }}
 [data-testid="stForm"] label, [data-testid="stForm"] p {{ color: #243447; font-size: 1rem; }}
 [data-testid="stForm"] input, [data-testid="stForm"] textarea {{ font-size: 1rem; }}
 [data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{ min-height: 3rem; font-size: 1.02rem;
   font-weight: 650; border-radius: 10px; }}
 [data-testid="stAlert"] {{ background: rgba(255, 255, 255, .97); border-radius: 12px; }}
 [data-testid="stAlert"] p {{ color: #263746; font-size: .98rem; }}
 .stApp h2, .stApp h3 {{ color: #fff; text-shadow: 0 1px 8px rgba(0,0,0,.38); }}
 [data-testid="stChatMessage"] {{ background: rgba(255,255,255,.96); border-radius: 14px; }}
 [data-testid="stChatMessage"] p {{ color: #243447; }}
 [data-testid="stChatInput"] textarea {{ background: #fff; border-radius: 12px; }}
 .footer-note {{ color: #fff; text-align: center; font-size: .9rem; line-height: 1.55;
   text-shadow: 0 1px 8px rgba(0,0,0,.55); padding-top: .3rem; }}
 @media (max-width: 600px) {{
   .block-container {{ padding: 1.4rem 1rem 2rem; }}
   .hero-logo {{ width: 68px; height: 68px; border-radius: 14px; }}
   [data-testid="stForm"] {{ padding: 1.1rem; }}
 }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
  <img class="hero-logo" src="data:image/png;base64,{logo_data}" alt="Logo Students Dormitory">
  <div>
    <h1 class="hero-title">Layanan Keluhan Asrama</h1>
    <p class="hero-subtitle">Sampaikan masalah atau kebutuhanmu. Pengelola akan menerima laporan untuk ditindaklanjuti.</p>
  </div>
</div>
""", unsafe_allow_html=True)
st.info("Jika ada bahaya yang sedang berlangsung, segera hubungi petugas keamanan/pengelola secara langsung. Jangan menunggu balasan aplikasi.")

st.subheader("Tanya Jawab Asrama")
st.write("Tanyakan tentang jam tutup, keamanan, fasilitas, pengelola, atau tujuan asrama.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Tulis pertanyaan tentang asrama...")
if question:
    st.session_state.chat_messages.append({"role": "user", "content": question})
    answer = jawab_pertanyaan(question)
    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    st.rerun()

with st.form("complaint_form", clear_on_submit=False):
    nama = st.text_input("Nama", max_chars=100, placeholder="Nama penghuni")
    kamar = st.text_input("Nomor kamar", max_chars=30, placeholder="Contoh: A-203")
    keluhan = st.text_area("Keluh kesah / laporan", height=170, max_chars=3000,
                           placeholder="Jelaskan apa yang terjadi, lokasi, dan sejak kapan...")
    consent = st.checkbox("Saya setuju informasi ini diteruskan kepada pengelola asrama untuk penanganan laporan.")
    submit = st.form_submit_button("Kirim keluhan", type="primary", use_container_width=True)

if submit:
    if not nama.strip() or not kamar.strip() or len(keluhan.strip()) < 8:
        st.error("Isi nama, nomor kamar, dan keluhan (minimal 8 karakter).")
    elif not consent:
        st.error("Mohon setujui penerusan informasi untuk memproses laporan.")
    else:
        kategori, confidence, unsure = classify(keluhan.strip(), get_model())
        level = priority(keluhan)
        report_id = simpan_laporan(nama.strip(), kamar.strip(), keluhan.strip(), kategori, level)
        st.success(f"Laporan berhasil dikirim. Nomor laporan: **ASR-{report_id:04d}**")
        st.write(RESPONSES.get(kategori, RESPONSES["pengaduan"]))
        if unsure:
            st.caption("Kategori belum dapat dipastikan oleh AI; laporan diteruskan sebagai keluhan umum agar tetap diterima.")
        else:
            st.caption(f"Kategori: {CATEGORIES.get(kategori, kategori)} · Keyakinan model: {confidence:.0%}")
        st.caption(f"Prioritas awal: {level} · Status: Menunggu")

st.divider()
st.markdown('<p class="footer-note">Data laporan digunakan untuk tindak lanjut pengelola asrama. Hindari menuliskan kata sandi atau data pribadi yang tidak diperlukan.</p>', unsafe_allow_html=True)
