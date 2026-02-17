"""Unit tests for hull resistance and performance module."""

import pytest
import math
from src.analysis.resistance import (
    # Constants
    WATER_DENSITY_FRESH,
    WATER_DENSITY_SALT,
    KINEMATIC_VISCOSITY,
    GRAVITY,
    DEFAULT_ROUGHNESS_ALLOWANCE,
    DEFAULT_PROPULSION_EFFICIENCY,
    # Functions
    calculate_reynolds_number,
    calculate_froude_number,
    calculate_hull_speed,
    calculate_ittc_friction_coefficient,
    calculate_frictional_resistance,
    calculate_residuary_coefficient,
    calculate_residuary_resistance,
    calculate_effective_power,
    calculate_paddler_power,
    calculate_resistance,
    calculate_resistance_curve,
    calculate_energy_for_distance,
    # Data class
    ResistanceResult,
)

# ============================================================================
# Test Reynolds Number Calculation
# ============================================================================


def test_reynolds_number_typical_kayak():
    """Test Reynolds number for typical kayak speed."""
    # 2 m/s (7.2 km/h) at 5m waterline length
    re = calculate_reynolds_number(speed=2.0, waterline_length=5.0)
    # Re = (2.0 × 5.0) / 1.19e-6 ≈ 8.4e6
    assert 8.0e6 < re < 9.0e6
    assert re > 1e6  # Turbulent flow regime


def test_reynolds_number_zero_speed():
    """Test Reynolds number at zero speed."""
    re = calculate_reynolds_number(speed=0.0, waterline_length=5.0)
    assert re == 0.0


def test_reynolds_number_high_speed():
    """Test Reynolds number at high speed."""
    # 4 m/s at 5m length
    re = calculate_reynolds_number(speed=4.0, waterline_length=5.0)
    assert re > 1.5e7


def test_reynolds_number_invalid_speed():
    """Test Reynolds number with negative speed raises ValueError."""
    with pytest.raises(ValueError, match="Speed must be non-negative"):
        calculate_reynolds_number(speed=-1.0, waterline_length=5.0)


def test_reynolds_number_invalid_length():
    """Test Reynolds number with zero/negative length raises ValueError."""
    with pytest.raises(ValueError, match="Waterline length must be positive"):
        calculate_reynolds_number(speed=2.0, waterline_length=0.0)
    with pytest.raises(ValueError, match="Waterline length must be positive"):
        calculate_reynolds_number(speed=2.0, waterline_length=-1.0)


def test_reynolds_number_invalid_viscosity():
    """Test Reynolds number with zero/negative viscosity raises ValueError."""
    with pytest.raises(ValueError, match="Kinematic viscosity must be positive"):
        calculate_reynolds_number(speed=2.0, waterline_length=5.0, kinematic_viscosity=0.0)
    with pytest.raises(ValueError, match="Kinematic viscosity must be positive"):
        calculate_reynolds_number(speed=2.0, waterline_length=5.0, kinematic_viscosity=-1e-6)


# ============================================================================
# Test Froude Number Calculation
# ============================================================================


def test_froude_number_typical_kayak():
    """Test Froude number for typical kayak speed."""
    # 2 m/s at 5m waterline
    fn = calculate_froude_number(speed=2.0, waterline_length=5.0)
    # Fn = 2.0 / sqrt(9.81 × 5.0) ≈ 0.286
    assert 0.28 < fn < 0.29


def test_froude_number_zero_speed():
    """Test Froude number at zero speed."""
    fn = calculate_froude_number(speed=0.0, waterline_length=5.0)
    assert fn == 0.0


def test_froude_number_hull_speed():
    """Test Froude number at hull speed (Fn ≈ 0.40)."""
    # Hull speed for 5m waterline
    v_hull = 0.40 * math.sqrt(GRAVITY * 5.0)
    fn = calculate_froude_number(speed=v_hull, waterline_length=5.0)
    assert abs(fn - 0.40) < 0.001


