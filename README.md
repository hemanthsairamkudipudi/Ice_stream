Ah, I understand. 👍 You want the **entire README in one proper Markdown code block** so you can click **Copy** once and paste it directly into `README.md`.

Here it is:

```markdown
# IceStream: Real-Time Lakehouse Observability

> A production-style real-time data quality and observability platform for streaming e-commerce checkout telemetry.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-4.0-black)
![Apache Flink](https://img.shields.io/badge/Apache%20Flink-2.2-orange)
![Apache Iceberg](https://img.shields.io/badge/Apache%20Iceberg-1.12-blue)
![React](https://img.shields.io/badge/React-Vite-61DAFB)
![Tests](https://img.shields.io/badge/Tests-58%20Passed-success)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

---

## 1. Project Overview

IceStream is a real-time lakehouse observability platform designed to detect, contain, and monitor data-quality problems in streaming e-commerce checkout telemetry.

Traditional batch-oriented data pipelines may allow bad data to remain undetected until dashboards, reports, or downstream analytical systems are affected.

IceStream introduces continuous data-quality monitoring into the streaming lakehouse pipeline.

The system follows this flow:

```text
Checkout Events
      |
      v
Apache Kafka
      |
      v
Apache Flink
      |
      v
Apache Iceberg
      |
      v
Data Quality Engine
      |
      +----------------------+
      |                      |
   Valid Data             Invalid Data
      |                      |
      v                      v
 Continue              Circuit Breaker
                             |
                             v
                       Quarantine / DLQ
                             |
                             v
                       Incident Logging
                             |
                             v
                       Observability
                         Dashboard
```

The platform is designed around the principle:

> Detect bad data early, prevent it from propagating downstream, quarantine affected records, record the incident, and support controlled recovery.

---

## 2. Problem Statement

Modern e-commerce platforms generate large volumes of real-time checkout telemetry.

Examples include:

- Order information
- Customer information
- Product information
- Transaction amounts
- Tax amounts
- Payment status
- Event timestamps

When bad data enters a traditional batch pipeline, the problem may not be detected until much later.

Examples of data-quality problems include:

- Negative transaction amounts
- NULL values
- Invalid values
- Schema changes
- Duplicate records
- Unexpected distributions

These problems can affect:

- Business dashboards
- Analytics
- Machine learning pipelines
- Financial calculations
- Operational decision-making

IceStream addresses this problem by introducing real-time quality monitoring and automated containment.

---

## 3. Objectives

The main objectives of IceStream are:

1. Ingest real-time checkout events.
2. Process streaming data using Apache Kafka and Apache Flink.
3. Store streaming data in Apache Iceberg.
4. Continuously validate incoming data.
5. Detect data-quality violations.
6. Calculate the error rate of a batch.
7. Open a circuit when the error rate exceeds the configured threshold.
8. Quarantine invalid records.
9. Maintain an incident log.
10. Provide incident history through an API.
11. Support a controlled recovery workflow.
12. Provide a real-time observability dashboard.
13. Validate the system through automated tests.

---

## 4. System Architecture

```text
                     +----------------------+
                     |  Checkout Generator  |
                     +----------+-----------+
                                |
                                v
                     +----------------------+
                     |    Apache Kafka      |
                     |   checkout-topic     |
                     +----------+-----------+
                                |
                                v
                     +----------------------+
                     |    Apache Flink      |
                     | Streaming Processing |
                     +----------+-----------+
                                |
                                v
                     +----------------------+
                     |    Apache Iceberg    |
                     |    Lakehouse Table   |
                     +----------+-----------+
                                |
                                v
                     +----------------------+
                     |  Data Quality Engine |
                     +----------+-----------+
                                |
                   +------------+------------+
                   |                         |
                Valid                     Invalid
                   |                         |
                   v                         v
             Continue               +----------------+
                                    | Circuit Breaker|
                                    +-------+--------+
                                            |
                                            v
                                    +----------------+
                                    |   Iceberg DLQ  |
                                    |   Quarantine   |
                                    +-------+--------+
                                            |
                                            v
                                    +----------------+
                                    |  Incident Log  |
                                    +-------+--------+
                                            |
                                            v
                                    +----------------+
                                    | React Dashboard|
                                    +----------------+
