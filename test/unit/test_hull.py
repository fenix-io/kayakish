"""Unit tests for the hull preparation module in geometry.hull."""

import pytest
from src.geometry.hull import PreparedHull, prepare_hull
from src.geometry.profile import Profile
from src.model.model import Hull, Metadata, Profile as ModelProfile, YZPoint


class TestPreparedHullInit:
    """Tests for PreparedHull initialization."""

    def test_prepared_hull_creation(self):
        """Test creating a PreparedHull instance."""
        prep_hull = PreparedHull()
        assert prep_hull is not None
        # Attributes should be class-level annotations, not initialized


class TestPreparedHullAddProfile:
    """Tests for the add_profile method."""

    def test_add_profile_first_profile(self):
        """Test adding the first profile to an empty PreparedHull."""
        prep_hull = PreparedHull()
        profile = Profile(station=1.0)
        profile.add_point(1.0, 0.0, 0.5)
        
        prep_hull.add_profile(profile)
        
        assert hasattr(prep_hull, 'profiles')
        assert len(prep_hull.profiles) == 1
        assert prep_hull.profiles[0].station == 1.0

    def test_add_multiple_profiles(self):
        """Test adding multiple profiles."""
        prep_hull = PreparedHull()
        
        profile1 = Profile(station=1.0)
        profile1.add_point(1.0, 0.0, 0.5)
        
        profile2 = Profile(station=2.0)
        profile2.add_point(2.0, 0.1, 0.4)
        
        prep_hull.add_profile(profile1)
        prep_hull.add_profile(profile2)
        
        assert len(prep_hull.profiles) == 2
        assert prep_hull.profiles[0].station == 1.0
        assert prep_hull.profiles[1].station == 2.0

    def test_add_profile_maintains_order(self):
        """Test that profiles are added in the order they're given."""
        prep_hull = PreparedHull()
        
        for station in [1.0, 3.0, 2.0, 4.0]:
            profile = Profile(station=station)
            prep_hull.add_profile(profile)
        
        assert len(prep_hull.profiles) == 4
        assert prep_hull.profiles[0].station == 1.0
        assert prep_hull.profiles[1].station == 3.0
        assert prep_hull.profiles[2].station == 2.0
        assert prep_hull.profiles[3].station == 4.0


class TestPreparedHullToJson:
    """Tests for the to_json method."""

    def test_to_json_returns_prepared_hull(self):
        """Test that to_json returns a PreparedHull instance."""
        prep_hull = PreparedHull()
        result = prep_hull.to_json()
        
        assert isinstance(result, PreparedHull)


class TestPrepareHull:
    """Tests for the prepare_hull function."""

    def test_prepare_hull_empty_profiles(self):
        """Test prepare_hull with a hull containing no profiles."""
        metadata = Metadata(
            name="Test Kayak",
            description="A test kayak",
            target_waterline=0.1,
            target_payload=80.0
        )
        hull = Hull(metadata=metadata, profiles=[])
        
        result = prepare_hull(hull)
        
        assert result.name == "Test Kayak"
        assert result.description == "A test kayak"
        assert result.target_waterline == 0.1
        assert result.target_payload == 80.0

    def test_prepare_hull_single_profile(self):
        """Test prepare_hull with a single profile."""
        metadata = Metadata(name="Kayak 001")
        profile = ModelProfile(
            station=1.0,
            port_points=[
                YZPoint(y=0.0, z=0.5),
                YZPoint(y=0.2, z=0.4)
            ]
        )
        hull = Hull(metadata=metadata, profiles=[profile])
        
        result = prepare_hull(hull)
        
        assert result.name == "Kayak 001"
        assert hasattr(result, 'profiles')
        assert len(result.profiles) == 1

    def test_prepare_hull_multiple_profiles(self):
        """Test prepare_hull with multiple profiles."""
        metadata = Metadata(name="Multi Profile Kayak")
        profiles = [
            ModelProfile(
                station=0.0,
                port_points=[YZPoint(y=0.0, z=0.3)]
            ),
            ModelProfile(
                station=1.0,
                port_points=[
                    YZPoint(y=0.0, z=0.5),
                    YZPoint(y=0.2, z=0.4)
                ]
            ),
            ModelProfile(
                station=2.0,
                port_points=[
                    YZPoint(y=0.0, z=0.6),
                    YZPoint(y=0.3, z=0.5)
                ]
            )
        ]
        hull = Hull(metadata=metadata, profiles=profiles)
        
        result = prepare_hull(hull)
        
        assert result.name == "Multi Profile Kayak"
        assert len(result.profiles) == 3

    def test_prepare_hull_with_none_metadata_fields(self):
        """Test prepare_hull with optional metadata fields as None."""
        metadata = Metadata(
            name="Minimal Kayak",
            description=None,
            target_waterline=None,
            target_payload=None
        )
        hull = Hull(metadata=metadata, profiles=[])
        
        result = prepare_hull(hull)
        
        assert result.name == "Minimal Kayak"
        assert result.description is None
        assert result.target_waterline is None
        assert result.target_payload is None

    def test_prepare_hull_profile_processing(self):
        """Test that profiles are processed (sorted, completed)."""
        metadata = Metadata(name="Processing Test")
        profile = ModelProfile(
            station=1.0,
            port_points=[
                YZPoint(y=0.3, z=0.3),
                YZPoint(y=0.0, z=0.5),
                YZPoint(y=0.2, z=0.4)
            ]
        )
        hull = Hull(metadata=metadata, profiles=[profile])
        
        result = prepare_hull(hull)
        
        # Profile should be added
        assert hasattr(result, 'profiles')
        assert len(result.profiles) == 1


