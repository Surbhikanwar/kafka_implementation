"""
Simple rule engine: transform telemetry -> alert decisions.
You can replace this with a more advanced rules engine later.
"""
from typing import Dict, Tuple

def simple_rules_check(data: Dict) -> Tuple[bool, str]:
    """
    Returns (is_alert, alert_message).
    Rules:
      - engine_temp > 110 -> High engine temp
      - fuel_level < 5 -> Low fuel
      - speed > 130 -> Overspeed
      - vibration > 4.0 -> High vibration (possible mechanical issue)
      - battery_voltage < 11.8 -> Low battery
    """
    if data.get("engine_temp", 0) > 110:
        return True, f"High engine temperature: {data['engine_temp']}C"
    if data.get("fuel_level", 100) < 5:
        return True, f"Low fuel level: {data['fuel_level']}%"
    if data.get("speed", 0) > 130:
        return True, f"Overspeed detected: {data['speed']} km/h"
    if data.get("vibration", 0) > 4.0:
        return True, f"High vibration detected: {data['vibration']}"
    if data.get("battery_voltage", 0) < 11.8:
        return True, f"Low battery voltage: {data['battery_voltage']}V"
    return False, ""
