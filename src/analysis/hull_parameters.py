"""Hull form parameters and coefficients calculation module.

This module provides functions to calculate dimensionless hull form coefficients
and geometric parameters that characterize hull shape. These parameters are used
as inputs to resistance estimation methods and hull performance analysis.

Form coefficients include:
- Block coefficient (Cb): Fullness relative to bounding box
- Prismatic coefficient (Cp): Volume distribution along length
- Midship coefficient (Cm): Fullness of largest cross-section
- Waterplane coefficient (Cwp): Fullness of waterplane area

References:
- Winters, J. — "The Shape of the Canoe"
- Marchaj, C.A. — "Sail Performance"
- Holtrop, J. & Mennen, G.G.J. (1982) — "An approximate power prediction method"
"""

from typing import Optional
from src.geometry.hull import Hull
from src.geometry.profile import Profile


def calculate_draft(hull: Hull, waterline: Optional[float] = None) -> float:
    """Calculate the draft (depth of submersion) of the hull.

    Draft (T) is the vertical distance from the waterline to the deepest point
    of the hull (keel).

    Args:
        hull: Hull object with calculated waterline
        waterline: The z-coordinate of the waterline. If None, uses hull.waterline.

    Returns:
        float: Draft in meters (m)

    Raises:
        ValueError: If waterline is not set or invalid

    Example:
        >>> draft = calculate_draft(hull)
        0.150  # m
    """
    if waterline is None:
        waterline = hull.waterline
    if waterline is None:
        raise ValueError(
            "Waterline is not set. "
            "Ensure waterline is calculated before calling calculate_draft()."
        )

    # Draft is waterline height above the keel (min_z)
    return waterline - hull.min_z


def calculate_waterplane_area(
    hull: Hull, waterline: Optional[float] = None, step: float = 0.05
) -> float:
    """Calculate the waterplane area (area of hull's footprint on water surface).

    Waterplane area (Awp) is the area enclosed by the waterline when viewed from above.
    This is the hull's "footprint" on the water surface. It affects initial stability
    and wave-making resistance.

    Args:
        hull: Hull object with calculated waterline
        waterline: The z-coordinate of the waterline. If None, uses hull.waterline.
        step: The longitudinal step size for integration in meters. Default 0.05 m.

    Returns:
        float: Waterplane area in square meters (m²)

    Raises:
        ValueError: If waterline is not set or invalid

    Example:
        >>> awp = calculate_waterplane_area(hull)
        1.850  # m²
    """
    if waterline is None:
        waterline = hull.waterline
    if waterline is None:
        raise ValueError(
            "Waterline is not set. "
            "Ensure waterline is calculated before calling calculate_waterplane_area()."
        )

    x = hull.min_x
    half_beams = []  # Half-beam at each station (centerline to max y)
    stations = []

    # Calculate half-beam at waterline for each station
    while x <= hull.max_x:
        points = []
        for curve in hull.curves:
            try:
                point = curve.eval_x(x)
                points.append(point)
            except ValueError:
                continue

        if len(points) >= 3:
            # Find y-coordinates where hull intersects waterline
            waterline_y_coords = []
            n = len(points)

            for i in range(n):
                p1 = points[i]
                p2 = points[(i + 1) % n]

                # If point is at waterline, add it
                if abs(p1.z - waterline) < 1e-6:
                    waterline_y_coords.append(abs(p1.y))

                # If edge crosses waterline, interpolate
                if (p1.z < waterline < p2.z) or (p2.z < waterline < p1.z):
                    t = (waterline - p1.z) / (p2.z - p1.z)
                    intersect_y = p1.y + t * (p2.y - p1.y)
                    waterline_y_coords.append(abs(intersect_y))

            if waterline_y_coords:
                # Half-beam is maximum y-coordinate at this station
                half_beam = max(waterline_y_coords)
                half_beams.append(half_beam)
                stations.append(x)

        x += step

    if len(half_beams) < 2:
        return 0.0

    # Integrate half-beam along length, then double for full waterplane area
    # Awp = 2 * ∫ half_beam(x) dx  (factor of 2 for port and starboard)
    area = 0.0
    for i in range(len(half_beams) - 1):
        avg_half_beam = (half_beams[i] + half_beams[i + 1]) / 2.0
        dx = stations[i + 1] - stations[i]
        area += avg_half_beam * dx

    return 2.0 * area  # Double for full waterplane (port + starboard)


