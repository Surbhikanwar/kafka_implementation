"""
Mock vehicle telemetry generator.
Provides a reusable function to generate telemetry dicts.
"""
import random
from datetime import datetime
from typing import Dict

def generate_vehicle_data(vehicle_id: str) -> Dict:
    # You can extend these sensors as needed.
    return {
        "vehicle_id": vehicle_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "speed": round(random.uniform(0, 140), 2),            # km/h
        "engine_temp": round(random.uniform(60, 120), 2),     # Celsius
        "fuel_level": round(random.uniform(0, 100), 2),       # Percentage
        "vibration": round(random.uniform(0.0, 5.0), 2),      # G or arbitrary unit
        "battery_voltage": round(random.uniform(11.5, 14.8), 2),
        "gps": {
            "lat": round(random.uniform(12.8, 13.2), 6),
            "lon": round(random.uniform(77.4, 77.9), 6),
        }
    }
