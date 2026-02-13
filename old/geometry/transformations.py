"""
Coordinate transformation functions for kayak hull geometry.

This module provides comprehensive transformation functions for:
1. Heel angle transformations (roll about longitudinal axis)
2. Trim angle transformations (pitch about transverse axis)
3. Combined heel and trim transformations
4. Waterline intersection calculations for various conditions
5. Coordinate system conversions

These transformations are essential for stability analysis, displacement
calculations at different attitudes, and visualization.
"""

import numpy as np
from typing import List, Tuple, Optional
from .point import Point3D
from .profile import Profile
from .hull import KayakHull


# ============================================================================
# HEEL TRANSFORMATIONS (Roll about X-axis)
# ============================================================================


def apply_heel(
    point: Point3D, heel_angle: float, reference_point: Optional[Point3D] = None
) -> Point3D:
    """
    Apply heel angle (roll) to a point about the longitudinal axis.

    Heel angle represents rotation about the X-axis (longitudinal). Positive
    heel angle means starboard side goes down (roll to starboard).

    Args:
        point: Point to transform
        heel_angle: Heel angle in degrees (positive = starboard down)
        reference_point: Center of rotation (default: origin)

    Returns:
        Transformed Point3D

    Example:
        >>> point = Point3D(1.0, 0.5, 0.1)
        >>> heeled = apply_heel(point, 15.0)  # 15° heel to starboard
    """
    if reference_point is None:
        reference_point = Point3D(0, 0, 0)

    # Translate to reference point, rotate, translate back
    translated = point.translate(-reference_point.x, -reference_point.y, -reference_point.z)
    rotated = translated.rotate_x(heel_angle)
    result = rotated.translate(reference_point.x, reference_point.y, reference_point.z)

    return result


def apply_heel_to_profile(
    profile: Profile, heel_angle: float, reference_point: Optional[Point3D] = None
) -> Profile:
    """
    Apply heel angle to an entire profile.

    Args:
        profile: Profile to transform
        heel_angle: Heel angle in degrees (positive = starboard down)
        reference_point: Center of rotation (default: origin)

    Returns:
        New Profile with transformed points

    Example:
        >>> profile = Profile(2.0, points)
        >>> heeled_profile = apply_heel_to_profile(profile, 20.0)
    """
    if reference_point is None:
        reference_point = Point3D(0, 0, 0)

    heeled_points = [apply_heel(point, heel_angle, reference_point) for point in profile.points]

    return Profile(profile.station, heeled_points)


def apply_heel_to_hull(
    hull: KayakHull, heel_angle: float, reference_point: Optional[Point3D] = None
) -> KayakHull:
    """
    Apply heel angle to entire hull.

    Args:
        hull: Hull to transform
        heel_angle: Heel angle in degrees (positive = starboard down)
        reference_point: Center of rotation (default: hull origin)

    Returns:
        New KayakHull with all profiles heeled

    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles ...
        >>> heeled_hull = apply_heel_to_hull(hull, 30.0)
    """
    if reference_point is None:
        reference_point = hull.origin

    heeled_hull = KayakHull(origin=apply_heel(hull.origin, heel_angle, reference_point))

    for station, profile in hull.profiles.items():
        heeled_profile = apply_heel_to_profile(profile, heel_angle, reference_point)
        heeled_hull.add_profile(heeled_profile)

    return heeled_hull


# ============================================================================
# TRIM TRANSFORMATIONS (Pitch about Y-axis)
# ============================================================================


def apply_trim(
    point: Point3D, trim_angle: float, reference_point: Optional[Point3D] = None
) -> Point3D:
    """
    Apply trim angle (pitch) to a point about the transverse axis.

    Trim angle represents rotation about the Y-axis (transverse). Positive
    trim angle means bow up (pitch bow up/stern down).

    Args:
        point: Point to transform
        trim_angle: Trim angle in degrees (positive = bow up)
        reference_point: Center of rotation (default: origin)

    Returns:
        Transformed Point3D

    Example:
        >>> point = Point3D(2.0, 0.0, 0.1)
        >>> trimmed = apply_trim(point, 5.0)  # 5° bow up
    """
    if reference_point is None:
        reference_point = Point3D(0, 0, 0)

    # Translate to reference point, rotate, translate back
    translated = point.translate(-reference_point.x, -reference_point.y, -reference_point.z)
    rotated = translated.rotate_y(trim_angle)
    result = rotated.translate(reference_point.x, reference_point.y, reference_point.z)

    return result


