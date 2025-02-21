import subprocess
import httpx
import time
import os

# Configure the folder to watch and Slack webhook
WATCHED_FOLDER = "/home/john/Documents/test_directory"  # 🔹 Change this to your target folder
SLACK_WEBHOOK_URL = "http://localhost:5000/slack-webhook"

def setup_auditd_rule():
    """Adds an auditd rule to monitor only file and directory deletions."""
    try:
        rule_check = subprocess.run(["auditctl", "-l"], capture_output=True, text=True)
        if WATCHED_FOLDER in rule_check.stdout:
            print(f"✅ Audit rule already exists for {WATCHED_FOLDER}")
        else:
            subprocess.run(["auditctl", "-w", WATCHED_FOLDER, "-p", "wa", "-k", "file_delete"], check=True)
            print(f"🚀 Added auditd rule to monitor {WATCHED_FOLDER}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set up auditd rule: {e}")

def get_deleted_files():
    """Fetches the latest file deletion logs from auditd."""
    try:
        result = subprocess.run(["ausearch", "-k", "file_delete", "--start", "recent"], capture_output=True, text=True)
        if "no matches" in result.stdout.lower():
            return None
        return result.stdout
    except Exception as e:
        return str(e)

def extract_deletion_info(logs):
    """Extracts file deletion details, including the user who deleted the file."""
    if not logs:
        return None

    alerts = []
    lines = logs.split("\n")

    for line in lines:
        if "DELETE" in line:  # Ensure we only capture DELETE events
            try:
                filepath = line.split(" name=")[-1].split(" ")[0].strip('"')

                # Get user who performed the action
                user_id = line.split("uid=")[1].split(" ")[0]
                user = subprocess.run(["id", "-un", user_id], capture_output=True, text=True).stdout.strip()

                alert_msg = f"🚨 File Deleted! \n📂 File: {filepath} \n👤 User: {user}"
                alerts.append(alert_msg)
            except Exception as e:
                alerts.append(f"⚠️ Error extracting deletion info: {str(e)}")

    return "\n\n".join(alerts) if alerts else None

def send_to_slack(message):
    """Sends a formatted message to Slack."""
    try:
        payload = {"text": message}
        response = httpx.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("✅ Slack alert sent!")
    except httpx.HTTPError as e:
        print(f"❌ Failed to send to Slack: {e}")

def monitor_deletions():
    """Continuously monitors for file deletions and alerts Slack."""
    print("🔍 Monitoring file deletions...")
    setup_auditd_rule()

    # while True:
    logs = get_deleted_files()
    alert_message = extract_deletion_info(logs)

    if alert_message:
        send_to_slack(alert_message)

    # time.sleep(10)  # Avoid excessive Slack messages

if __name__ == "__main__":
    monitor_deletions()
