"""
AnalysisAgent: Processes incoming telemetry data and raises alerts
when anomalies (e.g., over-speeding or overheating) are detected.
"""

from message_bus.producer_agent import AlertProducer

class AnalysisAgent:
    def __init__(self):
        # Initialize the alert producer
        self.alert_producer = AlertProducer()

    def process_telemetry(self, data: dict):
        """Process a single vehicle telemetry record and detect anomalies."""
        vehicle_id = data.get("vehicle_id", "UNKNOWN")
        speed = data.get("speed", 0)
        temp = data.get("engine_temp", 0)

        # Rule-based anomaly detection
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
