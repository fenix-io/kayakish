from typing import Tuple
import numpy as np
from src.geometry.hull import Hull, read_file
from src.geometry.point import Point3D

# Physical constants
GRAVITY = 9.81  # m/s² - acceleration due to gravity


def calculate_combined_cg(
    hull_weight: float,
    hull_cg: Point3D,
    payload_weight: float,
    payload_cg_z: float,
) -> Point3D:
    """Calculate combined CG of hull and payload.

    Args:
        hull_weight: Weight of the hull in kg
        hull_cg: Center of gravity of the hull
        payload_weight: Weight of the payload (paddler) in kg
        payload_cg_z: Height of payload CG above hull bottom (m)
                      Typically 0.35-0.38m for a seated paddler

    Returns:
        Combined center of gravity as Point3D
    """
    total_weight = hull_weight + payload_weight

    # Assume payload is centered longitudinally and laterally
    # (paddler sits at center of kayak)
    payload_cg_x = hull_cg.x  # Same longitudinal position as hull CG
    payload_cg_y = 0.0  # Centered laterally

    # Weighted average of CG positions
    cg_x = (hull_weight * hull_cg.x + payload_weight * payload_cg_x) / total_weight
    cg_y = (hull_weight * hull_cg.y + payload_weight * payload_cg_y) / total_weight
    cg_z = (hull_weight * hull_cg.z + payload_weight * payload_cg_z) / total_weight

    return Point3D(cg_x, cg_y, cg_z)


def create_stability_curve_points(
    hull: Hull,
    paddler_cg_z: float = 0.25,
    paddler_weight: float = None,
    hull_weight: float = None,
    max_angle: float = 90,
    step: float = 3,
    break_on_vanishing: bool = False,
) -> Tuple[float, float, float, list[dict]]:
    """Calculate stability curve (GZ curve) for a hull with payload.

    The righting arm GZ is the horizontal distance between:
    - The line of action of weight (through combined CG, pointing down)
    - The line of action of buoyancy (through CB, pointing up)

    When the hull heels to angle θ:
    - The hull rotates around its own CG (hull.cg)
    - CB moves as the submerged volume changes
    - The combined CG (hull + paddler) also rotates with the hull
    - GZ = CB.y - combined_CG.y (in the rotated reference frame)

    Args:
        hull: The Hull object to analyze
        payload_cg_z: Height of paddler's CG above hull bottom (m)
                      Default 0.36m for seated paddler
        max_angle: Maximum heel angle to calculate (degrees)
        step: Angle increment (degrees)

    Returns:
        List of dicts with angle, GZ, moment, CB position, etc.
    """
    hull_weight = hull_weight or hull.target_weight
    paddler_weight = paddler_weight or hull.target_payload
    total_weight = hull_weight + paddler_weight

    # Calculate combined CG
    combined_cg = calculate_combined_cg(hull_weight, hull.cg, paddler_weight, paddler_cg_z)

    # print(f"Hull CG:     x={hull.cg.x:.3f}, y={hull.cg.y:.3f}, z={hull.cg.z:.3f} m")
    # print(f"Paddler CG:  x={hull.cg.x:.3f}, y=0.000, z={paddler_cg_z:.3f} m")
    # print(f"Combined CG: x={combined_cg.x:.3f}, y={combined_cg.y:.3f}, z={combined_cg.z:.3f} m")
    # print(f"Hull weight: {hull_weight} kg, Paddler: {paddler_weight} kg, Total: {total_weight} kg")
    # print()

    stability_points = []

    for angle_deg in np.arange(0, max_angle + step, step):
        angle_rad = np.radians(angle_deg)

        # Calculate waterline and CB for this heel angle
        # Hull rotates around its own CG
        # Positive angle = heel to starboard (starboard side goes down)
        waterline, cb, displacement = hull._calculate_waterline(total_weight, angle=angle_deg)

        # The combined CG rotates with the hull around hull.cg
        # Calculate the position of combined CG after rotation
        # Relative to hull.cg:
        rel_y = combined_cg.y - hull.cg.y  # = 0 (both centered)
        rel_z = combined_cg.z - hull.cg.z  # positive (combined CG is higher)

        # Rotate this relative position (positive angle = heel to starboard)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        rotated_rel_y = rel_y * cos_a - rel_z * sin_a
        rotated_rel_z = rel_y * sin_a + rel_z * cos_a

        # Combined CG position after rotation
        combined_cg_y_rotated = hull.cg.y + rotated_rel_y
        combined_cg_z_rotated = hull.cg.z + rotated_rel_z

        # GZ = righting arm (horizontal distance for restoring moment)
        # For heel to starboard: CB moves to starboard (y<0), CG also moves but less
        # Positive GZ = restoring moment = CG.y - CB.y (CB more to starboard)
        gz = combined_cg_y_rotated - cb.y

        # Righting moment = Weight (force) × GZ
        # Weight = mass × gravity, so moment is in N·m
        moment = total_weight * GRAVITY * gz  # in N·m

        stability_points.append(
            {
                "angle": angle_deg,
                "gz": gz,
                "moment": moment,
                "cb_y": cb.y,
                "cb_z": cb.z,
                "cg_y": combined_cg_y_rotated,
                "cg_z": combined_cg_z_rotated,
                "waterline": waterline,
                "displacement": displacement,
            }
        )

        # print(
        #     f"Angle {angle_deg:5.1f}° | GZ={gz:+.4f}m | "
        #     f"Moment={moment:+.1f} N·m | "
        #     f"CB.y={cb.y:+.4f} | CG.y={combined_cg_y_rotated:+.4f}"
        # )
        if break_on_vanishing and gz < 0 and angle_deg > 0:
            # print("Vanishing stability reached, stopping calculation.")
            break

    # Find angle of vanishing stability (where GZ becomes negative)
    vanishing_angle = None
    max_moment = 0.0
    max_moment_angle = 0.0
    for i in range(1, len(stability_points)):
        if stability_points[i]["gz"] < 0 and stability_points[i - 1]["gz"] >= 0:
            # Linear interpolation to find exact angle
            gz1 = stability_points[i - 1]["gz"]
            gz2 = stability_points[i]["gz"]
            a1 = stability_points[i - 1]["angle"]
            a2 = stability_points[i]["angle"]
            vanishing_angle = a1 + (0 - gz1) * (a2 - a1) / (gz2 - gz1)
            break
        if stability_points[i]["moment"] > max_moment:
            max_moment = stability_points[i]["moment"]
            max_moment_angle = stability_points[i]["angle"]

    # if vanishing_angle:
    #     print(f"\n⚠️  Angle of vanishing stability: {vanishing_angle:.1f}°")
    # else:
    #     print(f"\n✓ Positive stability throughout range (0° to {max_angle}°)")

    # Find maximum GZ and its angle
    # max_gz_point = max(stability_points, key=lambda p: p["gz"])
    # print(f"Maximum GZ: {max_gz_point['gz']:.4f}m at {max_gz_point['angle']:.1f}°")
    # print(f"Maximum Righting Moment: {max_moment:.1f} N·m at {max_moment_angle:.1f}°")

    return vanishing_angle, max_moment, max_moment_angle, stability_points


