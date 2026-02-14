# Kayak Calculation Tool (kayakish)

This tool is intended to provide a simple solution to the complex kayak or small boat calculations.
The tool is intended to work as an API server and host a HTML UI allowing the input of the hull data, and finding centers of gravity/buoyancy, doing analysis of displacement and building stability curves with different loads, so you can have an early idea about the behavior expected from the hull.


---

## Design
Application is built using
- Python 3.11+ as the main language
- Pydantic and FastAPI for the API interface
- Numpy for the raw calculations
- Docker with Nginx + Gunicorn for production deployment

---

## Quick Start

### Using Docker (Recommended)

The easiest way to run Kayakish is using Docker:

```bash
# Start the application
docker-compose up -d

# Access the application at http://localhost:8080
```

For detailed Docker deployment instructions, see [DOCKER.md](DOCKER.md).

### Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run development server:**
   ```bash
   uvicorn src.main:app --reload
   ```

4. **Access the application:**
   - Open your browser to: `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`

### Using Makefile

The project includes a Makefile for common tasks:

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev           # Run development server
make docker-up     # Start Docker containers
make docker-logs   # View Docker logs
```

---

## Configuration

The application can be configured using environment variables. Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
```

Available configuration options:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_PATH` | `data` | Directory for storing kayak hull files |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `DEBUG` | `false` | Enable debug mode |

---

## Features

- **Hull Analysis**: Calculate displacement, volume, and geometric properties
- **Center of Gravity (CG)**: Compute mass centroid position
- **Center of Buoyancy (CB)**: Calculate buoyancy centroid
- **Stability Curves**: Generate GZ curves for different heel angles
- **Web Interface**: User-friendly HTML interface for data input and visualization
- **REST API**: FastAPI-based API for programmatic access
- **Data Persistence**: Hull data stored in volume-backed files

---

## Project Structure

```
kayakish/
├── src/                    # Application source code
│   ├── analysis/          # Stability analysis modules
│   ├── geometry/          # Hull geometry calculations
│   ├── model/             # Pydantic data models
│   ├── routes/            # FastAPI route handlers
│   ├── utils/             # Utility functions
│   ├── config.py          # Application configuration
│   └── main.py            # FastAPI application entry point
├── visualization/          # HTML/CSS/JS frontend
├── docker/                # Docker configuration files
├── data/                  # Hull data files (gitignored)
├── test/                  # Unit tests
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
└── requirements.txt       # Python dependencies
``` 



