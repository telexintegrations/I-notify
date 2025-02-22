# File Deletion Monitor

## Overview
This project monitors file deletions in a specified directory using `auditd`, logs events to a PostgreSQL database, and sends alerts via Telex Webhook.

## Features
- Monitors file deletions in a specified directory.
- Logs deleted files to a PostgreSQL database.
- Sends alerts to a Telex Webhook.
- Uses `auditd` for real-time monitoring.

## Installation

### 1. Clone the Repository
```sh
git clone <repository-url>
cd <repository-folder>
```

### 2. Install Dependencies
Ensure you have Python installed. Then, install the required dependencies:
```sh
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root with the following content:
```
WATCHED_FOLDER=/home/ubuntu/test_directory
TELEX_WEBHOOK_URL=http://127.0.0.1:5000/telex-webhook
DB_NAME=file_monitor
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```
Replace the values as needed.

### 4. Set Up PostgreSQL Database
Ensure PostgreSQL is running and create the necessary table:
```sh
psql -U postgres -d file_monitor -c "CREATE TABLE IF NOT EXISTS file_deletions (id SERIAL PRIMARY KEY, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, file_path TEXT NOT NULL, deleted_by TEXT NOT NULL);"
```

### 5. Run the Monitor
Start the script using:
```sh
sudo python monitor.py
```
The script will continuously monitor for file deletions and log them.

## Troubleshooting
- Ensure `auditd` is installed and running:
  ```sh
  sudo apt install auditd
  sudo systemctl start auditd
  ```
- Check if the rule is set:
  ```sh
  auditctl -l
  ```
- Manually trigger an event to test:
  ```sh
  rm /home/ubuntu/test_directory/testfile.txt
  ```

## License
MIT License

