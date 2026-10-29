"""NOVFERCHE AI dashboard for manual or device-fed monitoring data."""

from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "model" / "monitoring_model.pkl"
READINGS_PATH = BASE_DIR / "dataset" / "processed" / "sensor_readings.csv"
FEATURES = [
    "temperature_celsius",
    "activity_level",
    "movement_index",
    "rest_duration_hour",
]
BASELINE_WINDOW = 20
MIN_BASELINE_READINGS = 10
ANOMALY_THRESHOLD = 3.0


def classify(model, sensor_data: pd.DataFrame) -> tuple[float, str]:
    probabilities = model.predict_proba(sensor_data[FEATURES])[0]
    classes = list(model.classes_)
    if 1 not in classes:
        raise ValueError("Model tidak memiliki kelas 'perlu pemantauan' (1).")
    indicator = float(probabilities[classes.index(1)] * 100)
    if indicator < 30:
        return indicator, "PEMANTAUAN RUTIN"
    if indicator < 70:
        return indicator, "PERLU PEMANTAUAN"
    return indicator, "PEMANTAUAN LEBIH INTENSIF"


def find_sensor_changes(readings: pd.DataFrame, cow_id: str) -> tuple[list[str], int] | None:
    """Compare the latest cow reading with its own recent sensor baseline.

    This is a provisional anomaly flag, not a mastitis classifier. A robust
    deviation threshold is used only to surface large sensor changes.
    """
    cow_readings = readings[readings["cow_id"].astype(str) == str(cow_id)].copy()
    cow_readings = cow_readings.sort_values("timestamp")
    if len(cow_readings) < MIN_BASELINE_READINGS + 1:
        return None

    latest = cow_readings.iloc[-1]
    baseline = cow_readings.iloc[-(BASELINE_WINDOW + 1):-1]
    changed_features = []
    for feature in FEATURES:
        values = pd.to_numeric(baseline[feature], errors="coerce").dropna()
        current = pd.to_numeric(pd.Series([latest[feature]]), errors="coerce").iloc[0]
        if len(values) < MIN_BASELINE_READINGS or pd.isna(current):
            continue
        median = values.median()
        mad = (values - median).abs().median()
        scale = 1.4826 * mad
        if scale <= 1e-9:
            scale = values.std(ddof=0)
        deviation = abs(current - median) / scale if scale > 1e-9 else (0 if current == median else float("inf"))
        if deviation >= ANOMALY_THRESHOLD:
            changed_features.append(feature)
    return changed_features, len(baseline)


st.set_page_config(page_title="NOVFERCHE AI", page_icon="🐄", layout="wide")
st.title("🐄 NOVFERCHE AI")
st.subheader("Sistem Peringatan Dini Mastitis pada Sapi Perah Berbasis AI")
st.caption(
    "Berbasis AI melalui integrasi sensor suhu dan analisis perilaku, "
    "dirancang agar terjangkau untuk peternak rakyat."
)
st.info(
    "Prototipe menerima suhu tubuh dan fitur perilaku (aktivitas, gerakan, "
    "istirahat). Peringatan perubahan sensor membandingkan pembacaan terbaru "
    "dengan riwayat sapi yang sama. Perubahan ini tidak spesifik untuk mastitis. "
    "Model AI aktif masih dilatih pada data simulasi, bukan data berlabel mastitis."
)

if not MODEL_PATH.is_file():
    st.error("Model klasifikasi belum tersedia. Latih model terlebih dahulu:")
    st.code("python src\\train_monitoring_model.py", language="powershell")
    st.stop()

try:
    model = joblib.load(MODEL_PATH)
except Exception as error:
    st.error(f"Model gagal dimuat: {error}")
    st.stop()

st.sidebar.header("📡 Sumber data")
source = st.sidebar.radio("Pilih sumber", ["Input manual", "Sensor via API"])
sensor_data = None
cow_id = ""
sample_time = None
sensor_history = None

if source == "Input manual":
    cow_id = st.sidebar.text_input("ID sapi", value="COW-001")
    temperature = st.sidebar.number_input(
        "Suhu tubuh (°C)", min_value=35.0, max_value=42.0, value=39.5, step=0.1
    )
    activity = st.sidebar.number_input(
        "Aktivitas (%)", min_value=0.0, max_value=100.0, value=35.0, step=1.0
    )
    movement = st.sidebar.number_input(
        "Indeks gerakan", min_value=0.0, max_value=100.0, value=25.0, step=1.0
    )
    rest = st.sidebar.number_input(
        "Durasi istirahat (jam)", min_value=0.0, max_value=24.0, value=10.0, step=0.5
    )
    analyze = st.sidebar.button(
        "🔍 Klasifikasikan", type="primary", use_container_width=True
    )
    if analyze:
        sensor_data = pd.DataFrame(
            [[temperature, activity, movement, rest]], columns=FEATURES
        )