def test_froude_number_wave_resistance_regimes():
    """Test Froude number regimes for wave resistance."""
    lwl = 5.0

    # Low wave resistance: Fn < 0.35
    fn_low = calculate_froude_number(speed=2.0, waterline_length=lwl)
    assert fn_low < 0.35

    # Moderate wave resistance: Fn ≈ 0.35-0.40
    fn_mod = calculate_froude_number(speed=2.6, waterline_length=lwl)
    assert 0.35 <= fn_mod <= 0.42

    # High wave resistance: Fn > 0.40
    fn_high = calculate_froude_number(speed=3.5, waterline_length=lwl)
    assert fn_high > 0.40


def test_froude_number_invalid_speed():
    """Test Froude number with negative speed raises ValueError."""
    with pytest.raises(ValueError, match="Speed must be non-negative"):
        calculate_froude_number(speed=-1.0, waterline_length=5.0)


def test_froude_number_invalid_length():
    """Test Froude number with zero/negative length raises ValueError."""
    with pytest.raises(ValueError, match="Waterline length must be positive"):
        calculate_froude_number(speed=2.0, waterline_length=0.0)


# ============================================================================
# Test Hull Speed Calculation
# ============================================================================


def test_hull_speed_5m_waterline():
    """Test hull speed for 5m waterline."""
    v_hull = calculate_hull_speed(5.0)
    # V_hull ≈ 0.40 × sqrt(9.81 × 5.0) ≈ 2.80 m/s ≈ 10.1 km/h
    assert 2.7 < v_hull < 2.9
    assert abs(v_hull - 2.8014) < 0.01


def test_hull_speed_4m_waterline():
    """Test hull speed for shorter kayak (4m)."""
    v_hull = calculate_hull_speed(4.0)
    # V_hull ≈ 0.40 × sqrt(9.81 × 4.0) ≈ 2.51 m/s
    assert 2.4 < v_hull < 2.6


def test_hull_speed_6m_waterline():
    """Test hull speed for longer kayak (6m)."""
    v_hull = calculate_hull_speed(6.0)
    # V_hull ≈ 0.40 × sqrt(9.81 × 6.0) ≈ 3.06 m/s
    assert 3.0 < v_hull < 3.2


def test_hull_speed_invalid_length():
    """Test hull speed with zero/negative length raises ValueError."""
    with pytest.raises(ValueError, match="Waterline length must be positive"):
        calculate_hull_speed(0.0)
    with pytest.raises(ValueError, match="Waterline length must be positive"):
        calculate_hull_speed(-5.0)


# ============================================================================
# Test ITTC Friction Coefficient Calculation
# ============================================================================


def test_ittc_friction_coefficient_typical_reynolds():
    """Test ITTC friction coefficient for typical kayak Reynolds number."""
    # Re ≈ 8.4e6 (2 m/s, 5m length)
    cf = calculate_ittc_friction_coefficient(8.4e6)
    # Cf should be around 0.0028-0.0032 with roughness allowance
    assert 0.0025 < cf < 0.0035


def test_ittc_friction_coefficient_no_roughness():
    """Test ITTC friction coefficient with zero roughness allowance."""
    cf_smooth = calculate_ittc_friction_coefficient(8.4e6, roughness_allowance=0.0)
    cf_rough = calculate_ittc_friction_coefficient(8.4e6, roughness_allowance=0.0004)
    # Rough surface should have higher Cf
    assert cf_rough > cf_smooth
    assert abs(cf_rough - cf_smooth - 0.0004) < 1e-10


def test_ittc_friction_coefficient_formula():
    """Test ITTC 1957 formula against known values."""
    # Test at specific Reynolds numbers
    # Re = 1e6: Cf ≈ 0.0046875 (smooth, ITTC 1957)
    cf_1e6 = calculate_ittc_friction_coefficient(1e6, roughness_allowance=0.0)
    assert 0.0045 < cf_1e6 < 0.0048

    # Re = 1e7: Cf = 0.075/(7-2)² = 0.075/25 = 0.003 (smooth)
    cf_1e7 = calculate_ittc_friction_coefficient(1e7, roughness_allowance=0.0)
    assert 0.0028 < cf_1e7 < 0.0032

    # Higher Re → lower Cf (decreases with log(Re))
    assert cf_1e6 > cf_1e7


