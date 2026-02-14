# Kayakish — Architecture Document

**Version:** 1.0  
**Date:** February 2026

---

## 1. Overview

Kayakish is a web application for calculating hydrostatic parameters and stability characteristics of kayaks and small boats. It combines a **FastAPI** backend with a **vanilla HTML/CSS/JS** frontend, allowing users to define hull geometry through longitudinal curves, compute displacement and buoyancy properties, and generate stability curves (GZ curves) for varying loading conditions.

The core idea is simple: the user provides a set of 3D curves that describe the hull surface (gunwale, chine, keel, etc.), and the system interpolates transverse profiles, calculates volumes by numerical integration, and iteratively finds the equilibrium waterline for a given total weight. From there, it can heel the hull at incremental angles and produce a full stability analysis.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Browser)                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  visualization/                                           │  │
│  │  ├── index.html   (layout, modals, tabs)                  │  │
│  │  ├── script.js    (API calls, canvas drawing, UI logic)   │  │
│  │  └── styles.css   (grid layout, theming)                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │  HTTP (fetch)                      │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                          │
│                                                                  │
│  src/main.py              Application entry point                │
│  ├── src/routes/hull.py   REST endpoints (CRUD + stability)     │
│  ├── src/model/models.py  Pydantic request/response schemas     │
│  ├── src/config.py        Environment-based configuration       │
│  │                                                               │
│  ├── src/geometry/        Core computation engine                │
│  │   ├── point.py         Point3D: 3D vector operations         │
│  │   ├── spline.py        Spline3D: cubic spline interpolation  │
│  │   ├── curve.py         Curve: hull curve (extends Spline3D)  │
│  │   ├── profile.py       Profile: transverse cross-section     │
│  │   ├── hull.py          Hull: full hull geometry & hydrostatics│
│  │   └── weight.py        Weight: simple weight+CG container    │
│  │                                                               │
│  ├── src/analysis/                                               │
│  │   └── stability.py     Stability curve (GZ) computation      │
│  │                                                               │
│  └── src/utils/                                                  │
│      └── filename.py      Filename sanitization                  │
│                                                                  │
│  data/                    Persistent .hull files (JSON)          │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Topology

| Mode | Stack | Port |
|------|-------|------|
| **Development** | Uvicorn (serves API + static files) | `8000` |
| **Production (Docker)** | Nginx → Gunicorn/Uvicorn, managed by Supervisord | `80` (mapped to host `8080`) |

In production, Nginx serves the static `visualization/` files directly and proxies `/hulls/*` requests to the Gunicorn application server.

---

## 3. Component Details

### 3.1 Entry Point — `src/main.py`

Creates the FastAPI `app` instance, registers the hull API router under the `/hulls` prefix, and mounts the `visualization/` directory as a static file server at the root path `/`. The static mount is registered last so that API routes take priority.

### 3.2 Configuration — `src/config.py`

Uses `pydantic-settings` to load configuration from environment variables and an optional `.env` file:

| Setting | Default | Purpose |
|---------|---------|---------|
| `DATA_PATH` | `data` | Directory where `.hull` files are stored |
| `API_HOST` | `0.0.0.0` | Uvicorn bind address |
| `API_PORT` | `8000` | Uvicorn bind port |
| `APP_NAME` | `Kayakish - Hull Analysis Tool` | Application display name |
| `DEBUG` | `false` | Debug mode toggle |

### 3.3 API Layer — `src/routes/hull.py`