def plot_stability_curve(stability_points: list[dict], hull_name: str = "Hull"):
    """Plot the GZ curve."""
    import matplotlib.pyplot as plt

    angles = [p["angle"] for p in stability_points]
    gz_values = [p["gz"] for p in stability_points]
    moments = [p["moment"] for p in stability_points]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # GZ curve
    ax1.plot(angles, gz_values, "b-o", linewidth=2, markersize=4)
    ax1.axhline(y=0, color="red", linestyle="--", linewidth=1)
    ax1.fill_between(
        angles, gz_values, 0, where=[g > 0 for g in gz_values], alpha=0.3, color="green"
    )
    ax1.fill_between(angles, gz_values, 0, where=[g < 0 for g in gz_values], alpha=0.3, color="red")
    ax1.set_ylabel("GZ - Righting Arm (m)")
    ax1.set_title(f"Stability Curve (GZ) - {hull_name}")
    ax1.grid(True, alpha=0.3)
    ax1.legend(["GZ", "Zero line", "Positive stability", "Negative stability"])

    # Moment curve
    ax2.plot(angles, moments, "g-o", linewidth=2, markersize=4)
    ax2.axhline(y=0, color="red", linestyle="--", linewidth=1)
    ax2.fill_between(angles, moments, 0, where=[m > 0 for m in moments], alpha=0.3, color="green")
    ax2.fill_between(angles, moments, 0, where=[m < 0 for m in moments], alpha=0.3, color="red")
    ax2.set_xlabel("Heel Angle (degrees)")
    ax2.set_ylabel("Righting Moment (N·m)")
    ax2.set_title("Righting Moment vs Heel Angle")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("stability_curve.png", dpi=120)
    print("\nPlot saved to stability_curve.png")
    plt.show()


if __name__ == "__main__":
    file_path = "data/k01.json"
    data = read_file(file_path)

    hull = Hull()
    hull.build(data)

    print(f"Hull Name: {hull.name}")
    print(f"Hull Beam: {hull.beam():.3f} m")
    print(f"Hull Depth: {hull.depth():.3f} m")
    print(f"Hull Length: {hull.length():.3f} m")
    print(f"Waterline: {hull.waterline:.3f} m")
    print()

    # Paddler CG height: typically 35-38cm above hull bottom for seated position
    payload_cg_z = 0.25  # meters

    print("=" * 70)
    print(f"Calculating stability curve with paddler CG at z={payload_cg_z}m")
    print("=" * 70)

    stability_curve = create_stability_curve_points(
        hull, paddler_cg_z=payload_cg_z, max_angle=90, step=5
    )

    print("\n" + "=" * 70)
    plot_stability_curve(stability_curve, hull.name)