def calculate_max_section_area(
    hull: Hull, waterline: Optional[float] = None, step: float = 0.05
) -> float:
    """Calculate the maximum submerged cross-section area.

    Maximum section area (Amax) is the largest cross-sectional area of the hull
    below the waterline, typically found near the widest point (midship).

    Args:
        hull: Hull object with calculated waterline
        waterline: The z-coordinate of the waterline. If None, uses hull.waterline.
        step: The longitudinal step size for sampling in meters. Default 0.05 m.

    Returns:
        float: Maximum submerged cross-section area in square meters (m²)

    Raises:
        ValueError: If waterline is not set or invalid

    Example:
        >>> amax = calculate_max_section_area(hull)
        0.095  # m²
    """
    if waterline is None:
        waterline = hull.waterline
    if waterline is None:
        raise ValueError(
            "Waterline is not set. "
            "Ensure waterline is calculated before calling calculate_max_section_area()."
        )

    x = hull.min_x
    max_area = 0.0

    # Find maximum cross-section area along the hull
    while x <= hull.max_x:
        points = []
        for curve in hull.curves:
            try:
                point = curve.eval_x(x)
                points.append(point)
            except ValueError:
                continue

        if len(points) >= 3:
            # Get points below waterline
            points_below = hull._get_points_below_waterline(points, waterline)
            profile = Profile(x, points_below)

            if profile.is_valid():
                area = profile.calculate_area()
                max_area = max(max_area, area)

        x += step

    return max_area


def calculate_block_coefficient(
    hull: Hull,
    waterline: Optional[float] = None,
    lwl: Optional[float] = None,
    bwl: Optional[float] = None,
    draft: Optional[float] = None,
) -> float:
    """Calculate the block coefficient (Cb) of the hull.

    Block coefficient describes the fullness of the hull relative to its bounding
    rectangular box below the waterline:
        Cb = ∇ / (LWL × BWL × T)

    Where:
        ∇ = displaced volume (m³)
        LWL = waterline length (m)
        BWL = waterline beam (m)
        T = draft (m)

    Typical values for kayaks: 0.25-0.40
    Higher Cb means a fuller, boxier hull; lower means finer ends.

    Args:
        hull: Hull object with calculated volume and waterline
        waterline: The z-coordinate of the waterline. If None, uses hull.waterline.
        lwl: Waterline length (m). If None, calculates from hull.
        bwl: Waterline beam (m). If None, calculates from hull.
        draft: Draft (m). If None, calculates from hull.

    Returns:
        float: Block coefficient (dimensionless, typically 0.2-0.5)

    Raises:
        ValueError: If required parameters are invalid or zero

    Example:
        >>> cb = calculate_block_coefficient(hull)
        0.352
    """
    if waterline is None:
        waterline = hull.waterline
    if waterline is None:
        raise ValueError(
            "Waterline is not set. "
            "Ensure waterline is calculated before calling calculate_block_coefficient()."
        )

    # Get displaced volume
    volume = hull.volume
    if volume <= 0:
        raise ValueError("Hull volume must be greater than zero.")

    # Calculate or use provided parameters
    if lwl is None:
        lwl = hull.waterline_length(waterline)
    if bwl is None:
        bwl = hull.waterline_beam(waterline)
    if draft is None:
        draft = calculate_draft(hull, waterline)

    if lwl <= 0 or bwl <= 0 or draft <= 0:
        raise ValueError(
            f"Invalid hull parameters: LWL={lwl}, BWL={bwl}, T={draft}. "
            "All must be greater than zero."
        )

    cb = volume / (lwl * bwl * draft)
    return cb


def calculate_prismatic_coefficient(
    hull: Hull,
    waterline: Optional[float] = None,
    lwl: Optional[float] = None,
    amax: Optional[float] = None,
) -> float:
    """Calculate the prismatic coefficient (Cp) of the hull.

    Prismatic coefficient describes how volume is distributed along the hull length:
        Cp = ∇ / (Amax × LWL)

    Where:
        ∇ = displaced volume (m³)
        Amax = maximum submerged cross-section area (m²)
        LWL = waterline length (m)

    Typical values for kayaks: 0.50-0.60
    Low Cp (0.50-0.55): Fine ends, volume concentrated amidships
    High Cp (0.60-0.70): Fuller ends, volume more evenly distributed

    Args:
        hull: Hull object with calculated volume and waterline
        waterline: The z-coordinate of the waterline. If None, uses hull.waterline.
        lwl: Waterline length (m). If None, calculates from hull.
        amax: Maximum section area (m²). If None, calculates from hull.

    Returns:
        float: Prismatic coefficient (dimensionless, typically 0.4-0.7)

    Raises:
        ValueError: If required parameters are invalid or zero

    Example:
        >>> cp = calculate_prismatic_coefficient(hull)
        0.528
    """
    if waterline is None:
        waterline = hull.waterline
    if waterline is None:
        raise ValueError(
            "Waterline is not set. "
            "Ensure waterline is calculated before calling calculate_prismatic_coefficient()."
        )

    # Get displaced volume
    volume = hull.volume
    if volume <= 0:
        raise ValueError("Hull volume must be greater than zero.")

    # Calculate or use provided parameters
    if lwl is None:
        lwl = hull.waterline_length(waterline)
    if amax is None:
        amax = calculate_max_section_area(hull, waterline)

    if lwl <= 0 or amax <= 0:
        raise ValueError(
            f"Invalid hull parameters: LWL={lwl}, Amax={amax}. " "All must be greater than zero."
        )

    cp = volume / (amax * lwl)
    return cp