Implements a RESTful CRUD interface plus a stability analysis endpoint:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/hulls/` | List all saved hulls (summary) |
| `GET` | `/hulls/{name}` | Get full hull details |
| `POST` | `/hulls/` | Create a new hull from curve data |
| `PUT` | `/hulls/{name}` | Update an existing hull |
| `DELETE` | `/hulls/{name}` | Delete a hull |
| `POST` | `/hulls/{name}/stability` | Run stability analysis |

**Create/Update flow:**
1. Receive a `CreateHullModel` (name, metadata, curves).
2. Instantiate a `Hull` object and call `hull.build()`.
3. The build process: parses curves → mirrors non-centerline curves → generates transverse profiles at 0.05 m intervals → calculates total volume and CG → iteratively finds the equilibrium waterline for the target weight.
4. Map the computed `Hull` to a `HullModel` response and persist as a `.hull` JSON file.

**Stability flow:**
1. Load an existing hull from its `.hull` file.
2. Call `create_stability_curve_points()` with user-provided parameters (paddler weight, CG height, angle range, step).
3. Return the array of stability points (angle, GZ, moment, waterline, displacement) plus summary metrics (vanishing angle, max moment).

### 3.4 Data Models — `src/model/models.py`

All models use Pydantic v2 `BaseModel`:

| Model | Role |
|-------|------|
| `CurveModel` | A named curve with a list of `(x, y, z)` tuples and an optional `mirrored` flag |
| `ProfileModel` | A transverse profile at a given station with its points |
| `CreateHullModel` | Input schema for creating/updating a hull (name, metadata, curves) |
| `HullModel` | Full hull response including computed properties (volume, CG, CB, waterline, displacement, profiles, bounds) |
| `HullSummaryModel` | Lightweight summary for list views |
| `StabilityAnalysisModel` | Input parameters for stability analysis |
| `StabilityPointModel` | A single point on the stability curve |
| `StabilityAnalysisResultModel` | Complete stability analysis output |

### 3.5 Geometry Engine — `src/geometry/`

This is the computational core of the application.

#### 3.5.1 `Point3D` (`point.py`)

A lightweight 3D point/vector class with:
- Arithmetic operators (`+`, `-`, `*`, `/`)
- Rotation around X, Y, Z axes (important for heel calculations)
- Distance, dot product, cross product
- Uses `__slots__` for memory efficiency

#### 3.5.2 `Spline3D` (`spline.py`)

Parametric cubic spline interpolation through 3D control points:

- **Parametrization modes:**
  - `x` — when x-coordinates are strictly monotonic, uses `PchipInterpolator` (shape-preserving) directly on x.
  - `chord` — parametrizes by cumulative chord length, uses `CubicSpline` for all three coordinates.
  - `auto` — automatically selects `x` if monotonic, otherwise `chord`.

- **Key methods:**
  - `eval_x(x)` — evaluate the curve at a given x-coordinate (uses Brent's root-finding for chord parametrization).
  - `eval_t(t)` — evaluate at a raw parameter value.
  - `apply_rotation_on_x_axis(origin, angle)` — returns a new spline with all control points rotated around the x-axis (used for heel simulation).
  - `tangent(t)`, `curvature(t)`, `normal(t)` — differential geometry operations.
  - `sample(n)` — generate n evenly-spaced points along the curve.

#### 3.5.3 `Curve` (`curve.py`)

Extends `Spline3D` with a `mirrored` flag to indicate port/starboard relationship.

#### 3.5.4 `Profile` (`profile.py`)

Represents a transverse cross-section of the hull at a given x-station:

- Points are deduplicated on construction and sorted in circular (counterclockwise) order around their centroid.
- **Area:** computed via the shoelace formula on the (y, z) plane.
- **Centroid:** computed from the signed-area formula.
- **Volume:** area × step width (slab integration).

#### 3.5.5 `Hull` (`hull.py`)

The central orchestrator. Two initialization paths:

1. **`build(data)`** — from raw curve input:
   - Parses curves and creates mirror curves for any non-centerline curve (y ≠ 0).
   - Tracks bounding box (min/max x, y, z).
   - Steps along the x-axis at 0.05 m intervals, evaluating each curve at that x to get profile points.
   - Computes total volume and volume-weighted CG.
   - Iteratively solves for the waterline where displacement = target weight using a convergence loop.

2. **`initialize_from_data(data)`** — from a previously saved hull (loads precomputed values).

**Waterline calculation** (`_calculate_waterline`):
- Accepts total weight and an optional heel angle.
- At each angle, rotates all curves about the x-axis through the CG.
- Steps along x, collects profile points, clips to below-waterline (including intersection points).
- Computes submerged volume and center of buoyancy.
- Adjusts waterline iteratively until `|weight - displacement| ≤ 1 kg`.

**Below-waterline clipping** (`_get_points_below_waterline`):
- Sorts points in angular order around their centroid.
- Walks adjacent pairs; if a segment crosses the waterline, a linear intersection point is inserted.
- Returns only points at or below the waterline.

### 3.6 Stability Analysis — `src/analysis/stability.py`

**`create_stability_curve_points(hull, ...)`:**

1. Computes the combined CG of hull + paddler as a volume-weighted average.
2. For each heel angle (0° to max, in steps):
   - Calls `hull._calculate_waterline(total_weight, angle)` to find the equilibrium waterline at that heel.
   - Rotates the combined CG to the heeled position.
   - Computes the righting arm: `GZ = CG_y_rotated - CB_y`.
   - Computes the righting moment: `moment = total_weight × g × GZ`.
3. Determines the **vanishing angle** by linear interpolation where GZ crosses zero.
4. Reports maximum righting moment and its angle.

### 3.7 Frontend — `visualization/`

A single-page application using vanilla HTML, CSS, and JavaScript (no framework dependencies).

**Layout:**
- **Left sidebar:** Kayak list (with New/Edit/Delete) + Summary panel (toggleable to show detailed curves/profiles).
- **Main area:** Tabbed interface with three views:
  - **Visualization** — canvas rendering of hull curves in multiple projections (isometric, side, top, front, 3D perspective), with waterline indication and color coding.
  - **Stability** — form to configure stability parameters, triggers API call, renders GZ and righting moment graphs on two canvases.
  - **Profiles** — station selector with navigation buttons, renders the cross-section profile at the selected x-station plus a hull side-view showing the station position.

**Data flow:**
1. On load, fetches `GET /hulls/` to populate the list.
2. Selecting a kayak fetches `GET /hulls/{name}` for full details.
3. Create/Edit opens a modal, submits `POST /hulls/` or `PUT /hulls/{name}`.
4. Stability analysis submits `POST /hulls/{name}/stability` and draws results.

**Curves input format** (in create/edit modals):
```
curve: starboard gunnel
0.00, 0.00, 0.30
1.00, 0.18, 0.28
...
curve: keel
0.00, 0.00, 0.30
...
```

### 3.8 Data Persistence

Hull data is stored as `.hull` files (JSON format following the `HullModel` schema) in the directory specified by `DATA_PATH`. No database is required. Filenames are derived from the hull name via `sanitize_filename()` (lowercased, special characters removed, spaces replaced with underscores).

---

## 4. Coordinate System

All coordinates follow a right-hand orthogonal system:

| Axis | Direction | Reference |
|------|-----------|-----------|
| **x** | Stern → Bow (longitudinal) | 0 at the stern projection on centerline |
| **y** | Centerline → Port (positive), Centerline → Starboard (negative) | 0 at the centerline |
| **z** | Bottom → Top (vertical) | 0 at the deepest hull point |

The system assumes **port/starboard symmetry**: only starboard (or port) curves need to be defined; the mirror is generated automatically during the build process. The keel curve (y = 0) is not mirrored.

---

## 5. Calculation Pipeline

```
Input Curves          Spline            Profiles              Volume
(control points) → Interpolation → (cross-sections at → (numerical integration
                                    every 0.05m along x)   via slab method)
                                         │
                                         ▼
                                    Area (shoelace)
                                    Centroid (signed area)
                                    Volume = Area × step
                                         │
                          ┌──────────────┤
                          ▼              ▼
                    Total Volume     Volume-weighted CG
                          │
                          ▼
                  Waterline Iteration
                  (adjust waterline until
                   displacement = weight)
                          │
                          ▼
                  CB (center of buoyancy)
                  Displacement (submerged vol × 1000 kg/m³)
                          │
                          ▼
              Stability Analysis (per angle)
              ├── Rotate hull curves by angle
              ├── Find new waterline at angle
              ├── Compute CB at angle
              ├── Rotate CG to heeled position
              ├── GZ = CG_y - CB_y
              └── Moment = Weight × g × GZ