def apply_trim_to_profile(
    profile: Profile, trim_angle: float, reference_point: Optional[Point3D] = None
) -> Profile:
    """
    Apply trim angle to an entire profile.

    Args:
        profile: Profile to transform
        trim_angle: Trim angle in degrees (positive = bow up)
        reference_point: Center of rotation (default: origin)

    Returns:
        New Profile with transformed points

    Note:
        When a profile is trimmed, the points rotate and their x-coordinates
        change. The new profile station is the average x-coordinate of the
        transformed points.
    """
    if reference_point is None:
        reference_point = Point3D(0, 0, 0)

    trimmed_points = [apply_trim(point, trim_angle, reference_point) for point in profile.points]

    # Calculate average x-coordinate of transformed points for new station
    if trimmed_points:
        new_station = sum(p.x for p in trimmed_points) / len(trimmed_points)

        # Adjust all points to have exactly this x-coordinate
        # (they should be close already, just fix numerical precision)
        adjusted_points = [Point3D(new_station, p.y, p.z) for p in trimmed_points]
    else:
        new_station = profile.station
        adjusted_points = []

    return Profile(new_station, adjusted_points)


def apply_trim_to_hull(
    hull: KayakHull, trim_angle: float, reference_point: Optional[Point3D] = None
) -> KayakHull:
    """
    Apply trim angle to entire hull.

    Args:
        hull: Hull to transform
        trim_angle: Trim angle in degrees (positive = bow up)
        reference_point: Center of rotation (default: hull origin)

    Returns:
        New KayakHull with all profiles trimmed
    """
    if reference_point is None:
        reference_point = hull.origin

    trimmed_hull = KayakHull(origin=apply_trim(hull.origin, trim_angle, reference_point))

    for station, profile in hull.profiles.items():
        trimmed_profile = apply_trim_to_profile(profile, trim_angle, reference_point)
        trimmed_hull.add_profile(trimmed_profile)

    return trimmed_hull


# ============================================================================
# COMBINED TRANSFORMATIONS
# ============================================================================


def apply_heel_and_trim(
    point: Point3D,
    heel_angle: float,
    trim_angle: float,
    reference_point: Optional[Point3D] = None,
    order: str = "heel_first",
) -> Point3D:
    """
    Apply both heel and trim angles to a point.

    Args:
        point: Point to transform
        heel_angle: Heel angle in degrees (positive = starboard down)
        trim_angle: Trim angle in degrees (positive = bow up)
        reference_point: Center of rotation (default: origin)
        order: Rotation order ('heel_first' or 'trim_first')

    Returns:
        Transformed Point3D

    Note:
        Order matters for combined rotations. 'heel_first' is typically
        more appropriate for ship/kayak motion (roll then pitch).
    """
    if order == "heel_first":
        result = apply_heel(point, heel_angle, reference_point)
        result = apply_trim(result, trim_angle, reference_point)
    elif order == "trim_first":
        result = apply_trim(point, trim_angle, reference_point)
        result = apply_heel(result, heel_angle, reference_point)
    else:
        raise ValueError(f"Invalid order: {order}. Use 'heel_first' or 'trim_first'")

    return result


def apply_heel_and_trim_to_hull(
    hull: KayakHull,
    heel_angle: float,
    trim_angle: float,
    reference_point: Optional[Point3D] = None,
    order: str = "heel_first",
) -> KayakHull:
    """
    Apply both heel and trim angles to entire hull.

    Args:
        hull: Hull to transform
        heel_angle: Heel angle in degrees (positive = starboard down)
        trim_angle: Trim angle in degrees (positive = bow up)
        reference_point: Center of rotation (default: hull origin)
        order: Rotation order ('heel_first' or 'trim_first')

    Returns:
        New KayakHull with combined transformation applied
    """
    if order == "heel_first":
        result = apply_heel_to_hull(hull, heel_angle, reference_point)
        result = apply_trim_to_hull(result, trim_angle, reference_point)
    elif order == "trim_first":
        result = apply_trim_to_hull(hull, trim_angle, reference_point)
        result = apply_heel_to_hull(result, heel_angle, reference_point)
    else:
        raise ValueError(f"Invalid order: {order}. Use 'heel_first' or 'trim_first'")

    return result


