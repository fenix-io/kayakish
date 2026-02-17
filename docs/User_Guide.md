# Kayakish — User Guide

**Version:** 1.0  
**Date:** February 2026

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Understanding Hull Geometry](#2-understanding-hull-geometry)
3. [Loading a Kayak via the Web UI](#3-loading-a-kayak-via-the-web-ui)
4. [Loading a Kayak via the API](#4-loading-a-kayak-via-the-api)
5. [Viewing Hull Visualizations](#5-viewing-hull-visualizations)
6. [Viewing Profile Cross-Sections](#6-viewing-profile-cross-sections)
7. [Running Stability Analysis](#7-running-stability-analysis)
8. [Running Resistance Analysis](#8-running-resistance-analysis)
9. [Editing and Deleting Hulls](#9-editing-and-deleting-hulls)
10. [Understanding the Results](#10-understanding-the-results)
11. [Sample Hull Data](#11-sample-hull-data)
12. [Tips and Best Practices](#12-tips-and-best-practices)

---

## 1. Getting Started

Make sure the Kayakish server is running:

- **Development:** `make dev` → open http://localhost:8000
- **Docker:** `docker-compose up -d` → open http://localhost:8080

When you open the application in a browser, you'll see:
- A **left sidebar** with the list of available kayaks and a summary panel.
- A **main area** with four tabs: Visualization, Stability, Resistance, and Profiles.

---

## 2. Understanding Hull Geometry

Kayakish defines a hull using **longitudinal curves** — lines that run from stern to bow along the hull surface. Common curves include:

| Curve | Description |
|-------|-------------|
| **Keel** | The bottom centerline of the hull (y = 0) |
| **Chine** | An angular edge between the bottom and sides |
| **Gunwale** | The upper edge where the deck meets the hull |

Each curve is a series of 3D control points `(x, y, z)` that the system interpolates with cubic splines.

### Coordinate System

| Axis | Direction | Zero Reference |
|------|-----------|----------------|
| **x** | Longitudinal (stern → bow) | Stern projection on centerline |
| **y** | Transverse (centerline → port = positive) | Centerline |
| **z** | Vertical (bottom → top) | Deepest point of the hull |

### Symmetry

You only need to define curves on **one side** of the hull (typically the starboard side, with positive y values). The system automatically creates the mirror curves for the opposite side. The keel (y = 0 on all points) is not mirrored.

### Hull Parameters

| Parameter | Description |
|-----------|-------------|
| **Name** | Unique identifier for the hull |
| **Description** | Free text description |
| **Target Waterline** | Initial guess for waterline height (m) |
| **Target Payload** | Paddler + gear weight (kg) |
| **Target Weight** | Hull weight (kg) |

---

## 3. Loading a Kayak via the Web UI

### Step 1: Open the Create Modal

Click the **+ New** button at the top of the kayak list in the left sidebar.

### Step 2: Fill in Metadata

| Field | Required | Example |
|-------|----------|---------|
| Name | Yes | `Sea Kayak Pro` |
| Description | No | `High-performance touring kayak` |
| Target Waterline | No | `0.11` |
| Target Payload | No | `90` (kg — paddler + gear) |
| Target Weight | No | `10` (kg — hull weight) |

### Step 3: Enter Curve Data

In the **Curves Data** textarea, enter your curves using this text format:

```
curve: starboard gunnel
0.00, 0.00, 0.30
1.00, 0.18, 0.28
2.00, 0.30, 0.28
3.00, 0.30, 0.28
4.00, 0.14, 0.28
5.00, 0.00, 0.30

curve: starboard chine
0.20, 0.00, 0.16
1.00, 0.12, 0.12
2.00, 0.22, 0.11
3.00, 0.22, 0.11
4.00, 0.10, 0.12
4.70, 0.00, 0.16

curve: keel
0.00, 0.00, 0.30
0.20, 0.00, 0.16
0.50, 0.00, 0.00
4.20, 0.00, 0.00
4.70, 0.00, 0.16
5.00, 0.00, 0.30
```

**Format rules:**
- Start each curve with `curve: <name>`.
- List points as `x, y, z` — one point per line.
- Separate curves with a blank line (optional, for readability).
- Points must be ordered by **increasing x** (stern to bow).
- x-coordinates within a curve must be **strictly increasing** (no duplicate x values).
- Each curve needs at least **2 control points**.

### Step 4: Submit

Click **Create Kayak**. The system will:
1. Parse the curves.
2. Mirror non-centerline curves to the opposite side.
3. Generate transverse profiles every 5 cm along the hull.
4. Calculate total volume and center of gravity.
5. Iteratively find the equilibrium waterline for the target weight.
6. Save the hull and display it in the list.

A success notification will appear, and the new kayak will be selected automatically.

---

## 4. Loading a Kayak via the API

### Create a Hull (POST)

```bash
curl -X POST http://localhost:8000/hulls/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kayak 001",
    "description": "Test kayak hull",
    "target_waterline": 0.11,
    "target_payload": 90,
    "target_weight": 10,
    "curves": [
      {
        "name": "starboard gunnel",
        "points": [
          [0.00, 0.00, 0.30],
          [1.00, 0.18, 0.28],
          [2.00, 0.30, 0.28],
          [3.00, 0.30, 0.28],
          [4.00, 0.14, 0.28],
          [5.00, 0.00, 0.30]
        ]
      },
      {
        "name": "starboard chine",
        "points": [
          [0.20, 0.00, 0.16],
          [1.00, 0.12, 0.12],
          [2.00, 0.22, 0.11],
          [3.00, 0.22, 0.11],
          [4.00, 0.10, 0.12],
          [4.70, 0.00, 0.16]
        ]
      },
      {
        "name": "keel",
        "points": [
          [0.00, 0.00, 0.30],
          [0.20, 0.00, 0.16],
          [0.50, 0.00, 0.00],
          [4.20, 0.00, 0.00],
          [4.70, 0.00, 0.16],
          [5.00, 0.00, 0.30]
        ]
      }
    ]
  }'
```

### JSON Schema

```json
{
  "name": "string (required, unique)",
  "description": "string (optional)",
  "target_waterline": "float (optional, meters)",
  "target_payload": "float (optional, kg)",
  "target_weight": "float (optional, kg)",
  "curves": [
    {
      "name": "string (required)",
      "points": [
        [x, y, z],
        [x, y, z]
      ]
    }
  ]
}
```

Each point is a 3-element array `[x, y, z]` in the hull coordinate system.

### Response

The API returns a `HullModel` with all computed properties:

```json
{
  "name": "Kayak 001",
  "description": "Test kayak hull",
  "length": 5.0,
  "beam": 0.6,
  "depth": 0.3,
  "volume": 0.339,
  "cg": [2.431, 0.000, 0.175],
  "waterline": 0.134,
  "cb": [2.439, 0.000, 0.089],
  "displacement": 100.91,
  "curves": [...],
  "profiles": [...]
}
```

### List All Hulls (GET)

```bash
curl http://localhost:8000/hulls/
```

Returns an array of summaries (name, description, length, beam, depth, volume, waterline, displacement).

### Get Full Hull Details (GET)

```bash
curl http://localhost:8000/hulls/Kayak%20001
```

Returns the complete `HullModel` including all curves, profiles, and computed properties.

### Update a Hull (PUT)

```bash
curl -X PUT http://localhost:8000/hulls/Kayak%20001 \
  -H "Content-Type: application/json" \
  -d '{ ... same format as POST ... }'
```

### Delete a Hull (DELETE)

```bash
curl -X DELETE http://localhost:8000/hulls/Kayak%20001
```

### Interactive API Documentation

The auto-generated Swagger UI is available at:
- **Development:** http://localhost:8000/docs
- **Docker:** http://localhost:8080/docs

You can try all endpoints directly from the browser.

---

## 5. Viewing Hull Visualizations

After selecting a kayak from the list:

1. The **Visualization** tab shows the hull curves drawn on a canvas.
2. Use the **View** dropdown to switch between projections:

| View | What it shows |
|------|---------------|
| **Isometric Side View** | Angled perspective showing length and depth |
| **Side View (X-Z)** | Profile from the side (length vs. height) |
| **Top View (X-Y)** | Plan view from above (length vs. beam) |
| **Front View (Y-Z)** | Cross-section from the bow (beam vs. height) |
| **3D Perspective** | Three-dimensional projection |

### Color Coding

| Element | Color | Meaning |
|---------|-------|---------|
| Dark blue lines | `#0000CC` | Curve segments above the waterline |
| Light blue lines | `#99CCFF` | Curve segments below the waterline |
| Red dots | `#CC0000` | Control points above the waterline |
| Pink dots | `#FFB3B3` | Control points below the waterline |
| Cyan line | `cyan` | Waterline plane |

---

## 6. Viewing Profile Cross-Sections

Switch to the **Profiles** tab to browse the transverse cross-sections generated during hull construction.

### Navigation

- Use the **Station dropdown** to jump to a specific x-position.
- Use the **< >** buttons to move one station forward/backward.
- Use the **<< >>** buttons to jump 10 stations at a time.

### What You See

- **Left canvas (Profile Cross-Section):** The Y-Z plane cross-section at the selected station, showing the hull shape as a closed polygon with the waterline marked.
- **Right canvas (Hull Side View):** The hull side silhouette with a vertical line indicating the current station position.

The station info shows the x-coordinate and station index (e.g., "Station 20 of 100 at x = 1.000 m").

---

## 7. Running Stability Analysis

### Via the Web UI

1. Select a kayak from the list.
2. Switch to the **Stability** tab.
3. Fill in the analysis parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| **Paddler Weight** | Weight of the paddler + gear (kg) | From hull `target_payload` |
| **Paddler CG Height** | Vertical position of paddler's center of gravity (m) | `0.25` |
| **Hull Weight** | Weight of the kayak hull (kg) | From hull `target_weight` |
| **Max Angle** | Maximum heel angle to simulate (degrees) | `90` |
| **Angle Step** | Increment between heel angles (degrees) | `3` |
| **Break on vanishing** | Stop calculation when GZ becomes negative | Unchecked |

4. Click **Analyze Stability**.
5. The system computes the equilibrium waterline at each heel angle and produces two graphs:

   - **GZ (Righting Arm) vs. Heel Angle** — shows how much the hull resists capsizing at each angle. Green area = positive stability, red area = negative stability.
   - **Righting Moment vs. Heel Angle** — the torque (in N·m) that acts to return the hull upright.

### Via the API

```bash
curl -X POST http://localhost:8000/hulls/kayak_001/stability \
  -H "Content-Type: application/json" \
  -d '{
    "hull_name": "Kayak 001",
    "paddler_weight": 80,
    "paddler_cg_z": 0.25,
    "hull_weight": 10,
    "max_angle": 90,
    "step": 3,
    "break_on_vanishing": false
  }'
```

### API Response

```json
{
  "vanishing_angle": 54.2,
  "max_moment": 187.3,
  "max_moment_angle": 27.0,
  "stability_points": [
    {
      "angle": 0.0,
      "gz": 0.0,
      "moment": 0.0,
      "waterline": 0.134,
      "displacement": 100.9
    },
    {
      "angle": 3.0,
      "gz": 0.0082,
      "moment": 72.4,
      "waterline": 0.135,
      "displacement": 100.8
    }
  ]
}
```

### Stability Parameters Reference

| Parameter | API Field | Type | Required | Description |
|-----------|-----------|------|----------|-------------|
| Hull name | `hull_name` | string | Yes | Name of the hull to analyze |
| Paddler weight | `paddler_weight` | float | No | Paddler + gear weight (kg). Defaults to hull's `target_payload` |
| Paddler CG Z | `paddler_cg_z` | float | No | Height of paddler's center of gravity (m). Default: `0.25` |
| Hull weight | `hull_weight` | float | No | Hull weight (kg). Defaults to hull's `target_weight` |
| Max angle | `max_angle` | float | No | Maximum heel angle (degrees). Default: `90` |
| Step | `step` | float | No | Angle increment (degrees). Default: `3` |
| Break on vanishing | `break_on_vanishing` | bool | No | Stop when GZ goes negative. Default: `false` |

---

## 8. Running Resistance Analysis

The resistance analysis feature estimates the force, power, and energy required to move your kayak at various speeds, based on the hull geometry and water conditions.

### Via the Web UI

1. Select a kayak from the list.
2. Switch to the **Resistance** tab.
3. Configure the analysis parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| **Speed Unit** | Choose between m/s, km/h, or knots | `km/h` |
| **Min Speed** | Starting speed for the analysis | `1` (depends on unit) |
| **Max Speed** | Ending speed for the analysis | `10` (depends on unit) |
| **Speed Step** | Increment between speed points | `0.5` (depends on unit) |
| **Water Type** | Fresh water or salt water (affects density) | `Fresh` |
| **Propulsion Efficiency** | Paddle efficiency (0.0-1.0) | `0.60` (60%) |
| **Roughness Allowance** | Hull surface roughness coefficient | `0.0004` |

**Roughness Allowance Guide:**
- `0.0002`: Very smooth (polished composite)
- `0.0004`: Standard kayak finish (gelcoat, thermoformed plastic)
- `0.0006`: Rougher surfaces (worn or textured)

4. Click **Analyze Resistance**.
5. The system computes:
   - Hull form coefficients (block, prismatic, midship, waterplane)
   - Wetted surface area and waterline dimensions
   - Hull speed estimate
   - Resistance components (frictional and wave-making) at each speed
   - Power requirements (effective power and paddler power)

6. Results are displayed as:
   - **Parameters table**: Hull speed, waterline dimensions, wetted surface, form coefficients
   - **Total Resistance vs. Speed graph**: Shows how drag force increases with speed
   - **Resistance Components graph**: Breakdown of frictional (blue) and residuary/wave (red) resistance
   - **Power Requirements graph**: Effective power and paddler power needed at each speed

### Via the API

```bash
curl -X POST http://localhost:8000/hulls/kayak_001/resistance \
  -H "Content-Type: application/json" \
  -d '{
    "hull_name": "Kayak 001",
    "speed_unit": "kmh",
    "min_speed": 1.0,
    "max_speed": 10.0,
    "speed_step": 0.5,
    "water_type": "fresh",
    "propulsion_efficiency": 0.60,
    "roughness_allowance": 0.0004
  }'
```

### API Response

```json
{
  "hull_speed_ms": 2.89,
  "hull_speed_kmh": 10.4,
  "hull_speed_knots": 5.62,
  "waterline_length": 4.95,
  "waterline_beam": 0.58,
  "wetted_surface": 2.35,
  "block_coefficient": 0.48,
  "prismatic_coefficient": 0.55,
  "midship_coefficient": 0.87,
  "waterplane_coefficient": 0.73,
  "resistance_points": [
    {
      "speed": 1.39,
      "speed_kmh": 5.0,
      "speed_knots": 2.7,
      "froude_number": 0.20,
      "reynolds_number": 5.8e6,
      "friction_coefficient": 0.00304,
      "residuary_coefficient": 0.00001,
      "frictional_resistance": 6.3,
      "residuary_resistance": 0.02,
      "total_resistance": 6.32,
      "effective_power": 8.78,
      "paddler_power": 14.6
    }
  ]
}
```

### Resistance Parameters Reference

| Parameter | API Field | Type | Required | Description |
|-----------|-----------|------|----------|-------------|
| Hull name | `hull_name` | string | Yes | Name of the hull to analyze |
| Speed unit | `speed_unit` | string | No | `"ms"`, `"kmh"`, or `"knots"`. Default: `"ms"` |
| Min speed | `min_speed` | float | No | Minimum speed in selected unit. Default: `0.5` m/s |
| Max speed | `max_speed` | float | No | Maximum speed in selected unit. Default: `3.5` m/s |
| Speed step | `speed_step` | float | No | Speed increment. Default: `0.1` in selected unit |
| Water type | `water_type` | string | No | `"fresh"` (1000 kg/m³) or `"salt"` (1025 kg/m³). Default: `"fresh"` |
| Propulsion efficiency | `propulsion_efficiency` | float | No | Paddle efficiency (0-1). Default: `0.60` |
| Roughness allowance | `roughness_allowance` | float | No | Surface roughness coefficient. Default: `0.0004` |

### Understanding the Results

**Hull Form Coefficients:**
- **Block Coefficient ($C_b$)**: Fullness of hull relative to a rectangular box. Lower = finer hull. Typical kayaks: 0.45–0.55
- **Prismatic Coefficient ($C_p$)**: How volume is distributed along length. Lower = ends are finer. Typical kayaks: 0.50–0.60
- **Midship Coefficient ($C_m$)**: Fullness of the largest cross-section. Typical kayaks: 0.80–0.90
- **Waterplane Coefficient ($C_{wp}$)**: Fullness of waterplane area. Affects initial stability. Typical kayaks: 0.70–0.80

**Resistance Components:**
- **Frictional Resistance**: Viscous drag on wetted surface (70–90% of total at typical paddling speeds)
- **Residuary Resistance**: Wave-making and pressure drag (becomes significant near hull speed)
- **Total Resistance**: Sum of frictional and residuary components

**Power:**
- **Effective Power**: Power needed to overcome hull resistance (ignores propulsion losses)
- **Paddler Power**: Actual power the paddler must produce (accounts for paddle efficiency)

**Hull Speed**: Theoretical maximum displacement speed, approximately $1.34 \sqrt{L_{WL}}$ knots. Resistance increases dramatically beyond this speed.

---

## 9. Editing and Deleting Hulls

### Edit (Web UI)

1. Hover over a kayak in the list to reveal the **edit** (pencil) button.
2. Click it to open the Edit modal, pre-filled with the current hull data.
3. Modify any field (name, metadata, curves).
4. Click **Save Changes** to rebuild and recalculate the hull.

### Edit (API)

```bash
curl -X PUT http://localhost:8000/hulls/Old%20Name \
  -H "Content-Type: application/json" \
  -d '{ ... updated CreateHullModel ... }'
```

If you change the name, the old `.hull` file is renamed.

### Delete (Web UI)

1. Hover over a kayak and click the **delete** (trash) button.
2. Confirm the deletion in the dialog.

### Delete (API)

```bash
curl -X DELETE http://localhost:8000/hulls/Kayak%20001
```

---

## 10. Understanding the Results

### Hull Summary

After creating or selecting a hull, the summary panel shows:

| Property | Description |
|----------|-------------|
| **Length** | Overall hull length (m), from stern to bow |
| **Beam** | Maximum hull width (m), port to starboard |
| **Depth** | Maximum hull depth (m), keel to gunwale |
| **Volume** | Total enclosed volume (m³) |
| **Waterline** | Equilibrium waterline height (m) for the target weight |
| **Displacement** | Weight of water displaced (kg) — should match total weight |

Click **+ Details** to see the full list of curves and profiles with their point data.

### Stability Analysis Results

| Metric | Description |
|--------|-------------|
| **GZ (Righting Arm)** | Horizontal distance (m) between the center of gravity and center of buoyancy when heeled. Positive = self-righting. |
| **Righting Moment** | The torque (N·m) that acts to return the hull upright: `moment = weight × g × GZ`. |
| **Vanishing Angle** | The heel angle where GZ crosses zero — beyond this angle, the hull will capsize. |
| **Max Righting Moment** | The peak restoring torque and the angle at which it occurs. |

### Interpreting the GZ Curve

- A **steep initial slope** means high initial stability (the kayak feels "stiff").
- A **gentle initial slope** means lower initial stability (the kayak feels "tender" or "tippy") but may have a wider range of positive stability.
- The **area under the GZ curve** represents the total energy needed to capsize the kayak.
- A higher **vanishing angle** means the kayak can recover from more extreme heels.

---

## 11. Sample Hull Data

### Minimal Example (2 curves)

A simple hull with just a gunwale and keel:

**UI format:**
```
curve: starboard gunnel
0.00, 0.00, 0.30
2.50, 0.25, 0.28
5.00, 0.00, 0.30

curve: keel
0.00, 0.00, 0.30
0.50, 0.00, 0.00
4.50, 0.00, 0.00
5.00, 0.00, 0.30
```

### Standard Example (3 curves)

A hull with gunwale, chine, and keel:

**UI format:**
```
curve: starboard gunnel
0.00, 0.00, 0.30
1.00, 0.18, 0.28
2.00, 0.30, 0.28
3.00, 0.30, 0.28
4.00, 0.14, 0.28
5.00, 0.00, 0.30

curve: starboard chine
0.20, 0.00, 0.16
1.00, 0.12, 0.12
2.00, 0.22, 0.11
3.00, 0.22, 0.11
4.00, 0.10, 0.12
4.70, 0.00, 0.16

curve: keel
0.00, 0.00, 0.30
0.20, 0.00, 0.16
0.50, 0.00, 0.00
4.20, 0.00, 0.00
4.70, 0.00, 0.16
5.00, 0.00, 0.30
```

### Tips for Hull Design

- The **bow and stern** are where curves converge to y = 0 (the centerline). They usually share elevated z values (the hull rises at the ends).
- The **keel** always has y = 0 on all points. Its lowest z values define the bottom of the hull.
- **More curves** = better hull shape resolution. A gunwale, one or two chines, and a keel give good results for most kayak shapes.
- Each curve should span from near the **stern (low x)** to near the **bow (high x)**.
- Curves don't need to start and end at the same x — the system interpolates within each curve's x-range.

---

## 12. Tips and Best Practices

### General

- All values use **metric units** (meters, kilograms). Water density is 1000 kg/m³.
- Set a reasonable **target waterline** (typically 1/4 to 1/3 of hull depth) to speed up waterline convergence.
- The **target payload** should include the paddler, gear, and any cargo.
- The **target weight** is just the empty hull weight.

### Stability Analysis

- Start with **3° steps** for a good balance of resolution and speed.
- Use **smaller steps** (e.g., 1°) around angles of interest for more precise results.
- A **paddler CG height** of 0.25 m is typical for a seated paddler; increase it for a higher seating position.
- Enable **Break on vanishing** to speed up analysis when you only need the positive stability range.

### Resistance Analysis

- **Speed ranges**: Start with 1–10 km/h for recreational paddling, or 1–8 km/h for typical touring speeds
- **Hull speed**: Resistance increases dramatically beyond hull speed (typically 8–12 km/h for kayaks). This represents the theoretical maximum for displacement hulls
- **Propulsion efficiency**: 0.60 (60%) is typical for recreational paddlers. Experienced paddlers may achieve 0.65–0.70; beginners closer to 0.50
- **Water type**: Use "salt" for ocean kayaking (slightly higher resistance due to increased density and buoyancy shift)
- **Interpreting curves**:
  - Frictional resistance dominates at low speeds (linear-ish growth with V²)
  - Residuary resistance becomes significant near Froude number 0.35–0.40
  - Power requirements grow as V³, so doubling speed requires ~8× more power
- **Form coefficients**:
  - Lower $C_b$ and $C_p$ = finer hull = lower wave resistance but possibly wetter ride
  - Higher $C_b$ and $C_p$ = fuller hull = more cargo capacity but higher resistance
  - Use resistance analysis to compare design tradeoffs

### Curve Data Quality

- Ensure your points form a **smooth progression** — avoid sharp jumps in y or z between adjacent points.
- The stern and bow points of different curves don't all need to meet at the same point, but they should converge near the centerline (y → 0).
- Use **6-10 control points per curve** for a typical 5 m kayak. More points give finer control over the shape.
- The spline interpolation will smooth the shape between your control points — you don't need to provide dense point sets.

### API Usage

- Use the **Swagger UI** at `/docs` to explore and test the API interactively.
- Hull names are case-sensitive in the API. The filename on disk is a sanitized lowercase version.
- After creating a hull, you can retrieve its full data (including generated profiles) via `GET /hulls/{name}`.
