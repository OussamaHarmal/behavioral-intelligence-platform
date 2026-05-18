from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"


def load_phishing_model():

    model_path = MODELS_DIR / "phishing_model.joblib"

    vectorizer_path = MODELS_DIR / "tfidf_vectorizer.joblib"

    if not model_path.exists() or not vectorizer_path.exists():
        return None, None

    model = joblib.load(model_path)

    vectorizer = joblib.load(vectorizer_path)

    return model, vectorizer