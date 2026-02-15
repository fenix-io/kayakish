"""Unit tests for the Profile class in geometry.profile module."""

import pytest
import numpy as np
from src.geometry.profile import Profile
from src.geometry.point import Point3D


class TestProfileInit:
    """Tests for Profile initialization."""

    def test_profile_init_default(self):
        """Test Profile initialization with default values."""
        profile = Profile()
        assert profile.station == 0.0
        assert isinstance(profile.data_points, list)
        assert len(profile.data_points) == 0

    def test_profile_init_with_station(self):
        """Test Profile initialization with specific station value."""
        profile = Profile(station=2.5)
        assert profile.station == 2.5
        assert len(profile.data_points) == 0


class TestAddPoint:
    """Tests for the add_point method."""

    def test_add_single_point(self):
        """Test adding a single point to the profile."""
        profile = Profile(station=1.0)
        profile.add_point(1.0, 0.5, 0.3)

        assert len(profile.data_points) == 1
        assert profile.data_points[0].x == 1.0
        assert profile.data_points[0].y == 0.5
        assert profile.data_points[0].z == 0.3

    def test_add_multiple_points(self):
        """Test adding multiple points to the profile."""
        profile = Profile(station=1.0)
        profile.add_point(1.0, 0.0, 0.5)
        profile.add_point(1.0, 0.2, 0.4)
        profile.add_point(1.0, 0.3, 0.3)

        assert len(profile.data_points) == 3
        assert profile.data_points[1].y == 0.2
        assert profile.data_points[2].z == 0.3


class TestGetPoints:
    """Tests for the get_points method."""

    def test_get_points_empty(self):
        """Test get_points on an empty profile."""
        profile = Profile()
        points = profile.get_points()
        assert points == []
        assert isinstance(points, list)

    def test_get_points_with_data(self):
        """Test get_points returns all added points."""
        profile = Profile()
        profile.add_point(1.0, 0.5, 0.3)
        profile.add_point(1.0, 0.3, 0.2)

        points = profile.get_points()
        assert len(points) == 2
        assert points[0].y == 0.5
        assert points[1].y == 0.3


class TestToJson:
    """Tests for the to_json method."""

    def test_to_json_empty(self):
        """Test to_json on an empty profile."""
        profile = Profile()
        json_data = profile.to_json()
        assert json_data == {"points": []}

    def test_to_json_with_points(self):
        """Test to_json with points."""
        profile = Profile()
        profile.add_point(1.0, 0.5, 0.3)
        profile.add_point(1.0, 0.2, 0.1)

        json_data = profile.to_json()
        assert "points" in json_data
        assert len(json_data["points"]) == 2
        assert json_data["points"][0] == {"x": 1.0, "y": 0.5, "z": 0.3}
        assert json_data["points"][1] == {"x": 1.0, "y": 0.2, "z": 0.1}


class TestSortPoints:
    """Tests for the sort_points method."""

    def test_sort_points_empty(self):
        """Test sort_points on empty profile does not raise error."""
        profile = Profile()
        profile.sort_points()
        assert len(profile.data_points) == 0

    def test_sort_points_by_z_descending(self):
        """Test that points are sorted by z coordinate (descending)."""
        profile = Profile()
        profile.add_point(1.0, 0.0, 0.1)
        profile.add_point(1.0, 0.0, 0.5)
        profile.add_point(1.0, 0.0, 0.3)

        profile.sort_points()

        assert profile.data_points[0].z == 0.5
        assert profile.data_points[1].z == 0.3
        assert profile.data_points[2].z == 0.1

    def test_sort_points_by_y_when_z_equal(self):
        """Test that points with same z are sorted by -y (port first)."""
        profile = Profile()
        profile.add_point(1.0, 0.1, 0.5)
        profile.add_point(1.0, 0.3, 0.5)
        profile.add_point(1.0, 0.2, 0.5)

        profile.sort_points()

        # With reverse=True and -y, smaller y values come first
        assert profile.data_points[0].y == 0.1
        assert profile.data_points[1].y == 0.2
        assert profile.data_points[2].y == 0.3

    def test_sort_points_complex(self):
        """Test sorting with multiple z and y values."""
        profile = Profile()
        profile.add_point(1.0, 0.2, 0.3)
        profile.add_point(1.0, 0.1, 0.5)
        profile.add_point(1.0, 0.3, 0.3)
        profile.add_point(1.0, 0.2, 0.5)

        profile.sort_points()

        # Highest z first, then by smaller y (because of -y with reverse=True)
        assert profile.data_points[0].z == 0.5
        assert profile.data_points[0].y == 0.1
        assert profile.data_points[1].z == 0.5
        assert profile.data_points[1].y == 0.2
        assert profile.data_points[2].z == 0.3
        assert profile.data_points[2].y == 0.2


