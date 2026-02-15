# Docker Deployment Guide

This guide explains how to deploy the Kayakish application using Docker.

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and start the application:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Open your browser and navigate to: `http://localhost:8080`
   - The API documentation is available at: `http://localhost:8080/docs`

3. **View logs:**
   ```bash
   docker-compose logs -f kayakish
   ```

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

5. **Stop and remove data volume:**
   ```bash
   docker-compose down -v
   ```

### Using Docker CLI

1. **Build the image:**
   ```bash
   docker build -t kayakish:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name kayakish \
     -p 8080:80 \
     -v kayak_data:/app/data \
     -e DATA_PATH=/app/data \
     kayakish:latest
   ```

3. **Access the application:**
   - Open your browser and navigate to: `http://localhost:8080`

## Configuration

### Environment Variables

You can configure the application using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_PATH` | `/app/data` | Path to store kayak hull data files |
| `API_HOST` | `127.0.0.1` | Host for the FastAPI application |
| `API_PORT` | `8000` | Port for the FastAPI application |
| `APP_NAME` | `Kayakish - Hull Analysis Tool` | Application name |
| `DEBUG` | `false` | Enable debug mode |

### Custom Configuration with Docker Compose

Edit the `docker-compose.yml` file to customize environment variables:

```yaml
environment:
  - DATA_PATH=/custom/path
  - DEBUG=true
```

### Custom Configuration with Docker CLI

```bash
docker run -d \
  --name kayakish \
  -p 8080:80 \
  -v kayak_data:/app/data \
  -e DATA_PATH=/app/data \
  -e DEBUG=true \
  kayakish:latest
```

## Data Persistence

The application uses Docker volumes to persist kayak hull data:

- **Volume name:** `kayak_data`
- **Mount point:** `/app/data`

### Backup Data

```bash
# Create a backup
docker run --rm -v kayak_data:/data -v $(pwd):/backup alpine tar czf /backup/kayak_data_backup.tar.gz -C /data .
```

### Restore Data

```bash
# Restore from backup
docker run --rm -v kayak_data:/data -v $(pwd):/backup alpine tar xzf /backup/kayak_data_backup.tar.gz -C /data
```

### Access Data Directory

```bash
# List files in the data volume
docker run --rm -v kayak_data:/data alpine ls -la /data

# Copy a file from the volume to host
docker cp kayakish:/app/data/my_kayak.hull ./my_kayak.hull
```

## Architecture

The Docker image uses:
- **Base image:** Python 3.11-slim
- **Web server:** Nginx (serves static files and acts as reverse proxy)
- **Application server:** Gunicorn with Uvicorn workers
- **Process manager:** Supervisord (manages nginx and gunicorn)

### Ports

- **80** - HTTP port (nginx)
  - Static files served from `/app/visualization`
  - API requests proxied to FastAPI backend at `127.0.0.1:8000`

### Health Check

The application includes a health check endpoint:
- **Endpoint:** `http://localhost/health`
- **Interval:** 30 seconds
- **Timeout:** 10 seconds

## Troubleshooting

### View logs

```bash
# All logs
docker-compose logs -f

# Only application logs
docker-compose logs -f kayakish

# Nginx logs
docker exec kayakish tail -f /var/log/nginx/access.log
docker exec kayakish tail -f /var/log/nginx/error.log
```

### Access container shell

```bash
docker exec -it kayakish /bin/bash
```

### Rebuild after changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Force rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Check running processes

```bash
docker exec kayakish ps aux
```

### Test API directly

```bash
# From host
curl http://localhost:8080/health
curl http://localhost:8080/hulls/

# From within container
docker exec kayakish curl http://localhost/health
```

## Production Deployment

For production deployment, consider:

1. **Use a reverse proxy** (e.g., Traefik, Caddy) for HTTPS
2. **Set appropriate resource limits:**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 1G
       reservations:
         cpus: '0.5'
         memory: 512M
   ```

3. **Enable log rotation**
4. **Set up monitoring and alerts**
5. **Use Docker secrets for sensitive data**
6. **Regular backups of the data volume**

## Development

To run in development mode with live code reloading:

```bash
# Mount source code as volume
docker run -d \
  --name kayakish-dev \
  -p 8080:80 \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/visualization:/app/visualization \
  -v kayak_data:/app/data \
  -e DEBUG=true \
  kayakish:latest
```

Or create a `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  kayakish:
    volumes:
      - ./src:/app/src
      - ./visualization:/app/visualization
    environment:
      - DEBUG=true
```
