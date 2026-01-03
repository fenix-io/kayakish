# GitHub Copilot Instructions

## Project Overview
This is a Python application for calculating kayak hydrostatic parameters and stability characteristics.

## Core Functionality
The application calculates:
- **Displacement**: Volume of water displaced by the kayak
- **Stability Curves**: GZ curves showing righting moment vs. heel angle
- **Center of Gravity (CG)**: Vertical and horizontal position of the mass centroid
- **Center of Buoyancy (CB)**: Centroid of the displaced volume, both upright and heeled

## Input Data Structure
- Surface points on the kayak hull defined at:
  - Traverse profiles containing points on the sirface of the hull 
  - Other metadata
- All coordinates must be referenced in orthonal coordinates where
  - x coordinates will grow from stern to bow of the boat, being the 0 exactly over the projection of the stern on the centerline.
  - y coordinates will be positive from centerline to port, and negative from centerline to starboard. like you were looking the kayak from the bow or the tipo o x axis.
  - Z coordinates will grow up from the deepest point of the kayak. Being the 0 the deepest point in the hull.

## Calculation Methodology

### Volume Integration
- Numerical integration of transverse cross-sections along the kayak length
- Cross-section areas calculated from profile points
- Integration methods: trapezoidal rule, or similar numerical methods

### Point Interpolation
- **Transverse interpolation**: Linear interpolation between port and starboard points on each profile
- **Longitudinal interpolation**: Linear interpolation between adjacent profiles to generate intermediate sections
- **Bow/stern interpolation**: Linear interpolation from end profiles to bow/stern points

### Heel Calculations
- Transform coordinates to simulate heel angle (roll about longitudinal axis)
- Recalculate waterline intersection at heeled positions
- Compute submerged volume and center of buoyancy for each heel angle
- Generate stability curve by calculating righting arm (GZ) vs. heel angle

## Technical Considerations
- Use Fastapi for the API definition.
- Use a Vainilla HTML + CSS site to input data and execute the API calls
- Use NumPy for numerical operations and array manipulations
- Consider using SciPy for integration routines
- Matplotlib for plotting stability curves
- Maintain symmetry assumptions (kayak symmetric about centerline)
- Handle waterline intersection calculations carefully when heeled

## Code Organization Preferences
- Separate modules for:
  - Routing, to separate the API routes
  - Geometry definitions and transformations
  - Volume and centroid calculations
  - Stability analysis
  - Visualization/plotting
  - Input/output handling
  - Static HTML visualization and input
- Use type hints for better code clarity
- Document formulas and calculation steps clearly
- Please write Unit Tests for new code where is applicacble
- Please run the linter (flake8) and formatter (black) on the code before submission using make lint and make format commands.


# Planning and Tasks
- For every task, please create a detailed plan before implement it.
- Break down complex calculations into smaller, manageable functions.
- Write all task to be implemented in a tasks.md file and get approval before starting coding.


# Running commands
- An venv should be created in .venv for dependency management.
- Every time that you need to run a python, pytest, sphynx or other commands that could indirectly call python environment, activate first the venv using: `source .venv/bin/activate`


