import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# ==========================================
# PATH PROJECT
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


DATA_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "processed",
    "behavior_features.csv"
)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "behavior_model.pkl"
)



# ==========================================
# LOAD DATA
# ==========================================

print("Loading dataset...")


df = pd.read_csv(
    DATA_PATH
)


print("\nDataset:")
print(df.shape)


print(df.head())



# ==========================================
# FEATURE & LABEL
# ==========================================

X = df.drop(
    columns=[
        "Behavior_Status",
        "Cow_ID"
    ]
)


y = df[
    "Behavior_Status"
]



print("\nDistribusi label:")
print(
    y.value_counts()
)



# ==========================================
# SPLIT DATA
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.2,

    random_state=42,

    stratify=y

)



print("\nData training:")
print(
    X_train.shape
)


print("Data testing:")
print(
    X_test.shape
)



# ==========================================
# MACHINE LEARNING MODEL
# RANDOM FOREST
# ==========================================


print("\nTraining Random Forest...")


model = RandomForestClassifier(

    n_estimators=100,

    random_state=42,

    class_weight="balanced"

)



model.fit(

    X_train,

    y_train

)



# ==========================================
# EVALUATION
# ==========================================

prediction = model.predict(
    X_test
)



accuracy = accuracy_score(

    y_test,

    prediction

)



print("\nAccuracy:")

print(
    accuracy
)



print("\nClassification Report:")

print(
    classification_report(
        y_test,
        prediction
    )
)



# ==========================================
# SAVE MODEL
# ==========================================


os.makedirs(

    os.path.dirname(MODEL_PATH),

    exist_ok=True

)



joblib.dump(

    model,

    MODEL_PATH

)



print("\nModel berhasil disimpan:")

print(
    MODEL_PATH
)