```

### 5.1 Profile Generation

At each x-station (every 0.05 m from stern to bow), every curve is evaluated using `curve.eval_x(x)`. The resulting set of points forms a transverse profile. Points are sorted angularly around their centroid to form a closed polygon.

### 5.2 Volume Integration

Each profile's area is computed using the **shoelace formula** on the (y, z) plane. The volume contribution of each slab is `area × step_width`. Total volume is the sum of all slab volumes. The center of gravity is the volume-weighted average of all slab centroids.

### 5.3 Waterline Convergence

Starting from an initial guess (target waterline or 1/3 of hull depth), the system iteratively:
1. Clips all profile points to below the current waterline.
2. Computes submerged volume → displacement (volume × 1000 kg/m³ for fresh water).
3. Adjusts the waterline proportionally: `increment = (weight − displacement) / weight × waterline`.
4. Converges when `|weight − displacement| ≤ 1 kg`.

### 5.4 Heel/Stability Computation

For each heel angle:
1. All curve control points are rotated around the x-axis through the CG.
2. The waterline convergence is repeated with the rotated geometry.
3. The center of buoyancy shifts laterally as the hull heels.
4. The **righting arm (GZ)** measures the transverse distance between the rotated CG and the CB — positive GZ means the hull tends to right itself.
5. The **vanishing angle** is where GZ crosses zero (the hull will capsize beyond this point).

---

## 6. Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11+ | Application logic |
| Web framework | FastAPI | REST API, request validation, OpenAPI docs |
| Data validation | Pydantic v2 | Input/output schemas |
| Configuration | pydantic-settings | Environment variable loading |
| Numerical computing | NumPy | Array operations, trigonometry |
| Interpolation | SciPy (`CubicSpline`, `PchipInterpolator`, `brentq`) | Curve fitting, root finding |
| Plotting | Matplotlib | Server-side plot generation (scripts) |
| ASGI server | Uvicorn | Development server |
| Production server | Gunicorn + Uvicorn workers | Production ASGI server |
| Reverse proxy | Nginx | Static files + API proxying |
| Process manager | Supervisord | Manages Nginx + Gunicorn in Docker |
| Containerization | Docker + Docker Compose | Production deployment |
| Frontend | Vanilla HTML/CSS/JS + Canvas API | UI, data visualization |
| Testing | pytest | Unit tests |
| Linting | flake8 | Code style enforcement |
| Formatting | black | Code formatting |

---

## 7. Directory Structure

```
kayakish/
├── src/                        # Python application source
│   ├── main.py                 # FastAPI app creation & mounting
│   ├── config.py               # Settings (env-based)
│   ├── routes/
│   │   └── hull.py             # API endpoints
│   ├── model/
│   │   └── models.py           # Pydantic schemas
│   ├── geometry/
│   │   ├── point.py            # Point3D class
│   │   ├── spline.py           # Spline3D parametric interpolation
│   │   ├── curve.py            # Curve (Spline3D + mirrored flag)
│   │   ├── profile.py          # Transverse cross-section
│   │   ├── hull.py             # Hull geometry & hydrostatics
│   │   └── weight.py           # Weight + CG container
│   ├── analysis/
│   │   └── stability.py        # GZ curve calculation
│   ├── services/               # (reserved for future service layer)
│   └── utils/
│       ├── __init__.py
│       └── filename.py         # Filename sanitization
├── visualization/              # Frontend SPA
│   ├── index.html              # Main page layout
│   ├── script.js               # Application logic (~1900 lines)
│   └── styles.css              # Styling (~900 lines)
├── data/                       # Hull data files (.hull, .json)
│   ├── k01.json                # Sample hull definition
│   └── sea_kayak_pro.json      # Sample hull definition
├── test/                       # Test suite
│   ├── unit/
│   │   ├── test_hull.py
│   │   └── test_profile.py
│   └── scripts/                # Visualization/debug scripts
├── docker/                     # Docker support files
│   ├── nginx.conf
│   └── supervisord.conf
├── docs/                       # Documentation
├── Dockerfile                  # Multi-stage production image
├── docker-compose.yml          # Compose configuration
├── Makefile                    # Dev/ops commands
├── pyproject.toml              # Project metadata & tool config
├── requirements.txt            # Python dependencies
├── DOCKER.md                   # Docker deployment guide
├── GLOSSARY.md                 # Naval architecture terminology
└── README.md                   # Project overview
```

---

## 8. Data Flow Diagrams

### 8.1 Hull Creation

```
User (Browser)                API Server                     Filesystem
     │                            │                              │
     │  POST /hulls/              │                              │
     │  {name, curves, ...}       │                              │
     │ ──────────────────────────>│                              │
     │                            │  Hull.build()                │
     │                            │  ├── Parse curves            │
     │                            │  ├── Mirror non-keel curves  │
     │                            │  ├── Generate profiles (0.05m)│
     │                            │  ├── Calculate volume & CG   │
     │                            │  └── Find waterline (iterate)│
     │                            │                              │
     │                            │  Save .hull file ──────────> │
     │                            │                              │
     │  <── HullModel response ───│                              │
     │                            │                              │
