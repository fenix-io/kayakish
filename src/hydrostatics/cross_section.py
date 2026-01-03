"""
Cross-section properties calculation for kayak hull hydrostatics.

This module provides classes and functions for calculating hydrostatic properties
of transverse cross-sections, including:
- Submerged cross-sectional area
- Centroid position (center of area)
- Properties at various heel angles

Mathematical Background:
- Area calculation uses the Shoelace formula (surveyor's formula)
- Centroid calculation uses polygon moment formulas
- All calculations are performed on the submerged portion below the waterline

References:
- Rawson, K. J., & Tupper, E. C. (2001). Basic ship theory (5th ed.).
- Principles of Naval Architecture Series, SNAME
"""

from typing import List, Tuple
from dataclasses import dataclass
import numpy as np

from ..geometry import Profile


@dataclass
class CrossSectionProperties:
    """
    Hydrostatic properties of a transverse cross-section.

    This class encapsulates the calculated properties of a hull cross-section
    at a specific longitudinal station, waterline, and heel angle.

    Attributes:
        area: Submerged cross-sectional area (m² or consistent units)
        centroid_y: Transverse position of area centroid (m)
        centroid_z: Vertical position of area centroid (m)
        station: Longitudinal position of cross-section (m)
        waterline_z: Z-coordinate of the waterline (m)
        heel_angle: Heel angle in degrees (0 = upright, positive = starboard down)

    Properties:
        centroid: Tuple of (y, z) centroid coordinates

    Note:
        - For upright conditions, centroid_y should be close to 0 (centerline)
        - For heeled conditions, centroid_y shifts to the low side
        - Centroid_z is always negative (below waterline) for submerged sections
    """

    area: float
    centroid_y: float
    centroid_z: float
    station: float
    waterline_z: float
    heel_angle: float = 0.0

    @property
    def centroid(self) -> Tuple[float, float]:
        """Get centroid coordinates as a tuple (y, z)."""
        return (self.centroid_y, self.centroid_z)

    def __repr__(self) -> str:
        """String representation of cross-section properties."""
        return (
            f"CrossSectionProperties(\n"
            f"  station={self.station:.4f},\n"
            f"  area={self.area:.6f},\n"
            f"  centroid=({self.centroid_y:.6f}, {self.centroid_z:.6f}),\n"
            f"  waterline_z={self.waterline_z:.4f},\n"
            f"  heel_angle={self.heel_angle:.2f}°\n"
            f")"
        )

    def is_valid(self) -> bool:
        """
        Check if the properties represent a valid submerged section.

        Returns:
            True if area > 0 and centroid is below waterline
        """
        return self.area > 0 and self.centroid_z <= self.waterline_z


def calculate_section_properties(
    profile: Profile, waterline_z: float = 0.0, heel_angle: float = 0.0
) -> CrossSectionProperties:
    """
    Calculate hydrostatic properties of a cross-section.

    This function computes the submerged area and centroid position for a
    given profile at a specified waterline and heel angle. If a heel angle
    is provided, the profile is first rotated about the longitudinal axis
    (X-axis) before calculating properties.

    Args:
        profile: Profile object defining the cross-section geometry
        waterline_z: Z-coordinate of the waterline (default: 0.0)
        heel_angle: Heel angle in degrees (default: 0.0)
                   Positive = starboard down, negative = port down

    Returns:
        CrossSectionProperties object containing calculated properties

    Example:
        >>> profile = Profile(station=2.0, points=[...])
        >>> props = calculate_section_properties(profile, waterline_z=0.0)
        >>> print(f"Area: {props.area:.3f} m²")
        >>> print(f"Centroid: {props.centroid}")

    Note:
        - If heel_angle != 0, a new rotated profile is created (original unchanged)
        - Zero area is returned if profile is entirely above waterline
        - Uses Profile.calculate_area_below_waterline() and
          Profile.calculate_centroid_below_waterline() methods
    """
    # Apply heel angle if specified
    if not np.isclose(heel_angle, 0.0):
        working_profile = profile.rotate_about_x(heel_angle)
    else:
        working_profile = profile

    # Calculate area and centroid
    area = working_profile.calculate_area_below_waterline(waterline_z)
    centroid_y, centroid_z = working_profile.calculate_centroid_below_waterline(waterline_z)

    # Create and return properties object
    return CrossSectionProperties(
        area=area,
        centroid_y=centroid_y,
        centroid_z=centroid_z,
        station=profile.station,
        waterline_z=waterline_z,
        heel_angle=heel_angle,
    )


