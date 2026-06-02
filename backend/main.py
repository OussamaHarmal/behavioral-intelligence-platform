from fastapi import FastAPI
from schemas import PhishingRequest
from models_loader import load_phishing_model
from data_loader import load_alerts, load_kpis, load_profiles
from fastapi.middleware.cors import CORSMiddleware
from data_loader import load_profiles, load_cert_data
from routes.video_live_analytics import router as video_live_router
app = FastAPI(
    title="NeuroTrace AI API",
    description="AI Behavioral Intelligence and Investigation Backend",
    version="1.0.0"
)
app.include_router(video_live_router)

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
    
    
@app.get("/graph")
def get_graph(limit: int = 100):

    df = load_cert_data()

    if df.empty:
        return {
            "nodes": [],
            "edges": []
        }

    df = df.head(limit)

    nodes_set = set()

    edges = []

    for _, row in df.iterrows():

        sender = str(row["from"]).split("@")[0]

        receivers = str(row["to"]).split(";")

        for receiver in receivers:

            receiver = receiver.strip()

            if "@" in receiver:
                receiver = receiver.split("@")[0]

            nodes_set.add(sender)
            nodes_set.add(receiver)

            edges.append({
                "source": sender,
                "target": receiver
            })

    nodes = []

    for node in nodes_set:

        nodes.append({
            "id": node,
            "label": node,
            "risk": "LOW",
            "score": 0
        })

    return {
        "nodes": nodes,
        "edges": edges
    }
    
    
@app.get("/alerts")
def get_alerts(limit: int = 25):

    profiles = load_profiles()

    if profiles.empty:
        return []

    alerts = []

    for _, row in profiles.iterrows():

        score = float(row["user_risk_score"])

        if score >= 20:
            risk_level = "HIGH"
            alert_type = "HIGH_RISK_USER"
        elif score >= 10:
            risk_level = "MEDIUM"
            alert_type = "SUSPICIOUS_ACTIVITY"
        else:
            risk_level = "LOW"
            alert_type = "USER_MONITORING"

        alerts.append({
            "user": row["user"],
            "alert_type": alert_type,
            "risk": risk_level,
            "severity": risk_level,
            "score": round(score, 2),
            "night_activity": int(row["night_emails"]),
            "external_emails": int(row["external_to_count"]),
            "attachments": int(row["attachment_count"]),
            "risky_attachments": int(row["attachment_risk_count"]),
            "explanation": (
                f"Risk score {round(score, 2)} based on behavioral indicators. "
                f"External emails: {int(row['external_to_count'])}, "
                f"attachments: {int(row['attachment_count'])}, "
                f"risky attachments: {int(row['attachment_risk_count'])}."
            )
        })

    alerts.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return alerts[:limit]


@app.get("/investigate/{user_id}")
def investigate_user(user_id: str):

    profiles = load_profiles()

    if profiles.empty:
        return {
            "message": "No user profiles found."
        }

    user = profiles[
        profiles["user"].astype(str) == str(user_id)
    ]

    if user.empty:
        return {
            "message": "User not found"
        }

    row = user.iloc[0]

    score = float(row["user_risk_score"])

    if score >= 20:
        risk_level = "HIGH"
    elif score >= 10:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "user": row["user"],
        "risk_level": risk_level,
        "score": round(score, 2),

        "total_emails": int(row["total_emails"]),
        "night_emails": int(row["night_emails"]),

        "external_to_count": int(row["external_to_count"]),
        "external_cc_count": int(row["external_cc_count"]),
        "external_bcc_count": int(row["external_bcc_count"]),

        "attachments": int(row["attachment_count"]),
        "risky_attachments": int(row["attachment_risk_count"]),

        "explanation":
            f"Risk score {round(score,2)} based on user behavior analysis.",

        "recommendation":
            "Immediate review required"
            if risk_level == "HIGH"
            else "Monitor activity"
    }