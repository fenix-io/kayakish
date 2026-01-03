"""
Profile class for representing transverse cross-sections of a kayak hull.
"""

import numpy as np
from typing import List, Tuple
from .point import Point3D


class Profile:
    """
    Represents a transverse cross-section (profile) of the kayak hull.

    A profile is defined by a list of points at a specific longitudinal station.
    The profile is assumed to be symmetric about the centerline (y=0).

    Attributes:
        station (float): Longitudinal position of this profile (x-coordinate)
        points (List[Point3D]): List of points defining the profile
    """

    def __init__(self, station: float, points: List[Point3D]):
        """
        Initialize a profile at a given station.

        Args:
            station: Longitudinal position (x-coordinate) of this profile
            points: List of Point3D objects defining the profile shape
        """
        self.station = float(station)
        self.points = list(points)
        self._validate_points()

    def _validate_points(self) -> None:
        """
        Validate that all points have the same x-coordinate (station).

        Raises:
            ValueError: If points have inconsistent x-coordinates
        """
        if not self.points:
            return

        for i, point in enumerate(self.points):
            if not np.isclose(point.x, self.station):
                raise ValueError(
                    f"Point {i} has x={point.x}, but profile station is {self.station}. "
                    f"All points in a profile must have the same x-coordinate."
                )

    @property
    def num_points(self) -> int:
        """Get the number of points in this profile."""
        return len(self.points)

    def add_point(self, point: Point3D) -> None:
        """
        Add a point to this profile.

        Args:
            point: Point3D to add

        Raises:
            ValueError: If point x-coordinate doesn't match station
        """
        if not np.isclose(point.x, self.station):
            raise ValueError(f"Point x={point.x} doesn't match profile station {self.station}")
        self.points.append(point)

    def sort_points(self, by: str = "y") -> None:
        """
        Sort points in the profile.

        Args:
            by: Coordinate to sort by ('y' or 'z')
        """
        if by == "y":
            self.points.sort(key=lambda p: p.y)
        elif by == "z":
            self.points.sort(key=lambda p: p.z)
        else:
            raise ValueError(f"Invalid sort key: {by}. Use 'y' or 'z'.")

    def get_y_coordinates(self) -> np.ndarray:
        """
        Get array of y-coordinates from all points.

        Returns:
            Numpy array of y-coordinates
        """
        return np.array([p.y for p in self.points])

    def get_z_coordinates(self) -> np.ndarray:
        """
        Get array of z-coordinates from all points.

        Returns:
            Numpy array of z-coordinates
        """
        return np.array([p.z for p in self.points])

    def interpolate_points(self, num_points: int) -> "Profile":
        """
        Create a new profile with interpolated points along the profile curve.

        This creates evenly spaced points along the profile by interpolating
        between the existing points.

        Args:
            num_points: Number of points in the interpolated profile

        Returns:
            New Profile with interpolated points
        """
        if len(self.points) < 2:
            raise ValueError("Need at least 2 points to interpolate")

        # Sort points by y-coordinate for consistent interpolation
        sorted_points = sorted(self.points, key=lambda p: p.y)

        y_coords = np.array([p.y for p in sorted_points])
        z_coords = np.array([p.z for p in sorted_points])

        # Create evenly spaced y-coordinates for interpolation
        y_new = np.linspace(y_coords.min(), y_coords.max(), num_points)

        # Interpolate z-coordinates
        z_new = np.interp(y_new, y_coords, z_coords)

        # Create new points
        new_points = [Point3D(self.station, y, z) for y, z in zip(y_new, z_new)]

        return Profile(self.station, new_points)

    def find_waterline_intersection(self, waterline_z: float = 0.0) -> List[Point3D]:
        """
        Find intersection points of this profile with a horizontal waterline.

        Args:
            waterline_z: Z-coordinate of the waterline (default 0.0)

        Returns:
            List of Point3D objects at waterline intersections
        """
        intersections = []

        # Sort points by y-coordinate
        sorted_points = sorted(self.points, key=lambda p: p.y)

        # Check each segment between consecutive points
        for i in range(len(sorted_points) - 1):
            p1 = sorted_points[i]
            p2 = sorted_points[i + 1]

            # Check if waterline crosses this segment
            if (p1.z <= waterline_z <= p2.z) or (p2.z <= waterline_z <= p1.z):
                # Calculate intersection point
                if np.isclose(p1.z, p2.z):
                    # Horizontal segment at waterline - both points are on waterline
                    if np.isclose(p1.z, waterline_z):
                        intersections.append(p1.copy())
                        intersections.append(p2.copy())
                else:
                    # Linear interpolation to find intersection
                    t = (waterline_z - p1.z) / (p2.z - p1.z)
                    y_intersect = p1.y + t * (p2.y - p1.y)
                    intersections.append(Point3D(self.station, y_intersect, waterline_z))

        return intersections

    def calculate_area_below_waterline(self, waterline_z: float = 0.0) -> float:
        """
        Calculate the cross-sectional area below the waterline.

        Uses the Shoelace formula (surveyor's formula) to calculate the area
        of the polygon formed by the points below the waterline.

        Args:
            waterline_z: Z-coordinate of the waterline (default 0.0)

        Returns:
            Area of the submerged cross-section
        """
        # Get submerged points (including waterline intersections)
        submerged_points = self._get_submerged_polygon(waterline_z)

        if len(submerged_points) < 3:
            return 0.0  # Need at least 3 points to form an area

        # Apply Shoelace formula
        y_coords = np.array([p.y for p in submerged_points])
        z_coords = np.array([p.z for p in submerged_points])

        # Shoelace formula: A = 0.5 * |sum(y[i]*(z[i+1]-z[i-1]))|
        area = 0.5 * np.abs(np.sum(y_coords * (np.roll(z_coords, -1) - np.roll(z_coords, 1))))

        return area

    def calculate_centroid_below_waterline(self, waterline_z: float = 0.0) -> Tuple[float, float]:
        """
        Calculate the centroid of the submerged cross-section.

        Args:
            waterline_z: Z-coordinate of the waterline (default 0.0)

        Returns:
            Tuple of (y_centroid, z_centroid) coordinates
        """
        # Get submerged points
        submerged_points = self._get_submerged_polygon(waterline_z)

        if len(submerged_points) < 3:
            return (0.0, 0.0)

        # Calculate area first
        area = self.calculate_area_below_waterline(waterline_z)

        if area == 0:
            return (0.0, 0.0)

        y_coords = np.array([p.y for p in submerged_points])
        z_coords = np.array([p.z for p in submerged_points])

        # Calculate centroid using polygon formula
        n = len(submerged_points)
        y_c = 0.0
        z_c = 0.0

        for i in range(n):
            j = (i + 1) % n
            cross = y_coords[i] * z_coords[j] - y_coords[j] * z_coords[i]
            y_c += (y_coords[i] + y_coords[j]) * cross
            z_c += (z_coords[i] + z_coords[j]) * cross

        factor = 1.0 / (6.0 * area)
        y_c *= factor
        z_c *= factor

        return (y_c, z_c)

    def _get_submerged_polygon(self, waterline_z: float = 0.0) -> List[Point3D]:
        """
        Get the polygon points representing the submerged portion of the profile.

        Args:
            waterline_z: Z-coordinate of the waterline

        Returns:
            List of Point3D objects forming the submerged polygon
        """
        polygon = []

        # Sort points by y-coordinate
        sorted_points = sorted(self.points, key=lambda p: p.y)

        # Build the submerged polygon
        for i in range(len(sorted_points) - 1):
            p1 = sorted_points[i]
            p2 = sorted_points[i + 1]

            # Add p1 if it's below waterline
            if p1.z <= waterline_z:
                polygon.append(p1.copy())

            # Check if segment crosses waterline
            if (p1.z < waterline_z < p2.z) or (p2.z < waterline_z < p1.z):
                # Calculate intersection point
                t = (waterline_z - p1.z) / (p2.z - p1.z)
                y_intersect = p1.y + t * (p2.y - p1.y)
                polygon.append(Point3D(self.station, y_intersect, waterline_z))

        # Add last point if below waterline
        if sorted_points[-1].z <= waterline_z:
            polygon.append(sorted_points[-1].copy())

        return polygon

    def rotate_about_x(self, angle_deg: float) -> "Profile":
        """
        Create a new profile rotated about the X-axis (heel angle).

        This is used to simulate the profile shape when the kayak is heeled.

        Args:
            angle_deg: Heel angle in degrees (positive = starboard down)

        Returns:
            New Profile with rotated points
        """
        rotated_points = [p.rotate_x(angle_deg) for p in self.points]
        return Profile(self.station, rotated_points)

    def translate(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> "Profile":
        """
        Create a new profile translated by given offsets.

        Args:
            dx: Translation in x direction
            dy: Translation in y direction
            dz: Translation in z direction

        Returns:
            New Profile with translated points
        """
        translated_points = [p.translate(dx, dy, dz) for p in self.points]
        # Update station if x translation is applied
        new_station = self.station + dx
        return Profile(new_station, translated_points)

    def __repr__(self) -> str:
        """String representation of the profile."""
        return f"Profile(station={self.station:.4f}, num_points={self.num_points})"

    def __len__(self) -> int:
        """Get number of points in profile."""
        return len(self.points)

    def copy(self) -> "Profile":
        """
        Create a copy of this profile.

        Returns:
            New Profile with copied points
        """
        return Profile(self.station, [p.copy() for p in self.points])
