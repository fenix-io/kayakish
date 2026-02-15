# Kayakish — Kayak & Small Boat Hydrostatics Calculator

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Kayakish is a web-based tool for calculating hydrostatic parameters and stability characteristics of kayaks and small boats. Define your hull geometry through longitudinal curves, and the system will compute displacement, centers of gravity and buoyancy, equilibrium waterlines, and full stability curves (GZ curves) under varying loading conditions.

Whether you're designing a new kayak or analyzing an existing hull, Kayakish gives you early insight into the expected behavior of the boat on the water.

---

## What It Does

- **Hull Geometry Processing** — Define a hull using a small set of longitudinal curves (gunwale, chine, keel, etc.). The system automatically mirrors the curves for symmetry, interpolates transverse profiles, and builds a complete 3D hull representation.
- **Hydrostatic Calculations** — Compute total volume, center of gravity (CG), equilibrium waterline, center of buoyancy (CB), and displacement for any given loading.
- **Stability Analysis** — Generate GZ (righting arm) and righting moment curves by heeling the hull through a range of angles. Find the angle of vanishing stability and maximum righting moment.
- **Interactive Visualization** — View hull curves in multiple projections (isometric, side, top, front, 3D), browse transverse profile cross-sections, and see stability graphs — all in the browser.
- **REST API** — Full programmatic access to all features via a documented FastAPI interface with auto-generated OpenAPI/Swagger docs.

---

## Quick Start

### Option 1: Docker (Recommended for Production)

```bash
# Clone the repository
git clone https://github.com/fenix-io/kayakish.git
cd kayakish

# Start the application
docker-compose up -d

# Open in browser
open http://localhost:8080
```

For detailed Docker deployment instructions, see [Docker Guide](docs/Docker.md).

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/fenix-io/kayakish.git
cd kayakish

# Create virtual environment and install dependencies
make install

# Start the development server
make dev

# Open in browser
open http://localhost:8000
```

Or manually:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Accessing the Application

| Interface | Development | Docker |
|-----------|-------------|--------|
| **Web UI** | http://localhost:8000 | http://localhost:8080 |
| **API Docs (Swagger)** | http://localhost:8000/docs | http://localhost:8080/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | http://localhost:8080/redoc |

---

## Using the Web UI

1. **Create a kayak** — Click  **+ New**, fill in the hull metadata, and enter curve data in the text format (see [User Guide](docs/User_Guide.md)).
2. **Browse hulls** — Select a kayak from the left sidebar to see its summary, visualization, and profiles.
3. **Run stability analysis** — Switch to the Stability tab, enter paddler weight and paddler CG height, and click *Analyze Stability* to generate GZ and moment curves.
4. **View profiles** — Switch to the Profiles tab to browse transverse cross-sections at each station along the hull.

For a complete walkthrough, see the [User Guide](docs/User_Guide.md).

---

## Using the API

The API follows REST conventions. All hull endpoints are under `/hulls/`.

**List all hulls:**
```bash
curl http://localhost:8000/hulls/
```

**Create a hull:**
```bash
curl -X POST http://localhost:8000/hulls/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Kayak",
    "description": "Test hull",
    "target_waterline": 0.11,
    "target_payload": 90,
    "target_weight": 10,
    "curves": [
      {
        "name": "starboard gunnel",
        "points": [[0,0,0.30],[1,0.18,0.28],[2,0.30,0.28],[3,0.30,0.28],[4,0.14,0.28],[5,0,0.30]]
      },
      {
        "name": "keel",
        "points": [[0,0,0.30],[0.2,0,0.16],[0.5,0,0],[4.2,0,0],[4.7,0,0.16],[5,0,0.30]]
      }
    ]
  }'
```

**Run stability analysis:**
```bash
curl -X POST http://localhost:8000/hulls/my_kayak/stability \
  -H "Content-Type: application/json" \
  -d '{
    "hull_name": "My Kayak",
    "paddler_weight": 80,
    "paddler_cg_z": 0.25,
    "hull_weight": 10,
    "max_angle": 90,
    "step": 3
  }'
```

Full API documentation is available at `/docs` (Swagger UI) when the server is running.

---

## Configuration

The application is configured via environment variables (or a `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_PATH` | `data` | Directory for storing `.hull` data files |
| `API_HOST` | `0.0.0.0` | API server bind address |
| `API_PORT` | `8000` | API server bind port |
| `APP_NAME` | `Kayakish - Hull Analysis Tool` | Application display name |
| `DEBUG` | `false` | Enable debug mode |

---

## Makefile Commands

```bash
make help            # Show all available commands
make install         # Create venv and install dependencies
make dev             # Run development server (uvicorn --reload)
make test            # Run pytest test suite
make lint            # Run flake8 linter
make format          # Format code with black
make clean           # Remove __pycache__ and temp files
make docker-build    # Build Docker image
make docker-up       # Start Docker containers
make docker-down     # Stop Docker containers
make docker-logs     # Tail container logs
make docker-backup   # Backup data volume
make docker-restore  # Restore data from backup
```

---

## Project Structure

```
kayakish/
├── src/                        # Python application source
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment-based configuration
│   ├── routes/hull.py          # REST API endpoints
│   ├── model/models.py         # Pydantic data schemas
│   ├── geometry/               # Core computation engine
│   │   ├── point.py            # 3D point/vector operations
│   │   ├── spline.py           # Parametric cubic spline interpolation
│   │   ├── curve.py            # Hull curve (spline + mirroring)
│   │   ├── profile.py          # Transverse cross-section
│   │   ├── hull.py             # Hull geometry & hydrostatics
│   │   └── weight.py           # Weight + CG container
│   ├── analysis/stability.py   # Stability curve (GZ) calculation
│   └── utils/filename.py       # Filename sanitization
├── visualization/              # Frontend (vanilla HTML/CSS/JS)
│   ├── index.html              # Page layout with modals and tabs
│   ├── script.js               # API calls, canvas rendering, UI logic
│   └── styles.css              # Grid layout, theming
├── data/                       # Persistent hull files (.hull)
├── test/                       # Unit tests and debug scripts
├── docs/                       # Documentation
│   ├── Architecture.md         # Architecture overview
│   └── User_Guide.md           # User guide
├── docker/                     # Nginx & Supervisord configs
├── Dockerfile                  # Multi-stage production image
├── docker-compose.yml          # Docker Compose configuration
├── Makefile                    # Development & operations commands
├── pyproject.toml              # Project metadata & tool config
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Web Framework | FastAPI |
| Data Validation | Pydantic v2 |
| Numerical Computing | NumPy, SciPy |
| Plotting | Matplotlib |
| Frontend | Vanilla HTML/CSS/JS, Canvas API |
| Dev Server | Uvicorn |
| Production | Nginx + Gunicorn + Supervisord (Docker) |
| Testing | pytest |
| Linting/Formatting | flake8, black |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/Architecture.md) | System architecture, components, data flow, and design decisions |
| [User Guide](docs/User_Guide.md) | How to create hulls, run stability analysis, and view profiles |
| [Docker Guide](docs/Docker.md) | Docker deployment, configuration, and operations |
| [Glossary](docs/Glossary.md) | Naval architecture and hydrostatics terminology |
| [Test Suite Summary](docs/Test_suite_summary.md) | Comprehensive unit test documentation and coverage details |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run linting and formatting: `make lint && make format`
5. Run tests: `make test`
6. Commit and push
7. Open a Pull Request

---

## License

This project is licensed under the MIT License. See [pyproject.toml](pyproject.toml) for details. 