```

---

## 5. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data generation, quality engine, remediation, API |
| Apache Kafka | Real-time event streaming |
| Apache Flink | Stream processing |
| Apache Iceberg | Lakehouse table format |
| RustFS | S3-compatible object storage |
| Iceberg REST Catalog | Iceberg catalog management |
| PyIceberg | Python access to Iceberg |
| PyArrow | Data processing and Iceberg interaction |
| FastAPI | Backend API |
| React | Observability dashboard |
| React Flow | Pipeline lineage visualization |
| Vite | Dashboard development/build |
| Docker | Infrastructure and service deployment |
| Docker Compose | Local service orchestration |
| Pytest | Automated testing |

---

## 6. Project Structure

```text
Ice_stream/
│
├── generator/
│   ├── __init__.py
│   ├── checkout_generator.py
│   └── config.py
│
├── quality/
│   ├── __init__.py
│   ├── config.py
│   ├── engine.py
│   ├── iceberg_reader.py
│   ├── rules.py
│   └── run_quality_check.py
│
├── remediation/
│   ├── __init__.py
│   ├── config.py
│   ├── circuit_breaker.py
│   ├── dlq.py
│   ├── iceberg_dlq.py
│   ├── incident_log.py
│   └── remediation_service.py
│
├── integration/
│   └── run_remediation_integration.py
│
├── api/
│   ├── __init__.py
│   ├── app.py
│   └── status.py
│
├── flink/
│
├── iceberg/
│
├── dashboard/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── ...
│
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose-flink-iceberg.yml
│   └── flink-iceberg/
│       └── Dockerfile
│
├── tests/
│   ├── test_generator.py
│   ├── test_kafka.py
│   ├── test_quality.py
│   ├── test_circuit_breaker.py
│   ├── test_dlq.py
│   ├── test_remediation_service.py
│   ├── test_iceberg_dlq.py
│   ├── test_status.py
│   ├── test_iceberg_concurrency.py
│   ├── test_iceberg_time_travel.py
│   ├── test_incident_log.py
│   └── test_api.py
│
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 7. Data Flow

### Step 1 — Event Generation

The checkout generator creates checkout telemetry containing fields such as:

```text
order_id
customer_id
product_id
amount
tax_amount
payment_status
timestamp
```

The generator can produce normal records as well as records containing invalid values for testing the quality-monitoring pipeline.

### Step 2 — Kafka Ingestion

Checkout events are published to:

```text
checkout-topic
```

The default external Kafka bootstrap server is:

```text
localhost:9092
```

The project uses:

```text
3 Kafka partitions
```

---

## 8. Flink Streaming Layer

Apache Flink acts as the streaming-processing layer between Kafka and the Iceberg lakehouse.

The Flink pipeline consumes checkout events from Kafka and processes them before writing them into the Iceberg table.

The project includes a Docker-based Flink environment containing:

- Flink JobManager
- Flink TaskManager
- Kafka connector
- Iceberg runtime
- Required Hadoop/S3 dependencies

---

## 9. Apache Iceberg Lakehouse

IceStream stores checkout events in an Apache Iceberg table.

The target table is:

```text
checkout.checkout_events
```

The schema includes:

```text
order_id          STRING
customer_id       STRING
product_id        STRING
amount            DOUBLE
tax_amount        DOUBLE
payment_status    STRING
event_timestamp   TIMESTAMP_LTZ
```

Iceberg provides table-level features useful for the project, including:

- Snapshot-based storage
- Historical reads
- Concurrent commits
- Atomic table updates
- Time travel

---

## 10. Data Quality Engine

The Data Quality Engine validates individual records and reports validation errors.

One implemented validation rule is:

```text
amount must be >= 0
```

