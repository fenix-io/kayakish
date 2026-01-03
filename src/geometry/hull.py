"""
KayakHull class for defining and managing kayak hull geometry.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from .point import Point3D
from .profile import Profile


class KayakHull:
    """
    Represents the complete hull geometry of a kayak.

    The hull is defined by a collection of transverse profiles at various
    longitudinal stations. The coordinate system is referenced to the centerline
    plane (y=0), with:
    - X-axis: Longitudinal (along kayak length)
    - Y-axis: Transverse (port negative, starboard positive)
    - Z-axis: Vertical (down negative, up positive)

    Attributes:
        profiles (Dict[float, Profile]): Dictionary mapping station positions to profiles
        origin (Point3D): Reference origin point on centerline
        coordinate_system (str): Coordinate system reference ('bow_origin', 'stern_origin', etc.)
        bow_points (Optional[List[Point3D]]): Bow end points (multi-point or single apex)
        stern_points (Optional[List[Point3D]]): Stern end points (multi-point or single apex)
        bow_apex (Optional[Point3D]): Legacy property - first bow point if exists
        stern_apex (Optional[Point3D]): Legacy property - first stern point if exists
        metadata (Optional[Dict]): Additional metadata from input file
        length (float): Overall length of kayak
        beam (float): Maximum beam (width)
    """

    def __init__(
        self,
        origin: Optional[Point3D] = None,
        bow_apex: Point3D = None,
        stern_apex: Point3D = None,
        profiles: List[Profile] = None,
       
    ):
        """
        Initialize a kayak hull.

        Args:
            origin: Reference origin point (default: Point3D(0, 0, 0))
            coordinate_system: Coordinate system reference (default: 'bow_origin')
            bow_apex: Optional single bow apex point (legacy, converted to bow_points)
            stern_apex: Optional single stern apex point (legacy, converted to stern_points)
            bow_points: Optional list of bow end points (preferred)
            stern_points: Optional list of stern end points (preferred)

        Note:
            For backward compatibility, if bow_apex/stern_apex are provided instead of
            bow_points/stern_points, they will be automatically converted to single-element lists.
        """
        self.profiles = profiles
        
        self.coordinate_system = coordinate_system

        # Handle backward compatibility: convert single apex to list
        if bow_points is not None:
            self.bow_points = bow_points
        elif bow_apex is not None:
            self.bow_points = [bow_apex]
        else:
            self.bow_points = None

        if stern_points is not None:
            self.stern_points = stern_points
        elif stern_apex is not None:
            self.stern_points = [stern_apex]
        else:
            self.stern_points = None

        self.metadata: Optional[Dict] = None
        self._sorted_stations: Optional[List[float]] = None

    @property
    def bow_apex(self) -> Optional[Point3D]:
        """
        Legacy property for backward compatibility.
        Returns the first bow point if bow_points exists, otherwise None.
        """
        if self.bow_points and len(self.bow_points) > 0:
            return self.bow_points[0]
        return None

    @property
    def stern_apex(self) -> Optional[Point3D]:
        """
        Legacy property for backward compatibility.
        Returns the first stern point if stern_points exists, otherwise None.
        """
        if self.stern_points and len(self.stern_points) > 0:
            return self.stern_points[0]
        return None

    def add_profile(self, profile: Profile) -> None:
        """
        Add a profile to the hull at its station position.

        Args:
            profile: Profile object to add

        Raises:
            ValueError: If a profile already exists at this station
        """
        station = profile.station

        if station in self.profiles:
            raise ValueError(
                f"Profile already exists at station {station}. "
                f"Use update_profile() to replace it."
            )

        self.profiles[station] = profile
        self._sorted_stations = None  # Invalidate cached sorted stations

    def add_profile_from_points(self, station: float, points: List[Point3D]) -> None:
        """
        Create and add a profile from a list of points.

        Args:
            station: Longitudinal position for the profile
            points: List of Point3D objects defining the profile

        Raises:
            ValueError: If a profile already exists at this station
        """
        profile = Profile(station, points)
        self.add_profile(profile)

    def update_profile(self, profile: Profile) -> None:
        """
        Update or add a profile at its station position.

        Args:
            profile: Profile object to update/add
        """
        self.profiles[profile.station] = profile
        self._sorted_stations = None

    def remove_profile(self, station: float) -> None:
        """
        Remove a profile at the specified station.

        Args:
            station: Station position of profile to remove

        Raises:
            KeyError: If no profile exists at this station
        """
        if station not in self.profiles:
            raise KeyError(f"No profile exists at station {station}")

        del self.profiles[station]
        self._sorted_stations = None

    def get_profile(self, station: float, interpolate: bool = True) -> Optional[Profile]:
        """
        Retrieve a profile at the specified station.

        If a profile exists exactly at the station, return it.
        If interpolate=True and no exact match, interpolate between adjacent profiles.

        Args:
            station: Longitudinal position
            interpolate: Whether to interpolate if no exact match (default: True)

        Returns:
            Profile at the station, or None if not found and interpolate=False

        Raises:
            ValueError: If interpolation requested but insufficient profiles exist
        """
        # Check for exact match
        if station in self.profiles:
            return self.profiles[station]

        if not interpolate:
            return None

        # Interpolate between adjacent profiles
        return self._interpolate_profile(station)

    def _interpolate_profile(self, station: float) -> Profile:
        """
        Interpolate a profile at the given station from adjacent profiles.

        Args:
            station: Longitudinal position for interpolation

        Returns:
            Interpolated Profile

        Raises:
            ValueError: If insufficient profiles for interpolation
        """
        if len(self.profiles) < 2:
            raise ValueError(
                "Need at least 2 profiles to interpolate. "
                f"Currently have {len(self.profiles)} profile(s)."
            )

        stations = self.get_stations()

        # Check if station is within range
        if station < stations[0] or station > stations[-1]:
            raise ValueError(
                f"Station {station} is outside the hull range " f"[{stations[0]}, {stations[-1]}]"
            )

        # Find adjacent stations
        station_before = None
        station_after = None

        for s in stations:
            if s < station:
                station_before = s
            elif s > station:
                station_after = s
                break

        if station_before is None or station_after is None:
            raise ValueError(f"Cannot find adjacent profiles for station {station}")

        # Get the two profiles
        profile_before = self.profiles[station_before]
        profile_after = self.profiles[station_after]

        # Linear interpolation factor
        t = (station - station_before) / (station_after - station_before)

        # Interpolate points between the two profiles
        interpolated_points = self._interpolate_points_between_profiles(
            profile_before, profile_after, t, station
        )

        return Profile(station, interpolated_points)

    def _interpolate_points_between_profiles(
        self, profile1: Profile, profile2: Profile, t: float, target_station: float
    ) -> List[Point3D]:
        """
        Interpolate points between two profiles.

        This method handles profiles with different numbers of points by
        interpolating both profiles to a common set of y-coordinates.

        Args:
            profile1: First profile (at lower station)
            profile2: Second profile (at higher station)
            t: Interpolation factor (0 = profile1, 1 = profile2)
            target_station: Target station for interpolated profile

        Returns:
            List of interpolated Point3D objects
        """
        # Sort points by y-coordinate
        points1 = sorted(profile1.points, key=lambda p: p.y)
        points2 = sorted(profile2.points, key=lambda p: p.y)

        # Get y-coordinate ranges
        y1 = np.array([p.y for p in points1])
        z1 = np.array([p.z for p in points1])

        y2 = np.array([p.y for p in points2])
        z2 = np.array([p.z for p in points2])

        # Determine common y-coordinate range
        y_min = max(y1.min(), y2.min())
        y_max = min(y1.max(), y2.max())

        # Use the average number of points
        num_points = (len(points1) + len(points2)) // 2
        num_points = max(num_points, 10)  # Minimum 10 points

        # Create common y-coordinates
        y_common = np.linspace(y_min, y_max, num_points)

        # Interpolate z-coordinates for both profiles
        z1_interp = np.interp(y_common, y1, z1)
        z2_interp = np.interp(y_common, y2, z2)

        # Linear interpolation between the two profiles
        z_result = (1 - t) * z1_interp + t * z2_interp

        # Create interpolated points
        interpolated_points = [Point3D(target_station, y, z) for y, z in zip(y_common, z_result)]

        return interpolated_points

    def get_stations(self) -> List[float]:
        """
        Get sorted list of all station positions.

        Returns:
            Sorted list of station positions
        """
        if self._sorted_stations is None:
            self._sorted_stations = sorted(self.profiles.keys())
        return self._sorted_stations

    @property
    def num_profiles(self) -> int:
        """Get the number of profiles in the hull."""
        return len(self.profiles)

    @property
    def length(self) -> float:
        """
        Get overall length of the hull.

        Returns:
            Distance between bow and stern stations (including apex points if defined)
        """
        if len(self.profiles) == 0 and self.bow_apex is None and self.stern_apex is None:
            return 0.0

        # Use bow/stern station methods to account for apex points
        try:
            return abs(self.get_bow_station() - self.get_stern_station())
        except ValueError:
            # If we can't get bow/stern stations, fall back to profile range
            if len(self.profiles) < 2:
                return 0.0
            stations = self.get_stations()
            return abs(stations[-1] - stations[0])

    @property
    def max_beam(self) -> float:
        """
        Get maximum beam (width) of the hull.

        Returns:
            Maximum transverse distance across all profiles
        """
        if len(self.profiles) == 0:
            return 0.0

        max_width = 0.0

        for profile in self.profiles.values():
            y_coords = profile.get_y_coordinates()
            if len(y_coords) > 0:
                width = y_coords.max() - y_coords.min()
                max_width = max(max_width, width)

        return max_width

    def validate_symmetry(self, tolerance: float = 1e-6) -> Tuple[bool, List[str]]:
        """
        Validate that all profiles are symmetric about the centerline (y=0).

        Args:
            tolerance: Maximum allowed asymmetry

        Returns:
            Tuple of (is_symmetric, list_of_error_messages)
        """
        is_symmetric = True
        errors = []

        for station, profile in self.profiles.items():
            # Get y-coordinates
            y_coords = profile.get_y_coordinates()

            # Check if we have points on both sides of centerline
            port_points = y_coords[y_coords < -tolerance]
            stbd_points = y_coords[y_coords > tolerance]

            if len(port_points) == 0 and len(stbd_points) == 0:
                # All points on centerline - symmetric
                continue

            if len(port_points) == 0 or len(stbd_points) == 0:
                is_symmetric = False
                errors.append(
                    f"Station {station}: Profile has points only on one side of centerline"
                )
                continue

            # Check symmetry by comparing port and starboard points
            # For each starboard point, find corresponding port point
            for p in profile.points:
                if abs(p.y) < tolerance:  # Skip centerline points
                    continue

                # Find mirror point
                mirror_y = -p.y
                found_mirror = False

                for p2 in profile.points:
                    if abs(p2.y - mirror_y) < tolerance:
                        # Check if z-coordinate matches
                        if abs(p2.z - p.z) < tolerance:
                            found_mirror = True
                            break

                if not found_mirror:
                    is_symmetric = False
                    errors.append(
                        f"Station {station}: No symmetric point found for y={p.y:.4f}, z={p.z:.4f}"
                    )
                    break  # Only report first error per profile

        return is_symmetric, errors

    def validate_bow_stern_points(self, tolerance: float = 1e-6) -> bool:
        """
        Validate that all bow/stern points are on the centerline (y = 0.0).

        Args:
            tolerance: Maximum allowed deviation from centerline (default: 1e-6)

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If any bow/stern point is not on centerline
        """
        if self.bow_points is not None:
            for i, point in enumerate(self.bow_points):
                if abs(point.y) > tolerance:
                    raise ValueError(
                        f"Bow point {i} at ({point.x:.4f}, {point.y:.4f}, {point.z:.4f}) "
                        f"is not on centerline. y-coordinate must be 0.0 (within {tolerance})"
                    )

        if self.stern_points is not None:
            for i, point in enumerate(self.stern_points):
                if abs(point.y) > tolerance:
                    raise ValueError(
                        f"Stern point {i} at ({point.x:.4f}, {point.y:.4f}, {point.z:.4f}) "
                        f"is not on centerline. y-coordinate must be 0.0 (within {tolerance})"
                    )

        return True

    def verify_bow_stern_point_count(self) -> bool:
        """
        Verify that bow/stern point count matches expected structure.

        This checks that if multi-point bow/stern are defined, they have a reasonable
        number of points that could correspond to profile levels.

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If point counts seem inconsistent
        """
        if self.bow_points and len(self.bow_points) > 1:
            # Multi-point bow - check it's reasonable
            if len(self.profiles) == 0:
                raise ValueError("Multi-point bow defined but no profiles exist to match against")

            # Get a sample profile to check structure
            sample_profile = next(iter(self.profiles.values()))
            # Count unique y-coordinates (approximate levels)
            unique_y = len(set(abs(pt.y) for pt in sample_profile.points))

            if len(self.bow_points) > unique_y:
                raise ValueError(
                    f"Bow has {len(self.bow_points)} points but profiles only have "
                    f"~{unique_y} distinct levels. Point count may be too high."
                )

        if self.stern_points and len(self.stern_points) > 1:
            # Multi-point stern - check it's reasonable
            if len(self.profiles) == 0:
                raise ValueError("Multi-point stern defined but no profiles exist to match against")

            # Get a sample profile to check structure
            sample_profile = next(iter(self.profiles.values()))
            # Count unique y-coordinates (approximate levels)
            unique_y = len(set(abs(pt.y) for pt in sample_profile.points))

            if len(self.stern_points) > unique_y:
                raise ValueError(
                    f"Stern has {len(self.stern_points)} points but profiles only have "
                    f"~{unique_y} distinct levels. Point count may be too high."
                )

        return True

    def validate_data_consistency(self) -> Tuple[bool, List[str]]:
        """
        Validate data consistency across all profiles.

        Checks:
        - All profiles have at least 3 points
        - Profiles are ordered by station
        - No duplicate stations
        - All profile points have correct x-coordinate

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        is_valid = True
        errors = []

        if len(self.profiles) == 0:
            errors.append("Hull has no profiles")
            return False, errors

        stations = self.get_stations()

        # Check for minimum points in each profile
        for station, profile in self.profiles.items():
            if len(profile.points) < 3:
                is_valid = False
                errors.append(
                    f"Station {station}: Profile has only {len(profile.points)} points "
                    f"(minimum 3 required)"
                )

            # Validate that all points have correct x-coordinate
            for i, point in enumerate(profile.points):
                if not np.isclose(point.x, station):
                    is_valid = False
                    errors.append(
                        f"Station {station}: Point {i} has x={point.x} " f"(should be {station})"
                    )

        # Check for reasonable station spacing
        if len(stations) > 1:
            spacings = np.diff(stations)
            if np.any(spacings <= 0):
                is_valid = False
                errors.append("Stations are not in ascending order")

        return is_valid, errors

    def get_bow_station(self) -> float:
        """
        Get the bow (forward) station position.

        Returns the station of the bow, respecting the coordinate system.
        If bow_apex is defined, returns its x-coordinate.
        Otherwise, returns the appropriate extreme station based on coordinate system.

        Returns:
            Bow station position
        """
        if len(self.profiles) == 0 and self.bow_apex is None:
            raise ValueError("Hull has no profiles and no bow_apex defined")

        # If explicit bow apex is defined, use it
        if self.bow_apex is not None:
            return self.bow_apex.x

        # Otherwise determine from profiles based on coordinate system
        stations = list(self.profiles.keys())
        if self.coordinate_system == "bow_origin":
            # Bow is at minimum x (origin is at bow)
            return min(stations)
        elif self.coordinate_system == "stern_origin":
            # Bow is at maximum x (origin is at stern)
            return max(stations)
        elif self.coordinate_system == "midship_origin":
            # Bow is at maximum x (origin is at midship)
            return max(stations)
        else:
            # Default: bow at minimum (bow_origin behavior)
            return min(stations)

    def get_stern_station(self) -> float:
        """
        Get the stern (aft) station position.

        Returns the station of the stern, respecting the coordinate system.
        If stern_apex is defined, returns its x-coordinate.
        Otherwise, returns the appropriate extreme station based on coordinate system.

        Returns:
            Stern station position
        """
        if len(self.profiles) == 0 and self.stern_apex is None:
            raise ValueError("Hull has no profiles and no stern_apex defined")

        # If explicit stern apex is defined, use it
        if self.stern_apex is not None:
            return self.stern_apex.x

        # Otherwise determine from profiles based on coordinate system
        stations = list(self.profiles.keys())
        if self.coordinate_system == "bow_origin":
            # Stern is at maximum x (origin is at bow)
            return max(stations)
        elif self.coordinate_system == "stern_origin":
            # Stern is at minimum x (origin is at stern)
            return min(stations)
        elif self.coordinate_system == "midship_origin":
            # Stern is at minimum x (origin is at midship)
            return min(stations)
        else:
            # Default: stern at maximum (bow_origin behavior)
            return max(stations)

    def rotate_about_x(self, angle_deg: float) -> "KayakHull":
        """
        Create a new hull rotated about the X-axis (heel angle).

        This is used to simulate the hull geometry when heeled.

        Args:
            angle_deg: Heel angle in degrees (positive = starboard down)

        Returns:
            New KayakHull with all profiles rotated
        """
        # Rotate bow/stern points if they exist
        rotated_bow_points = None
        if self.bow_points is not None:
            rotated_bow_points = [pt.rotate_x(angle_deg) for pt in self.bow_points]

        rotated_stern_points = None
        if self.stern_points is not None:
            rotated_stern_points = [pt.rotate_x(angle_deg) for pt in self.stern_points]

        new_hull = KayakHull(
            origin=self.origin.rotate_x(angle_deg),
            coordinate_system=self.coordinate_system,
            bow_points=rotated_bow_points,
            stern_points=rotated_stern_points,
        )

        for station, profile in self.profiles.items():
            rotated_profile = profile.rotate_about_x(angle_deg)
            new_hull.add_profile(rotated_profile)

        return new_hull

    def translate(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> "KayakHull":
        """
        Create a new hull translated by given offsets.

        Args:
            dx: Translation in x direction
            dy: Translation in y direction
            dz: Translation in z direction

        Returns:
            New KayakHull with all profiles translated
        """
        # Translate bow/stern points if they exist
        translated_bow_points = None
        if self.bow_points is not None:
            translated_bow_points = [pt.translate(dx, dy, dz) for pt in self.bow_points]

        translated_stern_points = None
        if self.stern_points is not None:
            translated_stern_points = [pt.translate(dx, dy, dz) for pt in self.stern_points]

        new_hull = KayakHull(
            origin=self.origin.translate(dx, dy, dz),
            coordinate_system=self.coordinate_system,
            bow_points=translated_bow_points,
            stern_points=translated_stern_points,
        )

        for station, profile in self.profiles.items():
            translated_profile = profile.translate(dx, dy, dz)
            new_hull.add_profile(translated_profile)

        return new_hull

    def convert_coordinate_system(self, target_system: str) -> "KayakHull":
        """
        Convert hull to a different coordinate system.

        This method creates a new hull with stations transformed to the target
        coordinate system. Currently supports conversion between 'bow_origin'
        and 'stern_origin' systems.

        Args:
            target_system: Target coordinate system ('bow_origin' or 'stern_origin')

        Returns:
            New KayakHull in the target coordinate system

        Raises:
            ValueError: If conversion between specified systems is not supported
        """
        if self.coordinate_system == target_system:
            # No conversion needed
            return self.copy()

        if self.coordinate_system == "bow_origin" and target_system == "stern_origin":
            # Convert from bow_origin to stern_origin
            hull_length = self.length
            if hull_length <= 0:
                raise ValueError(
                    "Cannot convert coordinate system: " "hull has zero or negative length"
                )

            # Transform bow/stern points
            new_bow_points = None
            new_stern_points = None

            if self.bow_points is not None:
                new_bow_points = [
                    Point3D(hull_length - pt.x, pt.y, pt.z, level=pt.level)
                    for pt in self.bow_points
                ]

            if self.stern_points is not None:
                new_stern_points = [
                    Point3D(hull_length - pt.x, pt.y, pt.z, level=pt.level)
                    for pt in self.stern_points
                ]

            # Create new hull
            new_hull = KayakHull(
                origin=self.origin,
                coordinate_system=target_system,
                bow_points=new_bow_points,
                stern_points=new_stern_points,
            )

            # Transform all profiles
            for station, profile in self.profiles.items():
                new_station = hull_length - station
                # Create new points with transformed x-coordinates, preserving level
                new_points = [
                    Point3D(new_station, pt.y, pt.z, level=pt.level) for pt in profile.points
                ]
                # Create new profile with transformed station and points
                new_profile = Profile(new_station, new_points)
                new_hull.add_profile(new_profile)

            return new_hull

        elif self.coordinate_system == "stern_origin" and target_system == "bow_origin":
            # Convert from stern_origin to bow_origin
            hull_length = self.length
            if hull_length <= 0:
                raise ValueError(
                    "Cannot convert coordinate system: " "hull has zero or negative length"
                )

            # Transform bow/stern points
            new_bow_points = None
            new_stern_points = None

            if self.bow_points is not None:
                new_bow_points = [
                    Point3D(hull_length - pt.x, pt.y, pt.z, level=pt.level)
                    for pt in self.bow_points
                ]

            if self.stern_points is not None:
                new_stern_points = [
                    Point3D(hull_length - pt.x, pt.y, pt.z, level=pt.level)
                    for pt in self.stern_points
                ]

            # Create new hull
            new_hull = KayakHull(
                origin=self.origin,
                coordinate_system=target_system,
                bow_points=new_bow_points,
                stern_points=new_stern_points,
            )

            # Transform all profiles
            for station, profile in self.profiles.items():
                new_station = hull_length - station
                # Create new points with transformed x-coordinates, preserving level
                new_points = [
                    Point3D(new_station, pt.y, pt.z, level=pt.level) for pt in profile.points
                ]
                # Create new profile with transformed station and points
                new_profile = Profile(new_station, new_points)
                new_hull.add_profile(new_profile)

            return new_hull

        else:
            raise ValueError(
                f"Coordinate system conversion from '{self.coordinate_system}' "
                f"to '{target_system}' is not supported"
            )

    def copy(self) -> "KayakHull":
        """
        Create a deep copy of this hull.

        Returns:
            New KayakHull with copied profiles
        """
        new_hull = KayakHull(origin=self.origin.copy())

        for station, profile in self.profiles.items():
            new_hull.add_profile(profile.copy())

        return new_hull

    def __repr__(self) -> str:
        """String representation of the hull."""
        return (
            f"KayakHull(num_profiles={self.num_profiles}, "
            f"length={self.length:.4f}, max_beam={self.max_beam:.4f})"
        )

    def __len__(self) -> int:
        """Get number of profiles in hull."""
        return len(self.profiles)
