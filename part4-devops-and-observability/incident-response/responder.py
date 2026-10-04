import json
import logging
from typing import Any, Dict
from fastapi import FastAPI, BackgroundTasks, Request, status
from fastapi.responses import JSONResponse
from agent_runner import investigate_and_respond, INCIDENTS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("responder_api")

app = FastAPI(
    title="Automated AI On-Call Incident Responder",
    description="Webhook listener receiving Grafana/OTel alerts and launching headless AI agent investigations",
    version="1.0.0",
)

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "incident-responder"}

@app.post("/alerts", status_code=status.HTTP_202_ACCEPTED)
async def receive_alerts(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse incoming alert JSON: {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Invalid JSON"})
    
    logger.info(f"Received alert notification: {json.dumps(body)[:250]}...")
    
    # Run the investigation
    record = investigate_and_respond(body)
    
    return {
        "status": "received",
        "incident_id": record.get("incident_id"),
        "agent_response": record.get("agent_response"),
    }

@app.get("/incidents")
def list_incidents():
    incidents = []
    for f in sorted(INCIDENTS_DIR.glob("*.json"), reverse=True):
        try:
            with open(f, "r") as fp:
                incidents.append(json.load(fp))
        except Exception:
            pass
    return {"incidents": incidents}

@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    target = INCIDENTS_DIR / f"{incident_id}.json"
    if not target.exists():
        return JSONResponse(status_code=404, content={"detail": "Incident not found"})
    with open(target, "r") as fp:
        return json.load(fp)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
