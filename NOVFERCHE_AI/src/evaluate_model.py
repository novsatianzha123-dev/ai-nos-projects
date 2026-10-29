import os
import pandas as pd
import joblib

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

import matplotlib.pyplot as plt
import seaborn as sns


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

data = pd.read_csv(
    DATA_PATH
)


print("Dataset:")
print(data.shape)



# ==========================================
# LOAD MODEL
# ==========================================

print("\nLoading model...")

model = joblib.load(
    MODEL_PATH
)


print("Model loaded")



# ==========================================
# PREPARE DATA
# ==========================================

X = data.drop(
    [
        "Label",
        "Cow_ID",
        "Behavior_Status"
    ],
    axis=1,
    errors="ignore"
)


y = data[
    "Behavior_Status"
]



# ==========================================
# PREDICTION
# ==========================================

print("\nPredicting...")

y_pred = model.predict(
    X
)



# ==========================================
# ACCURACY
# ==========================================

accuracy = accuracy_score(
    y,
    y_pred
)


print("\nAccuracy:")
print(
    accuracy
)



# ==========================================
# CLASSIFICATION REPORT
# ==========================================

print(
    "\nClassification Report:"
)

print(
    classification_report(
        y,
        y_pred
    )
)



# ==========================================
# CONFUSION MATRIX
# ==========================================

cm = confusion_matrix(
    y,
    y_pred
)


print(
    "\nConfusion Matrix:"
)

print(cm)



# ==========================================
# SAVE RESULT
# ==========================================

RESULT_PATH = os.path.join(
    BASE_DIR,
    "evaluation_result.txt"
)


with open(
    RESULT_PATH,
    "w"
) as f:

    f.write(
        "NOVFERCHE AI MODEL EVALUATION\n\n"
    )

    f.write(
        f"Accuracy : {accuracy}\n\n"
    )

    f.write(
        classification_report(
            y,
            y_pred
        )
    )



print(
    "\nEvaluation saved:"
)

print(
    RESULT_PATH
)



# ==========================================
# CONFUSION MATRIX IMAGE
# ==========================================

plt.figure(
    figsize=(6,5)
)


sns.heatmap(
    cm,
    annot=True,
    fmt="d"
)


plt.xlabel(
    "Prediction"
)


plt.ylabel(
    "Actual"
)


plt.title(
    "Confusion Matrix - NOVFERCHE AI"
)


IMAGE_PATH = os.path.join(
    BASE_DIR,
    "confusion_matrix.png"
)


plt.savefig(
    IMAGE_PATH
)


plt.close()



print(
    "Confusion matrix saved:"
)

print(
    IMAGE_PATH
)