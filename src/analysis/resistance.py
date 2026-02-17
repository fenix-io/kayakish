"""Hull resistance and performance estimation module.

This module provides functions to calculate the resistance components, power requirements,
and performance characteristics of a kayak hull at various speeds.

Resistance components:
- Frictional resistance (Rf): Viscous drag using ITTC 1957 correlation line
- Residuary resistance (Rr): Wave-making and pressure resistance
- Total resistance (Rt): Sum of frictional and residuary components

Performance metrics:
- Effective power: Power required to overcome hull resistance
- Paddler power: Actual power output accounting for propulsion efficiency
- Hull speed: Theoretical maximum displacement speed
- Froude number: Dimensionless speed parameter

References:
- ITTC (1957) — Friction resistance correlation line
- Holtrop, J. & Mennen, G.G.J. (1982) — "An approximate power prediction method"
- Winters, J. — "The Shape of the Canoe"
- Marchaj, C.A. — "Sail Performance"
- Froude, W. — Wave resistance formulation
"""

import math
from typing import List, Optional
from dataclasses import dataclass

# Physical constants
WATER_DENSITY_FRESH = 1000.0  # kg/m³ - fresh water
WATER_DENSITY_SALT = 1025.0  # kg/m³ - salt water
KINEMATIC_VISCOSITY = 1.19e-6  # m²/s - water at 15°C
GRAVITY = 9.81  # m/s²

# Default parameters
DEFAULT_ROUGHNESS_ALLOWANCE = 0.0004  # Typical for kayak hulls (gelcoat, thermoformed plastic)
DEFAULT_PROPULSION_EFFICIENCY = 0.60  # Typical paddle efficiency (0.5-0.7 range)


@dataclass
class ResistanceResult:
    """Container for resistance calculation results at a single speed.

    Attributes:
        speed: Boat speed in m/s
        froude_number: Dimensionless speed parameter (Fn = V / sqrt(g * Lwl))
        reynolds_number: Dimensionless parameter for viscous flow
        friction_coefficient: ITTC frictional resistance coefficient (Cf)
        residuary_coefficient: Residuary resistance coefficient (Cr)
        frictional_resistance: Frictional drag force in Newtons
        residuary_resistance: Wave-making and pressure drag in Newtons
        total_resistance: Total drag force in Newtons
        effective_power: Power to overcome resistance in Watts
        paddler_power: Required paddler power output in Watts (with efficiency)
    """

    speed: float
    froude_number: float
    reynolds_number: float
    friction_coefficient: float
    residuary_coefficient: float
    frictional_resistance: float
    residuary_resistance: float
    total_resistance: float
    effective_power: float
    paddler_power: float


def calculate_reynolds_number(
    speed: float, waterline_length: float, kinematic_viscosity: float = KINEMATIC_VISCOSITY
) -> float:
    """Calculate Reynolds number for flow along the hull.

    Reynolds number characterizes the flow regime (laminar vs. turbulent).
    For kayaks, Re is typically > 10^6, indicating turbulent flow.

    Formula: Re = (V × Lwl) / ν

    Args:
        speed: Boat speed in m/s
        waterline_length: Waterline length (Lwl) in meters
        kinematic_viscosity: Kinematic viscosity of water in m²/s (default: 1.19e-6 at 15°C)

    Returns:
        float: Reynolds number (dimensionless)

    Raises:
        ValueError: If speed, waterline_length, or kinematic_viscosity are <= 0

    Example:
        >>> calculate_reynolds_number(speed=2.0, waterline_length=5.0)
        8403361.344537815  # Turbulent flow
    """
    if speed < 0:
        raise ValueError(f"Speed must be non-negative, got {speed}")
    if waterline_length <= 0:
        raise ValueError(f"Waterline length must be positive, got {waterline_length}")
    if kinematic_viscosity <= 0:
        raise ValueError(f"Kinematic viscosity must be positive, got {kinematic_viscosity}")

    return (speed * waterline_length) / kinematic_viscosity


