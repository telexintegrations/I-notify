import subprocess
import time
import os
import psycopg2
import httpx

from dotenv import load_dotenv
# 🔹 Load environment variables
load_dotenv()

# 🔹 Configuration
WATCHED_FOLDER = os.getenv("WATCHED_FOLDER", "/home/ubuntu/test_directory")
TELEX_WEBHOOK_URL = os.getenv("TELEX_WEBHOOK_URL", "http://127.0.0.1:5000/telex-webhook")

# 🔹 PostgreSQL Configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "file_monitor"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "yourpassword"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

# 🔹 Store last processed event ID (prevents duplicate alerts)
last_event_id = None



def setup_database():
    """Creates the necessary table in PostgreSQL if it doesn't exist."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_deletions (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT NOT NULL,
                deleted_by TEXT NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database setup complete.")
    except Exception as e:
        print(f"❌ Database setup error: {e}")

def setup_auditd_rule():
    """Adds an auditd rule to monitor only file deletions."""
    try:
        rule_check = subprocess.run(["auditctl", "-l"], capture_output=True, text=True)
        if WATCHED_FOLDER in rule_check.stdout:
            print(f"✅ Audit rule already exists for {WATCHED_FOLDER}")
        else:
            subprocess.run(["auditctl", "-w", WATCHED_FOLDER, "-p", "wa", "-k", "file_delete"], check=True)
            print(f"🚀 Added auditd rule to monitor {WATCHED_FOLDER}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set up auditd rule: {e}")

def get_latest_deletion_log():
    """Fetches the most recent file deletion log from auditd."""
    try:
        result = subprocess.run(["ausearch", "-k", "file_delete", "--start", "recent"], capture_output=True, text=True)
        logs = result.stdout.strip()
        if "no matches" in logs.lower():
            return None
        return logs
    except Exception as e:
        print(f"❌ Error fetching deletion logs: {e}")
        return None

def extract_deletion_info(logs):
    """Extracts details of the last deletion event and ensures it's new."""
    global last_event_id
    if not logs:
        return None

    lines = logs.split("\n")
    event_id = None
    filepath = None
    user_id = None

    for line in reversed(lines):  # Start from the latest entry
        if "type=DELETE" in line:
            try:
                event_id = line.split("msg=audit(")[-1].split(")")[0]

                # 🔹 Avoid duplicate alerts
                if event_id == last_event_id:
                    return None

                last_event_id = event_id

                # 🔹 Extract file path
                if "name=" in line:
                    filepath = line.split("name=")[-1].split(" ")[0].strip('"')

                # 🔹 Extract user ID and convert to username
                if "uid=" in line:
                    user_id = line.split("uid=")[1].split(" ")[0].strip()
                    user = subprocess.run(["id", "-un", user_id], capture_output=True, text=True).stdout.strip()
                else:
                    user = "Unknown"

                if filepath:
                    log_to_db(filepath, user)  # 🔹 Save to database
                    send_to_telex(filepath, user)  # 🔹 Send Alert
                    print(f"✅ Logged to database: {filepath} by {user}")
                    return

            except Exception as e:
                print(f"⚠ Error extracting deletion info: {e}")
                return None

    return None

def log_to_db(file_path, deleted_by):
    """Logs deletion events to PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO file_deletions (file_path, deleted_by) VALUES (%s, %s)",
            (file_path, deleted_by)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database logging error: {e}")

def send_to_telex(file_path, user):
    """Sends a deletion alert to Telex."""
    try:
        payload = {
            "message": f"🚨 File Deleted! \n📂 Path: {file_path} \n👤 User: {user}",
            "event_name": "❌ DELETE ALERT",
            "status": "success",
            "username": "I-notify"
        }
        response = httpx.post(TELEX_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("✅ Telex alert sent!")
    except httpx.HTTPError as e:
        print(f"❌ Failed to send to Telex: {e}")

def monitor_deletions():
    """Monitors file deletions and logs them to the database."""
    print("🔍 Monitoring file deletions started...")
    setup_database()
    setup_auditd_rule()

    while True:
        logs = get_latest_deletion_log()
        extract_deletion_info(logs)
        time.sleep(5)

# 📌 Start monitoring in a separate process
#import threading
#threading.Thread(target=monitor_deletions, daemon=True).start()

if __name__== "__main__":
    monitor_deletions()
