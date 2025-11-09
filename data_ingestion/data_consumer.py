import json
import time
from kafka import KafkaConsumer
from analysis_agent import AnalysisAgent

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'vehicle.telematics',       # ✅ Topic name (matches the one you saw)
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='vehicle_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(3, 6, 1)
)

print("[Consumer] Listening for vehicle telemetry data...")

# Initialize analysis agent
analysis_agent = AnalysisAgent()

for message in consumer:
    data = message.value
    print(f"[Consumer] Received data: {data}")
    analysis_agent.process_telemetry(data)
    time.sleep(0.2)