def calculate_froude_number(
    speed: float, waterline_length: float, gravity: float = GRAVITY
) -> float:
    """Calculate Froude number, the dimensionless speed parameter.

    Froude number characterizes the wave-making regime:
    - Fn < 0.35: Low wave resistance, displacement regime
    - Fn 0.35-0.40: Moderate wave resistance, approaching hull speed
    - Fn > 0.40: High wave resistance, resistance increases rapidly

    Formula: Fn = V / sqrt(g × Lwl)

    Args:
        speed: Boat speed in m/s
        waterline_length: Waterline length (Lwl) in meters
        gravity: Gravitational acceleration in m/s² (default: 9.81)

    Returns:
        float: Froude number (dimensionless)

    Raises:
        ValueError: If speed is negative or waterline_length or gravity are <= 0

    Example:
        >>> calculate_froude_number(speed=2.0, waterline_length=5.0)
        0.2857  # Low wave resistance regime
    """
    if speed < 0:
        raise ValueError(f"Speed must be non-negative, got {speed}")
    if waterline_length <= 0:
        raise ValueError(f"Waterline length must be positive, got {waterline_length}")
    if gravity <= 0:
        raise ValueError(f"Gravity must be positive, got {gravity}")

    return speed / math.sqrt(gravity * waterline_length)


def calculate_hull_speed(waterline_length: float, gravity: float = GRAVITY) -> float:
    """Calculate theoretical hull speed (speed at Fn ≈ 0.40).

    Hull speed is the speed at which wave resistance begins to dominate.
    For displacement hulls, exceeding hull speed requires disproportionately
    more power. This is a rough estimate; actual behavior depends on hull form.

    Formula: V_hull ≈ 1.34 × sqrt(Lwl_feet) knots
              V_hull ≈ 2.43 × sqrt(Lwl_m) km/h
              V_hull ≈ sqrt(g × Lwl) × 0.40 m/s (Fn = 0.40)

    Args:
        waterline_length: Waterline length (Lwl) in meters
        gravity: Gravitational acceleration in m/s² (default: 9.81)

    Returns:
        float: Hull speed in m/s

    Raises:
        ValueError: If waterline_length or gravity are <= 0

    Example:
        >>> calculate_hull_speed(5.0)
        2.8014  # m/s ≈ 10.1 km/h
    """
    if waterline_length <= 0:
        raise ValueError(f"Waterline length must be positive, got {waterline_length}")
    if gravity <= 0:
        raise ValueError(f"Gravity must be positive, got {gravity}")

    # Hull speed at Froude number = 0.40
    return 0.40 * math.sqrt(gravity * waterline_length)


def calculate_ittc_friction_coefficient(
    reynolds_number: float, roughness_allowance: float = DEFAULT_ROUGHNESS_ALLOWANCE
) -> float:
    """Calculate ITTC 1957 frictional resistance coefficient.

    The ITTC (International Towing Tank Conference) 1957 friction line is the
    standard method for estimating frictional resistance of ship hulls in turbulent flow.

    Formula: Cf = 0.075 / (log10(Re) - 2)² + ΔCf

    where ΔCf is a roughness allowance for surface finish.

    Args:
        reynolds_number: Reynolds number (dimensionless, typically > 10^6 for kayaks)
        roughness_allowance: Additional coefficient for surface roughness (default: 0.0004)
                           Typical values:
                           - 0.0004: Kayak hulls (gelcoat, thermoformed plastic, composite)
                           - 0.0002: Very smooth (polished)
                           - 0.0006: Rougher surfaces

    Returns:
        float: Frictional resistance coefficient Cf (dimensionless)

    Raises:
        ValueError: If reynolds_number <= 0 or roughness_allowance < 0

    Example:
        >>> calculate_ittc_friction_coefficient(8.4e6)
        0.00288
    """
    if reynolds_number <= 0:
        raise ValueError(f"Reynolds number must be positive, got {reynolds_number}")
    if roughness_allowance < 0:
        raise ValueError(f"Roughness allowance must be non-negative, got {roughness_allowance}")

    # ITTC 1957 friction line
    log_re = math.log10(reynolds_number)
    cf_smooth = 0.075 / ((log_re - 2) ** 2)

    # Add roughness allowance
    cf_total = cf_smooth + roughness_allowance

    return cf_total


