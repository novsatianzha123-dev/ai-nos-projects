"""Classify one sensor sample into a monitoring level."""

from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "model" / "monitoring_model.pkl"
FEATURES = [
    "temperature_celsius",
    "activity_level",
    "movement_index",
    "rest_duration_hour",
]


def classify_monitoring(model, sensor_values: dict[str, float]) -> tuple[float, str]:
    sensor_data = pd.DataFrame([sensor_values], columns=FEATURES)
    probabilities = model.predict_proba(sensor_data)[0]
    classes = list(model.classes_)
    if 1 not in classes:
        raise ValueError("Model tidak memiliki kelas 'perlu pemantauan' (1).")

    indicator = float(probabilities[classes.index(1)] * 100)
    if indicator < 30:
        category = "PEMANTAUAN RUTIN"
    elif indicator < 70:
        category = "PERLU PEMANTAUAN"
    else:
        category = "PEMANTAUAN LEBIH INTENSIF"
    return indicator, category


def main() -> None:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Model belum ada: {MODEL_PATH}\n"
            "Latih model dahulu dengan: python src\\train_monitoring_model.py"
        )

    model = joblib.load(MODEL_PATH)
    sample = {
        "temperature_celsius": 39.5,
        "activity_level": 35.0,
        "movement_index": 25.0,
        "rest_duration_hour": 10.0,
    }
    indicator, category = classify_monitoring(model, sample)

    print("NOVFERCHE AI — KLASIFIKASI PEMANTAUAN")
    print(pd.DataFrame([sample]).to_string(index=False))
    print(f"\nIndikator pemantauan: {indicator:.1f}/100")
    print(f"Klasifikasi: {category}")
    print("Gunakan hasil sebagai panduan pemantauan dan tinjau bersama kondisi aktual.")


if __name__ == "__main__":
    main()
