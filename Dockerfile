# Multi-stage Docker build for Kayakish application
# Stage 1: Build Python dependencies
FROM python:3.11-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Stage 2: Final image with nginx
FROM python:3.11-slim

# Install nginx and supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATA_PATH=/app/data \
    API_HOST=127.0.0.1 \
    API_PORT=8000

WORKDIR /app

# Copy Python dependencies from build stage
COPY --from=python-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-base /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy application code
COPY src/ /app/src/
COPY visualization/ /app/visualization/

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create data directory
RUN mkdir -p /app/data && \
    chown -R www-data:www-data /app/data && \
    # Create nginx directories
    mkdir -p /var/cache/nginx /var/log/nginx /run && \
    chown -R www-data:www-data /var/cache/nginx /var/log/nginx

# Expose port 80
EXPOSE 80

# Use supervisor to run both nginx and gunicorn
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