def calculate_frictional_resistance(
    speed: float,
    wetted_surface: float,
    friction_coefficient: float,
    water_density: float = WATER_DENSITY_FRESH,
) -> float:
    """Calculate frictional resistance force.

    Frictional resistance is the viscous drag on the wetted surface of the hull.
    This typically accounts for 70-90% of total resistance at kayak speeds.

    Formula: Rf = 0.5 × ρ × V² × Sw × Cf

    Args:
        speed: Boat speed in m/s
        wetted_surface: Wetted surface area in m²
        friction_coefficient: ITTC frictional resistance coefficient (Cf)
        water_density: Water density in kg/m³ (default: 1000 for fresh water)

    Returns:
        float: Frictional resistance in Newtons

    Raises:
        ValueError: If any parameter is negative or water_density/wetted_surface are zero

    Example:
        >>> calculate_frictional_resistance(speed=2.0, wetted_surface=2.5, friction_coefficient=0.003)
        15.0  # Newtons
    """
    if speed < 0:
        raise ValueError(f"Speed must be non-negative, got {speed}")
    if wetted_surface <= 0:
        raise ValueError(f"Wetted surface must be positive, got {wetted_surface}")
    if friction_coefficient < 0:
        raise ValueError(f"Friction coefficient must be non-negative, got {friction_coefficient}")
    if water_density <= 0:
        raise ValueError(f"Water density must be positive, got {water_density}")

    # Rf = 0.5 × ρ × V² × Sw × Cf
    return 0.5 * water_density * (speed**2) * wetted_surface * friction_coefficient


def calculate_residuary_coefficient(
    froude_number: float, prismatic_coefficient: Optional[float] = None
) -> float:
    """Calculate residuary (wave-making) resistance coefficient.

    This uses an empirical model suitable for slender displacement hulls like kayaks.
    The model is based on published data for canoes and kayaks (Winters, Marchaj).

    Wave resistance is negligible at low Froude numbers (< 0.3), increases
    moderately around Fn = 0.35-0.40 (hull speed), and grows rapidly beyond Fn = 0.45.

    The empirical relationship used here is:
    - Fn < 0.30: Cr ≈ 0 (negligible wave resistance)
    - Fn 0.30-0.40: Cr increases gradually
    - Fn > 0.40: Cr increases rapidly (exponential growth)

    Args:
        froude_number: Froude number (Fn = V / sqrt(g × Lwl))
        prismatic_coefficient: Prismatic coefficient (Cp), optional.
                             If provided, adjusts Cr based on hull fullness.
                             Higher Cp (fuller hull) → higher wave resistance.

    Returns:
        float: Residuary resistance coefficient Cr (dimensionless)

    Example:
        >>> calculate_residuary_coefficient(0.25)
        0.00005  # Low wave resistance
        >>> calculate_residuary_coefficient(0.40)
        0.0008   # Approaching hull speed
        >>> calculate_residuary_coefficient(0.50)
        0.0025   # High wave resistance
    """
    # Base empirical model for slender displacement hulls
    # This is a simplified model based on published kayak/canoe resistance data

    if froude_number < 0.0:
        froude_number = 0.0  # Handle edge case

    if froude_number < 0.30:
        # Very low wave resistance below Fn = 0.30
        cr_base = 0.0001 * (froude_number**2)
    elif froude_number < 0.40:
        # Moderate increase between Fn = 0.30 and 0.40
        # Linear interpolation in this range
        fn_normalized = (froude_number - 0.30) / 0.10  # 0 to 1 in this range
        cr_base = 0.00009 + fn_normalized * 0.0007
    else:
        # Rapid exponential increase above Fn = 0.40 (hull speed region)
        excess_fn = froude_number - 0.40
        cr_base = 0.00079 + 0.003 * (excess_fn**2) + 0.01 * (excess_fn**3)

    # Adjust for prismatic coefficient if provided
    if prismatic_coefficient is not None:
        # Fuller hulls (higher Cp) have higher wave resistance
        # Typical kayak Cp ≈ 0.50-0.60
        # Use 0.55 as reference; scale Cr accordingly
        cp_reference = 0.55
        cp_factor = 1.0 + 0.5 * (prismatic_coefficient - cp_reference)
        cr_base *= cp_factor

    return max(0.0, cr_base)  # Ensure non-negative