def test_ittc_friction_coefficient_invalid_reynolds():
    """Test ITTC friction coefficient with invalid Reynolds number."""
    with pytest.raises(ValueError, match="Reynolds number must be positive"):
        calculate_ittc_friction_coefficient(0.0)
    with pytest.raises(ValueError, match="Reynolds number must be positive"):
        calculate_ittc_friction_coefficient(-1e6)


def test_ittc_friction_coefficient_invalid_roughness():
    """Test ITTC friction coefficient with negative roughness."""
    with pytest.raises(ValueError, match="Roughness allowance must be non-negative"):
        calculate_ittc_friction_coefficient(8.4e6, roughness_allowance=-0.001)


# ============================================================================
# Test Frictional Resistance Calculation
# ============================================================================


def test_frictional_resistance_typical_kayak():
    """Test frictional resistance for typical kayak conditions."""
    # 2 m/s, 2.5 m² wetted surface, Cf = 0.003
    rf = calculate_frictional_resistance(speed=2.0, wetted_surface=2.5, friction_coefficient=0.003)
    # Rf = 0.5 × 1000 × 4 × 2.5 × 0.003 = 15 N
    assert abs(rf - 15.0) < 0.01


def test_frictional_resistance_zero_speed():
    """Test frictional resistance at zero speed."""
    rf = calculate_frictional_resistance(speed=0.0, wetted_surface=2.5, friction_coefficient=0.003)
    assert rf == 0.0


def test_frictional_resistance_speed_squared():
    """Test that frictional resistance scales with speed²."""
    rf_1 = calculate_frictional_resistance(
        speed=1.0, wetted_surface=2.5, friction_coefficient=0.003
    )
    rf_2 = calculate_frictional_resistance(
        speed=2.0, wetted_surface=2.5, friction_coefficient=0.003
    )
    rf_3 = calculate_frictional_resistance(
        speed=3.0, wetted_surface=2.5, friction_coefficient=0.003
    )

    # R ∝ V², so doubling speed quadruples resistance
    assert abs(rf_2 / rf_1 - 4.0) < 0.01
    assert abs(rf_3 / rf_1 - 9.0) < 0.01


def test_frictional_resistance_salt_water():
    """Test frictional resistance in salt water (higher density)."""
    rf_fresh = calculate_frictional_resistance(
        speed=2.0, wetted_surface=2.5, friction_coefficient=0.003, water_density=WATER_DENSITY_FRESH
    )
    rf_salt = calculate_frictional_resistance(
        speed=2.0, wetted_surface=2.5, friction_coefficient=0.003, water_density=WATER_DENSITY_SALT
    )

    # Salt water (1025 kg/m³) vs fresh water (1000 kg/m³)
    ratio = rf_salt / rf_fresh
    assert abs(ratio - 1.025) < 0.001


def test_frictional_resistance_invalid_inputs():
    """Test frictional resistance with invalid inputs."""
    with pytest.raises(ValueError, match="Speed must be non-negative"):
        calculate_frictional_resistance(-1.0, 2.5, 0.003)

    with pytest.raises(ValueError, match="Wetted surface must be positive"):
        calculate_frictional_resistance(2.0, 0.0, 0.003)

    with pytest.raises(ValueError, match="Friction coefficient must be non-negative"):
        calculate_frictional_resistance(2.0, 2.5, -0.001)

    with pytest.raises(ValueError, match="Water density must be positive"):
        calculate_frictional_resistance(2.0, 2.5, 0.003, water_density=0.0)


# ============================================================================
# Test Residuary Coefficient Calculation
# ============================================================================


def test_residuary_coefficient_low_froude():
    """Test residuary coefficient at low Froude number (Fn < 0.30)."""
    cr = calculate_residuary_coefficient(froude_number=0.25)
    # Very low wave resistance
    assert cr < 0.0001


