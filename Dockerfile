FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Download model during build and clear cache
RUN python -c "from rembg.session_factory import new_session; session = new_session('u2net_cloth_seg')" && \
    rm -rf /root/.cache/pip

# Environment variables
ENV PORT=10000
ENV WORKERS=2
ENV TIMEOUT=120

# Expose port
EXPOSE 10000

# Start API server with gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT --workers $WORKERS --timeout $TIMEOUT api_server:app
