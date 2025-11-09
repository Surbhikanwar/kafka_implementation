"""
Kafka producer that simulates vehicles sending telemetry.
Run: python vehicle_producer.py --count 5 --interval 1
"""
import argparse
import json
import time
import threading
from kafka import KafkaProducer
from .mock_vehicle_data import generate_vehicle_data
from .kafka_config import KAFKA_BOOTSTRAP_SERVERS, VEHICLE_TOPIC

def make_producer():
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5,
        api_version=(3, 6, 1)
    )

def start_single_vehicle(producer, vehicle_id, interval_seconds=2):
    try:
        while True:
            data = generate_vehicle_data(vehicle_id)
            producer.send(VEHICLE_TOPIC, value=data)
            producer.flush()
            print(f"[Producer] Sent: {vehicle_id} @ {data['timestamp']}")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print(f"[Producer] Stopping vehicle simulator {vehicle_id}")

def run_multi_vehicle(count=3, interval=2):
    producer = make_producer()
    threads = []
    for i in range(count):
        vid = f"VEH{1000 + i}"
        t = threading.Thread(target=start_single_vehicle, args=(producer, vid, interval), daemon=True)
        t.start()
        threads.append(t)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[Producer] Shutdown requested")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3, help="Number of vehicle simulators")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between messages per vehicle")
    args = parser.parse_args()
    run_multi_vehicle(count=args.count, interval=args.interval)