def test_residuary_coefficient_moderate_froude():
    """Test residuary coefficient at moderate Froude number (Fn ≈ 0.35)."""
    cr = calculate_residuary_coefficient(froude_number=0.35)
    # Moderate wave resistance
    assert 0.0001 < cr < 0.001


def test_residuary_coefficient_hull_speed():
    """Test residuary coefficient at hull speed (Fn = 0.40)."""
    cr = calculate_residuary_coefficient(froude_number=0.40)
    # Wave resistance becomes significant
    assert 0.0005 < cr < 0.0015


def test_residuary_coefficient_high_froude():
    """Test residuary coefficient at high Froude number (Fn > 0.45)."""
    cr = calculate_residuary_coefficient(froude_number=0.50)
    # High wave resistance (but still modest for slender hulls)
    assert cr > 0.0005  # Cr increases significantly but empirical model is conservative


def test_residuary_coefficient_increases_with_froude():
    """Test that residuary coefficient increases with Froude number."""
    cr_low = calculate_residuary_coefficient(0.25)
    cr_mid = calculate_residuary_coefficient(0.35)
    cr_hull = calculate_residuary_coefficient(0.40)
    cr_high = calculate_residuary_coefficient(0.50)

    assert cr_low < cr_mid < cr_hull < cr_high


def test_residuary_coefficient_with_prismatic():
    """Test residuary coefficient adjustment for prismatic coefficient."""
    fn = 0.40

    # Slender hull (low Cp)
    cr_slender = calculate_residuary_coefficient(fn, prismatic_coefficient=0.50)

    # Reference hull (Cp = 0.55)
    cr_ref = calculate_residuary_coefficient(fn, prismatic_coefficient=0.55)

    # Fuller hull (high Cp)
    cr_full = calculate_residuary_coefficient(fn, prismatic_coefficient=0.60)

    # Fuller hulls have higher wave resistance
    assert cr_slender < cr_ref < cr_full


def test_residuary_coefficient_zero_negative_froude():
    """Test residuary coefficient with zero or negative Froude number."""
    cr_zero = calculate_residuary_coefficient(0.0)
    assert cr_zero >= 0.0

    # Negative should be handled (treated as zero)
    cr_neg = calculate_residuary_coefficient(-0.1)
    assert cr_neg >= 0.0


# ============================================================================
# Test Residuary Resistance Calculation
# ============================================================================


def test_residuary_resistance_typical_kayak():
    """Test residuary resistance for typical kayak conditions."""
    # 2 m/s, 2.5 m² wetted surface, Cr = 0.0005
    rr = calculate_residuary_resistance(speed=2.0, wetted_surface=2.5, residuary_coefficient=0.0005)
    # Rr = 0.5 × 1000 × 4 × 2.5 × 0.0005 = 2.5 N
    assert abs(rr - 2.5) < 0.01


def test_residuary_resistance_zero_speed():
    """Test residuary resistance at zero speed."""
    rr = calculate_residuary_resistance(speed=0.0, wetted_surface=2.5, residuary_coefficient=0.0005)
    assert rr == 0.0


def test_residuary_resistance_speed_squared():
    """Test that residuary resistance scales with speed²."""
    rr_1 = calculate_residuary_resistance(1.0, 2.5, 0.0005)
    rr_2 = calculate_residuary_resistance(2.0, 2.5, 0.0005)

    # R ∝ V²
    assert abs(rr_2 / rr_1 - 4.0) < 0.01


def test_residuary_resistance_invalid_inputs():
    """Test residuary resistance with invalid inputs."""
    with pytest.raises(ValueError, match="Speed must be non-negative"):
        calculate_residuary_resistance(-1.0, 2.5, 0.0005)

    with pytest.raises(ValueError, match="Wetted surface must be positive"):
        calculate_residuary_resistance(2.0, 0.0, 0.0005)

    with pytest.raises(ValueError, match="Residuary coefficient must be non-negative"):
        calculate_residuary_resistance(2.0, 2.5, -0.001)


# ============================================================================
# Test Power Calculations
# ============================================================================


