"""Train the dormitory complaint intent classifier (TF-IDF + neural MLP)."""
from pathlib import Path
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import FeatureUnion, Pipeline

from dataset import data_asrama


ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "model"


def build_model():
    texts = [row["pertanyaan"].strip().lower() for row in data_asrama]
    labels = [row["intent"] for row in data_asrama]
    features = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                                 strip_accents="unicode", min_df=1,
                                 token_pattern=r"(?u)\b\w+\b")),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5),
                                 sublinear_tf=True, min_df=1,
                                 strip_accents="unicode")),
    ])
    classifier = MLPClassifier(hidden_layer_sizes=(96, 48), activation="relu",
                               solver="adam", alpha=0.002, learning_rate_init=0.002,
                               max_iter=500, early_stopping=True, validation_fraction=0.15,
                               n_iter_no_change=25, random_state=42)
    return Pipeline([("features", features), ("classifier", classifier)]), texts, labels


if __name__ == "__main__":
    model, texts, labels = build_model()
    model.fit(texts, labels)
    MODEL_DIR.mkdir(exist_ok=True)
    with (MODEL_DIR / "ai_model.pkl").open("wb") as f:
        pickle.dump(model, f)
    print(f"Model ANN dilatih dari {len(texts)} contoh, {len(set(labels))} kategori.")
    print(f"Model tersimpan di {MODEL_DIR / 'ai_model.pkl'}")