def calculate_residuary_resistance(
    speed: float,
    wetted_surface: float,
    residuary_coefficient: float,
    water_density: float = WATER_DENSITY_FRESH,
) -> float:
    """Calculate residuary (wave-making + pressure) resistance.

    Residuary resistance includes wave-making drag and form drag (pressure resistance).
    For kayaks at typical paddling speeds, this is typically 10-30% of total resistance.
    It becomes dominant only near and above hull speed (Fn > 0.40).

    Formula: Rr = 0.5 × ρ × V² × Sw × Cr

    Note: Some formulations use a different reference area, but using Sw is common
    in empirical models and simplifies the total resistance calculation.

    Args:
        speed: Boat speed in m/s
        wetted_surface: Wetted surface area in m²
        residuary_coefficient: Residuary resistance coefficient (Cr)
        water_density: Water density in kg/m³ (default: 1000 for fresh water)

    Returns:
        float: Residuary resistance in Newtons

    Raises:
        ValueError: If any parameter is negative or water_density/wetted_surface are zero

    Example:
        >>> calculate_residuary_resistance(speed=2.0, wetted_surface=2.5, residuary_coefficient=0.0005)
        2.5  # Newtons
    """
    if speed < 0:
        raise ValueError(f"Speed must be non-negative, got {speed}")
    if wetted_surface <= 0:
        raise ValueError(f"Wetted surface must be positive, got {wetted_surface}")
    if residuary_coefficient < 0:
        raise ValueError(f"Residuary coefficient must be non-negative, got {residuary_coefficient}")
    if water_density <= 0:
        raise ValueError(f"Water density must be positive, got {water_density}")

    # Rr = 0.5 × ρ × V² × Sw × Cr
    return 0.5 * water_density * (speed**2) * wetted_surface * residuary_coefficient


def calculate_effective_power(resistance: float, speed: float) -> float:
    """Calculate effective power to overcome resistance.

    Effective power is the power delivered to the water to overcome hull resistance.
    This does not include propulsion efficiency losses (paddle slip, etc.).

    Formula: Pe = R × V

    Args:
        resistance: Total resistance force in Newtons
        speed: Boat speed in m/s

    Returns:
        float: Effective power in Watts

    Raises:
        ValueError: If resistance or speed are negative

    Example:
        >>> calculate_effective_power(resistance=20.0, speed=2.0)
        40.0  # Watts
    """
    if resistance < 0:
        raise ValueError(f"Resistance must be non-negative, got {resistance}")
    if speed < 0:
        raise ValueError(f"Speed must be non-negative, got {speed}")

    return resistance * speed