For example:

```text
amount = -100
```

produces:

```text
amount must be >= 0
```

The engine produces an error mapping:

```text
record index -> list of validation errors
```

This allows the remediation service to identify exactly which records failed validation.

---

## 11. Circuit Breaker

IceStream uses a circuit breaker to prevent large-scale propagation of bad data.

The configured error-rate threshold is:

```text
2%
```

The circuit has three states:

```text
CLOSED
OPEN
HALF_OPEN
```

### CLOSED

The pipeline is operating normally.

```text
Error Rate <= 2%
```

### OPEN

When the error rate exceeds the threshold:

```text
Error Rate > 2%
```

the circuit opens.

Invalid records are sent to quarantine/DLQ and an incident is recorded.

### HALF_OPEN

During recovery, the system moves into:

```text
HALF_OPEN
```

to evaluate whether the corrected data can safely return to normal processing.

### CLOSED

If recovery succeeds:

```text
HALF_OPEN → CLOSED
```

The incident is resolved.

---

## 12. Dead Letter Queue / Quarantine

Invalid records are quarantined instead of continuing through the normal pipeline.

The project supports an Iceberg-backed DLQ.

The quarantine process stores:

- Original record
- Validation errors
- Record status
- Order ID

Duplicate quarantine is avoided for existing order IDs in the Iceberg DLQ.

---

## 13. Incident Management

When the circuit opens, IceStream creates an incident.

An incident contains:

```text
Incident ID
Detection time
Resolution time
State
Total records
Failed records
Error rate
Threshold
Quarantined records
Failure reasons
Action
```

Example:

```text
State:
OPEN

Error Rate:
3.45%

Threshold:
2.0%

Action:
CIRCUIT_OPENED + QUARANTINE
```

The system also prevents repeated creation of the same active incident during repeated status checks.

---

## 14. Incident History API

The FastAPI backend exposes incident history through:

```text
GET /api/v1/incidents
```

The endpoint returns recent incidents for display in the observability dashboard.

The API also exposes:

```text
GET /health
```

and:

```text
GET /api/v1/remediation/status
```

The remediation status endpoint reports:

- Circuit state
- Error rate
- Total records
- Failed records
- Quarantined records
- Incident information

---

## 15. Recovery Workflow

The recovery workflow follows:

```text
                 +--------+
                 | CLOSED |
                 +---+----+
                     |
              Error rate > threshold
                     |
                     v
                 +--------+
                 |  OPEN  |
                 +---+----+
                     |
                Begin recovery
                     |
                     v
                +---------+
                |HALF_OPEN|
                +----+----+
                     |
             Recovery successful
                     |
                     v
                 +--------+
                 | CLOSED |
                 +--------+
```

A successful recovery also resolves the associated incident.

### Recovery validation

The project successfully validated:

```text
OPEN
  ↓
HALF_OPEN
  ↓
CLOSED
```

The recovery test uses corrected in-memory validation results.

The actual Iceberg source table is not modified during this controlled recovery simulation.

---

## 16. Observability Dashboard

The frontend is implemented using:

- React
- Vite
- React Flow

The dashboard provides the following pipeline lineage:

```text
Checkout Generator
        ↓
      Kafka
        ↓
      Flink
        ↓
     Iceberg
        ↓
  Data Quality
        ↓
 Observability
```

The dashboard provides:

### Live Status

```text
Kafka       LIVE
Flink       LIVE
Iceberg     LIVE
```

### Data Quality

Example:

```text
1 failed / 33
3.0% ERROR
```

### Remediation Circuit

Example:

```text
OPEN
```

### Incident Log

Displays:

- Incident ID
- Detection time
- Failed records
- Error rate
- Threshold
- Quarantined records
- Action
- Failure reason

### Incident History

Recent incidents are displayed with their state:

```text
OPEN
CLOSED
```

---

## 17. Running the Project

### Prerequisites

Install:

- Python 3.13
- Node.js LTS
- Docker Desktop
- Git

