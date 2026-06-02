import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_READY_DIR = BASE_DIR / "backend_ready"


def load_profiles():
    path = BACKEND_READY_DIR / "final_profiles.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def load_alerts():
    path = BACKEND_READY_DIR / "alerts.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def load_kpis():
    path = BACKEND_READY_DIR / "kpis.json"
    if not path.exists():
        return {
            "message": "kpis.json not found. Run the notebook first."
        }

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data[0] if isinstance(data, list) and data else data


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



BASE_DIR = Path(__file__).resolve().parent.parent

DATASETS_DIR = BASE_DIR / "datasets"


def load_profiles():

    file_path = DATASETS_DIR / "features" / "user_behavior_profile.csv"

    if not file_path.exists():
        return pd.DataFrame()

    return pd.read_csv(file_path)


def load_cert_data():

    file_path = DATASETS_DIR / "raw" / "email.csv"

    if not file_path.exists():
        return pd.DataFrame()

    return pd.read_csv(file_path)