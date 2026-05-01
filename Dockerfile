FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config.py .
COPY activities.py .
COPY workflows.py .
COPY worker.py .

# Non-root user for security
RUN useradd -m -u 1000 worker
USER worker

CMD ["python", "worker.py"]