def calculate_paddler_power(
    effective_power: float, propulsion_efficiency: float = DEFAULT_PROPULSION_EFFICIENCY
) -> float:
    """Calculate required paddler power output.

    Paddler power is the actual mechanical power the paddler must produce,
    accounting for propulsion efficiency losses in the paddle stroke.

    Formula: Pp = Pe / η

    Typical paddle efficiency: 50-70% (η = 0.5-0.7)
    - Expert technique: 0.65-0.70
    - Average paddler: 0.55-0.60
    - Beginner: 0.50-0.55

    Args:
        effective_power: Effective power in Watts
        propulsion_efficiency: Paddle efficiency (0 < η ≤ 1), default: 0.60

    Returns:
        float: Paddler power output in Watts

    Raises:
        ValueError: If effective_power < 0 or propulsion_efficiency not in (0, 1]

    Example:
        >>> calculate_paddler_power(effective_power=40.0, propulsion_efficiency=0.60)
        66.67  # Watts
    """
    if effective_power < 0:
        raise ValueError(f"Effective power must be non-negative, got {effective_power}")
    if propulsion_efficiency <= 0 or propulsion_efficiency > 1:
        raise ValueError(
            f"Propulsion efficiency must be in range (0, 1], got {propulsion_efficiency}"
        )

    return effective_power / propulsion_efficiency


def calculate_resistance(
    speed: float,
    waterline_length: float,
    wetted_surface: float,
    prismatic_coefficient: Optional[float] = None,
    water_density: float = WATER_DENSITY_FRESH,
    kinematic_viscosity: float = KINEMATIC_VISCOSITY,
    roughness_allowance: float = DEFAULT_ROUGHNESS_ALLOWANCE,
    propulsion_efficiency: float = DEFAULT_PROPULSION_EFFICIENCY,
) -> ResistanceResult:
    """Calculate complete resistance and performance data at a given speed.

    This is the main function that combines all resistance components and
    performance metrics into a single result.

    Args:
        speed: Boat speed in m/s
        waterline_length: Waterline length (Lwl) in meters
        wetted_surface: Wetted surface area (Sw) in m²
        prismatic_coefficient: Prismatic coefficient (Cp), optional
        water_density: Water density in kg/m³ (default: 1000 fresh, 1025 salt)
        kinematic_viscosity: Kinematic viscosity in m²/s (default: 1.19e-6 at 15°C)
        roughness_allowance: Surface roughness coefficient (default: 0.0004)
        propulsion_efficiency: Paddle efficiency (default: 0.60)

    Returns:
        ResistanceResult: Complete resistance and performance data

    Example:
        >>> result = calculate_resistance(
        ...     speed=2.0,
        ...     waterline_length=5.0,
        ...     wetted_surface=2.5,
        ...     prismatic_coefficient=0.55
        ... )
        >>> print(f"Total resistance: {result.total_resistance:.1f} N")
        >>> print(f"Paddler power: {result.paddler_power:.1f} W")
    """
    # Calculate dimensionless parameters
    reynolds = calculate_reynolds_number(speed, waterline_length, kinematic_viscosity)
    froude = calculate_froude_number(speed, waterline_length)

    # Handle zero speed case (all resistances are zero)
    if speed == 0.0:
        return ResistanceResult(
            speed=speed,
            froude_number=froude,
            reynolds_number=reynolds,
            friction_coefficient=0.0,
            residuary_coefficient=0.0,
            frictional_resistance=0.0,
            residuary_resistance=0.0,
            total_resistance=0.0,
            effective_power=0.0,
            paddler_power=0.0,
        )

    # Calculate resistance coefficients
    cf = calculate_ittc_friction_coefficient(reynolds, roughness_allowance)
    cr = calculate_residuary_coefficient(froude, prismatic_coefficient)

    # Calculate resistance components
    rf = calculate_frictional_resistance(speed, wetted_surface, cf, water_density)
    rr = calculate_residuary_resistance(speed, wetted_surface, cr, water_density)
    rt = rf + rr

    # Calculate power
    pe = calculate_effective_power(rt, speed)
    pp = calculate_paddler_power(pe, propulsion_efficiency)

    return ResistanceResult(
        speed=speed,
        froude_number=froude,
        reynolds_number=reynolds,
        friction_coefficient=cf,
        residuary_coefficient=cr,
        frictional_resistance=rf,
        residuary_resistance=rr,
        total_resistance=rt,
        effective_power=pe,
        paddler_power=pp,
    )