else:
    st.sidebar.info("Data terbaru dibaca dari API lokal setelah diterima.")
    st.sidebar.button("↻ Muat ulang data sensor", use_container_width=True)
    if READINGS_PATH.is_file():
        try:
            readings = pd.read_csv(READINGS_PATH)
            if not readings.empty:
                readings["timestamp"] = pd.to_datetime(readings["timestamp"], utc=True)
                readings = readings.sort_values("timestamp")
                sensor_history = readings
                latest = readings.iloc[-1]
                cow_id = str(latest["cow_id"])
                sample_time = latest["timestamp"]
                sensor_data = pd.DataFrame(
                    [[pd.to_numeric(latest[column], errors="raise") for column in FEATURES]],
                    columns=FEATURES,
                )
        except (OSError, ValueError, KeyError, pd.errors.ParserError) as error:
            st.error(f"Data sensor lokal tidak dapat dibaca: {error}")

st.header("📊 Pemantauan")
if sensor_data is None:
    if source == "Sensor via API":
        st.info("Belum ada data sensor. Nyalakan API, lalu kirim sampel dari perangkat/gateway.")
        st.code("python -m uvicorn src.sensor_api:app --host 0.0.0.0 --port 8000", language="powershell")
        st.caption("Dokumentasi API tersedia di http://127.0.0.1:8000/docs")
    else:
        st.info("Isi data di panel sebelah kiri, lalu klik **Klasifikasikan**.")
else:
    values = sensor_data.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ID sapi", cow_id or "—")
    col2.metric("Suhu", f"{values['temperature_celsius']:.1f} °C")
    col3.metric("Aktivitas", f"{values['activity_level']:.0f}%")
    col4.metric("Gerakan / istirahat", f"{values['movement_index']:.0f} / {values['rest_duration_hour']:g} jam")
    if sample_time is not None:
        st.caption(f"Waktu data (UTC): {sample_time.strftime('%Y-%m-%d %H:%M:%S')}")
        age_seconds = (datetime.now(timezone.utc) - sample_time.to_pydatetime()).total_seconds()
        if age_seconds > 600:
            st.warning("Data terakhir lebih dari 10 menit. Periksa koneksi perangkat atau gateway.")

    st.divider()
    st.header("🚨 Peringatan dini perubahan sensor")
    if source != "Sensor via API" or sensor_history is None:
        st.info("Peringatan berbasis riwayat aktif saat menggunakan data Sensor via API.")
    else:
        try:
            changes = find_sensor_changes(sensor_history, cow_id)
            if changes is None:
                st.info(
                    f"Belum cukup riwayat untuk {cow_id}. Diperlukan minimal "
                    f"{MIN_BASELINE_READINGS} pembacaan sebelumnya dari sapi yang sama."
                )
            elif changes[0]:
                feature_names = {
                    "temperature_celsius": "suhu tubuh",
                    "activity_level": "aktivitas",
                    "movement_index": "indeks gerakan",
                    "rest_duration_hour": "durasi istirahat",
                }
                labels = ", ".join(feature_names[name] for name in changes[0])
                st.warning(
                    f"Ada perubahan sensor yang besar pada: {labels}. "
                    "Tinjau kondisi sapi dan lanjutkan pemantauan."
                )
                st.caption(
                    "Peringatan anomali sementara; perubahan dapat disebabkan "
                    "berbagai faktor dan tidak memastikan mastitis."
                )
            else:
                st.success("Belum terlihat perubahan sensor yang besar dibandingkan riwayat sapi ini.")
            st.caption(
                f"Pembanding: hingga {BASELINE_WINDOW} pembacaan sebelumnya; "
                f"ambang anomali sementara {ANOMALY_THRESHOLD:g} skala robust. "
                "Ambang ini belum divalidasi pada data peternakan."
            )
        except (KeyError, ValueError, TypeError) as error:
            st.error(f"Peringatan perubahan sensor tidak dapat dihitung: {error}")

    try:
        indicator, category = classify(model, sensor_data)
        st.divider()
        st.header("🧠 Tingkat pemantauan (indikator prototipe)")
        score_col, status_col = st.columns(2)
        score_col.metric("Indikator pemantauan", f"{indicator:.1f}/100")
        if indicator >= 70:
            status_col.error(f"🔴 {category}")
            st.warning("Tingkatkan frekuensi pemantauan dan tinjau perubahan sensor.")
        elif indicator >= 30:
            status_col.warning(f"🟡 {category}")
            st.info("Lanjutkan pemantauan berkala dan perhatikan perubahan kondisi.")
        else:
            status_col.success(f"🟢 {category}")
    except Exception as error:
        st.error(f"Klasifikasi gagal: {error}")

if source == "Sensor via API" and READINGS_PATH.is_file():
    with st.expander("Riwayat data terbaru"):
        try:
            history = pd.read_csv(READINGS_PATH).tail(20).iloc[::-1]
            st.dataframe(history, use_container_width=True, hide_index=True)
        except (OSError, pd.errors.ParserError) as error:
            st.warning(f"Riwayat belum dapat ditampilkan: {error}")

st.divider()
st.caption(
    "Klasifikasi ini adalah indikator pemantauan dari model prototipe. "
    "Dataset pelatihan bersifat sintetis; cocokkan dengan pengamatan kondisi aktual."
)
