"""
Kafka consumer that reads vehicle telematics and forwards them to AnalysisAgent.
Run: python -m data_ingestion.data_consumer
"""

import json
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # ✅ Fix import path

from kafka import KafkaConsumer
from data_ingestion.kafka_config import KAFKA_BOOTSTRAP_SERVERS, VEHICLE_TOPIC, GROUP_ID
from data_analysis.analysis_agent import AnalysisAgent


def make_consumer():
    consumer = KafkaConsumer(
        VEHICLE_TOPIC,
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        api_version=(3, 6, 1)
    )
    return consumer


def run_consumer():
    consumer = make_consumer()
    agent = AnalysisAgent()
    print("[Consumer] Listening for vehicle telemetry...")

    try:
        for msg in consumer:
            data = msg.value
            print(f"[Consumer] Received {data['vehicle_id']} @ {data['timestamp']}")
            agent.process_telemetry(data)
    except KeyboardInterrupt:
        print("[Consumer] Interrupted, shutting down.")
    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()
