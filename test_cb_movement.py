"""
Simple test to verify CB movement when hull is rotated around CG.

We create a simple box-like hull and verify that:
1. At 0 degrees, CB.y should be ~0 (centered)
2. When tilted, CB.y should move in the direction of the tilt
3. The magnitude of CB.y movement should increase with angle
"""

import numpy as np
from src.geometry.point import Point3D
from src.geometry.spline import Spline3D
from src.geometry.profile import Profile


def test_rotation_of_points():
    """Test that points rotate correctly around origin."""
    print("=" * 60)
    print("TEST 1: Point rotation around x-axis")
    print("=" * 60)
    
    # Create a simple point at (0, 0, 1) - directly above origin
    origin = Point3D(0, 0, 0)
    
    # Create a simple 2-point spline for testing rotation
    points = [Point3D(0, 0, 1), Point3D(1, 0, 1)]
    spline = Spline3D("test", points)
    
    for angle in [0, 15, 30, 45, 90]:
        rotated = spline.apply_rotation_on_x_axis(origin, angle)
        p = rotated.points[0]
        
        # Expected: rotating (0,0,1) around x-axis by angle degrees
        # y_new = 0 * cos(a) - 1 * sin(a) = -sin(a)
        # z_new = 0 * sin(a) + 1 * cos(a) = cos(a)
        expected_y = -np.sin(np.radians(angle))
        expected_z = np.cos(np.radians(angle))
        
        print(f"Angle {angle:3d}°: Point (0,0,1) -> y={p.y:+.4f}, z={p.z:+.4f}")
        print(f"         Expected:         y={expected_y:+.4f}, z={expected_z:+.4f}")
        
        assert abs(p.y - expected_y) < 0.001, f"Y mismatch at {angle}°"
        assert abs(p.z - expected_z) < 0.001, f"Z mismatch at {angle}°"
    
    print("✓ Point rotation test PASSED\n")


def test_cb_movement_simple_profile():
    """Test CB movement with a simple rectangular profile."""
    print("=" * 60)
    print("TEST 2: CB movement with rectangular profile")
    print("=" * 60)
    
    # Create a simple rectangular profile at x=0
    # Width: 0.5m (y from -0.25 to 0.25)
    # Height: 0.2m (z from 0 to 0.2)
    #
    #  (-0.25, 0.2) -------- (0.25, 0.2)
    #       |                    |
    #       |      CG here       |
    #       |                    |
    #  (-0.25, 0)  -------- (0.25, 0)
    
    width = 0.5
    height = 0.2
    
    # CG at center of the box
    cg = Point3D(0, 0, height / 2)  # (0, 0, 0.1)
    
    # Waterline at half height
    waterline = height / 2  # 0.1m
    
    print(f"Rectangle: width={width}m, height={height}m")
    print(f"CG: {cg}")
    print(f"Waterline: {waterline}m")
    print()
    
    for angle in [0, 10, 20, 30, 45]:
        # Create rectangular profile points
        points = [
            Point3D(0, -width/2, 0),      # bottom left
            Point3D(0, width/2, 0),       # bottom right
            Point3D(0, width/2, height),  # top right
            Point3D(0, -width/2, height), # top left
        ]
        
        # Rotate points around CG
        angle_rad = np.radians(angle)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        rotated_points = []
        for p in points:
            y = p.y - cg.y
            z = p.z - cg.z
            y_new = y * cos_a - z * sin_a + cg.y
            z_new = y * sin_a + z * cos_a + cg.z
            rotated_points.append(Point3D(p.x, y_new, z_new))
        
        # Get points below waterline
        below_waterline = [p for p in rotated_points if p.z <= waterline]
        
        # Also find intersection points with waterline
        n = len(rotated_points)
        for i in range(n):
            p1 = rotated_points[i]
            p2 = rotated_points[(i + 1) % n]
            if (p1.z < waterline < p2.z) or (p2.z < waterline < p1.z):
                t = (waterline - p1.z) / (p2.z - p1.z)
                intersect_y = p1.y + t * (p2.y - p1.y)
                below_waterline.append(Point3D(0, intersect_y, waterline))
        
        # Calculate centroid (CB) of submerged area
        if len(below_waterline) >= 3:
            cb_y = sum(p.y for p in below_waterline) / len(below_waterline)
            cb_z = sum(p.z for p in below_waterline) / len(below_waterline)
        else:
            cb_y = 0
            cb_z = 0
        
        print(f"Angle {angle:3d}°: CB.y = {cb_y:+.4f}m, CB.z = {cb_z:.4f}m")
        print(f"          Submerged points: {len(below_waterline)}")
        for p in below_waterline:
            print(f"            ({p.y:+.3f}, {p.z:.3f})")
    
    print()


