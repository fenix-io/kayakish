# Resistance & Performance Analysis — Planning Document

## Overview

This document describes the plan for adding **hull resistance and performance estimation** to Kayakish. The goal is to estimate the force, power, and energy required to move a kayak at a given speed, based on the hull geometry already defined in the system.

---

## 1. Existing Building Blocks

The current codebase already provides:

| Component | Module | What it gives us |
|---|---|---|
| Hull shape from curves/profiles | `src/geometry/hull.py` | Full 3D hull definition |
| Waterline calculation (iterative) | `Hull._calculate_waterline()` | Displacement-based waterline finding |
| Volume & center of buoyancy | `Hull._calculate_profiles_volume_and_cg()` | Displaced volume, CB position |
| Cross-section slicing | `Hull._get_points_at(x)` | Arbitrary station evaluation |
| Submerged cross-section | `Hull._get_points_below_waterline()` | Waterline clipping of profiles |
| Overall dimensions | `Hull.length()`, `beam()`, `depth()` | LOA, max beam, max depth |
| Profile area calculation | `Profile.calculate_area()` | Cross-section area (shoelace formula) |

---

## 2. New Calculations Required

### 2.1. Wetted Surface Area ($S_w$)

**Purpose**: Total area of hull surface in contact with water below the waterline. This is the primary input for frictional resistance.

**Method**: For each cross-section at station $x$:
1. Get the submerged profile points (already available via `_get_points_below_waterline`)
2. Compute the **wetted perimeter** — the arc length of the submerged portion of the profile (sum of Euclidean distances between consecutive below-waterline points)
3. Integrate the wetted perimeter along the hull length using the trapezoidal rule:

$$S_w = \int_0^{L} P_w(x) \, dx \approx \sum_{i} \frac{P_w(x_i) + P_w(x_{i+1})}{2} \Delta x$$

**Difficulty**: Medium — new geometry calculation, but follows the same pattern as volume integration.

---

### 2.2. Waterline Length ($L_{WL}$) and Waterline Beam ($B_{WL}$)

**Purpose**: The length and maximum width of the hull at the waterline. These are key inputs to all resistance formulas.

**Method**:
- $L_{WL}$: Find the most forward and most aft stations where the waterline intersects the hull.
- $B_{WL}$: Find the maximum beam at the waterline across all stations.

**Difficulty**: Easy — minor extension of existing waterline code.

---

### 2.3. Hull Form Coefficients

Dimensionless ratios that characterize the hull shape:

| Coefficient | Formula | Description |
|---|---|---|
| **Block Coefficient** $C_b$ | $\frac{\nabla}{L_{WL} \times B_{WL} \times T}$ | Fullness of hull relative to bounding box |
| **Prismatic Coefficient** $C_p$ | $\frac{\nabla}{A_{max} \times L_{WL}}$ | Volume distribution along the length |
| **Midship Coefficient** $C_m$ | $\frac{A_{max}}{B_{WL} \times T}$ | Fullness of the midship section |
| **Waterplane Coefficient** $C_{wp}$ | $\frac{A_{wp}}{L_{WL} \times B_{WL}}$ | Fullness of waterplane area |

Where:
- $\nabla$ = displaced volume (m³)
- $T$ = draft (waterline depth, m)
- $A_{max}$ = maximum submerged cross-section area (m²)
- $A_{wp}$ = waterplane area (m²)

**Difficulty**: Easy — derived from existing volume/area calculations.

---

### 2.4. Resistance Calculation

Total resistance of a displacement hull:

$$R_{total} = R_f + R_r$$

#### 2.4.1. Frictional Resistance ($R_f$)

Well-established formulation:

$$R_f = \frac{1}{2} \rho V^2 S_w C_f$$

Where:
- $\rho$ = water density (1000 kg/m³ for fresh water, 1025 for salt water)
- $V$ = boat speed (m/s)
- $S_w$ = wetted surface area (m²)
- $C_f$ = frictional resistance coefficient

$C_f$ is computed using the **ITTC 1957 friction line**:

$$C_f = \frac{0.075}{(\log_{10} Re - 2)^2}$$

Reynolds number:

$$Re = \frac{V \times L_{WL}}{\nu}$$

Where $\nu$ is the kinematic viscosity of water ($\approx 1.19 \times 10^{-6}$ m²/s at 15°C).

**Difficulty**: Easy — standard formula, ~20 lines of code.

#### 2.4.2. Residuary (Wave-Making) Resistance ($R_r$)

This is the harder part. Residuary resistance captures wave generation and pressure effects.

**Froude Number** — the key dimensionless speed:

$$F_n = \frac{V}{\sqrt{g \times L_{WL}}}$$

For kayaks at typical paddling speeds (3–8 km/h), $F_n$ is usually 0.2–0.5.

**Approach options**:

