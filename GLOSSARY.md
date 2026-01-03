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

### Cockpit
The opening in the deck where the paddler sits. The cockpit area typically has the maximum beam width.

**Context:** Hull Design  
**Related Terms:** Deck, Seating Position

### Coordinate System
The reference frame used to define positions on the kayak:
- **x-axis:** Longitudinal (bow to stern)
- **y-axis:** Transverse (port to starboard)
- **z-axis:** Vertical (down to up)
- **Origin:** Typically on the centerline at a reference waterline

**Context:** Geometry, Mathematics  
**Related Terms:** Axes, Origin, Station

### Cross-Section
A slice through the hull perpendicular to the longitudinal axis, showing the profile shape at that station.

**Context:** Geometry  
**Related Terms:** Profile, Station, Transverse

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
The angle of rotation about the longitudinal axis, measured from upright position. Positive typically indicates tilt to starboard.

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

**Methods:** Simpson's Rule, Trapezoidal Rule  
**Context:** Mathematics, Calculation  
**Related Terms:** Numerical Integration, Simpson's Rule, Volume Calculation

### Interpolation
Mathematical techniques for estimating values between known data points. Used extensively to create smooth hull surfaces from discrete profile data.

**Types:** Linear, Cubic, Spline  
**Context:** Geometry, Mathematics  
**Related Terms:** Linear Interpolation, Cubic Interpolation, Smoothing

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

**Methods:** Simpson's Rule, Trapezoidal Rule, Midpoint Rule  
**Context:** Mathematics, Computation  
**Related Terms:** Integration, Simpson's Rule, Volume Calculation

---

## O

### Origin
The reference point (0, 0, 0) in the coordinate system. Typically placed on the centerline at a convenient longitudinal position (often amidships) at a reference waterline or keel.

**Coordinates:** (0, 0, 0)  
**Context:** Coordinate System  
**Related Terms:** Coordinate System, Reference Point

---

## P

### Paddler
The person operating the kayak. The paddler's weight and position significantly affect the center of gravity and thus stability.

**Context:** Loading, Mass Distribution  
**Related Terms:** CG, Mass, Seating Position

### Pitch
Rotation about the transverse (y) axis, causing the bow to rise or fall relative to the stern.

**Units:** degrees (°)  
**Context:** Motion, Trim  
**Related Terms:** Trim, Bow, Stern

### Port
The left side of the kayak when facing forward (toward the bow). In the coordinate system, negative y-coordinates.

**Context:** Orientation  
**Related Terms:** Starboard, Left, Transverse

### Profile
A cross-sectional shape of the hull at a particular longitudinal station. Defined by a series of points representing the hull contour.

**Context:** Geometry, Hull Definition  
**Related Terms:** Cross-Section, Station, Points

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

### Reserve Buoyancy
The volume of the hull above the waterline that can provide additional buoyancy if the kayak is pushed lower in the water.

**Units:** cubic meters (m³)  
**Context:** Safety, Flotation  
**Related Terms:** Freeboard, Volume, Buoyancy

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
A numerical integration method that fits parabolas through groups of three points. More accurate than the trapezoidal rule for smooth curves.

**Context:** Mathematics, Integration  
**Related Terms:** Numerical Integration, Trapezoidal Rule, Volume Calculation

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

### Symmetry
Most kayak hulls are symmetric about the centerline (port and starboard sides are mirror images). Symmetry simplifies calculations and data definition.

**Context:** Geometry, Hull Design  
**Related Terms:** Centerline, Mirror Image, Profile

---

## T

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
A numerical integration method that approximates the area under a curve by dividing it into trapezoids. Simpler but less accurate than Simpson's Rule.

**Context:** Mathematics, Integration  
**Related Terms:** Numerical Integration, Simpson's Rule, Area Calculation

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
The force due to gravity acting on the kayak's mass (hull + paddler + gear). Equals mass times gravitational acceleration.

**Units:** Newtons (N) or expressed as mass in kilograms (kg)  
**Formula:** Weight = Mass × g (where g ≈ 9.81 m/s²)  
**Context:** Forces, Equilibrium  
**Related Terms:** Mass, Gravity, Load

### Wetted Surface
The area of the hull surface in contact with water. Affects drag and resistance.

**Units:** square meters (m²)  
**Context:** Hydrodynamics, Performance  
**Related Terms:** Surface Area, Drag, Hull

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
| GM | Metacentric Height | m |
| GZ | Righting Arm | m |
| LCB | Longitudinal Center of Buoyancy | m |
| LCG | Longitudinal Center of Gravity | m |
| LOA | Length Overall | m |
| TCB | Transverse Center of Buoyancy | m |
| TCG | Transverse Center of Gravity | m |
| VCB | Vertical Center of Buoyancy | m |
| VCG | Vertical Center of Gravity | m |
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
- **Simpson's 1/3 Rule**: For numerical integration
- **Trapezoidal Rule**: For simple numerical integration
- **Archimedes' Principle**: Foundation for buoyancy calculations

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

**Maintenance:**
- Update glossary when new terms are introduced
- Cross-reference with code docstrings
- Verify definitions match usage in examples

**Feedback:**
- Submit corrections or additions via project issues
- Suggest new terms that need clarification

---

*This glossary is part of the Kayak Calculation Tool documentation. For usage examples, see the USER_GUIDE.md and example scripts.*
