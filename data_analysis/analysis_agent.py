"""
AnalysisAgent: Processes incoming telemetry data and raises alerts
when anomalies (e.g., over-speeding or overheating) are detected.
"""
import json
import random
from kafka import KafkaConsumer
from message_bus.producer_agent import AlertProducer
from data_ingestion.kafka_config import KAFKA_BOOTSTRAP_SERVERS, VEHICLE_TOPIC, GROUP_ID

class AnalysisAgent:
    def __init__(self):
        # Initialize the alert producer that sends alerts to Kafka or log system
        self.alert_producer = AlertProducer()

    def process_telemetry(self, data: dict):
        """Process a single vehicle telemetry record and detect anomalies."""
        vehicle_id = data.get("vehicle_id", "UNKNOWN")
        speed = data.get("speed", 0)
        temp = data.get("engine_temp", 0)

        # Simple rule-based check
        if speed > 120 or temp > 120:
            alert = {
                "vehicle_id": vehicle_id,
                "timestamp": data.get("timestamp"),
                "issue": "High Speed or Engine Temperature Detected",
                "speed": speed,
                "engine_temp": temp,
            }
            print(f"[AnalysisAgent ⚠️] ALERT for {vehicle_id}: Speed={speed}, Temp={temp}")
            self.alert_producer.send_alert(alert)
        else:
            print(f"[AnalysisAgent ✅] {vehicle_id} operating normally (Speed={speed}, Temp={temp})")

def run_analysis_agent():
    """Initializes and runs the analysis agent."""
    agent = AnalysisAgent()
    consumer = KafkaConsumer(
        VEHICLE_TOPIC,
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        auto_offset_reset='latest',
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print("[AnalysisAgent] Started and listening for vehicle data...")
    try:
        for message in consumer:
            agent.process_telemetry(message.value)
    except KeyboardInterrupt:
        print("[AnalysisAgent] Shutdown requested.")
    finally:
        consumer.close()

if __name__ == "__main__":
    run_analysis_agent()
