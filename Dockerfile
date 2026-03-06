FROM python:3.11-slim

# Metadata
LABEL maintainer="your-email@example.com"
LABEL description="AI Customer Service Chatbot — multi-cloud, business-independent"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        flask>=3.0.0 \
        flask-cors>=4.0.0 \
        pyyaml>=6.0.1 \
        requests>=2.31.0 \
        gunicorn>=21.0.0

# Copy app source
COPY backend/   ./backend/
COPY frontend/  ./frontend/
COPY config/    ./config/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "backend.app:app"]