def calculate_properties_at_heel_angles(
    profile: Profile, heel_angles: List[float], waterline_z: float = 0.0
) -> List[CrossSectionProperties]:
    """
    Calculate cross-section properties at multiple heel angles.

    This is useful for generating stability curves and understanding how
    the submerged area and centroid position change with heel angle.

    Args:
        profile: Profile object defining the cross-section geometry
        heel_angles: List of heel angles in degrees to evaluate
        waterline_z: Z-coordinate of the waterline (default: 0.0)

    Returns:
        List of CrossSectionProperties, one for each heel angle

    Example:
        >>> profile = Profile(station=2.0, points=[...])
        >>> angles = [0, 5, 10, 15, 20, 25, 30]
        >>> properties = calculate_properties_at_heel_angles(profile, angles)
        >>> for props in properties:
        ...     print(f"Heel {props.heel_angle}°: Area={props.area:.3f}")

    Note:
        - Results are returned in the same order as heel_angles
        - This function is optimized for batch calculations
        - Consider plotting area and centroid vs. heel angle for analysis
    """
    properties_list = []

    for angle in heel_angles:
        props = calculate_section_properties(profile, waterline_z, angle)
        properties_list.append(props)

    return properties_list


def calculate_first_moment_of_area(
    profile: Profile, waterline_z: float = 0.0, heel_angle: float = 0.0, axis: str = "y"
) -> float:
    """
    Calculate first moment of area about a specified axis.

    The first moment of area is used in calculating centroids and is
    defined as the integral of area times distance from the axis.

    Args:
        profile: Profile object defining the cross-section geometry
        waterline_z: Z-coordinate of the waterline (default: 0.0)
        heel_angle: Heel angle in degrees (default: 0.0)
        axis: Axis about which to calculate moment ('y' or 'z')

    Returns:
        First moment of area (m³ or consistent units)

    Note:
        - First moment about y-axis: Q_y = ∫ z·dA
        - First moment about z-axis: Q_z = ∫ y·dA
        - Related to centroid by: centroid = Q / A
    """
    # Calculate properties
    props = calculate_section_properties(profile, waterline_z, heel_angle)

    if props.area == 0:
        return 0.0

    # First moment = area * centroid distance
    if axis == "y":
        # Moment about y-axis (using z-coordinate)
        return props.area * props.centroid_z
    elif axis == "z":
        # Moment about z-axis (using y-coordinate)
        return props.area * props.centroid_y
    else:
        raise ValueError(f"Invalid axis '{axis}'. Use 'y' or 'z'.")


def validate_cross_section_properties(
    props: CrossSectionProperties, tolerance: float = 1e-6
) -> Tuple[bool, List[str]]:
    """
    Validate cross-section properties for physical correctness.

    Checks for common issues such as:
    - Negative area
    - Centroid above waterline (for submerged area)
    - Unreasonable values

    Args:
        props: CrossSectionProperties object to validate
        tolerance: Numerical tolerance for comparisons

    Returns:
        Tuple of (is_valid, list_of_issues)

    Example:
        >>> is_valid, issues = validate_cross_section_properties(props)
        >>> if not is_valid:
        ...     print("Issues found:", issues)
    """
    issues = []

    # Check for negative area
    if props.area < -tolerance:
        issues.append(f"Negative area: {props.area}")

    # Check if centroid is above waterline (for non-zero area)
    if props.area > tolerance and props.centroid_z > props.waterline_z + tolerance:
        issues.append(
            f"Centroid above waterline: centroid_z={props.centroid_z}, "
            f"waterline_z={props.waterline_z}"
        )

    # Check for NaN or infinite values
    if not np.isfinite(props.area):
        issues.append(f"Non-finite area: {props.area}")

    if not np.isfinite(props.centroid_y) or not np.isfinite(props.centroid_z):
        issues.append(f"Non-finite centroid: ({props.centroid_y}, {props.centroid_z})")

    # Check heel angle range (typically -90 to +90 degrees)
    if abs(props.heel_angle) > 90 + tolerance:
        issues.append(f"Heel angle out of typical range: {props.heel_angle}°")

    is_valid = len(issues) == 0
    return is_valid, issues