def test_cb_movement_with_hull_method():
    """Test the actual hull _calculate_waterline method."""
    print("=" * 60)
    print("TEST 3: CB movement using Hull._calculate_waterline")
    print("=" * 60)
    
    from src.geometry.hull import Hull, read_file
    
    file_path = 'data/k01.json'
    data = read_file(file_path)
    
    hull = Hull()
    hull.initialize(data)
    
    print(f"Hull: {hull.name}")
    print(f"Beam: {hull.beam():.3f}m, Depth: {hull.depth():.3f}m")
    print(f"CG: x={hull.cg.x:.3f}, y={hull.cg.y:.3f}, z={hull.cg.z:.3f}")
    print(f"Initial CB: x={hull.cb.x:.3f}, y={hull.cb.y:.3f}, z={hull.cb.z:.3f}")
    print(f"Waterline: {hull.waterline:.3f}m")
    print(f"Weight: {hull.target_weight + hull.target_payload}kg")
    print()
    
    weight = hull.target_weight + hull.target_payload
    
    print("Angle (°) |   CB.y (m)  |   CB.z (m)  | Waterline | Displ.")
    print("-" * 65)
    
    prev_cb_y = None
    for angle in [0, -5, -10, -15, -20, -30, -45]:
        waterline, cb, displacement = hull._calculate_waterline(weight, angle=angle)
        
        delta = ""
        if prev_cb_y is not None:
            delta = f" (Δy={cb.y - prev_cb_y:+.4f})"
        prev_cb_y = cb.y
        
        # Calculate expected CB.y movement for a simple rectangular hull
        # at the same waterline (just for reference)
        half_beam = hull.beam() / 2
        expected_cb_y_shift = half_beam * np.sin(np.radians(abs(angle))) / 3  # rough approximation
        
        print(f"  {angle:+4d}    |  {cb.y:+.5f}  |   {cb.z:.5f}  |  {waterline:.4f}  | {displacement:.0f}kg {delta}")
    
    print()
    print("Expected CB.y at 45° for simple box: ~", hull.beam()/4, "m")


def test_single_profile_rotation():
    """Test CB of a single profile at different angles using Profile class."""
    print("=" * 60)
    print("TEST 4: Single profile CB at mid-hull (using Profile class)")
    print("=" * 60)
    
    from src.geometry.hull import Hull, read_file
    from src.geometry.profile import Profile
    
    file_path = 'data/k01.json'
    data = read_file(file_path)
    
    hull = Hull()
    hull.initialize(data)
    
    # Get points at mid-hull
    mid_x = (hull.min_x + hull.max_x) / 2
    
    print(f"Testing at x={mid_x:.2f}m")
    print(f"CG used for rotation: y={hull.cg.y:.3f}, z={hull.cg.z:.3f}")
    print()
    
    for angle in [0, -15, -30, -45]:
        # Recalculate waterline for this angle
        weight = hull.target_weight + hull.target_payload
        waterline, total_cb, displacement = hull._calculate_waterline(weight, angle=angle)
        
        # Now get profile at mid-hull with that waterline
        points = []
        for curve in hull.curves:
            if angle != 0.0:
                leaned_curve = curve.apply_rotation_on_x_axis(hull.cg, angle)
            else:
                leaned_curve = curve
            try:
                point = leaned_curve.eval_x(mid_x)
                points.append(point)
            except ValueError:
                continue
        
        # Get points below the calculated waterline
        submerged = hull._get_points_below_waterline(points, waterline)
        
        print(f"\nAngle {angle}°: waterline={waterline:.4f}m")
        print(f"  All points ({len(points)}):")
        for p in sorted(points, key=lambda p: p.y):
            marker = " [ABOVE]" if p.z > waterline else ""
            print(f"    y={p.y:+.4f}, z={p.z:.4f}{marker}")
        
        print(f"  Submerged polygon ({len(submerged)} points):")
        for p in submerged:
            print(f"    y={p.y:+.4f}, z={p.z:.4f}")
        
        if len(submerged) >= 3:
            profile = Profile(mid_x, submerged)
            area = profile.calculate_area()
            cy, cz = profile.calculate_centroid()
            print(f"  -> Profile area: {area:.6f} m²")
            print(f"  -> Profile centroid: y={cy:+.4f}, z={cz:.4f}")
            print(f"  -> Total hull CB at this angle: y={total_cb.y:+.4f}, z={total_cb.z:.4f}")


if __name__ == "__main__":
    test_rotation_of_points()
    # test_cb_movement_simple_profile()
    test_cb_movement_with_hull_method()
    test_single_profile_rotation()
    
    # Generate a simple plot
    print("\n" + "=" * 60)
    print("Generating plot of CB movement...")
    print("=" * 60)
    
    import matplotlib.pyplot as plt
    from src.geometry.hull import Hull, read_file
    
    hull = Hull()
    hull.initialize(read_file('data/k01.json'))
    weight = hull.target_weight + hull.target_payload
    
    angles = list(range(0, -50, -5))
    cb_y_values = []
    cb_z_values = []
    
    for angle in angles:
        _, cb, _ = hull._calculate_waterline(weight, angle=angle)
        cb_y_values.append(cb.y)
        cb_z_values.append(cb.z)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.plot(angles, cb_y_values, 'b-o', linewidth=2, markersize=6)
    ax1.set_xlabel('Heel Angle (degrees)')
    ax1.set_ylabel('CB.y (m)')
    ax1.set_title('Center of Buoyancy - Lateral Movement')
    ax1.grid(True)
    ax1.axhline(y=0, color='gray', linestyle='--')
    
    ax2.plot(cb_y_values, cb_z_values, 'r-o', linewidth=2, markersize=6)
    ax2.set_xlabel('CB.y (m)')
    ax2.set_ylabel('CB.z (m)')
    ax2.set_title('CB Path (Y-Z plane)')
    ax2.grid(True)
    # Mark CG position
    ax2.plot(hull.cg.y, hull.cg.z, 'g*', markersize=15, label='CG')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('cb_movement_plot.png', dpi=100)
    print("Plot saved to cb_movement_plot.png")
