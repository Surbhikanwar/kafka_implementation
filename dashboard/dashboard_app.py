import os
import sys
import time
import json
import threading
from collections import deque, defaultdict
from datetime import datetime, timezone

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from kafka import KafkaConsumer

# ---- path fix so we can import utils or config if needed ----
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Try to import Kafka config; else fallback to defaults
try:
    from data_ingestion.kafka_config import KAFKA_BOOTSTRAP_SERVERS, VEHICLE_TOPIC, ALERT_TOPIC, GROUP_ID
except Exception:
    KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
    VEHICLE_TOPIC = os.environ.get("VEHICLE_TOPIC", "vehicle.telematics")
    ALERT_TOPIC = os.environ.get("ALERT_TOPIC", "vehicle.alerts")
    GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "vehicle-dashboard-group")

# Try to import logger if available
try:
    from utils.logger import get_logger
    logger = get_logger("dashboard")
except Exception:
    def logger_print(*a, **k): print(*a, **k)
    logger = type("L", (), {"info": logger_print, "warning": logger_print, "error": logger_print, "exception": logger_print})

# -------------------------
# Shared storage (thread-safe)
# -------------------------
telemetry_lock = threading.Lock()
telemetry_store = {}                # vehicle_id -> last telemetry dict

alerts_lock = threading.Lock()
alerts_store = deque(maxlen=300)    # recent alerts

agent_activity_lock = threading.Lock()
agent_activity = deque(maxlen=200)  # agent logs

# -------------------------
# Kafka listener thread
# -------------------------
def kafka_listener():
    """
    Background thread: consumes from vehicle & alert topics,
    updates telemetry_store and alerts_store.
    """
    try:
        consumer = KafkaConsumer(
            VEHICLE_TOPIC,
            ALERT_TOPIC,
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            auto_offset_reset="latest",  # change to "earliest" for debugging
            enable_auto_commit=True,
            group_id=f"{GROUP_ID}-dashboard",
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )
        logger.info("[dashboard] Kafka consumer started")
    except Exception as e:
        logger.exception(f"[dashboard] Kafka consumer failed to start: {e}")
        return

    try:
        for msg in consumer:
            topic = msg.topic
            value = msg.value

            if topic == VEHICLE_TOPIC:
                vid = value.get("vehicle_id", "UNKNOWN")
                value["_received_at"] = datetime.now(timezone.utc).isoformat() + "Z"
                with telemetry_lock:
                    telemetry_store[vid] = value

            elif topic == ALERT_TOPIC:
                alert = {
                    "vehicle_id": value.get("vehicle_id", "UNKNOWN"),
                    "timestamp": value.get("timestamp", datetime.now(timezone.utc).isoformat() + "Z"),
                    "message": value.get("message", value.get("issue", str(value))),
                    "telemetry": value.get("telemetry", {})
                }
                with alerts_lock:
                    alerts_store.appendleft(alert)

                # Log UEBA-style entry
                ulog = {
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "agent": "AnalysisAgent",
                    "action": "published_alert",
                    "vehicle_id": alert["vehicle_id"],
                    "message": alert["message"]
                }
                with agent_activity_lock:
                    agent_activity.appendleft(ulog)

            else:
                logger.info(f"[dashboard] Unknown topic: {topic}")
    except Exception as e:
        logger.exception(f"[dashboard] Kafka listener error: {e}")
    finally:
        try:
            consumer.close()
        except Exception:
            pass
        logger.info("[dashboard] Kafka consumer stopped")

# Start listener thread once
if "kafka_thread_started" not in st.session_state:
    t = threading.Thread(target=kafka_listener, daemon=True, name="dashboard-kafka-listener")
    t.start()
    st.session_state["kafka_thread_started"] = True
    logger.info("[dashboard] Started kafka listener thread")