Verify:

```powershell
python --version
node --version
npm --version
docker --version
docker compose version
git --version
```

---

## 18. Clone the Repository

```powershell
git clone https://github.com/hemanthsairamkudipudi/Ice_stream.git
cd Ice_stream
```

Switch to the main branch:

```powershell
git checkout main
git pull origin main
```

---

## 19. Python Environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## 20. Start Kafka

From the project root:

```powershell
docker compose -f docker/docker-compose.yml up -d
```

Check:

```powershell
docker ps
```

Kafka should be running as:

```text
icestream-kafka
```

---

## 21. Start Flink + Iceberg

Run:

```powershell
docker compose -f docker/docker-compose-flink-iceberg.yml up -d
```

Check:

```powershell
docker ps
```

The environment includes services such as:

```text
icestream-flink-jobmanager
icestream-flink-taskmanager
icestream-iceberg-rest
icestream-rustfs
```

---

## 22. Start the Backend API

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn api.app:app --reload --port 8000
```

API:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

## 23. Start the Dashboard

Open another terminal:

```powershell
cd dashboard
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

## 24. Running Tests

From the project root with the virtual environment activated:

```powershell
pytest -q
```

Current validated result:

```text
58 passed
```

The test suite covers:

- Generator
- Kafka
- Data quality
- Circuit breaker
- DLQ
- Remediation service
- Iceberg DLQ
- API status
- API endpoints
- Incident logging
- Iceberg concurrency
- Iceberg time travel

---

## 25. Iceberg Concurrency Testing

The project includes a concurrency test where two independent writers attempt to append records.

The test verifies that both records are successfully committed.

During validation, Iceberg detected a concurrent commit and retried the operation.

This demonstrates the project's use of Iceberg's concurrent commit handling.

---

## 26. Iceberg Time Travel

The project also validates reading a historical Iceberg snapshot.

The time-travel test also validates behavior when an invalid snapshot ID is supplied.

---

## 27. Integration Test

The remediation integration workflow can be executed with:

```powershell
python -m integration.run_remediation_integration
```

The workflow:

1. Reads records from Iceberg.
2. Validates every record.
3. Detects quality failures.
4. Runs the remediation service.
5. Evaluates the circuit breaker.
6. Displays incident information.
7. Performs the controlled recovery simulation.
8. Verifies recovery.
9. Verifies incident resolution.
10. Displays DLQ information.

Example validated result:

```text
Records read from Iceberg: 29

Failed records: 1
Error rate: 3.45%
Circuit state: OPEN
```

Recovery:

```text
Recovery success: True
Circuit state: CLOSED

Recovery verification: PASSED
```

Incident resolution:

```text
Incident resolution verification: PASSED
No unresolved active incident remains.
```

---

## 28. Environment Configuration

Configuration values should be provided through environment variables where applicable.

Use:

```text
.env.example
```

as the configuration template.

Do not commit passwords, access keys, or other secrets to Git.

---

## 29. Team Development Workflow

The project uses Git branches for team development.

Recommended workflow:

```text
main
 |
 +---- feature branch
 |
 +---- feature branch
 |
 +---- feature branch
```

Create a feature branch:

```powershell
git checkout main
git pull origin main
git checkout -b feature-name
```

After making changes:

```powershell
git add .
git commit -m "describe the change"
git push origin feature-name
```

Create a Pull Request:

```text
feature-name → main
```

After review and testing, merge the Pull Request into `main`.

---

## 30. Project Validation

The final project has been validated through:

```text
+----------------------------------+
| Final Validation                 |
+----------------------------------+
| Automated Tests      58 / 58     |
| Dashboard Build      PASS        |
| Kafka Integration    PASS        |
| Flink Integration    PASS        |
| Iceberg Integration  PASS        |
| Quality Engine       PASS        |
| Circuit Breaker      PASS        |
| DLQ                  PASS        |
| Incident Logging     PASS        |
| API                  PASS        |
| Recovery Workflow    PASS        |
| Time Travel          PASS        |
| Concurrency Test     PASS        |
+----------------------------------+
```

