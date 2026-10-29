"""Train a mastitis classifier from clinically labelled cow-level sensor data.

This pipeline intentionally uses a separate dataset and model from the
synthetic monitoring-status classifier. It will not run until the required
field dataset is supplied.
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "dataset" / "raw" / "mastitis_labeled.csv"
MODEL_PATH = BASE_DIR / "model" / "mastitis_model.pkl"
RESULT_PATH = BASE_DIR / "mastitis_evaluation.txt"
FEATURES = [
    "temperature_celsius",
    "activity_level",
    "movement_index",
    "rest_duration_hour",
]
GROUP = "cow_id"
TARGET = "mastitis_status"


def main() -> None:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            f"Dataset mastitis berlabel belum tersedia: {DATA_PATH}\n"
            "Siapkan CSV dengan fitur sensor, cow_id, mastitis_status (0/1), "
            "dan sumber/rujukan label yang terdokumentasi. Jangan gunakan "
            "dataset simulasi monitoring_status sebagai label mastitis."
        )

    data = pd.read_csv(DATA_PATH)
    required = FEATURES + [GROUP, TARGET]
    missing = sorted(set(required) - set(data.columns))
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(missing)}")

    data = data[required].copy()
    for column in FEATURES + [TARGET]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=required)
    data[GROUP] = data[GROUP].astype(str).str.strip()
    data = data[data[GROUP] != ""]
    data = data[data[TARGET].isin([0, 1])]
    data[TARGET] = data[TARGET].astype(int)

    if data.empty or set(data[TARGET].unique()) != {0, 1}:
        raise ValueError("Dataset harus memuat label mastitis 0 dan 1.")
    if data[GROUP].nunique() < 4:
        raise ValueError(
            "Diperlukan sekurangnya empat ID sapi untuk evaluasi awal "
            "berdasarkan individu."
        )

    X = data[FEATURES]
    y = data[TARGET]
    groups = data[GROUP]
    splitter = GroupShuffleSplit(n_splits=200, test_size=0.2, random_state=42)
    split = None
    for train_idx, test_idx in splitter.split(X, y, groups):
        if set(y.iloc[train_idx]) == {0, 1} and set(y.iloc[test_idx]) == {0, 1}:
            split = (train_idx, test_idx)
            break
    if split is None:
        raise ValueError(
            "Tidak ditemukan pembagian latih/uji berbasis sapi yang memuat "
            "kedua kelas. Tambah jumlah sapi dan label positif/negatif."
        )

    train_idx, test_idx = split
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    train_cows = set(groups.iloc[train_idx])
    test_cows = set(groups.iloc[test_idx])
    if train_cows & test_cows:
        raise RuntimeError("Kebocoran ID sapi terdeteksi antara latih dan uji.")

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])
    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["TIDAK MASTITIS", "MASTITIS"],
        zero_division=0,
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    RESULT_PATH.write_text(
        "NOVFERCHE AI — EVALUASI MODEL MASTITIS\n"
        "Hasil ini hanya berlaku untuk dataset dan protokol label yang dicatat.\n\n"
        f"Sampel valid: {len(data)}\n"
        f"Sapi latih/uji: {len(train_cows)}/{len(test_cows)}\n"
        f"Sampel latih/uji: {len(train_idx)}/{len(test_idx)}\n"
        f"Akurasi uji: {accuracy_score(y_test, predictions):.4f}\n\n"
        f"Laporan klasifikasi:\n{report}\n"
        f"Confusion matrix [tidak mastitis, mastitis]:\n{matrix}\n\n"
        "Recall kelas MASTITIS perlu ditinjau khusus sebelum uji lapangan. "
        "Evaluasi ini bukan validasi klinis atau pengganti pemeriksaan dokter hewan.\n",
        encoding="utf-8",
    )
    print(f"Sapi latih/uji: {len(train_cows)}/{len(test_cows)}")
    print(f"Akurasi data uji: {accuracy_score(y_test, predictions):.4f}")
    print(report)
    print(f"Model disimpan: {MODEL_PATH}")
    print(f"Evaluasi disimpan: {RESULT_PATH}")


if __name__ == "__main__":
    main()
