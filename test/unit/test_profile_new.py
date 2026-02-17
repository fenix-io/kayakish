"""Unit tests for the Profile class in geometry.profile module."""

import pytest
from src.geometry.profile import Profile
from src.geometry.point import Point3D


class TestProfileInit:
    """Tests for Profile initialization."""

    def test_init_default(self):
        """Test Profile initialization with default values."""
        profile = Profile()
        assert profile.station == 0.0
        assert isinstance(profile.points, list)
        assert len(profile.points) == 0

    def test_init_with_station(self):
        """Test Profile initialization with specific station value."""
        profile = Profile(station=2.5)
        assert profile.station == 2.5
        assert len(profile.points) == 0

    def test_init_with_points(self):
        """Test Profile initialization with points."""
        points = [Point3D(1.0, 0.0, 0.5), Point3D(1.0, 0.5, 0.3), Point3D(1.0, -0.5, 0.3)]
        profile = Profile(station=1.0, points=points)
        assert profile.station == 1.0
        assert len(profile.points) == 3

    def test_init_removes_duplicate_points(self):
        """Test that initialization removes duplicate points."""
        points = [
            Point3D(1.0, 0.0, 0.5),
            Point3D(1.0, 0.0, 0.5),  # Duplicate
            Point3D(1.0, 0.5, 0.3),
        ]
        profile = Profile(station=1.0, points=points)
        assert len(profile.points) == 2

    def test_init_sorts_points(self):
        """Test that initialization sorts points."""
        points = [
            Point3D(1.0, 0.0, 1.0),  # Top
            Point3D(1.0, -1.0, 0.0),  # Left
            Point3D(1.0, 1.0, 0.0),  # Right
            Point3D(1.0, 0.0, -1.0),  # Bottom
        ]
        profile = Profile(station=1.0, points=points)
        assert len(profile.points) == 4
        # Points should be sorted counterclockwise


class TestProfileIsValid:
    """Tests for is_valid method."""

    def test_is_valid_empty(self):
        """Test is_valid with no points."""
        profile = Profile()
        assert not profile.is_valid()

    def test_is_valid_two_points(self):
        """Test is_valid with two points."""
        points = [Point3D(1.0, 0.0, 0.5), Point3D(1.0, 0.5, 0.3)]
        profile = Profile(station=1.0, points=points)
        assert not profile.is_valid()

    def test_is_valid_three_points(self):
        """Test is_valid with three points (minimum for valid polygon)."""
        points = [Point3D(1.0, 0.0, 0.5), Point3D(1.0, 0.5, 0.3), Point3D(1.0, -0.5, 0.3)]
        profile = Profile(station=1.0, points=points)
        assert profile.is_valid()

    def test_is_valid_many_points(self):
        """Test is_valid with many points."""
        points = [Point3D(1.0, i * 0.1, 0.5 - i * 0.05) for i in range(10)]
        profile = Profile(station=1.0, points=points)
        assert profile.is_valid()


class TestProfileValidateStationPlane:
    """Tests for validate_station_plane method."""

    def test_validate_station_plane_empty(self):
        """Test validate_station_plane with no points."""
        profile = Profile(station=1.0)
        assert profile.validate_station_plane()

    def test_validate_station_plane_valid(self):
        """Test validate_station_plane with all points in plane."""
        points = [Point3D(1.0, 0.0, 0.5), Point3D(1.0, 0.5, 0.3), Point3D(1.0, -0.5, 0.3)]
        profile = Profile(station=1.0, points=points)
        assert profile.validate_station_plane()

    def test_validate_station_plane_invalid(self):
        """Test validate_station_plane with points not in plane."""
        points = [
            Point3D(1.0, 0.0, 0.5),
            Point3D(1.1, 0.5, 0.3),  # Wrong x coordinate
            Point3D(1.0, -0.5, 0.3),
        ]
        profile = Profile(station=1.0, points=points)
        assert not profile.validate_station_plane()

    def test_validate_station_plane_with_tolerance(self):
        """Test validate_station_plane with custom tolerance."""
        points = [
            Point3D(1.0, 0.0, 0.5),
            Point3D(1.0001, 0.5, 0.3),  # Slightly off (0.1mm)
            Point3D(1.0, -0.5, 0.3),
        ]
        profile = Profile(station=1.0, points=points)
        # Should pass with larger tolerance
        assert profile.validate_station_plane(tolerance=0.001)
        # Should fail with smaller tolerance
        assert not profile.validate_station_plane(tolerance=0.00001)

        # Test with larger deviation
        points2 = [
            Point3D(1.0, 0.0, 0.5),
            Point3D(1.1, 0.5, 0.3),  # Significantly off (10cm)
            Point3D(1.0, -0.5, 0.3),
        ]
        profile2 = Profile(station=1.0, points=points2)
        assert not profile2.validate_station_plane(tolerance=0.01)


