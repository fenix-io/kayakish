# Kayak Hydrostatics and Stability - Glossary of Terms

**Version:** 1.0  
**Date:** December 26, 2025

This glossary defines technical terms used throughout the kayak calculation library, including code, documentation, examples, and output files. Terms are organized alphabetically for easy reference.

---

## A

### Apex Point
A single point at the extreme bow (front) or stern (rear) of the kayak where the hull tapers to a point. Legacy format for defining bow/stern geometry. Creates a simple pyramid/cone closure from the nearest profile station.

**Context:** Geometry, Interpolation, Legacy Format  
**Related Terms:** Bow Point, Stern Point, Multi-Point Bow/Stern, Profile  
**Note:** Multi-point bow/stern arrays provide more control over end geometry than single apex points.

### Area Under Curve
The integral of the GZ curve over a range of heel angles, representing dynamic stability or the energy required to capsize the vessel. Measured in meter-radians (m·rad).

**Units:** m·rad (meter-radians)  
**Context:** Stability Analysis  
**Related Terms:** Dynamic Stability, GZ Curve, Stability

### Aspect Ratio
The ratio of a hull's length to its beam (width). Used in validation and design analysis.

**Formula:** Length / Beam  
**Context:** Hull Design, Validation  
**Related Terms:** Beam, Length

---

## B

### Beam
The maximum width of the kayak hull, typically measured at the widest point of the cockpit area. A wider beam generally increases initial stability but may reduce speed.

**Units:** meters (m)  
**Context:** Hull Geometry  
**Related Terms:** Width, Hull, Aspect Ratio

### Bow
The front end of the kayak. The bow profile is the transverse cross-section at the forward-most station.

**Context:** Hull Geometry  
**Related Terms:** Stern, Profile, Apex Point

