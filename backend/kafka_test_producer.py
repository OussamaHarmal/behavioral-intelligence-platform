from kafka import KafkaProducer
import json
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

event = {
    "timestamp": datetime.now().isoformat(),
    "source": "neurotrace-video",
    "risk_level": "HIGH",
    "activity": "SUSPICIOUS"
}

producer.send("video-events", event)
producer.flush()

print("Event sent to Kafka:", event)