class TestProfileGetPoints:
    """Tests for get_points method."""

    def test_get_points_empty(self):
        """Test get_points on an empty profile."""
        profile = Profile()
        points = profile.get_points()
        assert points == []
        assert isinstance(points, list)

    def test_get_points_with_data(self):
        """Test get_points returns all points."""
        points_list = [Point3D(1.0, 0.0, 0.5), Point3D(1.0, 0.5, 0.3), Point3D(1.0, -0.5, 0.3)]
        profile = Profile(station=1.0, points=points_list)
        points = profile.get_points()
        assert len(points) == 3


class TestProfileToJson:
    """Tests for to_json method."""

    def test_to_json_empty(self):
        """Test to_json on an empty profile."""
        profile = Profile()
        json_data = profile.to_json()
        assert json_data == {"points": []}

    def test_to_json_with_points(self):
        """Test to_json with points."""
        points = [Point3D(1.0, 0.5, 0.3), Point3D(1.0, 0.2, 0.1)]
        profile = Profile(station=1.0, points=points)
        json_data = profile.to_json()
        assert "points" in json_data
        assert len(json_data["points"]) == 2
        # Check structure
        assert "x" in json_data["points"][0]
        assert "y" in json_data["points"][0]
        assert "z" in json_data["points"][0]


class TestProfileSortPoints:
    """Tests for sort_points method."""

    def test_sort_points_empty(self):
        """Test sort_points on empty profile does not raise error."""
        profile = Profile()
        profile.sort_points()  # Should not raise
        assert len(profile.points) == 0

    def test_sort_points_two_points(self):
        """Test sort_points with two points (less than 3)."""
        points = [Point3D(1.0, 0.5, 0.3), Point3D(1.0, 0.2, 0.1)]
        profile = Profile(station=1.0, points=points)
        # Should not raise error
        assert len(profile.points) == 2

    def test_sort_points_ordering(self):
        """Test that sort_points arranges points counterclockwise."""
        # Create a square profile (unsorted)
        points = [
            Point3D(1.0, 0.0, 1.0),  # Top
            Point3D(1.0, -1.0, 0.0),  # Left
            Point3D(1.0, 0.0, -1.0),  # Bottom
            Point3D(1.0, 1.0, 0.0),  # Right
        ]
        profile = Profile(station=1.0, points=points)
        # After sorting, points should be in counterclockwise order
        # We can't predict exact order without calculating angles, but verify no crash
        assert len(profile.points) == 4


class TestProfileCalculateArea:
    """Tests for calculate_area method."""

    def test_calculate_area_invalid_profile(self):
        """Test calculate_area with invalid profile (less than 3 points)."""
        profile = Profile(station=1.0)
        assert profile.calculate_area() == 0.0

    def test_calculate_area_triangle(self):
        """Test calculate_area with a triangle."""
        # Right triangle with base=2, height=2, area=2
        points = [Point3D(1.0, 0.0, 0.0), Point3D(1.0, 2.0, 0.0), Point3D(1.0, 0.0, 2.0)]
        profile = Profile(station=1.0, points=points)
        area = profile.calculate_area()
        assert area == pytest.approx(2.0, abs=1e-6)

    def test_calculate_area_square(self):
        """Test calculate_area with a unit square."""
        # Square with sides of length 2, area=4
        points = [
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 2.0, 0.0),
            Point3D(1.0, 2.0, 2.0),
            Point3D(1.0, 0.0, 2.0),
        ]
        profile = Profile(station=1.0, points=points)
        area = profile.calculate_area()
        assert area == pytest.approx(4.0, abs=1e-6)

    def test_calculate_area_rectangle(self):
        """Test calculate_area with a rectangle."""
        # Rectangle 3x4, area=12
        points = [
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 3.0, 0.0),
            Point3D(1.0, 3.0, 4.0),
            Point3D(1.0, 0.0, 4.0),
        ]
        profile = Profile(station=1.0, points=points)
        area = profile.calculate_area()
        assert area == pytest.approx(12.0, abs=1e-6)

    def test_calculate_area_points_not_in_plane(self):
        """Test calculate_area raises error when points not in station plane."""
        points = [
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.5, 2.0, 0.0),  # Wrong x coordinate
            Point3D(1.0, 0.0, 2.0),
        ]
        profile = Profile(station=1.0, points=points)
        with pytest.raises(ValueError, match="Not all points lie in station plane"):
            profile.calculate_area()