def calculate_midship_coefficient(
    hull: Hull,
    waterline: Optional[float] = None,
    bwl: Optional[float] = None,
    draft: Optional[float] = None,
    amax: Optional[float] = None,
) -> float:
    """Calculate the midship coefficient (Cm) of the hull.

    Midship coefficient describes the fullness of the largest cross-section:
        Cm = Amax / (BWL × T)

    Where:
        Amax = maximum submerged cross-section area (m²)
        BWL = waterline beam at widest station (m)
        T = draft (m)

    Typical values for kayaks: 0.60-0.80
    Round-bottom kayak: 0.60-0.80
    V-shaped hull: 0.50-0.65
    Flat-bottom: 0.95-1.0

    Note: Cb = Cp × Cm (relationship between coefficients)

    Args:
        hull: Hull object with calculated waterline
        waterline: The z-coordinate of the waterline. If None, uses hull.waterline.
        bwl: Waterline beam (m). If None, calculates from hull.
        draft: Draft (m). If None, calculates from hull.
        amax: Maximum section area (m²). If None, calculates from hull.

    Returns:
        float: Midship coefficient (dimensionless, typically 0.5-1.0)

    Raises:
        ValueError: If required parameters are invalid or zero

    Example:
        >>> cm = calculate_midship_coefficient(hull)
        0.667
    """
    if waterline is None:
        waterline = hull.waterline
    if waterline is None:
        raise ValueError(
            "Waterline is not set. "
            "Ensure waterline is calculated before calling calculate_midship_coefficient()."
        )

    # Calculate or use provided parameters
    if bwl is None:
        bwl = hull.waterline_beam(waterline)
    if draft is None:
        draft = calculate_draft(hull, waterline)
    if amax is None:
        amax = calculate_max_section_area(hull, waterline)

    if bwl <= 0 or draft <= 0 or amax <= 0:
        raise ValueError(
            f"Invalid hull parameters: BWL={bwl}, T={draft}, Amax={amax}. "
            "All must be greater than zero."
        )

    cm = amax / (bwl * draft)
    return cm


def calculate_waterplane_coefficient(
    hull: Hull,
    waterline: Optional[float] = None,
    lwl: Optional[float] = None,
    bwl: Optional[float] = None,
    awp: Optional[float] = None,
) -> float:
    """Calculate the waterplane coefficient (Cwp) of the hull.

    Waterplane coefficient describes the fullness of the waterplane area:
        Cwp = Awp / (LWL × BWL)

    Where:
        Awp = waterplane area (m²)
        LWL = waterline length (m)
        BWL = waterline beam (m)

    Typical values for kayaks: 0.65-0.80
    Affects initial stability and wave-making resistance.

    Args:
        hull: Hull object with calculated waterline
        waterline: The z-coordinate of the waterline. If None, uses hull.waterline.
        lwl: Waterline length (m). If None, calculates from hull.
        bwl: Waterline beam (m). If None, calculates from hull.
        awp: Waterplane area (m²). If None, calculates from hull.

    Returns:
        float: Waterplane coefficient (dimensionless, typically 0.6-0.9)

    Raises:
        ValueError: If required parameters are invalid or zero

    Example:
        >>> cwp = calculate_waterplane_coefficient(hull)
        0.725
    """
    if waterline is None:
        waterline = hull.waterline
    if waterline is None:
        raise ValueError(
            "Waterline is not set. "
            "Ensure waterline is calculated before calling calculate_waterplane_coefficient()."
        )

    # Calculate or use provided parameters
    if lwl is None:
        lwl = hull.waterline_length(waterline)
    if bwl is None:
        bwl = hull.waterline_beam(waterline)
    if awp is None:
        awp = calculate_waterplane_area(hull, waterline)

    if lwl <= 0 or bwl <= 0 or awp <= 0:
        raise ValueError(
            f"Invalid hull parameters: LWL={lwl}, BWL={bwl}, Awp={awp}. "
            "All must be greater than zero."
        )

    cwp = awp / (lwl * bwl)
    return cwp