def test_effective_power_typical():
    """Test effective power calculation."""
    # 20 N resistance at 2 m/s
    pe = calculate_effective_power(resistance=20.0, speed=2.0)
    # Pe = 20 × 2 = 40 W
    assert abs(pe - 40.0) < 0.01


def test_effective_power_zero_speed():
    """Test effective power at zero speed."""
    pe = calculate_effective_power(resistance=20.0, speed=0.0)
    assert pe == 0.0


def test_effective_power_zero_resistance():
    """Test effective power with zero resistance."""
    pe = calculate_effective_power(resistance=0.0, speed=2.0)
    assert pe == 0.0


def test_effective_power_invalid_inputs():
    """Test effective power with invalid inputs."""
    with pytest.raises(ValueError, match="Resistance must be non-negative"):
        calculate_effective_power(-10.0, 2.0)

    with pytest.raises(ValueError, match="Speed must be non-negative"):
        calculate_effective_power(20.0, -1.0)


def test_paddler_power_typical():
    """Test paddler power calculation with typical efficiency."""
    pp = calculate_paddler_power(effective_power=40.0, propulsion_efficiency=0.60)
    # Pp = 40 / 0.60 ≈ 66.67 W
    assert abs(pp - 66.67) < 0.1


def test_paddler_power_perfect_efficiency():
    """Test paddler power with 100% efficiency."""
    pp = calculate_paddler_power(effective_power=40.0, propulsion_efficiency=1.0)
    # Pp = Pe when η = 1.0
    assert abs(pp - 40.0) < 0.01


def test_paddler_power_low_efficiency():
    """Test paddler power with low efficiency (beginner)."""
    pp = calculate_paddler_power(effective_power=40.0, propulsion_efficiency=0.50)
    # Pp = 40 / 0.50 = 80 W
    assert abs(pp - 80.0) < 0.01


def test_paddler_power_zero_effective():
    """Test paddler power with zero effective power."""
    pp = calculate_paddler_power(effective_power=0.0, propulsion_efficiency=0.60)
    assert pp == 0.0


def test_paddler_power_invalid_inputs():
    """Test paddler power with invalid inputs."""
    with pytest.raises(ValueError, match="Effective power must be non-negative"):
        calculate_paddler_power(-10.0, 0.60)

    with pytest.raises(ValueError, match="Propulsion efficiency must be in range"):
        calculate_paddler_power(40.0, 0.0)

    with pytest.raises(ValueError, match="Propulsion efficiency must be in range"):
        calculate_paddler_power(40.0, 1.5)

    with pytest.raises(ValueError, match="Propulsion efficiency must be in range"):
        calculate_paddler_power(40.0, -0.1)


# ============================================================================
# Test Complete Resistance Calculation
# ============================================================================


def test_calculate_resistance_complete():
    """Test complete resistance calculation with all components."""
    result = calculate_resistance(
        speed=2.0, waterline_length=5.0, wetted_surface=2.5, prismatic_coefficient=0.55
    )

    # Check result type
    assert isinstance(result, ResistanceResult)

    # Check all fields are present and positive
    assert result.speed == 2.0
    assert result.froude_number > 0
    assert result.reynolds_number > 0
    assert result.friction_coefficient > 0
    assert result.residuary_coefficient >= 0
    assert result.frictional_resistance > 0
    assert result.residuary_resistance >= 0
    assert result.total_resistance > 0
    assert result.effective_power >= 0
    assert result.paddler_power >= 0

    # Total resistance = frictional + residuary
    assert (
        abs(result.total_resistance - (result.frictional_resistance + result.residuary_resistance))
        < 0.01
    )

    # Effective power = total resistance × speed
    assert abs(result.effective_power - result.total_resistance * 2.0) < 0.01

    # Paddler power > effective power (due to efficiency)
    assert result.paddler_power > result.effective_power


def test_calculate_resistance_frictional_dominates():
    """Test that frictional resistance dominates at typical kayak speeds."""
    result = calculate_resistance(
        speed=2.0,  # Typical paddling speed
        waterline_length=5.0,
        wetted_surface=2.5,
        prismatic_coefficient=0.55,
    )

    # At Fn ≈ 0.29, frictional should dominate (typically >95% for slender hulls at low speed)
    frictional_fraction = result.frictional_resistance / result.total_resistance
    assert frictional_fraction > 0.90  # Frictional dominates at low speed


