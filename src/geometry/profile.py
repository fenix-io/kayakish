import numpy as np
from typing import List
from src.geometry.point import Point3D


class Profile:
    station: float = 0.0

    def __init__(self, station: float = 0.0, points: List[Point3D] = None):
        if points is None:
            points = []
        self.points = []
        for new in points:
            for old in self.points:
                if (
                    np.isclose(new.x, old.x)
                    and np.isclose(new.y, old.y)
                    and np.isclose(new.z, old.z)
                ):
                    break
            else:
                self.points.append(new)
        self.station = station
        self.sort_points()

    def is_valid(self) -> bool:
        """Check if the profile has at least 3 points to form a valid shape."""
        return len(self.points) >= 3

    def validate_station_plane(self, tolerance: float = 1e-6) -> bool:
        """Validate that all points lie in the station plane x = self.station.

        Args:
            tolerance: Maximum allowed deviation from the station plane

        Returns:
            True if all points are in the plane, False otherwise
        """
        for point in self.points:
            if not np.isclose(point.x, self.station, atol=tolerance):
                return False
        return True

    def get_points(self) -> List[Point3D]:
        return self.points

    def to_json(self) -> str:
        points_list = [{"x": p.x, "y": p.y, "z": p.z} for p in self.points]
        return {"points": points_list}

    def sort_points(self):
        """Sort points in circular order (counterclockwise) around their centroid.

        This is necessary for the shoelace formula to work correctly.
        Points are sorted by their angle from the centroid in the y-z plane.
        """
        if not self.points or len(self.points) < 3:
            return

        # Calculate centroid of points (simple average)
        cy = sum(p.y for p in self.points) / len(self.points)
        cz = sum(p.z for p in self.points) / len(self.points)

        # Sort by angle from centroid (counterclockwise)
        def angle_from_centroid(p):
            return np.arctan2(p.z - cz, p.y - cy)

        self.points.sort(key=angle_from_centroid)

    def calculate_area(self) -> float:
        """Calculate the area of the profile using the shoelace formula.

        Assumes all points lie in the plane x = self.station.
        Points are automatically sorted in circular order before calculation.
        """
        if not self.is_valid():
            return 0.0  # Not a valid polygon

        # Validate that all points are in the station plane
        if not self.validate_station_plane():
            raise ValueError(f"Not all points lie in station plane x={self.station}")

        # Use y and z coordinates for 2D area calculation
        y = np.array([p.y for p in self.points])
        z = np.array([p.z for p in self.points])

        # Shoelace formula - always return positive area
        return 0.5 * np.abs(np.dot(y, np.roll(z, 1)) - np.dot(z, np.roll(y, 1)))

    def calculate_centroid(self) -> tuple[float, float]:
        """Calculate the centroid (center of mass) of the profile area.

        Returns (y_centroid, z_centroid) coordinates.
        Points are automatically sorted in circular order before calculation.
        """
        if not self.is_valid():
            return 0.0, 0.0

        # Calculate signed area (needed for centroid formula)
        n = len(self.points)
        signed_area = 0.0
        cy = 0.0
        cz = 0.0

        for i in range(n):
            j = (i + 1) % n  # Next point (wrapping around)
            yi, zi = self.points[i].y, self.points[i].z
            yj, zj = self.points[j].y, self.points[j].z

            cross = yi * zj - yj * zi
            signed_area += cross
            cy += (yi + yj) * cross
            cz += (zi + zj) * cross

        signed_area *= 0.5

        if abs(signed_area) < 1e-10:
            return 0.0, 0.0

        factor = 1.0 / (6.0 * signed_area)
        return cy * factor, cz * factor

    def calculate_volume_and_cg(self, step: float) -> tuple[float, Point3D]:
        """Calculate the volume and center of gravity of the profile assuming it is extruded along the x-axis."""

        area = self.calculate_area()
        volume = area * step

        # Calculate center of gravity (centroid) of the profile
        if area == 0:
            return volume, Point3D(self.station, 0.0, 0.0)

        cy, cz = self.calculate_centroid()

        # CG is at the centroid of the cross-section, at the center of the extrusion
        cg_x = self.station  # Center of the extrusion along x-axis
        cg_y = cy
        cg_z = cz

        return volume, Point3D(cg_x, cg_y, cg_z)