```

### 8.2 Stability Analysis

```
User (Browser)                API Server                     Filesystem
     │                            │                              │
     │  POST /hulls/{name}/       │                              │
     │  stability                 │                              │
     │  {paddler_weight,          │                              │
     │   paddler_cg_z, ...}       │                              │
     │ ──────────────────────────>│                              │
     │                            │  Load .hull file <────────── │
     │                            │                              │
     │                            │  For each angle (0° → max):  │
     │                            │  ├── Rotate curves           │
     │                            │  ├── Find waterline          │
     │                            │  ├── Compute CB              │
     │                            │  ├── Rotate CG               │
     │                            │  └── GZ = CG.y - CB.y       │
     │                            │                              │
     │  <── StabilityResult ──────│                              │
     │  {points[], vanishing,     │                              │
     │   max_moment}              │                              │
     │                            │                              │
     │  Draw GZ & Moment graphs   │                              │
     │  on Canvas                 │                              │
```

---

## 9. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Curves-based hull definition** | Defining a hull via longitudinal curves (gunwale, chine, keel) is intuitive for boat designers and requires fewer input points than a full point cloud. Profiles are computed automatically. |
| **Automatic mirroring** | Only one side of the hull needs to be defined; the system mirrors curves whose y-coordinates are non-zero, enforcing symmetry. |
| **Slab integration** | Simple and adequate for the required precision. Each profile is extruded by the step width (0.05 m) to form a volume slab. |
| **Iterative waterline** | A convergence loop adjusts the waterline until displacement matches the target weight, avoiding the need for an analytical waterline solver. |
| **File-based persistence** | `.hull` files in a data directory keep the system simple — no database required. Suitable for the expected number of hull models. |
| **Vanilla frontend** | No framework dependency keeps the frontend lightweight and easy to deploy as static files alongside the API. |
| **Canvas-based rendering** | The HTML5 Canvas API provides sufficient drawing capability for 2D hull projections, profile views, and stability graphs without requiring a 3D library. |
| **PCHIP interpolation for x-monotonic curves** | `PchipInterpolator` preserves the shape of the curve without overshooting, which is critical for hull fairness. |
| **Chord-length parametrization fallback** | For curves that are not monotonic in x (e.g., a keel with a hook), the system falls back to chord-length parametrization with `CubicSpline`. |

---

## 10. Extensibility Points

- **`src/services/`** — reserved for future service layer abstractions (e.g., hull comparison, optimization).
- **Additional analysis modules** — new modules in `src/analysis/` can implement features like wave resistance estimation, prismatic coefficient calculation, etc.
- **Database backend** — the file-based storage could be replaced with a database by modifying only the route handlers.
- **3D visualization** — the canvas rendering could be upgraded to WebGL/Three.js for true 3D interactive views.
- **Weight distribution** — the `Weight` class exists as a foundation for multi-item weight schedules (gear, paddler position, etc.).

---

## 11. Testing

Tests are located in `test/` and use `pytest`:

- **`test/unit/test_hull.py`** — unit tests for hull geometry calculations.
- **`test/unit/test_profile.py`** — unit tests for profile area, centroid, and volume computations.
- **`test/scripts/`** — standalone visualization scripts for debugging (profile areas, CB movement, profile rendering).

Run tests with:
```bash
source .venv/bin/activate
make test
```

---

## 12. Build & Deployment

### Development
```bash
make install    # Create venv and install dependencies
make dev        # Start uvicorn with --reload on port 8000
make test       # Run pytest
make lint       # Run flake8
make format     # Run black
```

### Production (Docker)
```bash
make docker-build   # Build the multi-stage Docker image
make docker-up      # Start with docker-compose (port 8080)
make docker-logs    # Tail container logs
make docker-backup  # Backup data volume
```

The Docker image uses a **multi-stage build**: the first stage installs Python dependencies, and the second stage copies them into a slim image with Nginx, Supervisord, and Gunicorn.
