"""
Point3D class for representing 3D coordinates and basic geometric operations.
"""

import numpy as np


class Point3D:
    """
    Represents a point in 3D space with x, y, z coordinates.

    Attributes:
        x (float): X-coordinate
        y (float): Y-coordinate (typically transverse, perpendicular to centerline)
        z (float): Z-coordinate (typically vertical)
        level (str | None): Optional level identifier (e.g., 'keel', 'chine', 'gunwale')
    """

    def __init__(self, x: float, y: float, z: float, level: str | None = None):
        """
        Initialize a 3D point.

        Args:
            x: X-coordinate
            y: Y-coordinate
            z: Z-coordinate
            level: Optional level identifier for the point
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.level = level

    @property
    def coordinates(self) -> np.ndarray:
        """
        Get coordinates as a numpy array.

        Returns:
            numpy array of [x, y, z]
        """
        return np.array([self.x, self.y, self.z])

    def distance_to(self, other: "Point3D") -> float:
        """
        Calculate Euclidean distance to another point.

        Args:
            other: Another Point3D object

        Returns:
            Distance between the two points
        """
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return np.sqrt(dx**2 + dy**2 + dz**2)

    def distance_to_origin(self) -> float:
        """
        Calculate distance from this point to the origin (0, 0, 0).

        Returns:
            Distance to origin
        """
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def translate(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> "Point3D":
        """
        Create a new point translated by given offsets.

        Args:
            dx: Translation in x direction
            dy: Translation in y direction
            dz: Translation in z direction

        Returns:
            New translated Point3D
        """
        return Point3D(self.x + dx, self.y + dy, self.z + dz, level=self.level)

    def rotate_x(self, angle_deg: float) -> "Point3D":
        """
        Rotate point around the X-axis (roll/heel).

        This is used for simulating heel angle in kayak stability calculations.
        The X-axis is the longitudinal axis along the kayak.

        Convention: positive angle = starboard down (heel to starboard)
        - Uses negative of angle for rotation to match naval architecture convention
        - With right-hand rule, negative rotation makes starboard side go down

        Args:
            angle_deg: Rotation angle in degrees (positive = starboard down)

        Returns:
            New rotated Point3D
        """
        # Negate angle to match convention: positive angle = starboard down
        angle_rad = np.radians(-angle_deg)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)

        # Rotation matrix around X-axis
        # [1    0       0   ]
        # [0  cos(a) -sin(a)]
        # [0  sin(a)  cos(a)]

        new_x = self.x
        new_y = self.y * cos_a - self.z * sin_a
        new_z = self.y * sin_a + self.z * cos_a

        return Point3D(new_x, new_y, new_z, level=self.level)

    def rotate_y(self, angle_deg: float) -> "Point3D":
        """
        Rotate point around the Y-axis (pitch/trim).

        Args:
            angle_deg: Rotation angle in degrees

        Returns:
            New rotated Point3D
        """
        angle_rad = np.radians(angle_deg)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)

        # Rotation matrix around Y-axis
        # [ cos(a)  0  sin(a)]
        # [   0     1    0   ]
        # [-sin(a)  0  cos(a)]

        new_x = self.x * cos_a + self.z * sin_a
        new_y = self.y
        new_z = -self.x * sin_a + self.z * cos_a

        return Point3D(new_x, new_y, new_z, level=self.level)

    def rotate_z(self, angle_deg: float) -> "Point3D":
        """
        Rotate point around the Z-axis (yaw).

        Args:
            angle_deg: Rotation angle in degrees

        Returns:
            New rotated Point3D
        """
        angle_rad = np.radians(angle_deg)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)

        # Rotation matrix around Z-axis
        # [cos(a) -sin(a)  0]
        # [sin(a)  cos(a)  0]
        # [  0       0     1]

        new_x = self.x * cos_a - self.y * sin_a
        new_y = self.x * sin_a + self.y * cos_a
        new_z = self.z

        return Point3D(new_x, new_y, new_z, level=self.level)

    def scale(self, sx: float = 1.0, sy: float = 1.0, sz: float = 1.0) -> "Point3D":
        """
        Create a new point scaled by given factors.

        Args:
            sx: Scale factor in x direction
            sy: Scale factor in y direction
            sz: Scale factor in z direction

        Returns:
            New scaled Point3D
        """
        return Point3D(self.x * sx, self.y * sy, self.z * sz, level=self.level)

    def __repr__(self) -> str:
        """String representation of the point."""
        if self.level is not None:
            return f"Point3D(x={self.x:.4f}, y={self.y:.4f}, z={self.z:.4f}, level='{self.level}')"
        return f"Point3D(x={self.x:.4f}, y={self.y:.4f}, z={self.z:.4f})"

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another point (within numerical tolerance).

        Args:
            other: Another Point3D object

        Returns:
            True if points are equal within tolerance (coordinates and level match)
        """
        if not isinstance(other, Point3D):
            return False
        return (
            np.isclose(self.x, other.x)
            and np.isclose(self.y, other.y)
            and np.isclose(self.z, other.z)
            and self.level == other.level
        )

    def __add__(self, other: "Point3D") -> "Point3D":
        """
        Add two points (vector addition).

        Args:
            other: Another Point3D object

        Returns:
            New Point3D with summed coordinates
        """
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Point3D") -> "Point3D":
        """
        Subtract two points (vector subtraction).

        Args:
            other: Another Point3D object

        Returns:
            New Point3D with difference coordinates
        """
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Point3D":
        """
        Multiply point by a scalar.

        Args:
            scalar: Scalar value

        Returns:
            New Point3D with scaled coordinates
        """
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> "Point3D":
        """
        Right multiplication by scalar (allows scalar * point).

        Args:
            scalar: Scalar value

        Returns:
            New Point3D with scaled coordinates
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Point3D":
        """
        Divide point by a scalar.

        Args:
            scalar: Scalar value (must be non-zero)

        Returns:
            New Point3D with divided coordinates
        """
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Point3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other: "Point3D") -> float:
        """
        Calculate dot product with another point (treating as vectors).

        Args:
            other: Another Point3D object

        Returns:
            Dot product value
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Point3D") -> "Point3D":
        """
        Calculate cross product with another point (treating as vectors).

        Args:
            other: Another Point3D object

        Returns:
            New Point3D representing the cross product
        """
        new_x = self.y * other.z - self.z * other.y
        new_y = self.z * other.x - self.x * other.z
        new_z = self.x * other.y - self.y * other.x
        return Point3D(new_x, new_y, new_z)

    def copy(self) -> "Point3D":
        """
        Create a copy of this point.

        Returns:
            New Point3D with same coordinates and level
        """
        return Point3D(self.x, self.y, self.z, level=self.level)
