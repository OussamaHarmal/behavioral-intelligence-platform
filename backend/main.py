from fastapi import FastAPI
from schemas import PhishingRequest
from models_loader import load_phishing_model
from data_loader import load_alerts, load_kpis, load_profiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NeuroTrace AI API",
    description="AI Behavioral Intelligence and Investigation Backend",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "NeuroTrace AI Backend is running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/kpis")
def get_kpis():
    return load_kpis()


@app.get("/alerts")
def get_alerts(limit: int = 20):
    alerts = load_alerts()

    if alerts.empty:
        return {
            "message": "No alerts found. Run the notebook first."
        }

    return alerts.head(limit).to_dict(orient="records")


@app.get("/users")
def get_users(limit: int = 20):
    profiles = load_profiles()

    if profiles.empty:
        return {
            "message": "No user profiles found. Run the notebook first."
        }

    return profiles.head(limit).to_dict(orient="records")


@app.get("/users/{user_id}")
def get_user(user_id: str):
    profiles = load_profiles()

    if profiles.empty:
        return {
            "message": "No user profiles found. Run the notebook first."
        }

    user_data = profiles[profiles["user"].astype(str) == user_id]

    if user_data.empty:
        return {
            "message": "User not found"
        }

    return user_data.iloc[0].to_dict()

@app.post("/predict-phishing")
def predict_phishing(request: PhishingRequest):
    model, vectorizer = load_phishing_model()

    if model is None or vectorizer is None:
        return {
            "message": "Phishing model not found. Run the notebook first."
        }

    text_vector = vectorizer.transform([request.text])
    prediction = model.predict(text_vector)[0]

    label = "PHISHING" if str(prediction) == "1" else "SAFE"

    return {
        "text": request.text,
        "prediction": label,
        "raw_prediction": str(prediction)
    }
    