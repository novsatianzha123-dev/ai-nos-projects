

from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "dataset" / "raw" / "sensor_data_raw.csv"
MODEL_PATH = BASE_DIR / "model" / "monitoring_model.pkl"
RESULT_PATH = BASE_DIR / "monitoring_evaluation.txt"
FEATURES = [
    "temperature_celsius",
    "activity_level",
    "movement_index",
    "rest_duration_hour",
]
TARGET = "monitoring_status"


def main() -> None:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            f"Dataset tidak ditemukan: {DATA_PATH}\n"
            "Buat dataset dengan: python src\\create_dataset.py"
        )

    data = pd.read_csv(DATA_PATH)
    if TARGET not in data.columns:
        raise ValueError(
            "Kolom label monitoring_status tidak ditemukan. "
            "Pelatihan mastitis memerlukan pipeline dan data mastitis berlabel "
            "yang tervalidasi secara terpisah."
        )
    target = TARGET
    required = FEATURES + [target]
    missing = sorted(set(required) - set(data.columns))
    if missing:
        raise ValueError(f"Kolom dataset tidak lengkap: {', '.join(missing)}")

    data = data[required].apply(pd.to_numeric, errors="coerce").dropna()
    if data.empty:
        raise ValueError("Dataset tidak memiliki baris lengkap untuk pelatihan.")
    labels = set(data[target].unique())
    if labels != {0, 1}:
        raise ValueError(
            f"Label pemantauan harus berisi kelas 0 dan 1; ditemukan: {sorted(labels)}"
        )

    X, y = data[FEATURES], data[target].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["NORMAL", "PERLU PEMANTAUAN"],
        zero_division=0,
    )
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    RESULT_PATH.write_text(
        "NOVFERCHE AI — EVALUASI KLASIFIKASI PEMANTAUAN (BUKAN DETEKSI MASTITIS)\n\n"
        f"Jumlah data: {len(data)}\n"
        f"Data latih: {len(X_train)} | Data uji: {len(X_test)}\n"
        f"Akurasi data uji: {accuracy:.4f}\n\n"
        f"Laporan klasifikasi:\n{report}\n"
        f"Confusion matrix [normal, perlu pemantauan]:\n{matrix}\n",
        encoding="utf-8",
    )

    print(f"Akurasi data uji: {accuracy:.4f}")
    print(report)
    print(f"Model disimpan: {MODEL_PATH}")
    print(f"Hasil evaluasi disimpan: {RESULT_PATH}")
    print("Kelas merepresentasikan status pemantauan dari dataset simulasi, bukan label mastitis.")


if __name__ == "__main__":
    main()
