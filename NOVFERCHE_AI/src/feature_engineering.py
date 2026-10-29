import pandas as pd
import numpy as np
import os


# ==========================================
# PATH PROJECT
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


INPUT_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "processed",
    "behavior_dataset_clean.csv"
)


OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "processed",
    "behavior_features.csv"
)


# ==========================================
# PARAMETER SENSOR
# ==========================================

# Sensor accelerometer:
# Sampling rate 25 Hz
# Window 2 detik = 50 data

WINDOW_SIZE = 50



# ==========================================
# LOAD DATA
# ==========================================

print("Loading clean dataset...")


data = pd.read_csv(
    INPUT_PATH
)


print("\nDataset awal:")
print(data.shape)


print("\nKolom:")
print(data.columns)



# ==========================================
# FEATURE EXTRACTION
# ==========================================

def extract_features(window):

    features = {}


    # -----------------------------
    # Acceleration X
    # -----------------------------

    features["mean_x"] = window["AccX"].mean()

    features["std_x"] = window["AccX"].std()

    features["min_x"] = window["AccX"].min()

    features["max_x"] = window["AccX"].max()

    features["range_x"] = (
        window["AccX"].max()
        -
        window["AccX"].min()
    )


    # -----------------------------
    # Acceleration Y
    # -----------------------------

    features["mean_y"] = window["AccY"].mean()

    features["std_y"] = window["AccY"].std()

    features["min_y"] = window["AccY"].min()

    features["max_y"] = window["AccY"].max()

    features["range_y"] = (
        window["AccY"].max()
        -
        window["AccY"].min()
    )



    # -----------------------------
    # Acceleration Z
    # -----------------------------

    features["mean_z"] = window["AccZ"].mean()

    features["std_z"] = window["AccZ"].std()

    features["min_z"] = window["AccZ"].min()

    features["max_z"] = window["AccZ"].max()

    features["range_z"] = (
        window["AccZ"].max()
        -
        window["AccZ"].min()
    )



    # -----------------------------
    # Magnitude
    # -----------------------------

    magnitude = np.sqrt(
        window["AccX"]**2 +
        window["AccY"]**2 +
        window["AccZ"]**2
    )


    features["mean_magnitude"] = (
        magnitude.mean()
    )


    features["std_magnitude"] = (
        magnitude.std()
    )


    features["max_magnitude"] = (
        magnitude.max()
    )



    # -----------------------------
    # Label asli sementara
    # -----------------------------

    features["Label"] = (
        window["Label"]
        .mode()[0]
    )


    # ID sapi

    features["Cow_ID"] = (
        window["Cow_ID"]
        .iloc[0]
    )


    return features




# ==========================================
# WINDOWING
# ==========================================

print("\nExtracting features...")


feature_list = []


for cow in data["Cow_ID"].unique():


    print(
        "Processing:",
        cow
    )


    cow_data = data[
        data["Cow_ID"] == cow
    ].reset_index(
        drop=True
    )


    for start in range(
        0,
        len(cow_data)-WINDOW_SIZE,
        WINDOW_SIZE
    ):


        window = cow_data[
            start:
            start + WINDOW_SIZE
        ]


        result = extract_features(
            window
        )


        feature_list.append(
            result
        )



# ==========================================
# DATAFRAME FEATURE
# ==========================================


features = pd.DataFrame(
    feature_list
)


print("\nFeature dataset:")
print(
    features.shape
)



# ==========================================
# LABEL TRANSFORMATION
# NORMAL vs ABNORMAL
# ==========================================


print("\nMengubah label perilaku...")


normal_behavior = [

    "RES",   # Resting

    "RUS",   # Ruminating

    "MOV",   # Moving

    "GRZ",   # Grazing

    "FES",   # Feeding

    "DRN"    # Drinking

]



features["Behavior_Status"] = features["Label"].apply(

    lambda x:

    "NORMAL"

    if x in normal_behavior

    else

    "ABNORMAL"

)



# hapus label lama

features = features.drop(
    columns=[
        "Label"
    ]
)



print("\nDistribusi kelas:")

print(
    features["Behavior_Status"]
    .value_counts()
)




# ==========================================
# SIMPAN DATASET
# ==========================================


os.makedirs(

    os.path.dirname(
        OUTPUT_PATH
    ),

    exist_ok=True

)



features.to_csv(

    OUTPUT_PATH,

    index=False

)



print("\nContoh data:")

print(
    features.head()
)



print(
    "\nBerhasil membuat:"
)


print(
    OUTPUT_PATH
)