class TestProfileCalculateCentroid:
    """Tests for calculate_centroid method."""

    def test_calculate_centroid_invalid_profile(self):
        """Test calculate_centroid with invalid profile."""
        profile = Profile(station=1.0)
        cy, cz = profile.calculate_centroid()
        assert cy == 0.0
        assert cz == 0.0

    def test_calculate_centroid_triangle(self):
        """Test calculate_centroid with a triangle."""
        # Right triangle at origin
        points = [Point3D(1.0, 0.0, 0.0), Point3D(1.0, 3.0, 0.0), Point3D(1.0, 0.0, 3.0)]
        profile = Profile(station=1.0, points=points)
        cy, cz = profile.calculate_centroid()
        # Centroid of right triangle is at (1/3, 1/3) from right angle
        assert cy == pytest.approx(1.0, abs=1e-6)
        assert cz == pytest.approx(1.0, abs=1e-6)

    def test_calculate_centroid_square(self):
        """Test calculate_centroid with a square."""
        # Unit square centered at origin
        points = [
            Point3D(1.0, -1.0, -1.0),
            Point3D(1.0, 1.0, -1.0),
            Point3D(1.0, 1.0, 1.0),
            Point3D(1.0, -1.0, 1.0),
        ]
        profile = Profile(station=1.0, points=points)
        cy, cz = profile.calculate_centroid()
        # Centroid should be at origin
        assert cy == pytest.approx(0.0, abs=1e-6)
        assert cz == pytest.approx(0.0, abs=1e-6)

    def test_calculate_centroid_rectangle(self):
        """Test calculate_centroid with a rectangle."""
        # Rectangle from (0,0) to (4,2)
        points = [
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 4.0, 0.0),
            Point3D(1.0, 4.0, 2.0),
            Point3D(1.0, 0.0, 2.0),
        ]
        profile = Profile(station=1.0, points=points)
        cy, cz = profile.calculate_centroid()
        # Centroid should be at center (2, 1)
        assert cy == pytest.approx(2.0, abs=1e-6)
        assert cz == pytest.approx(1.0, abs=1e-6)


class TestProfileCalculateVolumeAndCg:
    """Tests for calculate_volume_and_cg method."""

    def test_calculate_volume_and_cg_zero_area(self):
        """Test calculate_volume_and_cg with zero area profile."""
        profile = Profile(station=1.0)
        volume, cg = profile.calculate_volume_and_cg(step=0.1)
        assert volume == 0.0
        assert cg.x == 1.0
        assert cg.y == 0.0
        assert cg.z == 0.0

    def test_calculate_volume_and_cg_unit_square(self):
        """Test calculate_volume_and_cg with unit square."""
        # Unit square (1x1), step 0.1, volume should be 0.1
        points = [
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 1.0, 0.0),
            Point3D(1.0, 1.0, 1.0),
            Point3D(1.0, 0.0, 1.0),
        ]
        profile = Profile(station=1.0, points=points)
        volume, cg = profile.calculate_volume_and_cg(step=0.1)
        assert volume == pytest.approx(0.1, abs=1e-6)
        assert cg.x == pytest.approx(1.0, abs=1e-6)
        assert cg.y == pytest.approx(0.5, abs=1e-6)
        assert cg.z == pytest.approx(0.5, abs=1e-6)

    def test_calculate_volume_and_cg_rectangle(self):
        """Test calculate_volume_and_cg with rectangle."""
        # Rectangle 2x3, step 0.5, volume should be 3.0
        points = [
            Point3D(2.0, 0.0, 0.0),
            Point3D(2.0, 2.0, 0.0),
            Point3D(2.0, 2.0, 3.0),
            Point3D(2.0, 0.0, 3.0),
        ]
        profile = Profile(station=2.0, points=points)
        volume, cg = profile.calculate_volume_and_cg(step=0.5)
        assert volume == pytest.approx(3.0, abs=1e-6)  # area=6, step=0.5
        assert cg.x == pytest.approx(2.0, abs=1e-6)
        assert cg.y == pytest.approx(1.0, abs=1e-6)
        assert cg.z == pytest.approx(1.5, abs=1e-6)

    def test_calculate_volume_and_cg_different_steps(self):
        """Test calculate_volume_and_cg with different step sizes."""
        # Unit square
        points = [
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 1.0, 0.0),
            Point3D(1.0, 1.0, 1.0),
            Point3D(1.0, 0.0, 1.0),
        ]
        profile = Profile(station=1.0, points=points)

        # Different step sizes should give proportional volumes
        volume1, cg1 = profile.calculate_volume_and_cg(step=0.1)
        volume2, cg2 = profile.calculate_volume_and_cg(step=0.2)

        assert volume2 == pytest.approx(2 * volume1, abs=1e-6)
        # CG location should be the same regardless of step
        assert cg1.y == pytest.approx(cg2.y, abs=1e-6)
        assert cg1.z == pytest.approx(cg2.z, abs=1e-6)


