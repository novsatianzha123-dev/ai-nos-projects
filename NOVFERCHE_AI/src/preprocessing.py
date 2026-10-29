import pandas as pd
import os


# ==========================================
# PATH PROJECT
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


RAW_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "raw",
    "behavior_dataset_raw.csv"
)


PROCESSED_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "processed",
    "behavior_dataset_clean.csv"
)


# ==========================================
# LOAD DATASET RAW
# ==========================================

print("Loading behavior dataset...")

data = pd.read_csv(
    RAW_PATH
)


print("Dataset awal:")
print(data.shape)


print("\nKolom dataset:")
print(data.columns)


# ==========================================
# DATA CLEANING
# ==========================================

# Hapus data tanpa label
data = data.dropna(
    subset=["Label"]
)


# Hapus data yang tidak memiliki perilaku jelas
data = data[
    ~data["Label"].isin(
        [
            "BLN",
            "ETC"
        ]
    )
]


print("\nSetelah cleaning:")
print(data.shape)


# ==========================================
# PILIH FEATURE SENSOR
# ==========================================

clean_data = data[
    [
        "Cow_ID",
        "AccX",
        "AccY",
        "AccZ",
        "Label"
    ]
]


# ==========================================
# CEK DATA AKHIR
# ==========================================

print("\nData siap ML:")
print(clean_data.head())


print("\nDistribusi label:")
print(
    clean_data["Label"].value_counts()
)


# ==========================================
# SIMPAN DATA PROCESSED
# ==========================================

os.makedirs(
    os.path.dirname(PROCESSED_PATH),
    exist_ok=True
)


clean_data.to_csv(
    PROCESSED_PATH,
    index=False
)


print(
    "\nBerhasil menyimpan:"
)
print(
    PROCESSED_PATH
)