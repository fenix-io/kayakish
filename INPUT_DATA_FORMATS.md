# Kayak Hull Data Formats

This document describes the supported file formats for loading and saving kayak hull geometry in the kayak calculation tool.

## Table of Contents

- [Overview](#overview)
- [JSON Format](#json-format)
- [Metadata Fields](#metadata-fields)
- [Coordinate System](#coordinate-system)
- [Examples](#examples)
- [Validation Rules](#validation-rules)

---

## Overview

The kayak calculation tool supports a primary file formats for hull geometry:

1. **JSON** - Complete format with metadata and structured profile data

Both formats can represent the same hull geometry and can be converted between each other using the provided tools.

### Supported File Extensions

- `.json` - JSON format
---

## JSON Format

The JSON format provides a complete, structured representation of the kayak hull with explicit metadata and profile organization.

### Structure

```json
{
  "metadata": {
    "name": "string (optional)",
    "description": "string (optional)",
    "units": "string (required)",
    "target_waterline": number (required),
    "target_payload": number (required)
  },
  "profiles": [
    {
      "station": number,
      "port_points": [
        {
          "y": number,
          "z": number
        }
      ]
    }
  ]
}
```

### Field Descriptions

#### Metadata Section

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | No | - | Descriptive name for the kayak hull |
| `description` | string | No | - | Detailed description of the hull |
| `units` | string | Yes | "metric" | Length unit: `metric (m, kg)`, `imperial (ft, lb)` |
| `weight` | number | Yes | 20 | Weight of the Hull | 
| `target_draft` | number | No | - | Target distance between the deepest part of the hull and the waterline  |
| `target_payload` | number | No | - | Overall weight that the hull |

#### Coordinate Systems

**Important:** The coordinate system determines where x=0 is located:
- **`stern_origin`**: Origin at stern (back). x increases toward bow. x=0 is stern, x=length is bow.


#### Profiles Section

All the hull will be modeled using point on ist surface. This points should arranged in vertical profiles on the plane YZ.
So all point en one given profiles will share the same x coordinate.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `station` | number | Yes | Longitudinal position along the hull (x-coordinate) |
| `port_points` | array | Yes | Array of points defining the cross-section from the centerline to the port section at this station 

Definition must include a profile at the stern containig only the apex, and a last one at the bow containig also the apex.
Close to the bow or the stern the definition can include other profiles with only one point on the centerline. But the first one and the last one must contain only one point.



**Note:** The y coordinates will be positive goint to port and negative to starboard.

### Complete JSON Example

```json
{
  "metadata": {
    "name": "Sea Kayak Pro",
    "description": "High-performance sea kayak with excellent stability",
    "units": "metric",
    "hull_weight": 10,
    "target_waterline": 0.1,
    "target_payload": 100
  },
  "profiles": [
    {
      "station": 0.0,
      "port_points": [
        {"y": 0.0, "z": 0.30}
      ]
    },
    {
      "station": 1.0,
      "points": [
        {"y": 0.00, "z": 0.30},
        {"y": 0.18, "z": 0.28},
        {"y": 0.12, "z": 0.15},
        {"y": 0.09, "z": 0.05},
        {"y": 0.00, "z": 0.00}
      ]
    },
    {
      "station": 3.0,
      "points": [
        {"y": 0.00, "z": 0.30},
        {"y": 0.30, "z": 0.28},
        {"y": 0.20, "z": 0.15},
        {"y": 0.15, "z": 0.05},
        {"y": 0.00, "z": 0.00}
      ]
    },
    {
      "station": 4.0,
      "points": [
        {"y": 0.00, "z": 0.35},
        {"y": 0.28, "z": 0.28},
        {"y": 0.18, "z": 0.15},
        {"y": 0.12, "z": 0.05},
        {"y": 0.00, "z": 0.00}
      ]
    },
    {
      "station": 5.0,
      "port_points": [
        {"y": 0.0, "z": 0.30}
      ]
    }
  ]
}
```


## Coordinate System

### Axis Orientation

The kayak calculation tool uses a right-handed coordinate system:

```
        Z (up)
        ↑  ↑ Y (transverse)
        | /
        |/
        o----→ X (longitudinal)
    
```

**Conventions:**
- **X-axis**: Longitudinal direction (along kayak length)
  - Positive: Forward/bow direction
  - Increases from bow to stern

- **Y-axis**: Transverse direction (across kayak width)
  - `y = 0`: Centerline plane (plane of symmetry)
  - Positive (`y > 0`): Port (left side when facing forward)
  - Negative (`y < 0`): Starboard (right side when facing forward)

- **Z-axis**: Vertical direction
  - Positive (`z > 0`): Upward
  - Negative (`z < 0`): Downward
  - `z = 0`: Hull lower point reference plane

### Profile Organization

- **Profile**: A transverse cross-section at a specific longitudinal position (station)
- **Station**: The x-coordinate (longitudinal position) of a profile
- **Points**: 3D coordinates defining the hull surface at that cross-section

### Symmetry

The hull is assumed to be symmetric about the centerline (y=0):
- Each point at `(x, y, z)` with `y > 0`, will be matched with a corresponding point at `(x, -y, z)`
- Points exactly on the centerline have `y = 0`

### Profile Point Ordering

**Critical for accurate calculations:** Points within each profile must be ordered consistently.

**Recommended ordering (port → keel → starboard):**
1. Start at **port side** (y < 0) at deck
2. Progress **downward** along port side  
3. Continue through **keel** (y = 0, lowest point)

**Example point sequence for a kayak profile:**
```
Point 0: Port deck edge       (x, y=-0.30, z=0.20)   ← Start here
Point 1: Port chine           (x, y=-0.28, z=0.00)   ↓
Point 2: Port bilge           (x, y=-0.25, z=-0.15)  ↓
Point 3: Keel (centerline)    (x, y=0.00,  z=-0.20)  ← Lowest point
```

**Why consistent ordering matters:**
- Ensures correct cross-sectional area calculations (shoelace formula)
- Maintains proper waterline intersection detection
- Enables accurate longitudinal interpolation between profiles
- Prevents surface normal reversals
- Avoids twisted interpolated sections

**Important:** Use the **same traversal direction** for **ALL** profiles. Mixing directions (e.g., up→down on one profile, down→up on another) will cause calculation errors.

---

## Validation Rules

### Required Constraints

1. **Minimum profiles**: At least 3 profiles required: stern, one station, bow
2. **Minimum points per profile**: At least 1 point required
4. **Unique stations**: Each profile must have a unique station value
5. **Finite values**: All coordinates must be finite numbers (no NaN or Inf)

### Recommended Best Practices
2. **Centerline points**: Include points on centerline (y=0) for accuracy
3. **Station spacing**: Use reasonable spacing between stations
4. **Point density**: More points in areas of high curvature
5. **Waterline coverage**: Include points above and below anticipated waterlines
6. **Ordering**: Order stations from stern to bow consistently

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Missing required field" | Required metadata or data field omitted | Add missing field or let defaults apply |
| "x-coordinate doesn't match station" | Point x ≠ profile station | Ensure all points have x = station |
| "At least 3 profiles required" | Hull has < 3 profiles | Add more profiles |
| "Duplicate stations found" | Multiple profiles at same station | Ensure each profile has unique station |
| "Invalid unit" | Unrecognized unit string | Use: `metric` or `imperial` |
| "NaN or Inf value" | Non-finite number in data | Check for calculation errors in input |

---


## Additional Resources

- **Sample Files**: See `data/` directory for example hull geometries
- **Examples**: See `examples/data_input_examples.py` for usage examples
- **API Documentation**: See module docstrings in `src/io/`
- **Implementation Details**: See `docs/PHASE7_TASK7.1_SUMMARY.md`

---


## Support

For questions or issues with data formats:
1. Check sample files in `data/` directory
2. Review examples in `examples/data_input_examples.py`
3. Run validation: `validate_hull_data(data)`
4. Check error messages for specific issues