# ============================================================================
# WATERLINE CALCULATIONS
# ============================================================================


class Waterline:
    """
    Represents a water plane (waterline).

    The waterline can be horizontal (level) or inclined due to heel/trim.
    For general 3D plane equation: ax + by + cz + d = 0

    Attributes:
        a, b, c: Plane normal vector components (normalized)
        d: Plane offset
        z_reference: Reference z-coordinate (typically 0 for still water)
    """

    def __init__(self, z_reference: float = 0.0, heel_angle: float = 0.0, trim_angle: float = 0.0):
        """
        Initialize waterline plane.

        Args:
            z_reference: Reference z-coordinate for level waterline
            heel_angle: Heel angle in degrees (inclines waterline)
            trim_angle: Trim angle in degrees (inclines waterline)
        """
        self.z_reference = z_reference
        self.heel_angle = heel_angle
        self.trim_angle = trim_angle

        # Calculate plane normal vector
        self._calculate_plane_equation()

    def _calculate_plane_equation(self) -> None:
        """
        Calculate plane equation coefficients from heel and trim angles.

        For a horizontal waterline at z=z_ref, the plane is: z = z_ref
        With heel/trim, the plane rotates.
        """
        # Start with vertical normal (horizontal plane)
        normal = np.array([0.0, 0.0, 1.0])

        # Apply trim (rotation about Y-axis)
        if abs(self.trim_angle) > 1e-10:
            angle_rad = np.radians(self.trim_angle)
            cos_t = np.cos(angle_rad)
            sin_t = np.sin(angle_rad)
            # Rotate normal vector by trim angle about Y-axis
            R_trim = np.array([[cos_t, 0, sin_t], [0, 1, 0], [-sin_t, 0, cos_t]])
            normal = R_trim @ normal

        # Apply heel (rotation about X-axis)
        if abs(self.heel_angle) > 1e-10:
            angle_rad = np.radians(self.heel_angle)
            cos_h = np.cos(angle_rad)
            sin_h = np.sin(angle_rad)
            # Rotate normal vector by heel angle about X-axis
            R_heel = np.array([[1, 0, 0], [0, cos_h, -sin_h], [0, sin_h, cos_h]])
            normal = R_heel @ normal

        # Normalize
        normal = normal / np.linalg.norm(normal)

        self.a = normal[0]
        self.b = normal[1]
        self.c = normal[2]

        # Calculate d: plane passes through (0, 0, z_reference)
        # ax + by + cz + d = 0
        # a*0 + b*0 + c*z_ref + d = 0
        self.d = -self.c * self.z_reference

    def z_at_point(self, x: float, y: float) -> float:
        """
        Calculate z-coordinate of waterline at given (x, y) position.

        Args:
            x: Longitudinal coordinate
            y: Transverse coordinate

        Returns:
            Z-coordinate of waterline at (x, y)
        """
        # From plane equation: ax + by + cz + d = 0
        # Solve for z: z = -(ax + by + d) / c
        if abs(self.c) < 1e-10:
            # Nearly vertical plane - waterline not well defined
            return self.z_reference

        return -(self.a * x + self.b * y + self.d) / self.c

    def is_below_waterline(self, point: Point3D) -> bool:
        """
        Check if a point is below the waterline.

        Args:
            point: Point to check

        Returns:
            True if point is submerged (below waterline)
        """
        # Point is below if ax + by + cz + d <= 0 (assuming upward normal)
        value = self.a * point.x + self.b * point.y + self.c * point.z + self.d
        return value <= 0

    def signed_distance(self, point: Point3D) -> float:
        """
        Calculate signed distance from point to waterline.

        Args:
            point: Point to measure distance from

        Returns:
            Signed distance (negative = below waterline)
        """
        # Distance = (ax + by + cz + d) / sqrt(a^2 + b^2 + c^2)
        # Normal is already normalized, so denominator = 1
        return self.a * point.x + self.b * point.y + self.c * point.z + self.d


