from kafka import KafkaProducer
import json

class AlertProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(3, 6, 1)
        )
        self.alert_topic = "vehicle.alerts"

    def send_alert(self, alert: dict):
        """Publish alert to Kafka topic."""
        self.producer.send(self.alert_topic, alert)
        self.producer.flush()
        print(f"[AlertProducer 🚨] Sent alert for {alert['vehicle_id']}")
