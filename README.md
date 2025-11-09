# 🚗 Real-Time Vehicle Telemetry System

A real-time data processing pipeline that simulates vehicle telemetry, analyzes performance metrics, detects anomalies, and visualizes insights through an interactive dashboard powered by Apache Kafka and Streamlit.

---

## ✨ Features

- **Real-Time Data Streaming** — Simulates and streams vehicle telemetry data (speed, engine temperature, fuel level, vibration, battery voltage) to Kafka topics
- **Anomaly Detection** — Analyzes incoming data using rule-based engine to identify overspeeding, overheating, and other critical issues
- **Live Dashboard** — Interactive Streamlit dashboard displaying real-time vehicle metrics, alerts, and predictive maintenance insights
- **Dockerized Infrastructure** — Kafka and Zookeeper managed via Docker Compose for seamless setup and deployment

---

## 🏗️ Architecture

The system follows a microservices architecture with event-driven communication:

| Component | Description |
|-----------|-------------|
| **Producer** | Generates mock vehicle telemetry and publishes to `vehicle.telematics` topic |
| **Analysis Agent** | Consumes telemetry data, applies business rules, and publishes alerts to `vehicle.alerts` topic |
| **Dashboard** | Real-time Streamlit app consuming both topics to visualize metrics and alerts |
| **Message Bus** | Apache Kafka handles asynchronous communication between services |

```
Vehicle Producer → Kafka (vehicle.telematics) → Analysis Agent → Kafka (vehicle.alerts) → Dashboard
                                                       ↓
                                                   Dashboard
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** — For Kafka infrastructure
- **Python 3.9+** — For running application services

### Installation

**1. Clone and Setup**
```bash
git clone https://github.com/Surbhikanwar/kafka_implementation.git
cd kafka_implementation
```

**2. Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Start Kafka Infrastructure**
```bash
docker-compose up -d
```

### Running the System

Open **three separate terminals** and run each command:

**Terminal 1: Start Producer**
```bash
python -m data_ingestion.vehicle_producer --count 3 --interval 2
```

**Terminal 2: Start Analysis Agent**
```bash
python -m data_analysis.analysis_agent
```

**Terminal 3: Start Dashboard**
```bash
streamlit run dashboard/dashboard_app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
kafka_implementation/
│
├── 📂 data_ingestion/
│   ├── vehicle_producer.py      # Generates and publishes vehicle telemetry
│   ├── mock_vehicle_data.py     # Mock data generation logic
│   └── kafka_config.py          # Kafka connection settings
│
├── 📂 data_analysis/
│   ├── analysis_agent.py        # Consumes and analyzes telemetry
│   └── rules_engine.py          # Business rules for anomaly detection
│
├── 📂 dashboard/
│   ├── dashboard_app.py         # Streamlit dashboard application
│   ├── consumer_agent.py        # Dashboard Kafka consumer
│   └── producer_agent.py        # Alert producer
│
├── 📂 master_agent/
│   ├── orchestrator.py          # Service orchestration
│   └── registry.py              # Agent registry
│
├── 📂 utils/
│   ├── config.py                # Configuration management
│   └── logger.py                # Logging utilities
│
├── docker-compose.yml           # Kafka & Zookeeper configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 📊 Dashboard Features

Once running, the dashboard provides:

- **Overview** — System metrics, active vehicles, alerts count
- **Vehicle Telemetry** — Real-time sensor data for each vehicle
- **Predictive Maintenance** — AI-driven maintenance recommendations
- **Customer Scheduling** — Automated service appointment suggestions
- **Manufacturing Insights** — Component failure analysis
- **UEBA Security** — Agent behavior monitoring

---

## 🛠️ Built With

| Technology | Purpose |
|------------|---------|
| [Apache Kafka](https://kafka.apache.org/) | Distributed event streaming platform |
| [Streamlit](https://streamlit.io/) | Interactive data visualization dashboard |
| [Docker](https://www.docker.com/) | Containerization and orchestration |
| [Python 3.9+](https://www.python.org/) | Core programming language |
| [Pandas](https://pandas.pydata.org/) | Data manipulation and analysis |
| [Plotly](https://plotly.com/) | Interactive charts and graphs |

---

## 📝 License

This project is open source and available under the MIT License.

---

## 👤 Author

**Surbhi Kanwar**
- GitHub: [@Surbhikanwar](https://github.com/Surbhikanwar)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Surbhikanwar/kafka_implementation/issues).

