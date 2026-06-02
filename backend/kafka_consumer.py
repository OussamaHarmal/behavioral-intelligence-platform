from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "video-events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("Listening to Kafka topic: video-events")

for message in consumer:
    print("\nEVENT RECEIVED")
    print(message.value)