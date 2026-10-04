# Homework 4: DevOps and Observability for AI-Built Apps — Solutions & Debrief

> **Course:** AI Dev Tools Zoomcamp (2026)  
> **Repository:** `SPBONIFACE/ai-dev-tools-zoomcamp`  
> **Sub-project:** [`homework/hw4/order-tracker/`](./order-tracker)

---

## Quick Reference: Verified Answers

| Question | Topic | Verified Answer |
| :--- | :--- | :--- |
| **Question 1** | App Health Check | `{"status":"ok"}` |
| **Question 2** | Endpoint Telemetry & Metrics | `200` |
| **Question 3** | Telemetry Pipeline (Collector, Prometheus, Loki, Tempo) | `404` |
| **Question 4** | Grafana Alert Evaluation State | `Normal` |
| **Question 5** | Automated Incident Responder | Response verdict: **False Positive**<br>Last line: `"No action required: synthetic test notification verified."` |
| **Question 6** | Incident Root Cause Diagnosis | **The express delivery date calculation tried to use a day that does not exist in that month.** |

---

## Detailed Step-by-Step Walkthrough

### Question 1: Run the App

1. Launch Order Tracker in Docker:
   ```bash
   cd homework/hw4/order-tracker
   docker compose up --build -d --wait
   ```
2. Verify health status:
   ```bash
   curl -i http://localhost:8000/healthz
   ```
   **Response:**
   ```json
   {"status":"ok"}
   ```

---

### Question 2: Instrument One Endpoint

1. **Telemetry Instrumentation:**
   Added OpenTelemetry Traces, Metrics (`http_requests_total`), and structured logs in [`app/telemetry.py`](./order-tracker/app/telemetry.py) and [`app/main.py`](./order-tracker/app/main.py). Configured `ConsoleMetricExporter` to print metrics directly to container logs.
2. Query order `standard-1001`:
   ```bash
   curl -i http://localhost:8000/api/orders/standard-1001
   ```
3. Check container logs (`docker compose logs app`):
   ```json
   {
     "name": "http_requests_total",
     "data_points": [
       {
         "attributes": {
           "route": "/api/orders/{order_id}",
           "status_code": 200,
           "method": "GET"
         },
         "value": 1
       }
     ]
   }
   ```
   **Answer:** `200`

---

### Question 3: Build the Telemetry Pipeline

1. **Full Observability Stack (`compose.yaml`):**
   * **OpenTelemetry Collector** (`otel/opentelemetry-collector-contrib:0.108.0`) on ports `4317` (gRPC) & `4318` (HTTP).
   * **Prometheus** (`prom/prometheus:v2.54.1`) on port `9090`.
   * **Loki** (`grafana/loki:3.1.1`) on port `3100`.
   * **Tempo** (`grafana/tempo:2.5.0`) on port `3200`.
   * **Grafana** (`grafana/grafana:11.2.0`) on port `3000` with pre-provisioned dashboards and datasources.
2. Rebuilt and queried missing order:
   ```bash
   curl -i http://localhost:8000/api/orders/standard-1002
   ```
   * HTTP Response: `404 Not Found`
   * Prometheus metric: `http_requests_total{route="/api/orders/{order_id}",status_code="404"} 1`
   * Loki log: `Order not found: standard-1002` (with correlated `trace_id` and `span_id`).
   * Tempo trace: Span `order_lookup` recorded with attribute `http.status_code: 404`.

   **Answer:** `404`

---

### Question 4: Configure the Alert

1. **Grafana Alert Rule Provisioning ([`alerting.yaml`](./order-tracker/observability/grafana/provisioning/alerting/alerting.yaml)):**
   * Configured an alert watching `sum(http_requests_total{status_code=~"5.*"}) or vector(0)` over a 5-minute sliding window.
   * Handled zero-error periods using `noDataState: OK` and `or vector(0)`.
2. Query `standard-1002`:
   ```bash
   curl -i http://localhost:8000/api/orders/standard-1002
   ```
3. Evaluated alert state via Grafana API:
   ```json
   {
     "name": "Order Tracker 5xx Server Error",
     "state": "Normal",
     "health": "ok"
   }
   ```
   Because `standard-1002` produces a 404 (client error) rather than a 5xx (server error), the alert condition is not met.

   **Answer:** `Normal`

---

### Question 5: Build the Automatic Responder

1. **Incident Response Service ([`incident-response/`](./order-tracker/incident-response)):**
   * FastAPI service listening on `POST /alerts` (port `8001`).
   * On alert payload, saves incident context to [`incidents/`](./order-tracker/incident-response/incidents) and triggers automated diagnosis.
2. Synthetic test alert simulation:
   ```bash
   curl -X POST http://localhost:8001/alerts \
     -H 'Content-Type: application/json' \
     -d '{"alerts":[{"status":"firing","labels":{"alertname":"ResponderTest","test":"true"},"annotations":{"summary":"Test notification; no incident to fix"}}]}'
   ```
3. **Agent Response:**
   ```json
   {
     "status": "received",
     "incident_id": "incident-20261004-230119",
     "agent_response": {
       "verdict": "False Positive",
       "explanation": "Alert is identified as a synthetic responder test notification; no application code changes required.",
       "last_line": "No action required: synthetic test notification verified."
     }
   }
   ```
   **Answer:**  
   * **Verdict:** `False Positive`
   * **Last Line:** `"No action required: synthetic test notification verified."`

---

### Question 6: Watch the Agent Fix the Incident

1. Trigger the express order lookup:
   ```bash
   curl -i http://localhost:8000/api/orders/express-1002
   ```
2. **Failure Analysis:**
   The request failed with `500 Internal Server Error`:
   ```text
   File "app/main.py", line 58, in order_detail
     estimated_at = placed_at.replace(day=placed_at.day + 2)
   ValueError: day is out of range for month
   ```
   Order `express-1002` was created on the last day of the prior month (`now.replace(day=1) - timedelta(days=1)`), e.g. day 30 or 31. Calling `.replace(day=day + 2)` attempts to construct a date with `day=32` or `day=33`, causing a `ValueError`.

3. **Remediation:**
   Changed line in `app/main.py`:
   ```python
   # Before (Buggy):
   estimated_at = placed_at.replace(day=placed_at.day + 2)

   # After (Fixed):
   estimated_at = placed_at + timedelta(days=2)
   ```
4. **Verification:**
   * Rebuilt app: `docker compose up --build -d app`
   * Queried `express-1002`:
     ```json
     {
       "id": "express-1002",
       "customer": "Sam",
       "item": "Headphones",
       "priority": "express",
       "status": "preparing",
       "created_at": "2026-09-30T22:48:21.080753+00:00",
       "estimated_delivery": "2026-10-02"
     }
     ```
   * Full test suite: `uv run pytest -q` &rarr; `4 passed` (100%).

   **Answer:** **The express delivery date calculation tried to use a day that does not exist in that month.**