# -------------------------
# Predictive rules (simple demo)
# -------------------------
def predict_issues_from_telemetry(tele):
    issues = []
    speed = tele.get("speed", 0) or tele.get("Speed", 0)
    temp = tele.get("engine_temp", 0) or tele.get("Engine Temp (°C)", 0)
    vibration = tele.get("vibration", 0) or tele.get("Vibration", 0)
    battery = tele.get("battery_voltage", 0) or tele.get("Battery Voltage", 0)
    fuel = tele.get("fuel_level", 100) or tele.get("Fuel Level (%)", 100)

    if temp and temp > 110:
        issues.append(("Engine Overheat", min(99, int((temp - 90) * 2)), f"Engine temp {temp}°C"))
    if speed and speed > 130:
        issues.append(("Overspeeding", min(99, int((speed - 100))), f"Speed {speed} km/h"))
    if vibration and vibration > 4.0:
        issues.append(("High Vibration", 80, f"Vibration {vibration}"))
    if battery and battery < 11.8:
        issues.append(("Low Battery", 85, f"Battery {battery}V"))
    if fuel and fuel < 10:
        issues.append(("Low Fuel", 70, f"Fuel {fuel}%"))

    return issues

# -------------------------
# Streamlit Layout
# -------------------------
st.set_page_config(page_title="AutoSenseAI Dashboard", layout="wide")
st.title("🚘 AutoSenseAI — Predictive Maintenance Dashboard")
st.markdown("Real-time vehicle telemetry, predictive alerts, automated scheduling, and UEBA monitoring.")

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select page", ["Overview", "Vehicle Telemetry", "Predictive Maintenance", "Customer Scheduling", "Manufacturing Insights", "UEBA Security"])

# Sidebar controls
refresh_rate = st.sidebar.slider("Auto-refresh (seconds)", min_value=2, max_value=15, value=5)
selected_vehicle = st.sidebar.selectbox("Select vehicle", options=sorted(list(telemetry_store.keys()) + ["VEH1000", "VEH1001", "VEH1002"]), index=0)

# Copy shared data
with telemetry_lock:
    local_telemetry = dict(telemetry_store)
with alerts_lock:
    recent_alerts = list(alerts_store)
with agent_activity_lock:
    recent_agent_logs = list(agent_activity)

# Kafka Status Bar
st.markdown("---")
st.markdown(f"**🟢 Kafka Connected:** `{KAFKA_BOOTSTRAP_SERVERS}` | Telemetry: `{len(local_telemetry)}` | Alerts: `{len(recent_alerts)}` | Last Updated: `{datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}`")
st.markdown("---")

# ---------- PAGE: Overview ----------
if page == "Overview":
    st.subheader("System Overview")
    total_vehicles = len(local_telemetry)
    active_alerts = len(recent_alerts)
    predicted_issues = sum(1 for v in local_telemetry.values() if predict_issues_from_telemetry(v))
    anomalous_agents = sum(1 for a in recent_agent_logs if a.get("action") != "published_alert")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Vehicles", total_vehicles)
    c2.metric("Predicted Issues", predicted_issues)
    c3.metric("Active Alerts", active_alerts)
    c4.metric("Anomalous Agent Activities", anomalous_agents)

    st.markdown("### Live vehicle snapshot")
    if not local_telemetry:
        st.info("Waiting for telemetry — start producers.")
    else:
        df = pd.DataFrame.from_dict(local_telemetry, orient='index')
        if "_received_at" in df.columns:
            df = df.drop(columns=["_received_at"])
        st.dataframe(df.reset_index().rename(columns={"index": "vehicle_id"}), use_container_width=True)

# ---------- PAGE: Vehicle Telemetry ----------
elif page == "Vehicle Telemetry":
    st.subheader(f"Real-time Telemetry — {selected_vehicle}")
    tele = local_telemetry.get(selected_vehicle)
    if not tele:
        st.warning("No telemetry for selected vehicle (waiting for data).")
    else:
        cols = st.columns(3)
        cols[0].metric("Speed (km/h)", tele.get("speed", tele.get("Speed", "N/A")))
        cols[1].metric("Engine Temp (°C)", tele.get("engine_temp", tele.get("Engine Temp (°C)", "N/A")))
        cols[2].metric("Fuel Level (%)", tele.get("fuel_level", tele.get("Fuel Level (%)", "N/A")))

        st.markdown("#### Latest telemetry JSON")
        st.json(tele)

        st.markdown("#### Quick sensor trend (demo)")
        times = list(range(10))
        temp = [(tele.get("engine_temp", 80) + i % 3) for i in times]
        speed = [(tele.get("speed", 60) + (i % 5) * 2) for i in times]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=temp, name="Engine Temp (°C)"))
        fig.add_trace(go.Scatter(x=times, y=speed, name="Speed (km/h)"))
        fig.update_layout(height=350, xaxis_title="Samples", yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)