### Buoyancy
The upward force exerted by water on the submerged portion of the kayak, equal to the weight of water displaced (Archimedes' principle).

**Formula:** Buoyancy = Volume × Water Density × g  
**Units:** Newtons (N) or kg  
**Context:** Hydrostatics  
**Related Terms:** Displacement, Center of Buoyancy, Archimedes' Principle

### Buoyant Force
See **Buoyancy**

### Block Coefficient ($C_b$)
A dimensionless ratio describing the fullness of the hull relative to its bounding rectangular box below the waterline.

**Formula:** $C_b = \frac{\nabla}{L_{WL} \times B_{WL} \times T}$

**Inputs:**
- $\nabla$ — Displaced volume (m³)
- $L_{WL}$ — Waterline length (m)
- $B_{WL}$ — Waterline beam (m)
- $T$ — Draft (m)

**Output:** Dimensionless (0 to 1)

**Interpretation:** If you drew a rectangular box $L_{WL} \times B_{WL} \times T$ around the underwater hull, $C_b$ is the fraction of that box the hull fills. A value of 1.0 would be a rectangular barge; a kayak typically has $C_b \approx 0.25\text{–}0.40$.

**Typical values:**
- Kayak: 0.25–0.40
- Sailboat: 0.35–0.45
- Cargo ship: 0.80–0.85

**Usage downstream:** Input to wave resistance estimation methods (e.g., Holtrop-Mennen). Lower $C_b$ generally means lower wave resistance at the same displacement. Related to the other form coefficients by $C_b = C_p \times C_m$.

**Context:** Resistance Analysis, Hull Form
**Related Terms:** Prismatic Coefficient, Midship Coefficient, Displacement, Waterline Length
**Implementation:** Computed by `calculate_block_coefficient()` in `src/analysis/hull_parameters.py`. Used as an output metric in the `/hulls/{name}/resistance` API endpoint.

---

## C

### Capsize
The act of a kayak overturning beyond its angle of vanishing stability, resulting in loss of upright orientation.

**Context:** Stability Analysis  
**Related Terms:** Vanishing Stability, Angle of Vanishing Stability, Stability Range

### CB
Abbreviation for **Center of Buoyancy**

### Centerline
The vertical longitudinal plane of symmetry running through the middle of the kayak from bow to stern. The y-coordinate = 0 in the coordinate system.

**Context:** Coordinate System, Geometry  
**Related Terms:** Coordinate System, Symmetry, Transverse

### Center of Buoyancy (CB)
The centroid (geometric center) of the displaced volume of water. The point through which the buoyant force acts vertically upward.

**Coordinates:** (LCB, TCB, VCB)  
**Units:** meters (m)  
**Context:** Hydrostatics  
**Related Terms:** LCB, VCB, TCB, Buoyancy, Centroid

### Center of Gravity (CG)
The point through which the total weight of the kayak (including paddler and gear) acts vertically downward. Also called center of mass.

**Coordinates:** (LCG, TCG, VCG)  
**Units:** meters (m)  
**Context:** Mass Distribution, Stability  
**Related Terms:** LCG, VCG, TCG, Mass, Weight

### Centroid
The geometric center of a shape or volume. For a profile, it's the center of area; for displaced volume, it's the center of buoyancy.

**Context:** Geometry, Hydrostatics  
**Related Terms:** Center of Buoyancy, Center of Gravity

### CG
Abbreviation for **Center of Gravity**

### Chine
An angular edge or corner in the hull cross-section, as opposed to a smooth rounded shape. Multi-chine hulls have multiple angular transitions.

**Context:** Hull Design  
**Related Terms:** Profile, Cross-Section, Hull Shape

### Chord Length Parametrization
A method of parametrizing a spline curve by the cumulative Euclidean distance (chord length) between consecutive control points. Used when the curve is not monotonic in x (e.g., bow/stern sections that double back). Allows evaluation at any x-coordinate using root-finding (Brent's method).

**Context:** Geometry, Spline Interpolation  
**Related Terms:** Spline, PCHIP, Control Points, Parametrization

### Cockpit
The opening in the deck where the paddler sits. The cockpit area typically has the maximum beam width.

**Context:** Hull Design  
**Related Terms:** Deck, Seating Position

### Coordinate System
The reference frame used to define positions on the kayak:
- **x-axis:** Longitudinal, stern (x=0) to bow (positive x)
- **y-axis:** Transverse, centerline (y=0) to starboard (positive y), port is negative y
- **z-axis:** Vertical, deepest hull point (z=0) upward (positive z)
- **Origin:** On the centerline, at the stern projection, at the deepest hull point

**Context:** Geometry, Mathematics  
**Related Terms:** Axes, Origin, Station

### Cross-Section
A slice through the hull perpendicular to the longitudinal axis, showing the profile shape at that station.

**Context:** Geometry  
**Related Terms:** Profile, Station, Transverse

### Curve
A named hull curve defined by a series of 3D control points, extending the Spline3D class. Each curve represents a longitudinal feature of the hull (e.g., keel, chine, gunwale). Curves carry a `mirrored` flag indicating whether they were auto-generated as a port/starboard mirror during the hull build process.

**Code class:** `Curve` in `src/geometry/curve.py`  
**Context:** Geometry, Hull Definition  
**Related Terms:** Spline, Control Points, Mirrored, Profile

---

## D

### Deck
The top surface of the kayak that covers the hull. The deck level is typically near the waterline on an unloaded kayak.

**Context:** Hull Geometry  
**Related Terms:** Hull, Cockpit

### Displacement
The volume of water displaced by the submerged portion of the kayak hull. By Archimedes' principle, this equals the mass of water whose weight equals the total weight of the kayak system.

**Units:** cubic meters (m³) for volume, kilograms (kg) for mass  
**Context:** Hydrostatics  
**Related Terms:** Volume, Buoyancy, Submerged Volume

### Draft
The vertical distance from the waterline to the deepest point of the hull. Represents how deep the kayak sits in the water.

**Units:** meters (m)  
**Context:** Hydrostatics  
**Related Terms:** Waterline, Depth, Submersion

### Dynamic Stability
The total energy required to capsize a vessel, represented by the area under the GZ curve from upright to the angle of vanishing stability. Larger area means more energy needed to capsize.

**Units:** m·rad (meter-radians)  
**Context:** Stability Analysis  
**Related Terms:** Area Under Curve, GZ Curve, Energy

---

## E

### Effective Power ($P_{eff}$)
The power required to overcome the total hull resistance at a given speed. This is the power "absorbed" by the water — the paddler must produce more due to paddle inefficiency.

**Formula:** $P_{eff} = R_{total} \times V$

**Inputs:**
- $R_{total}$ — Total hull resistance (N)
- $V$ — Boat speed (m/s)

**Units:** Watts (W). Derivation: $\text{N} \times \text{m/s} = \text{W}$

**Typical values for kayaks:**
- 5 km/h cruising: ~15–25 W
- 7 km/h brisk pace: ~30–50 W
- 10 km/h (hull speed for 5m kayak): ~150–200 W

**Usage downstream:** Divided by paddle efficiency $\eta_p$ to get paddler power.

**Context:** Resistance Analysis, Performance
**Related Terms:** Power, Paddler Power, Total Resistance, Paddle Efficiency
**Implementation:** Computed by `calculate_effective_power()` in `src/analysis/resistance.py`.

### Equilibrium
The state where the kayak floats with buoyant force exactly balancing the weight, and all moments are balanced (no net rotation).

**Context:** Hydrostatics, Stability  
**Related Terms:** Balance, Flotation, Trim

---

## F

### First Moment of Area
The integral of area multiplied by distance from a reference axis. Used to calculate centroids.

**Formula:** Q = ∫ y · dA  
**Units:** m³  
**Context:** Mathematics, Hydrostatics  
**Related Terms:** Centroid, Center of Buoyancy, Second Moment

### Flotation
The state of floating on water, achieved when buoyant force equals weight.

**Context:** Hydrostatics  
**Related Terms:** Buoyancy, Equilibrium, Waterline

### Frictional Resistance ($R_f$)
The drag force caused by the viscous interaction between the hull surface and the water flowing past it. For kayaks at typical paddling speeds, frictional resistance is the dominant component (70–90% of total).

**Formula:** $R_f = \frac{1}{2} \rho V^2 S_w C_f$

**Inputs:**
- $\rho$ — Water density (kg/m³): 1000 (fresh), 1025 (salt)
- $V$ — Boat speed (m/s)
- $S_w$ — Wetted surface area (m²)
- $C_f$ — Friction coefficient from ITTC 1957 (dimensionless)

**Units:** Newtons (N). Derivation: $\frac{\text{kg}}{\text{m}^3} \times \frac{\text{m}^2}{\text{s}^2} \times \text{m}^2 \times 1 = \frac{\text{kg} \cdot \text{m}}{\text{s}^2} = \text{N}$

**Example:** At 5.4 km/h (1.5 m/s), $S_w$ = 2.0 m², $C_f$ = 0.00326 → $R_f$ ≈ 7.3 N (~0.75 kg of force).

**Surface roughness correction:** An additive allowance $\Delta C_f$ may be applied: polished gelcoat +0.0002, thermoformed plastic +0.0004, rotomolded polyethylene +0.0006.

**Usage downstream:** Added to residuary resistance to form total resistance: $R_{total} = R_f + R_r$.

**Context:** Resistance Analysis, Hydrodynamics
**Related Terms:** ITTC 1957, Reynolds Number, Wetted Surface, Residuary Resistance, Total Resistance
**Implementation:** Computed by `calculate_frictional_resistance()` in `src/analysis/resistance.py`. Uses ITTC 1957 correlation line.

### Froude Number ($F_n$)
A dimensionless number describing the ratio of boat speed to the natural wave propagation speed for the hull. It is the primary parameter governing wave-making resistance.

**Formula:** $F_n = \frac{V}{\sqrt{g \times L_{WL}}}$

**Inputs:**
- $V$ — Boat speed (m/s)
- $g$ — Gravitational acceleration (9.81 m/s²)
- $L_{WL}$ — Waterline length (m)

**Output:** Dimensionless. Units cancel: $\frac{\text{m/s}}{\sqrt{\text{m/s}^2 \times \text{m}}} = 1$

**Speed regimes:**
| $F_n$ | Regime | Description |
|---|---|---|
| < 0.30 | Sub-hull speed | Wave resistance small (< 15% of total), friction dominates |
| ≈ 0.35 | Efficient cruise | Wave resistance growing but manageable |
| ≈ 0.40 | Hull speed | Wave resistance rises steeply — "the wall" |
| > 0.50 | Beyond hull speed | Wave resistance dominates (> 60%), enormous power for small speed gain |

**Example:** For a 5.0 m waterline kayak at 7.2 km/h (2.0 m/s): $F_n = 2.0 / \sqrt{9.81 \times 5.0} = 0.286$ — comfortable cruise regime.

**Usage downstream:** Primary input to residuary resistance lookup: $C_r = f(F_n, C_p)$.

**Context:** Resistance Analysis, Hydrodynamics
**Related Terms:** Hull Speed, Residuary Resistance, Waterline Length, Prismatic Coefficient
**Implementation:** Computed by `calculate_froude_number()` in `src/analysis/resistance.py`. Used as a primary input to residuary resistance estimation.

### Freeboard
The vertical distance from the waterline to the deck or gunwale. Represents the reserve buoyancy above water.

**Units:** meters (m)  
**Context:** Hull Design, Safety  
**Related Terms:** Waterline, Deck, Reserve Buoyancy

---

## G

### GM (Metacentric Height)
The vertical distance between the center of gravity (G) and the metacenter (M). A measure of initial stability. Larger GM means stiffer initial stability but may be uncomfortable.

**Units:** meters (m)  
**Formula:** GM = GZ / sin(φ) for small angles φ  
**Context:** Stability Analysis  
**Related Terms:** Metacenter, Initial Stability, Stiffness

### Gunwale
The upper edge of the hull where it meets the deck (pronounced "gunnel").

**Context:** Hull Design  
**Related Terms:** Hull, Deck, Edge

### GZ (Righting Arm)
The horizontal distance between the center of gravity and the vertical line through the center of buoyancy when the kayak is heeled. The moment arm for the righting moment.

**Units:** meters (m)  
**Formula:** Righting Moment = Weight × GZ  
**Context:** Stability Analysis  
**Related Terms:** Righting Arm, Righting Moment, Stability Curve

### GZ Curve
A plot of righting arm (GZ) versus heel angle, showing the kayak's stability characteristics across a range of angles. Also called a stability curve.

**Axes:** Heel angle (degrees) vs. GZ (meters)  
**Context:** Stability Analysis  
**Related Terms:** Stability Curve, Righting Arm, Heel Angle

---

## H

### Heel
Rotation of the kayak about its longitudinal axis (tilting side to side). Also called roll.

**Units:** degrees (°)  
**Context:** Stability, Transformation  
**Related Terms:** Roll, Lean, Heel Angle

### Heel Angle
The angle of rotation about the longitudinal axis, measured from upright position.

> **Convention note:** In standard naval architecture, positive heel = starboard down. However, the Kayakish codebase uses the **mathematical right-hand rule** for all rotations, where a positive angle about the X-axis rotates port down (starboard up). To simulate heel to starboard in code, pass a **negative** angle to `rotate_x()` or `apply_rotation_on_x_axis()`.

**Units:** degrees (°)  
**Range:** Typically 0° to 90°  
**Context:** Stability Analysis  
**Related Terms:** Heel, Roll Angle, Inclination

### Hull
The main body of the kayak that provides flotation and contains the paddler. The hull shape determines hydrostatic and stability properties.

**Context:** Geometry, Structure  
**Related Terms:** Profile, Cross-Section, Displacement

### Hydrostatics
The study of fluids at rest and the forces on objects submerged in or floating on fluids. For kayaks, this includes displacement, buoyancy, and centers of buoyancy.

**Context:** Physics, Analysis  
**Related Terms:** Buoyancy, Displacement, Flotation

### Hull File Format (.hull)
The JSON file format used by Kayakish to persist hull definitions on disk. Contains all hull metadata, curve definitions, and computed properties. Files are stored in the configured `DATA_PATH` directory and named using a sanitized version of the hull name.

**Extension:** `.hull`  
**Format:** JSON  
**Context:** Data Persistence, I/O  
**Related Terms:** Hull, Curve, sanitize_filename

### Hull Speed
The speed at which the bow wave and stern wave created by the hull reinforce each other, causing a dramatic increase in wave-making resistance. Corresponds approximately to Froude number $F_n \approx 0.40$.

**Formula:** $V_{hull} \approx 1.25 \times \sqrt{L_{WL}}$ (m/s), or equivalently $V_{hull} \approx 4.50 \times \sqrt{L_{WL}}$ (km/h)

**Inputs:**
- $L_{WL}$ — Waterline length (m)

**Units:** m/s or km/h

**Example:** For a 5.0 m waterline kayak: $V_{hull} \approx 1.25 \times \sqrt{5.0} \approx 2.8$ m/s ≈ 10 km/h.

**Interpretation:** Below hull speed, resistance grows moderately; above it, resistance increases very steeply. Exceeding hull speed requires disproportionate effort — a paddler at 90% hull speed might need only half the power of one paddling at 110% hull speed.

**Context:** Resistance Analysis, Performance
**Related Terms:** Froude Number, Waterline Length, Residuary Resistance, Wave-Making Resistance
**Note:** *Not currently computed by the application — planned for resistance analysis feature.*

---

## I

### Initial Stability
The stability of a vessel at small heel angles (typically < 10°). Characterized by the metacentric height (GM). High initial stability feels "stiff" but may be twitchy.

**Measure:** GM (metacentric height)  
**Context:** Stability Analysis  
**Related Terms:** GM, Metacentric Height, Stiffness

### Inclination
See **Heel**

### Integration
Numerical methods used to calculate volumes, areas, and centroids by summing contributions from discrete sections or elements.

**Methods used:** Shoelace Formula (area), Slab Integration (volume)  
**Context:** Mathematics, Calculation  
**Related Terms:** Numerical Integration, Shoelace Formula, Slab Integration, Volume Calculation

### Interpolation
Mathematical techniques for estimating values between known data points. Used extensively to create smooth hull curves from discrete control points.

**Types used:** PCHIP (primary, shape-preserving), CubicSpline (chord-length parametrization), Linear (waterline intersection)  
**Context:** Geometry, Mathematics  
**Related Terms:** PCHIP, Cubic Interpolation, Spline, Smoothing

### ITTC 1957 Friction Line
The internationally agreed-upon formula for computing the frictional resistance coefficient of a smooth flat plate at a given Reynolds number. Adopted by the International Towing Tank Conference in 1957 as the standard model–ship correlation line.

**Formula:** $C_f = \frac{0.075}{(\log_{10} Re - 2)^2}$

**Inputs:**
- $Re$ — Reynolds number (dimensionless)

**Output:** $C_f$ — Frictional resistance coefficient (dimensionless), typically ~0.002–0.004 for kayaks.

**Example:** At $Re$ = 6,300,000: $\log_{10}(6{,}300{,}000) = 6.799$ → $C_f = 0.075 / (6.799 - 2)^2 = 0.00326$.

**Usage downstream:** $C_f$ is multiplied by the dynamic pressure and wetted surface area to get frictional resistance: $R_f = \frac{1}{2} \rho V^2 S_w C_f$.

**Context:** Resistance Analysis, Hydrodynamics
**Related Terms:** Frictional Resistance, Reynolds Number, Wetted Surface
**Implementation:** Computed by `calculate_ittc_friction_coefficient()` in `src/analysis/resistance.py`. Used to determine frictional resistance coefficient.

---

## K

### Keel
The bottom centerline of the hull running from bow to stern. Many kayaks have a shallow keel or are flat-bottomed.

**Context:** Hull Design  
**Related Terms:** Centerline, Bottom, Hull

### Kayak
A small, narrow watercraft propelled by a double-bladed paddle, typically with a closed deck and low seating position.

**Types:** Recreational, touring, sea kayak, whitewater  
**Context:** Vessel Type  
**Related Terms:** Hull, Canoe, Small Craft

### Kinematic Viscosity ($\nu$)
A physical property of water describing its resistance to flow under gravity. Depends on water temperature.

**Symbol:** $\nu$ (nu)

**Typical values:**
| Temperature | $\nu$ (m²/s) |
|---|---|
| 5°C | $1.52 \times 10^{-6}$ |
| 10°C | $1.31 \times 10^{-6}$ |
| 15°C | $1.19 \times 10^{-6}$ |
| 20°C | $1.00 \times 10^{-6}$ |
| 25°C | $0.89 \times 10^{-6}$ |

**Units:** m²/s

**Usage downstream:** Used to compute Reynolds number: $Re = V \times L_{WL} / \nu$. Lower viscosity (warmer water) → higher Reynolds number → slightly lower friction coefficient.

**Context:** Resistance Analysis, Fluid Properties
**Related Terms:** Reynolds Number, Water Density, ITTC 1957
**Note:** *Not currently computed by the application — planned for resistance analysis feature.*

---

## L

### LCB (Longitudinal Center of Buoyancy)
The x-coordinate of the center of buoyancy, indicating the fore-aft position of buoyancy along the kayak's length.

**Units:** meters (m)  
**Coordinate:** x-axis  
**Context:** Hydrostatics  
**Related Terms:** Center of Buoyancy, Longitudinal, CB

### LCG (Longitudinal Center of Gravity)
The x-coordinate of the center of gravity, indicating the fore-aft position of the combined mass (kayak + paddler + gear).

**Units:** meters (m)  
**Coordinate:** x-axis  
**Context:** Mass Distribution  
**Related Terms:** Center of Gravity, Longitudinal, CG

### Lean
See **Heel**

### Level
A horizontal classification of points on a hull profile, such as "keel", "chine", "gunwale". Used in multi-point bow/stern definitions to match bow/stern points with corresponding profile points at the same vertical position. Enables independent control of rocker at different heights.

**Context:** Geometry, Multi-Point Bow/Stern  
**Related Terms:** Chine, Gunwale, Keel, Multi-Point Bow/Stern, Profile  
**Example Levels:** "keel", "chine_lower", "chine_upper", "gunwale"

### Length
The overall length of the kayak from bow to stern. Longer kayaks generally track better and have higher maximum speed.

**Units:** meters (m)  
**Context:** Hull Dimensions  
**Related Terms:** LOA, Waterline Length, Hull

### Linear Interpolation
Interpolation method that connects known points with straight lines. Simple but may produce angular transitions.

**Context:** Mathematics, Interpolation  
**Related Terms:** Interpolation, Cubic Interpolation

### LOA (Length Overall)
Total length of the kayak from the foremost to aftmost points.

**Units:** meters (m)  
**Context:** Hull Dimensions  
**Related Terms:** Length, Waterline Length

### Longitudinal
Direction along the length of the kayak, parallel to the x-axis. From bow to stern.

**Context:** Orientation, Coordinate System  
**Related Terms:** x-axis, Length, Station

---

## M

### Metacenter (M)
The theoretical point where the line of action of buoyancy intersects the centerline when the kayak is heeled by a small angle. The metacenter is above the center of gravity for positive stability.

**Context:** Stability Theory  
**Related Terms:** GM, Metacentric Height, Initial Stability

### Metacentric Height
See **GM**

### Midship Coefficient ($C_m$)
A dimensionless ratio describing the fullness of the largest submerged cross-section relative to its bounding rectangle.

**Formula:** $C_m = \frac{A_{max}}{B_{WL} \times T}$

**Inputs:**
- $A_{max}$ — Largest submerged cross-section area (m²), typically at the widest station
- $B_{WL}$ — Waterline beam at the widest station (m)
- $T$ — Draft (m)

**Output:** Dimensionless (0 to 1)

**Interpretation:** Describes the shape of the midship section. Imagine a rectangle $B_{WL} \times T$ around the widest cross-section below the waterline; $C_m$ is the fraction of that rectangle the cross-section fills.

**Typical values:**
- Rectangular/flat-bottom hull: $C_m \approx 0.95\text{–}1.0$
- Round-bottom kayak: $C_m \approx 0.60\text{–}0.80$
- V-shaped hull: $C_m \approx 0.50\text{–}0.65$

**Usage downstream:**
- Used to calculate prismatic coefficient: $C_p = C_b / C_m$
- Direct input to Holtrop-Mennen wave resistance regression
- A blunter midship section (higher $C_m$) affects wave generation patterns

**Context:** Resistance Analysis, Hull Form
**Related Terms:** Block Coefficient, Prismatic Coefficient, Cross-Section, Profile
**Implementation:** Computed by `calculate_midship_coefficient()` in `src/analysis/hull_parameters.py`. Used as an output metric in the `/hulls/{name}/resistance` API endpoint.

### Moment
The rotational effect of a force, equal to force times perpendicular distance. In stability analysis, the righting moment opposes heeling.

**Units:** Newton-meters (N·m) or kilogram-meters (kg·m)  
**Formula:** Moment = Force × Distance  
**Context:** Mechanics, Stability  
**Related Terms:** Righting Moment, Torque, GZ

### Multi-Point Bow/Stern
An array of points defining bow or stern geometry at multiple vertical levels (e.g., keel, chines, gunwale) rather than a single apex point. Enables independent control of rocker curvature at different heights, creating more realistic and complex end shapes.

**Format:** Array of Point3D objects with optional level attributes  
**Context:** Geometry, Hull Definition, Advanced Features  
**Related Terms:** Apex Point, Level, Rocker, Bow, Stern, Profile  
**Benefits:** Better control over rocker, more accurate end geometry, smoother transitions

---

## N

### Numerical Integration
Mathematical techniques for approximating definite integrals using discrete sampling. Essential for calculating hull properties from profile data.

**Methods used:** Shoelace Formula (cross-section area), Slab method (volume = area × step width)  
**Context:** Mathematics, Computation  
**Related Terms:** Integration, Shoelace Formula, Slab Integration, Volume Calculation

---

## O

### Origin
The reference point (0, 0, 0) in the coordinate system. Placed on the centerline at the stern projection, at the deepest hull point (keel).

**Coordinates:** (0, 0, 0) = (stern, centerline, keel bottom)  
**Context:** Coordinate System  
**Related Terms:** Coordinate System, Reference Point

---

## P

### Paddle Efficiency ($\eta_p$)
The fraction of the paddler's mechanical power output that actually propels the kayak forward. Accounts for losses in the paddle stroke (blade slip, entry/exit splash, recovery phase, body mechanics).

**Symbol:** $\eta_p$ (eta)

**Typical values:**
- Recreational paddler: 0.50–0.55 (50–55%)
- Experienced touring paddler: 0.55–0.65
- Elite racing paddler: 0.65–0.70

**Units:** Dimensionless (0 to 1)

**Usage downstream:** Converts effective power to paddler power: $P_{paddler} = P_{eff} / \eta_p$. A paddler with 60% efficiency must produce 1.67× the effective power.

**Context:** Resistance Analysis, Performance
**Related Terms:** Power, Effective Power, Paddler Power
**Note:** *Not currently computed by the application — planned for resistance analysis feature.*

### Paddler
The person operating the kayak. The paddler's weight and position significantly affect the center of gravity and thus stability.

**Context:** Loading, Mass Distribution  
**Related Terms:** CG, Mass, Seating Position, Target Payload

### Paddler Power ($P_{paddler}$)
The total mechanical power a paddler must produce at the paddle shaft to maintain a given speed, accounting for paddle inefficiency.

**Formula:** $P_{paddler} = \frac{P_{eff}}{\eta_p} = \frac{R_{total} \times V}{\eta_p}$

**Inputs:**
- $P_{eff}$ — Effective power (W)
- $\eta_p$ — Paddle efficiency (dimensionless, typically 0.5–0.7)

**Units:** Watts (W)

**Typical values:**
- Comfortable sustained effort (recreational): 30–60 W
- Brisk touring pace: 60–100 W
- Trained endurance paddler: 100–150 W sustained
- Sprint effort: 300+ W (short duration)

**Context:** Resistance Analysis, Performance
**Related Terms:** Effective Power, Paddle Efficiency, Total Resistance
**Implementation:** Computed by `calculate_paddler_power()` in `src/analysis/resistance.py`. Converts effective power to paddler power accounting for paddle efficiency.

### PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)
A shape-preserving interpolation method that avoids overshoots between data points. Used as the primary interpolation method for hull curves when x-coordinates are monotonically increasing. Unlike standard cubic splines, PCHIP preserves monotonicity of the data.

**Implementation:** `scipy.interpolate.PchipInterpolator`  
**Context:** Geometry, Spline Interpolation  
**Related Terms:** Spline, Interpolation, Chord Length Parametrization, CubicSpline

### Pitch
Rotation about the transverse (y) axis, causing the bow to rise or fall relative to the stern.

**Units:** degrees (°)  
**Context:** Motion, Trim  
**Related Terms:** Trim, Bow, Stern

### Port
The left side of the kayak when facing forward (toward the bow). In the coordinate system, negative y-coordinates.

**Context:** Orientation  
**Related Terms:** Starboard, Left, Transverse

### Prismatic Coefficient ($C_p$)
A dimensionless ratio describing how the displaced volume is distributed along the hull's length. The most important hull form coefficient for resistance prediction.

**Formula:** $C_p = \frac{\nabla}{A_{max} \times L_{WL}}$

Or equivalently: $C_p = \frac{C_b}{C_m}$

**Inputs:**
- $\nabla$ — Displaced volume (m³)
- $A_{max}$ — Largest submerged cross-section area (m²)
- $L_{WL}$ — Waterline length (m)

**Output:** Dimensionless (0 to 1)

**Interpretation:** Imagine extruding the largest cross-section along the entire waterline length to form a prism. $C_p$ is the fraction of that prism the hull actually occupies. A low $C_p$ means volume is concentrated amidships with fine bow and stern; a high $C_p$ means volume is spread more evenly.

**Typical values:**
- Cruising kayak: $C_p \approx 0.50\text{–}0.55$ (fine ends, low-speed efficiency)
- Racing kayak: $C_p \approx 0.55\text{–}0.60$ (optimized for higher Froude numbers)
- Cargo ship: $C_p \approx 0.60\text{–}0.80$

**Design trade-off:**
- Low $C_p$ (0.50–0.55): Lower wave resistance at low speeds ($F_n < 0.35$)
- High $C_p$ (0.60–0.70): Better at higher speeds ($F_n > 0.40$) due to more favorable wave system

**Usage downstream:** The **primary input** to residuary resistance estimation. Empirical methods use $C_r = f(F_n, C_p)$ — residuary coefficient as a function of Froude number and prismatic coefficient.

**Relationship between coefficients:** $C_b = C_p \times C_m$. Only two of the three need to be computed independently; the third follows.

**Context:** Resistance Analysis, Hull Form
**Related Terms:** Block Coefficient, Midship Coefficient, Froude Number, Residuary Resistance
**Implementation:** Computed by `calculate_prismatic_coefficient()` in `src/analysis/hull_parameters.py`. Primary input to residuary resistance estimation.

### Profile
A cross-sectional shape of the hull at a particular longitudinal station. In Kayakish, profiles are **auto-generated** by evaluating all spline curves at a given x-coordinate during the build process. Users define curves (not profiles directly), and the system creates two types of profiles:

1. **Regular profiles** (`profiles`): Generated at regular 0.05 m intervals along the hull length for volume and hydrostatic calculations.
2. **Main profiles** (`main_profiles`): Generated at each data point station where curve control points are defined. These provide complete transversal information at the key defining stations of the hull geometry, ideal for visualization and detailed analysis.

**Context:** Geometry, Hull Definition  
**Related Terms:** Cross-Section, Station, Curve, Spline

### Point Cloud
A collection of 3D points representing the hull surface geometry.

**Context:** Geometry, Data Structure  
**Related Terms:** Points, 3D Coordinates, Hull

---

## R

### Range of Positive Stability
The range of heel angles over which the GZ curve has positive values (positive righting moment). From 0° to the angle of vanishing stability.

**Units:** degrees (°)  
**Context:** Stability Analysis  
**Related Terms:** GZ Curve, Vanishing Stability, Stability Range

### Residuary Resistance ($R_r$)
The component of hull resistance caused by wave generation and pressure effects — everything that is not frictional drag. Dominated by wave-making resistance for displacement hulls.

**Formula:** $R_r = \frac{1}{2} \rho V^2 S_w C_r$

(Same structure as frictional resistance, but with coefficient $C_r$ instead of $C_f$.)

**Inputs:**
- $\rho$ — Water density (kg/m³)
- $V$ — Boat speed (m/s)
- $S_w$ — Wetted surface area (m²)
- $C_r$ — Residuary resistance coefficient (dimensionless), obtained from empirical data

**Units:** Newtons (N)

**Obtaining $C_r$:** Unlike $C_f$, there is no clean analytical formula. $C_r$ comes from empirical data (towing tank experiments on model hulls) as a function of:
1. **Froude number** ($F_n$) — the dominant factor
2. **Prismatic coefficient** ($C_p$) — how volume is distributed

Approach options:
- **Empirical $C_r$ vs $F_n$ lookup table** for slender displacement hulls (planned initial approach)
- **Holtrop-Mennen regression** using multiple form coefficients (more accurate, future enhancement)

**Key behavior:** $C_r$ grows explosively with Froude number:
- At $F_n = 0.20$: $C_r$ ≈ 10% of $C_f$ (wave drag negligible)
- At $F_n = 0.40$: $C_r$ ≈ 150% of $C_f$ (wave drag dominates)
- At $F_n = 0.50$: $C_r$ ≈ 500% of $C_f$

**Usage downstream:** Added to frictional resistance to form total resistance: $R_{total} = R_f + R_r$.

**Context:** Resistance Analysis, Hydrodynamics
**Related Terms:** Frictional Resistance, Total Resistance, Froude Number, Prismatic Coefficient, Wave-Making Resistance
**Implementation:** Computed by `calculate_residuary_coefficient()` and `calculate_residuary_resistance()` in `src/analysis/resistance.py`. Uses empirical data tables based on Froude number and prismatic coefficient.

### Reserve Buoyancy
The volume of the hull above the waterline that can provide additional buoyancy if the kayak is pushed lower in the water.

**Units:** cubic meters (m³)  
**Context:** Safety, Flotation  
**Related Terms:** Freeboard, Volume, Buoyancy

### Reynolds Number ($Re$)
A dimensionless number describing the ratio of inertial forces to viscous forces in the water flowing around the hull. It determines whether the flow is laminar or turbulent, and is the sole input to the ITTC 1957 friction formula.

**Formula:** $Re = \frac{V \times L_{WL}}{\nu}$

**Inputs:**
- $V$ — Boat speed (m/s)
- $L_{WL}$ — Waterline length (m)
- $\nu$ — Kinematic viscosity of water (m²/s), ≈ $1.19 \times 10^{-6}$ at 15°C

**Output:** Dimensionless. Units cancel: $\frac{(\text{m/s}) \times \text{m}}{\text{m}^2/\text{s}} = 1$

**Flow regimes:**
- $Re$ < ~500,000: Laminar flow (smooth layers, low friction)
- $Re$ > ~500,000: Turbulent flow (chaotic near surface, higher friction)

For kayaks, $Re$ is always in the **turbulent** regime (typically 2–10 million).

**Example:** At 1.5 m/s with $L_{WL}$ = 5.0 m: $Re = (1.5 \times 5.0) / 1.19 \times 10^{-6} = 6{,}302{,}521$ — fully turbulent.

**Usage downstream:** Sole input to ITTC 1957 to compute $C_f$: $C_f = 0.075 / (\log_{10} Re - 2)^2$.

**Context:** Resistance Analysis, Hydrodynamics
**Related Terms:** ITTC 1957, Frictional Resistance, Kinematic Viscosity, Waterline Length
**Implementation:** Computed by `calculate_reynolds_number()` in `src/analysis/resistance.py`. Sole input to ITTC 1957 friction coefficient calculation.

### Righting Arm
See **GZ**

### Righting Moment
The moment (torque) that acts to return the kayak to upright position when heeled. Equal to the kayak's weight multiplied by the righting arm (GZ).

**Units:** Newton-meters (N·m) or kilogram-meters (kg·m)  
**Formula:** Righting Moment = Weight × GZ  
**Context:** Stability Analysis  
**Related Terms:** GZ, Moment, Restoring Force

### Roll
See **Heel**

### Rocker
The curvature of the keel line from bow to stern. More rocker (curved keel) makes the kayak more maneuverable; less rocker improves tracking.

**Context:** Hull Design  
**Related Terms:** Keel, Curvature, Hull Shape

---

## S

### Seating Position
The location where the paddler sits, typically near the midpoint of the kayak. Affects the center of gravity position.

**Context:** Ergonomics, CG Location  
**Related Terms:** Cockpit, Paddler, CG

### Secondary Stability
Stability at moderate to large heel angles (typically > 15-20°). Characterized by the shape of the GZ curve in the mid-angle range.

**Context:** Stability Analysis  
**Related Terms:** GZ Curve, Large Angle Stability

### Sheer
The curve of the deck edge (gunwale) from bow to stern when viewed from the side. Increased sheer helps keep water out of the cockpit.

**Context:** Hull Design  
**Related Terms:** Gunwale, Deck, Profile

### Simpson's Rule
A classical numerical integration method that fits parabolas through groups of three points. More accurate than the trapezoidal rule for smooth curves.

**Context:** Mathematics, Integration  
**Related Terms:** Numerical Integration, Trapezoidal Rule, Volume Calculation  
**Note:** *Not currently used in the application. The codebase uses the Shoelace Formula for area and Slab Integration for volume.*

### Shoelace Formula
A mathematical algorithm for computing the area of a simple polygon given its vertex coordinates. Used in Kayakish to calculate the cross-sectional area of hull profiles from their y,z point coordinates.

**Formula:** Area = ½ |Σ(yᵢ·zᵢ₊₁ − zᵢ·yᵢ₊₁)|  
**Code:** `Profile.calculate_area()` in `src/geometry/profile.py`  
**Context:** Mathematics, Area Calculation  
**Related Terms:** Profile, Area, Integration, Centroid

### Slab Integration
A volume calculation method that approximates the hull volume by summing thin longitudinal slabs. Each slab's volume equals the cross-sectional area at that station multiplied by the slab width (step size, typically 0.05 m).

**Formula:** Volume ≈ Σ(Areaᵢ × step)  
**Code:** `Profile.calculate_volume_and_cg()` in `src/geometry/profile.py`  
**Context:** Mathematics, Volume Calculation  
**Related Terms:** Integration, Shoelace Formula, Profile, Volume

### Spline (Spline3D)
A parametric 3D curve fitted through a set of control points using piecewise polynomial interpolation. The core geometric primitive in Kayakish. Supports two parametrization modes: x-based (using PCHIP for monotonic curves) and chord-length (using CubicSpline for non-monotonic curves). Provides methods for evaluation, sampling, tangent/curvature/normal computation, and rotation.

**Code class:** `Spline3D` in `src/geometry/spline.py`  
**Context:** Geometry, Interpolation  
**Related Terms:** Curve, PCHIP, Chord Length Parametrization, Control Points

### Stability
The tendency of the kayak to return to upright position after being heeled. Determined by the relationship between the centers of gravity and buoyancy.

**Types:** Initial Stability, Secondary Stability, Dynamic Stability  
**Context:** Analysis, Safety  
**Related Terms:** GZ, Righting Moment, Stability Curve

### Stability Criteria
Standard requirements or thresholds that a kayak should meet for safe operation. May include minimum GM, minimum GZ at specified angles, minimum range of stability.

**Context:** Safety, Design Standards  
**Related Terms:** Criteria, Safety Standards, Assessment

### Stability Curve
See **GZ Curve**

### Starboard
The right side of the kayak when facing forward (toward the bow). In the coordinate system, positive y-coordinates.

**Context:** Orientation  
**Related Terms:** Port, Right, Transverse

### Station
A specific longitudinal position (x-coordinate) along the kayak where a profile is defined. Stations are typically evenly spaced or concentrated in areas of rapid shape change.

**Units:** meters (m)  
**Coordinate:** x-axis  
**Context:** Geometry, Hull Definition  
**Related Terms:** Profile, Longitudinal, Cross-Section

### Stern
The rear end of the kayak. The stern profile is the transverse cross-section at the aft-most station.

**Context:** Hull Geometry  
**Related Terms:** Bow, Aft, Profile

### Stiffness
A measure of how resistant a kayak is to heeling. High stiffness (high GM) means the kayak resists heeling strongly and returns quickly to upright.

**Measure:** GM (metacentric height)  
**Context:** Stability, Feel  
**Related Terms:** Initial Stability, GM, Tender/Stiff

### Submerged Volume
The volume of the hull below the waterline, which displaces water and creates buoyancy.

**Units:** cubic meters (m³)  
**Context:** Hydrostatics  
**Related Terms:** Displacement, Waterline, Volume

### Surface Roughness Allowance ($\Delta C_f$)
An additive correction to the ITTC friction coefficient to account for real hull surface roughness (the ITTC formula assumes a perfectly smooth surface).

**Formula:** $C_f' = C_f + \Delta C_f$

**Typical values:**
| Hull material | $\Delta C_f$ |
|---|---|
| Polished gelcoat/composite | 0.0002 |
| Thermoformed plastic | 0.0004 |
| Rotomolded polyethylene | 0.0006 |

**Context:** Resistance Analysis, Hydrodynamics
**Related Terms:** ITTC 1957, Frictional Resistance
**Note:** *Not currently computed by the application — planned for resistance analysis feature.*

### Symmetry
Most kayak hulls are symmetric about the centerline (port and starboard sides are mirror images). Symmetry simplifies calculations and data definition.

**Context:** Geometry, Hull Design  
**Related Terms:** Centerline, Mirror Image, Profile

---

## T

### Target Payload
The mass of the paddler plus any gear or cargo, specified in kilograms. Used together with `target_weight` (hull mass) to determine the total mass for waterline equilibrium calculations.

**Units:** kilograms (kg)  
**Code field:** `Hull.target_payload`  
**Context:** Loading, Hydrostatics  
**Related Terms:** Target Weight, Weight, Paddler, Displacement

### Target Waterline
The initial estimated waterline height (z-coordinate) used as a starting point for the iterative waterline convergence algorithm. The algorithm adjusts this value until the displaced volume matches the total weight.

**Units:** meters (m)  
**Code field:** `Hull.target_waterline`  
**Context:** Hydrostatics, Calculation  
**Related Terms:** Waterline, Displacement, Equilibrium

### Target Weight
The mass of the empty hull (without paddler or cargo), specified in kilograms. Combined with `target_payload` to determine total system mass for equilibrium waterline computation.

**Units:** kilograms (kg)  
**Code field:** `Hull.target_weight`  
**Context:** Loading, Hydrostatics  
**Related Terms:** Target Payload, Weight, Hull, Displacement

### TCB (Transverse Center of Buoyancy)
The y-coordinate of the center of buoyancy. For a symmetric hull upright in calm water, TCB = 0 (on the centerline).

**Units:** meters (m)  
**Coordinate:** y-axis  
**Context:** Hydrostatics  
**Related Terms:** Center of Buoyancy, Transverse, CB

### TCG (Transverse Center of Gravity)
The y-coordinate of the center of gravity. TCG = 0 when weight is balanced on the centerline. Non-zero TCG indicates asymmetric loading.

**Units:** meters (m)  
**Coordinate:** y-axis  
**Context:** Mass Distribution  
**Related Terms:** Center of Gravity, Transverse, CG

### Tender
Describes a kayak with low initial stability (small GM) that feels "tippy" or easily heeled. Opposite of stiff.

**Context:** Stability Feel  
**Related Terms:** Stiffness, GM, Initial Stability

### Total Resistance ($R_{total}$)
The sum of all resistance forces acting on the hull, which the paddler must overcome to maintain a given speed.

**Formula:** $R_{total} = R_f + R_r = \frac{1}{2} \rho V^2 S_w (C_f + C_r)$

**Inputs:**
- $R_f$ — Frictional resistance (N)
- $R_r$ — Residuary (wave-making) resistance (N)

Or equivalently:
- $\rho$ — Water density (kg/m³)
- $V$ — Boat speed (m/s)
- $S_w$ — Wetted surface area (m²)
- $C_f$ — Friction coefficient (dimensionless)
- $C_r$ — Residuary coefficient (dimensionless)

**Units:** Newtons (N)

**Typical values for a touring kayak:**
- 5 km/h: ~10–15 N (light effort)
- 7 km/h: ~20–30 N (moderate effort)
- 10 km/h (hull speed): ~50–80 N (hard effort)
- 12 km/h: ~120–200 N (sprint)

**Usage downstream:** Multiplied by speed to get effective power: $P_{eff} = R_{total} \times V$.

**Context:** Resistance Analysis, Performance
**Related Terms:** Frictional Resistance, Residuary Resistance, Effective Power, Paddler Power
**Note:** *Not currently computed by the application — planned for resistance analysis feature.*

### Tracking
The tendency of a kayak to maintain a straight course. Longer kayaks and those with less rocker typically track better.

**Context:** Performance, Handling  
**Related Terms:** Course Keeping, Directional Stability

### Transformation
Mathematical operations that change coordinates, typically for heel or trim angles. Rotation matrices are used to transform hull geometry.

**Types:** Heel transformation, Trim transformation  
**Context:** Mathematics, Geometry  
**Related Terms:** Rotation, Coordinate System, Heel Angle

### Transverse
Direction perpendicular to the kayak's length, from port to starboard. Parallel to the y-axis.

**Context:** Orientation, Coordinate System  
**Related Terms:** y-axis, Beam, Port/Starboard

### Trapezoidal Rule
A classical numerical integration method that approximates the area under a curve by dividing it into trapezoids. Simpler but less accurate than Simpson's Rule.

**Context:** Mathematics, Integration  
**Related Terms:** Numerical Integration, Simpson's Rule, Area Calculation  
**Note:** *Not currently used in the application. The codebase uses the Shoelace Formula for area and Slab Integration for volume.*

### Trim
The orientation of the kayak in the longitudinal direction. A kayak is "in trim" when bow and stern sit at the designed waterline. "Down by the bow" means bow is lower; "down by the stern" means stern is lower.

**Context:** Hydrostatics, Loading  
**Related Terms:** Pitch, Balance, Waterline

### Trim Angle
The angle of rotation about the transverse axis, causing bow or stern to be lower.

**Units:** degrees (°)  
**Context:** Transformation, Hydrostatics  
**Related Terms:** Pitch, Trim, Rotation

---

## U

### Upright
The normal floating position with no heel angle (0°) and correct trim.

**Context:** Reference Position  
**Related Terms:** Equilibrium, Level, Zero Heel

---

## V

### Vanishing Stability
The condition where the righting arm (GZ) returns to zero at a large heel angle. Beyond this angle, the kayak will continue to capsize rather than return to upright.

**Context:** Stability Limit  
**Related Terms:** Angle of Vanishing Stability, Capsize, Stability Range

### Angle of Vanishing Stability
The heel angle at which the GZ curve crosses zero after the maximum GZ. Represents the limit of positive stability.

**Units:** degrees (°)  
**Context:** Stability Analysis  
**Related Terms:** Vanishing Stability, GZ Curve, Stability Range

### VCB (Vertical Center of Buoyancy)
The z-coordinate of the center of buoyancy, indicating the vertical position of the buoyancy centroid relative to the origin.

**Units:** meters (m)  
**Coordinate:** z-axis  
**Context:** Hydrostatics  
**Related Terms:** Center of Buoyancy, Vertical, CB

### VCG (Vertical Center of Gravity)
The z-coordinate of the center of gravity, indicating the vertical height of the combined mass center. Lower VCG improves stability.

**Units:** meters (m)  
**Coordinate:** z-axis  
**Context:** Mass Distribution, Stability  
**Related Terms:** Center of Gravity, Vertical, CG

### Volume
The three-dimensional space occupied by a region. For hydrostatics, typically the submerged volume of the hull.

**Units:** cubic meters (m³)  
**Context:** Geometry, Hydrostatics  
**Related Terms:** Displacement, Submerged Volume, Capacity

---

## W

### Water Density
The mass per unit volume of water. Used to convert displacement volume to displaced mass.

**Value:** 
- Fresh water: 1000 kg/m³
- Sea water: 1025 kg/m³

**Units:** kg/m³  
**Context:** Hydrostatics, Calculations  
**Related Terms:** Density, Displacement, Buoyancy

### Waterline
The line where the water surface meets the hull. The waterline level (z-coordinate) determines which parts of the hull are submerged.

**Units:** meters (m) for z-coordinate  
**Context:** Hydrostatics, Reference  
**Related Terms:** Draft, Freeboard, Waterline Length

### Waterline Length
The length of the kayak at the waterline, from the forward intersection to the aft intersection of the hull with the water surface. Usually less than LOA.

**Units:** meters (m)  
**Context:** Hydrostatics, Performance  
**Related Terms:** Length, LOA, Waterline

### Waterplane
The horizontal plane at the water surface level. The waterplane area affects initial stability.

**Units:** square meters (m²) for area  
**Context:** Hydrostatics, Stability  
**Related Terms:** Waterline, Surface, Area

### Weight
The gravitational force acting on the kayak system (hull + paddler + gear). In this application, weight is expressed in **kilogram-force (kgf)** — the unit universally used in practice. 1 kgf is the force exerted by gravity on 1 kg of mass.

**Units:** kgf (kilogram-force). All `target_weight`, `target_payload`, and `displacement` values in the code use kgf.  
**Equivalence:** 1 kgf = 9.81 N  
**Context:** Forces, Equilibrium  
**Related Terms:** Mass, Gravity, Load, Displacement

### Waterplane Coefficient ($C_{wp}$)
A dimensionless ratio describing the fullness of the waterplane area (the hull's footprint on the water surface) relative to its bounding rectangle.

**Formula:** $C_{wp} = \frac{A_{wp}}{L_{WL} \times B_{WL}}$

**Inputs:**
- $A_{wp}$ — Waterplane area (m²) — the area enclosed by the waterline when viewed from above
- $L_{WL}$ — Waterline length (m)
- $B_{WL}$ — Waterline beam (m)

**Output:** Dimensionless (0 to 1)

**Typical values:**
- Kayak: $C_{wp} \approx 0.65\text{–}0.80$
- Ship: $C_{wp} \approx 0.70\text{–}0.90$

**Context:** Resistance Analysis, Hull Form
**Related Terms:** Block Coefficient, Prismatic Coefficient, Waterplane
**Implementation:** Computed by `calculate_waterplane_coefficient()` in `src/analysis/hull_parameters.py`. Used as an output metric in the `/hulls/{name}/resistance` API endpoint.

### Wetted Surface ($S_w$)
The total area of the hull surface in contact with water below the waterline. The primary geometric input for frictional resistance calculation.

**Calculation method:** For each cross-section at station $x$, compute the wetted perimeter (arc length of the submerged profile), then integrate along the hull length:
$$S_w = \int_0^{L} P_w(x) \, dx \approx \sum_{i} \frac{P_w(x_i) + P_w(x_{i+1})}{2} \Delta x$$

**Typical values for kayaks:** 1.5–3.0 m²

**Units:** square meters (m²)  
**Context:** Hydrodynamics, Resistance Analysis  
**Related Terms:** Frictional Resistance, Wetted Perimeter, Hull, ITTC 1957
**Implementation:** Computed by `hull.wetted_surface_area()` in `src/geometry/hull.py`, integrating wetted perimeter along the hull length.

### Width
See **Beam**

---

## X, Y, Z

### x-axis
The longitudinal axis running from stern (negative or smaller x) to bow (positive or larger x) along the kayak's length.

**Direction:** Longitudinal (fore-aft)  
**Context:** Coordinate System  
**Related Terms:** Longitudinal, Station, LCG/LCB

### y-axis
The transverse axis running from port (negative y) to starboard (positive y) across the kayak's width.

**Direction:** Transverse (side-to-side)  
**Context:** Coordinate System  
**Related Terms:** Transverse, Beam, TCG/TCB

### z-axis
The vertical axis running from bottom (negative z) to top (positive z). Typically z = 0 at the waterline or keel.

**Direction:** Vertical (up-down)  
**Context:** Coordinate System  
**Related Terms:** Vertical, Draft, VCG/VCB

---

## Symbols and Abbreviations

| Symbol/Abbr | Meaning | Units |
|-------------|---------|-------|
| CB | Center of Buoyancy | m |
| CG | Center of Gravity | m |
| $C_b$ | Block Coefficient | dimensionless |
| $C_f$ | Frictional Resistance Coefficient | dimensionless |
| $C_m$ | Midship Coefficient | dimensionless |
| $C_p$ | Prismatic Coefficient | dimensionless |
| $C_r$ | Residuary Resistance Coefficient | dimensionless |
| $C_{wp}$ | Waterplane Coefficient | dimensionless |
| $F_n$ | Froude Number | dimensionless |
| GM | Metacentric Height | m |
| GZ | Righting Arm | m |
| LCB | Longitudinal Center of Buoyancy | m |
| LCG | Longitudinal Center of Gravity | m |
| LOA | Length Overall | m |
| $P_{eff}$ | Effective Power | W |
| $P_{paddler}$ | Paddler Power | W |
| $Re$ | Reynolds Number | dimensionless |
| $R_f$ | Frictional Resistance | N |
| $R_r$ | Residuary Resistance | N |
| $R_{total}$ | Total Resistance | N |
| $S_w$ | Wetted Surface Area | m² |
| TCB | Transverse Center of Buoyancy | m |
| TCG | Transverse Center of Gravity | m |
| VCB | Vertical Center of Buoyancy | m |
| VCG | Vertical Center of Gravity | m |
| $\eta_p$ | Paddle Efficiency | dimensionless |
| $\nu$ (nu) | Kinematic Viscosity | m²/s |
| φ (phi) | Heel angle | degrees (°) |
| θ (theta) | Trim angle | degrees (°) |
| ρ (rho) | Water density | kg/m³ |
| ∇ (nabla) | Displacement volume | m³ |
| Δ (delta) | Displacement mass | kg |

---

## Units Reference

### Length
- **m** - meters (SI base unit)
- **cm** - centimeters
- **mm** - millimeters

### Area
- **m²** - square meters

### Volume
- **m³** - cubic meters
- **L** - liters (1 L = 0.001 m³)

### Mass
- **kg** - kilograms

### Force
- **N** - Newtons (kg·m/s²)

### Power
- **W** - Watts (J/s = N·m/s)
- **kW** - kilowatts (1000 W)

### Angle
- **°** - degrees
- **rad** - radians (for calculations)

### Moment/Torque
- **N·m** - Newton-meters
- **kg·m** - kilogram-meters (when using mass × distance)

### Density
- **kg/m³** - kilograms per cubic meter

### Dynamic Stability
- **m·rad** - meter-radians (area under GZ curve)

---

## Mathematical Conventions

### Coordinate System (Right-Handed)
- **x**: Positive forward (bow direction)
- **y**: Positive to starboard (right side)
- **z**: Positive upward

### Sign Conventions
- **Heel angle**: Positive = tilt to starboard
- **Trim angle**: Positive = bow up
- **Above waterline**: z > waterline_z
- **Below waterline**: z < waterline_z

### Interpolation Order
- **0th order**: Constant (nearest neighbor)
- **1st order**: Linear
- **2nd order**: Quadratic
- **3rd order**: Cubic

---

## Related Standards and References

### Design Standards
- **ISO 12217**: Small craft stability standards (adapted for kayaks)
- **ASTM F1166**: Standard specification for recreational kayaks

### Calculation Methods
- **Shoelace Formula**: For cross-section area calculation
- **Slab Integration**: For volume computation (area × step width)
- **PCHIP Interpolation**: For shape-preserving curve fitting
- **Archimedes' Principle**: Foundation for buoyancy calculations
- **Brent's Method (brentq)**: For root-finding in curve evaluation
- **ITTC 1957 Friction Line**: For frictional resistance coefficient calculation
- **Froude Number Scaling**: For wave-making resistance regime classification

---

## Usage Notes

### For Users
- All input coordinates should be in the same unit system (typically meters)
- Water density can be specified; default is 1000 kg/m³ (fresh water)
- Heel angles are typically analyzed from 0° to 90°
- Negative GM indicates unstable equilibrium

### For Developers
- Maintain consistent coordinate system throughout code
- Always specify units in documentation and function signatures
- Use appropriate numerical precision (typically 3-4 decimal places for meters)
- Consider symmetry to optimize calculations

---

## Glossary Notes

**Version History:**
- v1.0 (2025-12-26): Initial comprehensive glossary
- v1.1 (2026-02-14): Cross-referenced with codebase; fixed coordinate system, integration methods, interpolation types, and profile definition
- v1.2 (2026-02-17): Added resistance analysis terms — hull form coefficients ($C_b$, $C_m$, $C_p$, $C_{wp}$), Reynolds number, Froude number, ITTC 1957, frictional resistance, residuary resistance, total resistance, hull speed, effective power, paddler power, paddle efficiency, kinematic viscosity, surface roughness allowance

**Maintenance:**
- Update glossary when new terms are introduced
- Cross-reference with code docstrings
- Verify definitions match usage in examples

**Feedback:**
- Submit corrections or additions via project issues
- Suggest new terms that need clarification

---

*This glossary is part of the Kayakish documentation. For usage examples, see the [User Guide](User_Guide.md) and [example scripts](../test/scripts/).*