def find_waterline_intersection_segment(
    p1: Point3D, p2: Point3D, waterline: Waterline
) -> Optional[Point3D]:
    """
    Find intersection of a line segment with waterline plane.

    Args:
        p1: First endpoint of segment
        p2: Second endpoint of segment
        waterline: Waterline plane

    Returns:
        Intersection point or None if no intersection
    """
    # Calculate signed distances
    d1 = waterline.signed_distance(p1)
    d2 = waterline.signed_distance(p2)

    # Check if segment crosses waterline
    if d1 * d2 > 0:
        # Both points on same side - no intersection
        return None

    if abs(d1 - d2) < 1e-10:
        # Segment parallel to waterline
        if abs(d1) < 1e-10:
            # Segment on waterline - return midpoint
            return Point3D((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, (p1.z + p2.z) / 2)
        return None

    # Linear interpolation to find intersection
    t = -d1 / (d2 - d1)

    return Point3D(p1.x + t * (p2.x - p1.x), p1.y + t * (p2.y - p1.y), p1.z + t * (p2.z - p1.z))


def find_profile_waterline_intersection(profile: Profile, waterline: Waterline) -> List[Point3D]:
    """
    Find intersection points of a profile with waterline.

    Args:
        profile: Profile to intersect with waterline
        waterline: Waterline plane

    Returns:
        List of intersection points (typically 0 or 2 for closed profiles)
    """
    intersections = []

    # Sort points by y-coordinate for consistent processing
    sorted_points = sorted(profile.points, key=lambda p: p.y)

    # Check each segment
    for i in range(len(sorted_points) - 1):
        p1 = sorted_points[i]
        p2 = sorted_points[i + 1]

        intersection = find_waterline_intersection_segment(p1, p2, waterline)
        if intersection is not None:
            intersections.append(intersection)

    # Also check closing segment (last to first)
    if len(sorted_points) > 2:
        intersection = find_waterline_intersection_segment(
            sorted_points[-1], sorted_points[0], waterline
        )
        if intersection is not None:
            intersections.append(intersection)

    return intersections


def get_submerged_points(
    profile: Profile, waterline: Waterline, include_intersections: bool = True
) -> List[Point3D]:
    """
    Get points of profile that are submerged (below waterline).

    Args:
        profile: Profile to analyze
        waterline: Waterline plane
        include_intersections: Whether to include waterline intersection points

    Returns:
        List of points forming submerged portion (ordered)
    """
    submerged = []
    sorted_points = sorted(profile.points, key=lambda p: p.y)

    for i in range(len(sorted_points)):
        p1 = sorted_points[i]
        p2 = sorted_points[(i + 1) % len(sorted_points)]

        # Add p1 if submerged
        if waterline.is_below_waterline(p1):
            submerged.append(p1.copy())

        # Check for intersection between p1 and p2
        if include_intersections:
            d1 = waterline.signed_distance(p1)
            d2 = waterline.signed_distance(p2)

            if d1 * d2 < 0:  # Opposite sides - intersection exists
                intersection = find_waterline_intersection_segment(p1, p2, waterline)
                if intersection is not None:
                    submerged.append(intersection)

    return submerged


def calculate_submerged_area(profile: Profile, waterline: Waterline) -> float:
    """
    Calculate submerged cross-sectional area.

    Uses the Shoelace formula on the submerged polygon.

    Args:
        profile: Profile to analyze
        waterline: Waterline plane

    Returns:
        Submerged area
    """
    submerged_points = get_submerged_points(profile, waterline)

    if len(submerged_points) < 3:
        return 0.0

    # Apply Shoelace formula
    y_coords = np.array([p.y for p in submerged_points])
    z_coords = np.array([p.z for p in submerged_points])

    area = 0.5 * np.abs(np.sum(y_coords * (np.roll(z_coords, -1) - np.roll(z_coords, 1))))

    return area


def calculate_waterplane_area(
    hull: KayakHull, waterline: Waterline, num_stations: int = 50
) -> float:
    """
    Calculate waterplane area (area of hull at waterline).

    Args:
        hull: Hull to analyze
        waterline: Waterline plane
        num_stations: Number of stations to use for integration

    Returns:
        Waterplane area
    """

    # Get stations for integration
    stations = hull.get_stations()
    if len(stations) < 2:
        return 0.0

    # Generate dense station spacing
    x_min, x_max = stations[0], stations[-1]
    target_stations = np.linspace(x_min, x_max, num_stations).tolist()

    # Get or interpolate profiles at these stations
    list(hull.profiles.values())

    # Find waterline half-breadths at each station
    half_breadths = []
    x_positions = []

    for x in target_stations:
        # Get profile at this station
        if x in hull.profiles:
            profile = hull.profiles[x]
        else:
            # Interpolate if needed
            profile = hull.get_profile(x, interpolate=True)
            if profile is None:
                continue

        # Find waterline intersections
        intersections = find_profile_waterline_intersection(profile, waterline)

        if len(intersections) >= 2:
            # Calculate half-breadth (from centerline to intersection)
            # Assume symmetric, take maximum y-coordinate
            y_coords = [abs(p.y) for p in intersections]
            half_breadth = max(y_coords)
            half_breadths.append(half_breadth)
            x_positions.append(x)

    if len(half_breadths) < 2:
        return 0.0

    # Integrate using trapezoidal rule (twice half-breadth for full width)
    # Area = ∫ 2*half_breadth dx
    dx = np.diff(x_positions)
    avg_breadths = (np.array(half_breadths[:-1]) + np.array(half_breadths[1:])) / 2
    area = 2 * np.sum(avg_breadths * dx)  # Factor of 2 for both sides

    return area


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def get_heel_angle_for_waterline(
    profile: Profile, target_draft: float, max_angle: float = 90.0, tolerance: float = 0.001
) -> float:
    """
    Find heel angle that produces a specific draft (vertical immersion).

    Uses iterative search to find the heel angle that results in the
    desired draft at a given profile.

    Args:
        profile: Profile to analyze
        target_draft: Desired draft (positive downward)
        max_angle: Maximum heel angle to search (degrees)
        tolerance: Convergence tolerance

    Returns:
        Heel angle in degrees
    """
    from scipy.optimize import brentq

    def draft_error(heel_angle):
        """
        Calculate error between actual and target draft at given heel angle.

        Args:
            heel_angle: Heel angle in degrees

        Returns:
            Draft error (actual - target)
        """
        # Apply heel to profile
        heeled = apply_heel_to_profile(profile, heel_angle)

        # Find lowest point (maximum draft)
        z_coords = heeled.get_z_coordinates()
        actual_draft = -z_coords.min()  # Negative z is down

        return actual_draft - target_draft

    try:
        result = brentq(draft_error, -max_angle, max_angle)
        return result
    except ValueError:
        # No solution found in range
        return 0.0


def transform_to_body_coordinates(
    point: Point3D, hull_orientation: Tuple[float, float, float] = (0, 0, 0)
) -> Point3D:
    """
    Transform point from earth-fixed to body-fixed coordinates.

    Args:
        point: Point in earth-fixed coordinates
        hull_orientation: (heel, trim, yaw) in degrees

    Returns:
        Point in body-fixed coordinates
    """
    heel, trim, yaw = hull_orientation

    # Apply inverse transformations
    result = point.copy()

    if abs(yaw) > 1e-10:
        result = result.rotate_z(-yaw)

    if abs(trim) > 1e-10:
        result = result.rotate_y(-trim)

    if abs(heel) > 1e-10:
        result = result.rotate_x(-heel)

    return result


def transform_to_earth_coordinates(
    point: Point3D, hull_orientation: Tuple[float, float, float] = (0, 0, 0)
) -> Point3D:
    """
    Transform point from body-fixed to earth-fixed coordinates.

    Args:
        point: Point in body-fixed coordinates
        hull_orientation: (heel, trim, yaw) in degrees

    Returns:
        Point in earth-fixed coordinates
    """
    heel, trim, yaw = hull_orientation

    # Apply forward transformations
    result = point.copy()

    if abs(heel) > 1e-10:
        result = result.rotate_x(heel)

    if abs(trim) > 1e-10:
        result = result.rotate_y(trim)

    if abs(yaw) > 1e-10:
        result = result.rotate_z(yaw)

    return result
