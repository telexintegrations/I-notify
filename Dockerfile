# Use a minimal Python image
FROM python:3.12-slim

# Install dependencies
RUN pip install httpx

# Install auditd inside the container
RUN apt-get update && apt-get install -y auditd audispd-plugins

# Set the working directory
WORKDIR /I-notify

# Copy the Python script
COPY file_monitor.py .

# Ensure it has execute permissions
RUN chmod +x file_monitor.py

# Run the script as an entrypoint (only when needed)
ENTRYPOINT ["python3", "/I-notify/file_monitor.py"]