def compare_properties(
    props1: CrossSectionProperties, props2: CrossSectionProperties, tolerance: float = 1e-6
) -> bool:
    """
    Compare two CrossSectionProperties objects for equality within tolerance.

    Args:
        props1: First properties object
        props2: Second properties object
        tolerance: Numerical tolerance for floating-point comparisons

    Returns:
        True if properties are equal within tolerance
    """
    return (
        np.isclose(props1.area, props2.area, atol=tolerance)
        and np.isclose(props1.centroid_y, props2.centroid_y, atol=tolerance)
        and np.isclose(props1.centroid_z, props2.centroid_z, atol=tolerance)
        and np.isclose(props1.station, props2.station, atol=tolerance)
        and np.isclose(props1.waterline_z, props2.waterline_z, atol=tolerance)
        and np.isclose(props1.heel_angle, props2.heel_angle, atol=tolerance)
    )


def calculate_full_section_properties(profile: Profile) -> Tuple[float, float, float]:
    """
    Calculate area and centroid of the entire hull cross-section.

    Unlike calculate_section_properties which computes properties for the
    submerged portion only, this function calculates properties for the
    complete hull section. This is useful for calculating the center of
    gravity of the hull structure.

    The calculation uses the Shoelace formula for area and polygon moment
    formulas for the centroid. The profile points should define a closed
    polygon representing the hull cross-section.

    Args:
        profile: Profile object defining the hull cross-section geometry

    Returns:
        Tuple of (area, centroid_y, centroid_z) where:
            - area: Total cross-sectional area (m²)
            - centroid_y: Transverse position of centroid (m)
            - centroid_z: Vertical position of centroid (m)

    Raises:
        ValueError: If profile has fewer than 3 points

    Example:
        >>> profile = Profile(station=2.0, points=[...])
        >>> area, cy, cz = calculate_full_section_properties(profile)
        >>> print(f"Full section area: {area:.4f} m²")
        >>> print(f"Centroid: ({cy:.4f}, {cz:.4f})")

    Note:
        - Points should form a closed polygon (clockwise or counter-clockwise)
        - For symmetric hulls, centroid_y should be approximately 0
        - The area includes the entire hull section, not just submerged portion
        - This assumes the profile points define the outer surface of the hull
    """
    if len(profile.points) < 3:
        raise ValueError(
            f"Need at least 3 points to calculate area and centroid. "
            f"Profile has {len(profile.points)} point(s)."
        )

    # Get coordinates as arrays
    y_coords = profile.get_y_coordinates()
    z_coords = profile.get_z_coordinates()

    # Calculate area using Shoelace formula
    # A = 0.5 * |sum(y[i]*(z[i+1]-z[i-1]))|
    area = 0.5 * np.abs(np.sum(y_coords * (np.roll(z_coords, -1) - np.roll(z_coords, 1))))

    if area == 0:
        # Degenerate polygon (all points collinear or overlapping)
        return (0.0, 0.0, 0.0)

    # Calculate centroid using polygon formula
    # For a polygon with vertices (y_i, z_i):
    # C_y = (1/(6A)) * sum((y_i + y_{i+1}) * (y_i * z_{i+1} - y_{i+1} * z_i))
    # C_z = (1/(6A)) * sum((z_i + z_{i+1}) * (y_i * z_{i+1} - y_{i+1} * z_i))

    n = len(profile.points)
    centroid_y = 0.0
    centroid_z = 0.0

    for i in range(n):
        j = (i + 1) % n  # Next vertex (wraps around to 0 at end)
        cross = y_coords[i] * z_coords[j] - y_coords[j] * z_coords[i]
        centroid_y += (y_coords[i] + y_coords[j]) * cross
        centroid_z += (z_coords[i] + z_coords[j]) * cross

    factor = 1.0 / (6.0 * area)
    centroid_y *= factor
    centroid_z *= factor

    return (area, centroid_y, centroid_z)