def test_calculate_resistance_wave_dominates_at_high_speed():
    """Test that wave resistance becomes significant at high Froude numbers."""
    result_low = calculate_resistance(
        speed=2.0, waterline_length=5.0, wetted_surface=2.5, prismatic_coefficient=0.55  # Fn ≈ 0.29
    )

    result_high = calculate_resistance(
        speed=3.5, waterline_length=5.0, wetted_surface=2.5, prismatic_coefficient=0.55  # Fn ≈ 0.50
    )

    # Wave resistance fraction should increase significantly
    wave_frac_low = result_low.residuary_resistance / result_low.total_resistance
    wave_frac_high = result_high.residuary_resistance / result_high.total_resistance

    assert wave_frac_high > wave_frac_low
    assert wave_frac_high > 0.10  # More than 10% at high speed


def test_calculate_resistance_zero_speed():
    """Test resistance calculation at zero speed."""
    result = calculate_resistance(speed=0.0, waterline_length=5.0, wetted_surface=2.5)

    # All resistances and powers should be zero
    assert result.froude_number == 0.0
    assert result.reynolds_number == 0.0
    assert result.frictional_resistance == 0.0
    assert result.residuary_resistance == 0.0
    assert result.total_resistance == 0.0
    assert result.effective_power == 0.0
    assert result.paddler_power == 0.0


# ============================================================================
# Test Resistance Curve Calculation
# ============================================================================


def test_calculate_resistance_curve():
    """Test resistance curve calculation over speed range."""
    speeds = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    results = calculate_resistance_curve(
        speed_range=speeds, waterline_length=5.0, wetted_surface=2.5, prismatic_coefficient=0.55
    )

    # Check we get results for all speeds
    assert len(results) == len(speeds)

    # Check speeds match
    for i, result in enumerate(results):
        assert result.speed == speeds[i]

    # Check resistance increases with speed
    for i in range(len(results) - 1):
        assert results[i + 1].total_resistance > results[i].total_resistance
        assert results[i + 1].paddler_power > results[i].paddler_power


def test_calculate_resistance_curve_empty():
    """Test resistance curve with empty speed range."""
    results = calculate_resistance_curve(speed_range=[], waterline_length=5.0, wetted_surface=2.5)
    assert len(results) == 0


# ============================================================================
# Test Energy for Distance Calculation
# ============================================================================


def test_energy_for_distance_typical():
    """Test energy calculation for typical kayak trip."""
    # 20 N resistance, 10 km (10,000 m), 60% efficiency
    energy = calculate_energy_for_distance(
        resistance=20.0, distance=10000.0, propulsion_efficiency=0.60
    )

    # E = (20 × 10000) / 0.60 = 333,333 J ≈ 333 kJ ≈ 80 kcal
    assert abs(energy - 333333.33) < 1.0

    # Convert to kcal (1 kcal = 4184 J)
    energy_kcal = energy / 4184
    assert 75 < energy_kcal < 85


def test_energy_for_distance_zero_distance():
    """Test energy with zero distance."""
    energy = calculate_energy_for_distance(20.0, 0.0, 0.60)
    assert energy == 0.0


def test_energy_for_distance_zero_resistance():
    """Test energy with zero resistance."""
    energy = calculate_energy_for_distance(0.0, 10000.0, 0.60)
    assert energy == 0.0


def test_energy_for_distance_perfect_efficiency():
    """Test energy with 100% efficiency."""
    energy_perfect = calculate_energy_for_distance(20.0, 10000.0, 1.0)
    energy_real = calculate_energy_for_distance(20.0, 10000.0, 0.60)

    # Real energy should be higher (1/0.60 = 1.67x)
    assert abs(energy_real / energy_perfect - 1.667) < 0.01