def calculate_resistance_curve(
    speed_range: List[float],
    waterline_length: float,
    wetted_surface: float,
    prismatic_coefficient: Optional[float] = None,
    water_density: float = WATER_DENSITY_FRESH,
    kinematic_viscosity: float = KINEMATIC_VISCOSITY,
    roughness_allowance: float = DEFAULT_ROUGHNESS_ALLOWANCE,
    propulsion_efficiency: float = DEFAULT_PROPULSION_EFFICIENCY,
) -> List[ResistanceResult]:
    """Calculate resistance curve over a range of speeds.

    This function computes resistance and performance data at multiple speeds,
    suitable for generating resistance/power curves for visualization.

    Args:
        speed_range: List of speeds in m/s to evaluate
        waterline_length: Waterline length (Lwl) in meters
        wetted_surface: Wetted surface area (Sw) in m²
        prismatic_coefficient: Prismatic coefficient (Cp), optional
        water_density: Water density in kg/m³ (default: 1000 fresh, 1025 salt)
        kinematic_viscosity: Kinematic viscosity in m²/s (default: 1.19e-6 at 15°C)
        roughness_allowance: Surface roughness coefficient (default: 0.0004)
        propulsion_efficiency: Paddle efficiency (default: 0.60)

    Returns:
        List[ResistanceResult]: Resistance data for each speed in range

    Example:
        >>> import numpy as np
        >>> speeds = np.linspace(0.5, 4.0, 20)  # 0.5 to 4.0 m/s
        >>> results = calculate_resistance_curve(
        ...     speed_range=speeds,
        ...     waterline_length=5.0,
        ...     wetted_surface=2.5,
        ...     prismatic_coefficient=0.55
        ... )
        >>> # Plot resistance vs speed, power vs speed, etc.
    """
    results = []
    for speed in speed_range:
        result = calculate_resistance(
            speed=speed,
            waterline_length=waterline_length,
            wetted_surface=wetted_surface,
            prismatic_coefficient=prismatic_coefficient,
            water_density=water_density,
            kinematic_viscosity=kinematic_viscosity,
            roughness_allowance=roughness_allowance,
            propulsion_efficiency=propulsion_efficiency,
        )
        results.append(result)

    return results


def calculate_energy_for_distance(
    resistance: float, distance: float, propulsion_efficiency: float = DEFAULT_PROPULSION_EFFICIENCY
) -> float:
    """Calculate energy required to travel a given distance at constant speed.

    This computes the mechanical energy the paddler must expend to cover
    a specified distance, assuming constant speed and resistance.

    Formula: E = (R × d) / η

    where:
    - R is the total resistance (N)
    - d is the distance (m)
    - η is the propulsion efficiency

    Args:
        resistance: Total resistance force in Newtons (at the cruising speed)
        distance: Distance to travel in meters
        propulsion_efficiency: Paddle efficiency (0 < η ≤ 1), default: 0.60

    Returns:
        float: Required energy in Joules

    Raises:
        ValueError: If resistance or distance are negative, or efficiency not in (0, 1]

    Example:
        >>> # 20 N resistance, travel 10 km (10,000 m)
        >>> energy_joules = calculate_energy_for_distance(20.0, 10000.0, 0.60)
        >>> energy_kcal = energy_joules / 4184  # Convert to kilocalories
        >>> print(f"Energy: {energy_kcal:.1f} kcal")
    """
    if resistance < 0:
        raise ValueError(f"Resistance must be non-negative, got {resistance}")
    if distance < 0:
        raise ValueError(f"Distance must be non-negative, got {distance}")
    if propulsion_efficiency <= 0 or propulsion_efficiency > 1:
        raise ValueError(
            f"Propulsion efficiency must be in range (0, 1], got {propulsion_efficiency}"
        )

    # Work = Force × Distance
    effective_work = resistance * distance

    # Account for propulsion efficiency
    paddler_energy = effective_work / propulsion_efficiency

    return paddler_energy
