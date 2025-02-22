import os
from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
import psycopg2
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from typing import List

app = FastAPI()
load_dotenv()

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        allow_credentials=True,
    )
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "file_monitor"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "yourpassword"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}



class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str

class LogPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]

@app.get("/integration.json")
def get_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {        
            "data": {
                "date": {
                "created_at": "2025-02-22",
                "updated_at": "2025-02-22"
                },
                "descriptions": {
                "app_name": "DELETE MONITOR",
                "app_description": "https://github.com/telexintegrations/I-notify/\n Auditd Setup – The app configures auditd to track deletions in the specified folder.\n    Real-Time Log Analysis – It continuously reads logs from ausearch --raw to detect file deletions.\n    User Attribution – Extracts the user ID from the logs and resolves it to a username.\n    Telex Notification – When a valid deletion is detected, the app sends an alert with the file path and username to a configured Telex webhook.",
                "app_logo": "https://www.pngegg.com/en/png-biocr",
                "app_url": f"{base_url}",
                "background_color": "#fff"
                },
                "is_active": True,
                "integration_type": "interval",
                "integration_category": "Monitoring & Logging",
                "key_features": [
                "\"Monitors a specified directory on a server\"",
                "\"Sends alert to a specified telex channel on any delete event in the directory\"",
                "\"Sends the user who did the event and root if through sudo\""
                ],
                "author": "John Tolulope Afariogun",
                "settings": [
                {
                    "label": "interval",
                    "type": "text",
                    "required": True,
                    "default": "59 23 * * *"
                },
                {
                    "label": "site",
                    "type": "text",
                    "required": True,
                    "default": f"{base_url}/logs"
                }
                ],
                "target_url": f"{base_url}",
                "tick_url": f"{base_url}/tick"
            }
    }



async def fetch_logs(site) -> List[dict]:
    """Fetch logs from the /logs endpoint."""
    today_date = datetime.today().strftime("%Y-%m-%d")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{site}/{today_date}", timeout=15)  # Adjust URL if necessary
            if response.status_code < 400:
                return response.json().get("logs", [])
            return f"{site} is down (status {response.status_code})"
    except Exception as e:
        return [{"error": f"Failed to fetch logs: {str(e)}"}]


def send_to_telex(message, TELEX_WEBHOOK_URL):
    """Sends a deletion alert to Telex."""
    try:
        payload = {
            "message": message,
            "event_name": "❌ DELETE LOGS",
            "status": "success" if message else "error",
            "username": "DELETE LOGGER"
        }
        response = httpx.post(TELEX_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except httpx.HTTPError as e:
        return str(e)


async def send_logs_task(payload: LogPayload):
    """Fetch logs and send them to the return URL."""
    sites = [s.default for s in payload.settings if s.label.startswith("site")]
    logs = await asyncio.gather(*(fetch_logs(site) for site in sites))
    send_to_telex(str(logs), payload.return_url)

@app.post("/tick", status_code=202)
def trigger_log_sending(payload: LogPayload, background_tasks: BackgroundTasks):
    """Triggers the log sending process asynchronously."""
    background_tasks.add_task(send_logs_task, payload)
    return {"status": "accepted"}


# 📌 FastAPI Endpoints
@app.get("/")
def root():
    return {"message": "File Monitor API is running!"}

@app.get("/logs")
def get_all_logs():
    """Retrieve all file deletion logs."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, file_path, deleted_by FROM file_deletions ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"logs": [{"id": log[0], "timestamp": log[1], "file_path": log[2], "deleted_by": log[3]} for log in logs]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/logs/{date}")
def get_logs_by_date(date: str):
    """Retrieve logs for a specific day (YYYY-MM-DD)."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, file_path, deleted_by FROM file_deletions WHERE DATE(timestamp) = %s ORDER BY timestamp DESC", (date,))
        logs = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"logs": [{"id": log[0], "timestamp": log[1], "file_path": log[2], "deleted_by": log[3]} for log in logs]}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