1. **Empirical $C_r$ vs $F_n$ lookup**: Use published residuary resistance coefficient data for slender displacement hulls. The coefficient $C_r$ is then applied as:

$$R_r = \frac{1}{2} \rho V^2 S_w C_r(F_n, C_p)$$

2. **Holtrop-Mennen method (simplified)**: A regression-based method widely used in ship design. It uses form coefficients ($C_p$, $C_m$, etc.) and hull dimensions to estimate wave resistance. This gives better accuracy for different hull shapes.

3. **Hull speed concept**: For rough estimates, resistance grows approximately as $V^4$ near hull speed:
   - **Hull speed**: $V_{hull} = 1.34 \sqrt{L_{WL} \text{ (ft)}}$ knots $\approx 2.43 \sqrt{L_{WL} \text{ (m)}}$ km/h
   - Below ~$F_n = 0.35$: wave resistance is small
   - Above ~$F_n = 0.40$: wave resistance dominates and grows rapidly

**Recommended**: Start with option 1 (empirical $C_r$ lookup for slender hulls), then optionally add Holtrop-Mennen later for better accuracy.

**Difficulty**: Medium-Hard — needs a suitable empirical model; accuracy depends on the method chosen.

---

### 2.5. Power and Force Output

Once total resistance $R_{total}$ is known at speed $V$:

$$F = R_{total} \quad \text{(force in Newtons)}$$

$$P_{effective} = R_{total} \times V \quad \text{(effective power in Watts)}$$

To account for propulsion efficiency (paddle efficiency $\eta_p \approx 0.5–0.7$):

$$P_{paddler} = \frac{P_{effective}}{\eta_p}$$

Energy for a given distance $d$ at constant speed:

$$E = P_{paddler} \times \frac{d}{V} = \frac{R_{total} \times d}{\eta_p}$$

**Difficulty**: Easy — just arithmetic on top of resistance calculation.

---

## 3. Key Physical Considerations for Kayaks

- **Frictional resistance dominates** at typical paddling speeds (3–8 km/h), contributing 70–90% of total resistance.
- **Wave-making resistance** becomes significant only near hull speed and above.
- **Surface roughness**: Kayak hulls vary (gelcoat, thermoformed plastic, composites). An allowance coefficient $\Delta C_f \approx 0.0004$ can be added for roughness.
- **Appendage drag**: Rudders and skegs add 2–5% resistance. Can be included as a simple multiplier.
- **Air resistance**: Negligible at kayak speeds, but could be added as $R_{air} = \frac{1}{2} \rho_{air} V^2 A_{frontal} C_d$ for completeness.
- **Symmetry assumption**: The hull is symmetric about the centerline, consistent with existing code.

---

## 4. Difficulty Summary

| Component | Difficulty | Estimated Effort |
|---|---|---|
| Wetted surface area | Medium | 0.5 day |
| Waterline length/beam | Easy | 0.25 day |
| Form coefficients | Easy | 0.25 day |
| Frictional resistance (ITTC) | Easy | 0.25 day |
| Residuary resistance (empirical) | Medium-Hard | 1 day |
| Power/force/energy curves | Easy | 0.25 day |
| API route + visualization | Easy | 0.5 day |
| Unit tests | Medium | 0.5 day |
| **Total** | | **~3 days** |

---

## 5. Proposed Implementation Architecture

### New Modules

- **`src/analysis/resistance.py`** — Core resistance calculations (ITTC friction, residuary, total resistance, power curves)
- **`src/analysis/hull_parameters.py`** — Wetted surface area, waterline dimensions, form coefficients

### Modified Modules

- **`src/geometry/hull.py`** — Add methods for waterline length, waterline beam, wetted perimeter integration
- **`src/geometry/profile.py`** — Add `wetted_perimeter()` method for submerged profiles
- **`src/routes/hull.py`** — Add API endpoint for resistance/performance analysis
- **`visualization/`** — Add resistance curve visualization

### Output

For a given hull and speed range, produce:
- **Resistance vs. Speed** curve (total, frictional, residuary components)
- **Power vs. Speed** curve (effective power and paddler power)
- **Froude number** at each speed
- **Hull speed** estimate
- **Key parameters** table (wetted surface, form coefficients, etc.)

---

## 6. References

- ITTC (1957) — Friction resistance correlation line
- Holtrop, J. & Mennen, G.G.J. (1982) — "An approximate power prediction method"
- Winters, J. — "The Shape of the Canoe" (empirical resistance data for canoes/kayaks)
- Marchaj, C.A. — "Sail Performance" (resistance components for displacement hulls)
- Froude, W. — Original wave resistance formulation

---

## 7. Future Extensions

- **Added resistance in waves**: Estimate power increase in rough conditions
- **Parametric hull optimization**: Vary hull form coefficients to minimize resistance at target speed
- **Comparison mode**: Compare resistance curves of multiple hull designs
- **CFD validation**: Compare empirical estimates with computational fluid dynamics results
