FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV PORT=8080
ENV WORKERS=1
ENV TIMEOUT=120
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Start API server
CMD ["python", "api_server.py"]
