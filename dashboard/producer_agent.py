"""
Simple alert producer. Publishes to ALERT_TOPIC.
"""
import json
from kafka import KafkaProducer
from ..data_ingestion.kafka_config import KAFKA_BOOTSTRAP_SERVERS, ALERT_TOPIC
from ..utils.logger import get_logger

logger = get_logger(__name__)

class AlertProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=5,
            api_version=(3, 6, 1)
        )

    def publish_alert(self, alert: dict):
        try:
            self.producer.send(ALERT_TOPIC, value=alert)
            self.producer.flush()
            logger.info(f"[AlertProducer] Published alert for {alert.get('vehicle_id')}")
        except Exception as e:
            logger.exception(f"[AlertProducer] Failed to publish alert: {e}")