class TestPrepareHullIntegration:
    """Integration tests for hull preparation workflow."""

    def test_full_hull_preparation_workflow(self):
        """Test complete workflow with realistic hull data."""
        metadata = Metadata(
            name="Sea Kayak Pro",
            description="High-performance sea kayak",
            target_waterline=0.12,
            target_payload=100.0
        )
        
        profiles = [
            ModelProfile(
                station=0.0,
                port_points=[YZPoint(y=0.0, z=0.30)]
            ),
            ModelProfile(
                station=1.0,
                port_points=[
                    YZPoint(y=0.00, z=0.30),
                    YZPoint(y=0.18, z=0.28),
                    YZPoint(y=0.12, z=0.15)
                ]
            ),
            ModelProfile(
                station=2.0,
                port_points=[
                    YZPoint(y=0.00, z=0.35),
                    YZPoint(y=0.20, z=0.30),
                    YZPoint(y=0.15, z=0.20)
                ]
            ),
            ModelProfile(
                station=3.0,
                port_points=[YZPoint(y=0.0, z=0.30)]
            )
        ]
        
        hull = Hull(metadata=metadata, profiles=profiles)
        result = prepare_hull(hull)
        
        # Verify all metadata transferred
        assert result.name == "Sea Kayak Pro"
        assert result.description == "High-performance sea kayak"
        assert result.target_waterline == 0.12
        assert result.target_payload == 100.0
        
        # Verify profiles were processed
        assert len(result.profiles) == 4
        
        # Check profile at station 1.0
        station_1_profile = result.profiles[1]
        assert station_1_profile.station == 1.0
        
        # Check data_points: 3 original + 2 mirrored (excluding centerline) = 5
        assert len(station_1_profile.data_points) == 5
        
        # Check circular interpolation points (should be 120 for 360/3 degrees)
        assert len(station_1_profile.points) > 0
        assert len(station_1_profile.points) <= 120
        
        # Sample some points around the circle to verify they have correct station
        for point in station_1_profile.points[::30]:  # Sample every 30th point
            assert point.x == 1.0  # All points should be at station 1.0
            # Verify points are within reasonable bounds
            assert -0.3 <= point.y <= 0.3
            assert 0.0 <= point.z <= 0.4

    def test_prepare_hull_with_complex_profiles(self):
        """Test hull preparation with complex profile data."""
        metadata = Metadata(name="Complex Hull")
        
        profiles = [
            ModelProfile(
                station=i * 0.5,
                port_points=[
                    YZPoint(y=0.0, z=0.5),
                    YZPoint(y=0.1 * (i + 1), z=0.4),
                    YZPoint(y=0.15 * (i + 1), z=0.3),
                    YZPoint(y=0.2 * (i + 1), z=0.2)
                ]
            )
            for i in range(5)
        ]
        
        hull = Hull(metadata=metadata, profiles=profiles)
        result = prepare_hull(hull)
        
        assert result.name == "Complex Hull"
        assert len(result.profiles) == 5
