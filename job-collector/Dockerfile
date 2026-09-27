FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (backend package is mounted at /backend by docker-compose;
# main.py resolves it via ../backend relative to /app)
COPY . .

# Run the hourly collection loop as a persistent service
CMD ["python", "main.py", "--loop"]