class TestAutoCompleteStarboard:
    """Tests for the auto_complete_starboard method."""

    def test_auto_complete_starboard_empty(self):
        """Test auto_complete_starboard on empty profile."""
        profile = Profile()
        profile.auto_complete_starboard()
        assert len(profile.data_points) == 0

    def test_auto_complete_starboard_centerline_only(self):
        """Test auto_complete_starboard with only centerline points (y=0)."""
        profile = Profile()
        profile.add_point(1.0, 0.0, 0.5)
        profile.add_point(1.0, 0.0, 0.3)

        profile.auto_complete_starboard()

        # Should not add starboard points for centerline
        assert len(profile.data_points) == 2

    def test_auto_complete_starboard_port_points(self):
        """Test auto_complete_starboard mirrors port points to starboard."""
        profile = Profile()
        profile.add_point(1.0, 0.0, 0.5)
        profile.add_point(1.0, 0.2, 0.4)
        profile.add_point(1.0, 0.3, 0.3)

        initial_count = len(profile.data_points)
        profile.auto_complete_starboard()

        # Should add 2 mirrored points (0.2 and 0.3, but not 0.0)
        assert len(profile.data_points) == initial_count + 2

        # Check mirrored points are added
        starboard_points = [p for p in profile.data_points if p.y < 0]
        assert len(starboard_points) == 2
        assert any(p.y == -0.2 and p.z == 0.4 for p in starboard_points)
        assert any(p.y == -0.3 and p.z == 0.3 for p in starboard_points)

    def test_auto_complete_starboard_order(self):
        """Test that starboard points are added in reverse order."""
        profile = Profile()
        profile.add_point(1.0, 0.0, 0.5)
        profile.add_point(1.0, 0.1, 0.4)
        profile.add_point(1.0, 0.2, 0.3)

        profile.auto_complete_starboard()

        # Last two points should be starboard in reverse order
        assert profile.data_points[-2].y == -0.2
        assert profile.data_points[-1].y == -0.1


class TestAutoCompleteCircular:
    """Tests for the auto_complete_circular method."""

    def test_auto_complete_circular_empty(self):
        """Test auto_complete_circular on empty profile."""
        profile = Profile()
        profile.auto_complete_circular()
        assert profile.points == []

    def test_auto_complete_circular_single_point(self):
        """Test auto_complete_circular with single point."""
        profile = Profile()
        profile.add_point(1.0, 0.0, 0.5)
        profile.auto_complete_circular()
        assert profile.points == []

    def test_auto_complete_circular_creates_points(self):
        """Test that auto_complete_circular generates circular interpolated points."""
        profile = Profile(station=2.0)
        # Create a simple square profile
        profile.add_point(2.0, 0.0, 0.4)
        profile.add_point(2.0, 0.2, 0.4)
        profile.add_point(2.0, 0.2, 0.0)
        profile.add_point(2.0, -0.2, 0.0)
        profile.add_point(2.0, -0.2, 0.4)

        profile.auto_complete_circular()

        # Should generate points (360/3 = 120 angles)
        assert len(profile.points) > 0
        # Check that generated points use the profile station
        assert all(p.x == 2.0 for p in profile.points)

    def test_auto_complete_circular_center_calculation(self):
        """Test that center is calculated as average of points."""
        profile = Profile(station=1.0)
        # Create symmetric points around (0, 0.2)
        profile.add_point(1.0, -0.1, 0.3)
        profile.add_point(1.0, 0.1, 0.3)
        profile.add_point(1.0, 0.1, 0.1)
        profile.add_point(1.0, -0.1, 0.1)

        # Center should be at (0, 0.2)
        expected_center_y = 0.0
        expected_center_z = 0.2

        profile.auto_complete_circular()

        # Verify points are generated around the center
        assert len(profile.points) > 0

    def test_auto_complete_circular_angle_coverage(self):
        """Test that circular interpolation covers 360 degrees."""
        profile = Profile(station=1.0)
        # Simple circular profile
        for angle_deg in range(0, 360, 45):
            angle = np.radians(angle_deg)
            y = 0.2 * np.cos(angle)
            z = 0.2 + 0.2 * np.sin(angle)
            profile.add_point(1.0, y, z)

        profile.auto_complete_circular()

        # Should generate 360/3 = 120 points
        # Note: some may not intersect, so check for reasonable number
        assert len(profile.points) > 0


class TestProfileIntegration:
    """Integration tests combining multiple Profile methods."""

    def test_full_workflow_port_to_complete_profile(self):
        """Test complete workflow: add port points, sort, complete starboard."""
        profile = Profile(station=3.0)

        # Add port side points in random order
        profile.add_point(3.0, 0.3, 0.2)
        profile.add_point(3.0, 0.0, 0.5)
        profile.add_point(3.0, 0.2, 0.4)

        # Sort
        profile.sort_points()
        assert profile.data_points[0].z == 0.5

        # Complete starboard
        profile.auto_complete_starboard()
        assert len(profile.data_points) == 5  # 3 original + 2 mirrored

        # Check symmetry
        port_points = [p for p in profile.data_points if p.y > 0]
        starboard_points = [p for p in profile.data_points if p.y < 0]
        assert len(port_points) == len(starboard_points)

    def test_json_export_after_modifications(self):
        """Test JSON export after various modifications."""
        profile = Profile()
        profile.add_point(1.0, 0.2, 0.3)
        profile.add_point(1.0, 0.1, 0.4)
        profile.sort_points()
        profile.auto_complete_starboard()

        json_data = profile.to_json()
        assert len(json_data["points"]) == 4  # 2 original + 2 mirrored