---

## 31. Key Demonstration Scenario

The recommended project demonstration is:

### Step 1

Generate or ingest checkout events.

### Step 2

Events enter Kafka.

### Step 3

Flink processes the stream.

### Step 4

Events are written to Iceberg.

### Step 5

The Data Quality Engine detects an invalid record.

Example:

```text
amount = -100
```

### Step 6

The error rate exceeds the configured threshold.

```text
Error Rate > 2%
```

### Step 7

The circuit breaker opens.

```text
CLOSED → OPEN
```

### Step 8

The invalid record is quarantined.

### Step 9

An incident is created.

### Step 10

The data is corrected.

### Step 11

Recovery is attempted.

```text
OPEN → HALF_OPEN → CLOSED
```

### Step 12

The incident is resolved.

This demonstrates the complete IceStream observability and remediation lifecycle.

---

## 32. Project Results

IceStream demonstrates a working prototype of real-time lakehouse observability with:

- Real-time Kafka ingestion
- Flink stream processing
- Apache Iceberg lakehouse storage
- Automated data-quality validation
- Error-rate-based circuit breaking
- Invalid-record quarantine
- Iceberg-backed DLQ
- Incident logging
- Incident history
- Recovery workflow
- REST API
- React observability dashboard
- Automated testing
- Iceberg concurrency validation
- Iceberg time-travel validation

The final automated test suite contains:

```text
58 / 58 tests passed
```

---

## 33. Limitations

IceStream is a production-style prototype rather than a fully deployed production platform.

Current limitations include:

1. The recovery demonstration uses corrected in-memory validation results rather than modifying the original Iceberg record.
2. The current environment is designed for local Docker-based execution.
3. The dashboard currently uses local API endpoints.
4. Authentication and authorization are outside the current prototype scope.
5. Advanced schema-drift and statistical anomaly detection can be extended in future versions.
6. Production-scale multi-node deployment would require additional infrastructure configuration.

---

## 34. Future Scope

Potential future improvements include:

- Advanced schema-drift detection
- Statistical anomaly detection
- Machine-learning-based anomaly detection
- Automatic source-data re-fetch
- Fully automated data repair
- Production Kubernetes deployment
- Prometheus metrics
- Grafana dashboards
- Alerting through email/Slack
- Authentication and role-based access
- Multi-stream monitoring
- Cloud object storage deployment
- Automated incident notification
- More advanced data-quality rules
- Distributed production deployment
- Historical quality trend analysis

---

## 35. Team

**IceStream — Real-Time Lakehouse Observability**

Team members:

1. **SURU SRIRAM**
2. **POORNA SAI LALAM**
3. **KUDUPUDI HEMA DURGA SAI RAM**
4. **SNEHA MAHESH DIXIT**

---

## 36. Conclusion

IceStream demonstrates how real-time streaming, lakehouse storage, automated data-quality validation, circuit breaking, quarantine, incident management, and observability can be combined into a single data-reliability platform.

Instead of waiting for downstream dashboards or reports to reveal a data problem, IceStream detects the problem close to the point where it occurs and provides an automated containment and recovery workflow.

```text
Detect
  ↓
Validate
  ↓
Contain
  ↓
Quarantine
  ↓
Record Incident
  ↓
Recover
  ↓
Resume
```

**IceStream — Real-Time Lakehouse Observability**

> Detect bad data before it breaks downstream analytics.
```

### Easiest way to copy it

Look at the **top-right corner of the large Markdown block** above. There should be a **Copy** button.

Click **Copy**, then:

1. Open `README.md` in VS Code.
2. Press **Ctrl + A**.
3. Press **Ctrl + V**.
4. Press **Ctrl + S**.
5. Press **Ctrl + Shift + V** to preview it.

Then you can commit it:

```powershell
git add README.md
git commit -m "docs: update IceStream README"
git push origin main
```