# ---------- PAGE: Predictive Maintenance ----------
elif page == "Predictive Maintenance":
    st.subheader("Predictive Maintenance Insights")
    rows = []
    for vid, tele in local_telemetry.items():
        issues = predict_issues_from_telemetry(tele)
        if issues:
            for issue in issues:
                rows.append({
                    "vehicle_id": vid,
                    "issue": issue[0],
                    "score": issue[1],
                    "detail": issue[2],
                    "last_seen": tele.get("_received_at", "N/A")
                })
    if not rows:
        st.success("No immediate predictive issues detected across fleet.")
    else:
        df_issues = pd.DataFrame(rows).sort_values(by=["score"], ascending=False)
        st.dataframe(df_issues, use_container_width=True)

# ---------- PAGE: Customer Scheduling ----------
elif page == "Customer Scheduling":
    st.subheader("Automated Service Scheduling")
    st.info("Shows scheduled services suggested by the system (simulated).")
    scheduled = []
    for vid, tele in local_telemetry.items():
        issues = predict_issues_from_telemetry(tele)
        high = any(i[1] >= 80 for i in issues)
        if high:
            scheduled.append({
                "vehicle_id": vid,
                "suggested_service": "Immediate Inspection",
                "proposed_date": datetime.now().date().isoformat(),
                "status": "Proposed"
            })
    scheduled += [
        {"vehicle_id": "VEH1001", "suggested_service": "Brake Check", "proposed_date": "2025-11-03", "status": "Confirmed"},
        {"vehicle_id": "VEH1002", "suggested_service": "Battery Replacement", "proposed_date": "2025-11-05", "status": "Pending"}
    ]
    st.dataframe(pd.DataFrame(scheduled), use_container_width=True)

# ---------- PAGE: Manufacturing Insights ----------
elif page == "Manufacturing Insights":
    st.subheader("Manufacturing Feedback & RCA")
    comp_counter = defaultdict(int)
    for a in recent_alerts:
        msg = a.get("message", "")
        if "engine" in msg.lower():
            comp = "Engine"
        elif "battery" in msg.lower():
            comp = "Battery"
        elif "brake" in msg.lower():
            comp = "Brakes"
        elif "vibration" in msg.lower() or "mount" in msg.lower():
            comp = "Engine Mount"
        else:
            comp = "Other"
        comp_counter[comp] += 1

    if comp_counter:
        comp_df = pd.DataFrame(list(comp_counter.items()), columns=["Component", "Failure Frequency"]).sort_values("Failure Frequency", ascending=False)
        st.dataframe(comp_df, use_container_width=True)
        fig = px.bar(comp_df, x="Component", y="Failure Frequency", title="Component Failure Frequency")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No manufacturing feedback yet (no alerts collected).")

# ---------- PAGE: UEBA Security ----------
elif page == "UEBA Security":
    st.subheader("UEBA — Agent Behavior Analytics")
    if not recent_agent_logs:
        st.info("No agent activity collected yet.")
    else:
        df_agents = pd.DataFrame(recent_agent_logs)
        st.dataframe(df_agents, use_container_width=True)

# ---------- Footer + Debug ----------
st.markdown("---")
st.caption(
    f"Data last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')} — Kafka Broker: {KAFKA_BOOTSTRAP_SERVERS}"
)

with st.expander("🔍 Debug Info"):
    st.write("Telemetry store size:", len(telemetry_store))
    st.write("Alert store size:", len(alerts_store))
    st.write("Agent activity size:", len(agent_activity))

# Auto-refresh
st.markdown(f"<meta http-equiv='refresh' content='{refresh_rate}'>", unsafe_allow_html=True)
