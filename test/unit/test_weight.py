"""Unit tests for the Weight class in geometry.weight module."""

import pytest
import json
from src.geometry.weight import Weight


class TestWeightInit:
    """Tests for Weight initialization."""

    def test_init_default(self):
        """Test Weight initialization with default values."""
        weight = Weight()
        assert weight.weight == 0.0
        assert weight.cg == (0.0, 0.0, 0.0)

    def test_init_with_weight_only(self):
        """Test Weight initialization with weight only."""
        weight = Weight(weight=50.0)
        assert weight.weight == 50.0
        assert weight.cg == (0.0, 0.0, 0.0)

    def test_init_with_cg_only(self):
        """Test Weight initialization with CG only."""
        weight = Weight(cg=(1.0, 2.0, 3.0))
        assert weight.weight == 0.0
        assert weight.cg == (1.0, 2.0, 3.0)

    def test_init_with_weight_and_cg(self):
        """Test Weight initialization with both weight and CG."""
        weight = Weight(weight=75.5, cg=(1.5, 2.5, 3.5))
        assert weight.weight == 75.5
        assert weight.cg == (1.5, 2.5, 3.5)

    def test_init_with_negative_weight(self):
        """Test Weight initialization with negative weight."""
        weight = Weight(weight=-10.0)
        assert weight.weight == -10.0

    def test_init_with_negative_cg_coordinates(self):
        """Test Weight initialization with negative CG coordinates."""
        weight = Weight(cg=(-1.0, -2.0, -3.0))
        assert weight.cg == (-1.0, -2.0, -3.0)


class TestWeightToJson:
    """Tests for to_json method."""

    def test_to_json_default(self):
        """Test to_json with default values."""
        weight = Weight()
        json_str = weight.to_json()

        # Parse the JSON string
        data = json.loads(json_str)
        assert data["weight"] == 0.0
        assert data["cg"] == [0.0, 0.0, 0.0]

    def test_to_json_with_values(self):
        """Test to_json with specific values."""
        weight = Weight(weight=100.0, cg=(2.5, 3.5, 4.5))
        json_str = weight.to_json()

        data = json.loads(json_str)
        assert data["weight"] == 100.0
        assert data["cg"] == [2.5, 3.5, 4.5]

    def test_to_json_returns_string(self):
        """Test that to_json returns a string."""
        weight = Weight()
        json_str = weight.to_json()
        assert isinstance(json_str, str)

    def test_to_json_is_valid_json(self):
        """Test that to_json produces valid JSON."""
        weight = Weight(weight=50.0, cg=(1.0, 2.0, 3.0))
        json_str = weight.to_json()

        # Should not raise an exception
        data = json.loads(json_str)
        assert "weight" in data
        assert "cg" in data

    def test_to_json_round_trip(self):
        """Test that we can round-trip through JSON."""
        original_weight = Weight(weight=123.45, cg=(6.7, 8.9, 10.11))
        json_str = original_weight.to_json()

        # Parse back
        data = json.loads(json_str)
        restored_weight = Weight(weight=data["weight"], cg=tuple(data["cg"]))

        assert restored_weight.weight == original_weight.weight
        assert restored_weight.cg == original_weight.cg


class TestWeightAttributes:
    """Tests for Weight attributes."""

    def test_weight_attribute_is_mutable(self):
        """Test that weight attribute can be modified."""
        weight = Weight(weight=50.0)
        weight.weight = 75.0
        assert weight.weight == 75.0

    def test_cg_attribute_is_mutable(self):
        """Test that cg attribute can be modified."""
        weight = Weight(cg=(1.0, 2.0, 3.0))
        weight.cg = (4.0, 5.0, 6.0)
        assert weight.cg == (4.0, 5.0, 6.0)

    def test_cg_is_tuple(self):
        """Test that cg is stored as a tuple."""
        weight = Weight(cg=(1.0, 2.0, 3.0))
        assert isinstance(weight.cg, tuple)
        assert len(weight.cg) == 3

    def test_weight_is_numeric(self):
        """Test that weight is a numeric type."""
        weight = Weight(weight=100.0)
        assert isinstance(weight.weight, (int, float))


class TestWeightEdgeCases:
    """Tests for edge cases."""

    def test_zero_weight(self):
        """Test Weight with zero weight."""
        weight = Weight(weight=0.0)
        assert weight.weight == 0.0

    def test_large_weight(self):
        """Test Weight with very large weight."""
        weight = Weight(weight=1e10)
        assert weight.weight == 1e10

    def test_large_cg_coordinates(self):
        """Test Weight with very large CG coordinates."""
        weight = Weight(cg=(1e6, 1e7, 1e8))
        assert weight.cg == (1e6, 1e7, 1e8)

    def test_small_cg_coordinates(self):
        """Test Weight with very small CG coordinates."""
        weight = Weight(cg=(1e-6, 1e-7, 1e-8))
        assert weight.cg == (1e-6, 1e-7, 1e-8)
