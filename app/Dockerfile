FROM python:3.12

# Install dependencies
RUN pip install inotify-simple httpx

# Set working directory
WORKDIR /app

# Copy script
COPY file_monitor.py .

# Run the script
CMD ["python", "file_monitor.py"]

