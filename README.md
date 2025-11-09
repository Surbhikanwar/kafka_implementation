# Real-Time Vehicle Data Analysis with Kafka and Streamlit

This project is a real-time data processing pipeline that simulates, ingests, analyzes, and visualizes vehicle data using Apache Kafka and Streamlit.

## Features

- **Real-time Data Ingestion:** Produces mock vehicle data and sends it to a Kafka topic.
- **Data Analysis:** Consumes data from Kafka, applies rules to it, and identifies anomalies.
- **Interactive Dashboard:** A Streamlit-based dashboard to visualize the real-time data and analysis results.
- **Dockerized Services:** Kafka and Zookeeper are managed using Docker Compose for easy setup.

## Architecture

The project follows a microservices-based architecture:

- **Data Ingestion:** A Python script (`vehicle_producer.py`) generates mock vehicle data and sends it to a Kafka topic.
- **Data Analysis:** A separate Python script (`analysis_agent.py`) consumes the data from the Kafka topic, processes it using a rules engine, and sends the results to another Kafka topic.
- **Dashboard:** A Streamlit application (`dashboard_app.py`) consumes the processed data from the results topic and displays it in a real-time dashboard.
- **Message Bus:** Apache Kafka is used as the message bus for communication between the services.
- **Orchestration:** A master agent is responsible for orchestrating the different agents in the system.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Docker and Docker Compose
- Python 3.9+

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/kafka_implementation.git
    cd kafka_implementation
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Start the Kafka and Zookeeper services:**

    ```bash
    docker-compose up -d
    ```

### Running the Application

1.  **Start the data ingestion service:**

    ```bash
    python -m data_ingestion.vehicle_producer
    ```

2.  **Start the data analysis service:**

    ```bash
    python -m data_analysis.analysis_agent
    ```

3.  **Start the dashboard:**

    ```bash
    streamlit run dashboard/dashboard_app.py
    ```

## Project Structure

```
.
├── data_ingestion
│   ├── vehicle_producer.py   # Produces mock vehicle data to Kafka
│   └── ...
├── data_analysis
│   ├── analysis_agent.py     # Consumes and analyzes vehicle data
│   └── rules_engine.py       # Defines rules for data analysis
├── dashboard
│   ├── dashboard_app.py      # Streamlit dashboard application
│   └── ...
├── master_agent
│   └── orchestrator.py       # Orchestrates the different agents
├── docker-compose.yml        # Docker Compose file for Kafka and Zookeeper
├── requirements.txt          # Python dependencies
└── README.md
```

## Usage

Once the application is running, you can:

-   **View the real-time data:** Open the Streamlit dashboard in your browser to see the vehicle data being processed and visualized in real-time.
-   **Extend the analysis:** Modify the `rules_engine.py` to add your own custom rules for data analysis.
-   **Customize the dashboard:** Edit the `dashboard_app.py` to change the layout and visualizations of the dashboard.

## Built With

-   [Apache Kafka](https://kafka.apache.org/) - Distributed streaming platform
-   [Streamlit](https://streamlit.io/) - The fastest way to build data apps in Python
-   [Docker](https://www.docker.com/) - Containerization platform
-   [Python](https://www.python.org/) - Programming language
-   [Pandas](https://pandas.pydata.org/) - Data manipulation and analysis library
-   [Numpy](https://numpy.org/) - Library for numerical computing