def test_energy_for_distance_invalid_inputs():
    """Test energy calculation with invalid inputs."""
    with pytest.raises(ValueError, match="Resistance must be non-negative"):
        calculate_energy_for_distance(-10.0, 10000.0, 0.60)

    with pytest.raises(ValueError, match="Distance must be non-negative"):
        calculate_energy_for_distance(20.0, -1000.0, 0.60)

    with pytest.raises(ValueError, match="Propulsion efficiency must be in range"):
        calculate_energy_for_distance(20.0, 10000.0, 0.0)

    with pytest.raises(ValueError, match="Propulsion efficiency must be in range"):
        calculate_energy_for_distance(20.0, 10000.0, 1.5)


# ============================================================================
# Integration Tests
# ============================================================================


def test_resistance_realistic_kayak_scenario():
    """Integration test with realistic kayak parameters."""
    # Typical sea kayak:
    # - 5.2m waterline length
    # - 2.8 m² wetted surface
    # - Cp ≈ 0.56
    # - Cruising speed: 2.2 m/s (≈ 8 km/h)

    result = calculate_resistance(
        speed=2.2,
        waterline_length=5.2,
        wetted_surface=2.8,
        prismatic_coefficient=0.56,
        water_density=WATER_DENSITY_SALT,  # Sea kayaking
        propulsion_efficiency=0.60,
    )

    # Sanity checks for realistic values
    assert 0.25 < result.froude_number < 0.35  # Displacement regime
    assert 8e6 < result.reynolds_number < 2e7  # Turbulent flow
    assert 15 < result.total_resistance < 30  # Typical resistance range (N)
    assert 40 < result.paddler_power < 100  # Typical paddling power (W)

    # Frictional should dominate
    assert result.frictional_resistance > result.residuary_resistance


def test_resistance_sprint_kayak_scenario():
    """Integration test with sprint kayak at high speed."""
    # Racing K1:
    # - 5.0m waterline
    # - 1.8 m² wetted surface (narrower, smoother)
    # - Cp ≈ 0.50 (slender)
    # - Sprint speed: 4.5 m/s (> 16 km/h)

    result = calculate_resistance(
        speed=4.5,
        waterline_length=5.0,
        wetted_surface=1.8,
        prismatic_coefficient=0.50,
        roughness_allowance=0.0002,  # Very smooth racing hull
        propulsion_efficiency=0.70,  # Expert technique
    )

    # High Froude number
    assert result.froude_number > 0.60

    # High power requirement
    assert result.paddler_power > 200  # Elite athlete power output

    # Wave resistance should be significant
    wave_fraction = result.residuary_resistance / result.total_resistance
    assert wave_fraction > 0.15  # More than 15%


def test_resistance_curve_crossing_hull_speed():
    """Test resistance curve behavior crossing hull speed."""
    import numpy as np

    # Speed range from below to above hull speed
    speeds = np.linspace(1.0, 4.0, 20)

    results = calculate_resistance_curve(
        speed_range=speeds.tolist(),
        waterline_length=5.0,
        wetted_surface=2.5,
        prismatic_coefficient=0.55,
    )

    # Hull speed for 5m kayak ≈ 2.8 m/s
    v_hull = calculate_hull_speed(5.0)

    # Find results before and after hull speed
    before_hull = [r for r in results if r.speed < v_hull]
    after_hull = [r for r in results if r.speed > v_hull]

    # Wave resistance fraction should increase after hull speed
    if before_hull and after_hull:
        wave_frac_before = np.mean(
            [r.residuary_resistance / r.total_resistance for r in before_hull]
        )
        wave_frac_after = np.mean([r.residuary_resistance / r.total_resistance for r in after_hull])

        assert wave_frac_after > wave_frac_before


def test_constants_have_correct_values():
    """Test that physical constants are defined correctly."""
    assert WATER_DENSITY_FRESH == 1000.0
    assert WATER_DENSITY_SALT == 1025.0
    assert KINEMATIC_VISCOSITY == 1.19e-6
    assert GRAVITY == 9.81
    assert 0 < DEFAULT_ROUGHNESS_ALLOWANCE < 0.001
    assert 0.5 <= DEFAULT_PROPULSION_EFFICIENCY <= 0.7
