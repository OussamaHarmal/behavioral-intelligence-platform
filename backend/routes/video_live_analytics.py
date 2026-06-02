from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from kafka import KafkaProducer
import cv2
import csv
import os
import time
import json
from datetime import datetime

router = APIRouter()

VIDEO_SOURCE = r"C:\Users\dell\Desktop\NeuroTrace_AI\backend\videos\shoplifting\Shoplifting005_x264.mp4"
VIDEO_LABEL = "SHOPLIFTING"

LOG_FILE = r"C:\Users\dell\Desktop\NeuroTrace_AI\backend_ready\video_live_events.csv"
KAFKA_TOPIC = "video-events"

previous_gray = None

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def ensure_log_file():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "video_label",
                "frame_index",
                "motion_score",
                "brightness",
                "activity_level",
                "risk_level"
            ])


def send_to_kafka(event):
    try:
        producer.send(KAFKA_TOPIC, event)
        producer.flush()
    except Exception as e:
        print("Kafka error:", e)


def analyze_frame(frame, frame_index):
    global previous_gray

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = float(gray.mean())

    motion_score = 0.0

    if previous_gray is not None:
        diff = cv2.absdiff(previous_gray, gray)
        motion_score = float(diff.mean())

    previous_gray = gray

    if VIDEO_LABEL == "SHOPLIFTING" and motion_score >= 1.5:
        activity_level = "SUSPICIOUS"
        risk_level = "HIGH"
    elif motion_score >= 5:
        activity_level = "HIGH"
        risk_level = "HIGH"
    elif motion_score >= 2:
        activity_level = "MEDIUM"
        risk_level = "MEDIUM"
    else:
        activity_level = "LOW"
        risk_level = "LOW"

    event = {
        "timestamp": datetime.now().isoformat(),
        "source": "video-live-analytics",
        "video_label": VIDEO_LABEL,
        "frame_index": frame_index,
        "motion_score": round(motion_score, 2),
        "brightness": round(brightness, 2),
        "activity_level": activity_level,
        "risk_level": risk_level
    }

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            event["timestamp"],
            event["video_label"],
            event["frame_index"],
            event["motion_score"],
            event["brightness"],
            event["activity_level"],
            event["risk_level"]
        ])

    send_to_kafka(event)

    return event


def generate_video_stream():
    global previous_gray

    ensure_log_file()
    previous_gray = None

    cap = cv2.VideoCapture(VIDEO_SOURCE)

    if not cap.isOpened():
        print(f"Cannot open video source: {VIDEO_SOURCE}")
        return

    frame_index = 0

    while True:
        success, frame = cap.read()

        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_index = 0
            previous_gray = None
            continue

        frame_index += 1

        if frame_index % 5 != 0:
            continue

        frame = cv2.resize(frame, (960, 540))

        event = analyze_frame(frame, frame_index)

        overlay_text = (
            f"Kafka: ON | "
            f"Label: {VIDEO_LABEL} | "
            f"Risk: {event['risk_level']} | "
            f"Activity: {event['activity_level']} | "
            f"Motion: {event['motion_score']}"
        )

        color = (0, 0, 255) if event["risk_level"] == "HIGH" else (0, 255, 255)

        cv2.putText(
            frame,
            overlay_text,
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2
        )

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        time.sleep(0.03)

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )

    cap.release()


@router.get("/video/live-analytics")
def video_live_analytics():
    return StreamingResponse(
        generate_video_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/video/events")
def get_video_events(limit: int = 20):
    ensure_log_file()

    events = []

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            events.append(row)

    return events[-limit:]


@router.get("/video/summary")
def get_video_summary():
    ensure_log_file()

    events = []

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            events.append(row)

    if not events:
        return {
            "total_events": 0,
            "latest_risk": "UNKNOWN",
            "latest_activity": "UNKNOWN",
            "high_risk_events": 0,
            "average_motion": 0
        }

    high_risk_events = [
        event for event in events
        if event["risk_level"] == "HIGH"
    ]

    avg_motion = sum(
        float(event["motion_score"]) for event in events
    ) / len(events)

    return {
        "total_events": len(events),
        "latest_risk": events[-1]["risk_level"],
        "latest_activity": events[-1]["activity_level"],
        "high_risk_events": len(high_risk_events),
        "average_motion": round(avg_motion, 2)
    }