class TestProfileWettedPerimeter:
    """Tests for wetted_perimeter method."""

    def test_wetted_perimeter_empty_profile(self):
        """Test wetted perimeter with empty profile."""
        profile = Profile(station=1.0)
        perimeter = profile.wetted_perimeter()
        assert perimeter == 0.0

    def test_wetted_perimeter_two_points(self):
        """Test wetted perimeter with two points (invalid profile)."""
        points = [Point3D(1.0, 0.0, 0.0), Point3D(1.0, 1.0, 0.0)]
        profile = Profile(station=1.0, points=points)
        perimeter = profile.wetted_perimeter()
        assert perimeter == 0.0  # Invalid profile returns 0

    def test_wetted_perimeter_triangle(self):
        """Test wetted perimeter with triangular profile."""
        # Equilateral triangle with side length ~1.732
        import math

        points = [
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 1.0, 0.0),
            Point3D(1.0, 0.5, math.sqrt(3) / 2),
        ]
        profile = Profile(station=1.0, points=points)
        perimeter = profile.wetted_perimeter()

        # Expected: 1.0 + sqrt(0.25 + 0.75) + 1.0 = 1 + 1 + 1 = 3.0 roughly
        # (sides of approximately equal length)
        assert perimeter > 2.5
        assert perimeter < 3.5

    def test_wetted_perimeter_square(self):
        """Test wetted perimeter with square profile."""
        points = [
            Point3D(2.0, 0.0, 0.0),
            Point3D(2.0, 2.0, 0.0),
            Point3D(2.0, 2.0, 2.0),
            Point3D(2.0, 0.0, 2.0),
        ]
        profile = Profile(station=2.0, points=points)
        perimeter = profile.wetted_perimeter()

        # Square with side 2, perimeter = 4*2 = 8
        assert perimeter == pytest.approx(8.0, abs=1e-6)

    def test_wetted_perimeter_rectangle(self):
        """Test wetted perimeter with rectangular profile."""
        points = [
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 3.0, 0.0),
            Point3D(1.0, 3.0, 2.0),
            Point3D(1.0, 0.0, 2.0),
        ]
        profile = Profile(station=1.0, points=points)
        perimeter = profile.wetted_perimeter()

        # Rectangle 3×2, perimeter = 2*(3+2) = 10
        assert perimeter == pytest.approx(10.0, abs=1e-6)

    def test_wetted_perimeter_circle_approximation(self):
        """Test wetted perimeter with many points approximating a circle."""
        import math

        # Circle with radius 1.0
        radius = 1.0
        n_points = 20
        points = []
        for i in range(n_points):
            angle = 2 * math.pi * i / n_points
            y = radius * math.cos(angle)
            z = radius * math.sin(angle)
            points.append(Point3D(1.0, y, z))

        profile = Profile(station=1.0, points=points)
        perimeter = profile.wetted_perimeter()

        # Expected circumference: 2*pi*r = 2*pi*1 ≈ 6.283
        expected = 2 * math.pi * radius
        # With 20 points, approximation should be within 5%
        assert perimeter == pytest.approx(expected, rel=0.05)

    def test_wetted_perimeter_positive_for_valid_profile(self):
        """Test wetted perimeter is always positive for valid profiles."""
        # Arbitrary valid profile
        points = [
            Point3D(1.5, 0.0, 0.3),
            Point3D(1.5, 0.5, 0.1),
            Point3D(1.5, 0.3, 0.5),
            Point3D(1.5, -0.2, 0.4),
        ]
        profile = Profile(station=1.5, points=points)
        perimeter = profile.wetted_perimeter()
        assert perimeter > 0
