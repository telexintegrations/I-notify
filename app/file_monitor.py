import os
import sys
import httpx
import subprocess
from inotify_simple import INotify, flags

# 🔹 Configuration
WATCH_DIR = "/home/ubuntu/test_directory"
SLACK_WEBHOOK_URL = "https://ping.telex.im/v1/webhooks/01951279-015e-7baa-b755-dd631bdba9bf"

# 🔹 Ensure the directory exists
if not os.path.exists(WATCH_DIR):
    print(f"Error: Directory {WATCH_DIR} does not exist.")
    sys.exit(1)

# 🔹 Setup inotify
inotify = INotify()
watch_flags = flags.DELETE | flags.DELETE_SELF  # Monitor deletions only

# 🔹 Register watches on the main directory and all subdirectories
watch_descriptors = {}

def add_watch_recursive(directory):
    """
    Recursively add all subdirectories to the inotify watch list.
    """
    for root, dirs, _ in os.walk(directory):
        if root not in watch_descriptors:
            wd = inotify.add_watch(root, watch_flags)
            watch_descriptors[wd] = root

add_watch_recursive(WATCH_DIR)

print(f"✅ Monitoring {WATCH_DIR} and all subdirectories for deletions...")

def get_user_who_deleted():
    """
    Fetches the most recent file deletion user from the audit logs.
    """
    try:
        audit_logs = subprocess.run(
            ["ausearch", "-k", "file_delete", "--start", "recent"],
            capture_output=True, text=True
        ).stdout

        # 🔹 Extract user ID (uid=1000, etc.)
        user_id_match = next((line for line in audit_logs.split("\n") if "uid=" in line), None)
        if user_id_match:
            user_id = user_id_match.split("uid=")[1].split()[0]
            user_name = subprocess.run(["id", "-un", user_id], capture_output=True, text=True).stdout.strip()
            return user_name
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return "Unknown"

def is_directory(deleted_path):
    """
    Checks if the deleted path was a directory.
    """
    return os.path.isdir(deleted_path)

def send_slack_alert(deleted_path, user_name, is_dir):
    """
    Send a Slack notification for deleted files or directories.
    """
    item_type = "📁 Directory" if is_dir else "📄 File"
    payload = {
        "username": "File Monitor",
        "event_name": "deletion",
        "status": "success",
        "message": f"🚨 {item_type} Deleted: `{deleted_path}`\n👤 Deleted by: `{user_name}`",
    }
    try:
        response = httpx.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"✅ Slack notification sent: {deleted_path}")
    except httpx.HTTPError as e:
        print(f"❌ Error sending Slack message: {e}")

try:
    while True:
        # 🔹 Wait for an event (10s timeout)
        events = inotify.read(timeout=10000)

        for event in events:
            deleted_path = os.path.join(watch_descriptors.get(event.wd, WATCH_DIR), event.name)
            user_name = get_user_who_deleted()
            was_dir = is_directory(deleted_path)  # Check if it was a directory

            if event.mask & flags.DELETE:
                print(f"🗑 { '📁 Directory' if was_dir else '📄 File' } deleted: {deleted_path} by {user_name}")
                send_slack_alert(deleted_path, user_name, was_dir)

            elif event.mask & flags.DELETE_SELF:
                print(f"🚨 Directory deleted: {deleted_path} by {user_name}")
                send_slack_alert(deleted_path, user_name, True)
                sys.exit(1)  # Exit if the main monitored directory is deleted

except KeyboardInterrupt:
    print("\n[INFO] Monitoring stopped by user.")

