"""
Visualize submerged profile at different heel angles.
"""

import matplotlib.pyplot as plt
import numpy as np
from src.geometry.hull import Hull, read_file
from src.geometry.profile import Profile


def visualize_profiles():
    hull = Hull()
    hull.build(read_file("data/k01.json"))

    weight = hull.target_weight + hull.target_payload
    mid_x = (hull.min_x + hull.max_x) / 2

    angles = [0, -15, -30, -45]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for idx, angle in enumerate(angles):
        ax = axes[idx]

        # Calculate waterline for this angle
        waterline, total_cb, displacement = hull._calculate_waterline(weight, angle=angle)

        # Get all points at mid-hull
        all_points = []
        for curve in hull.curves:
            if angle != 0.0:
                leaned_curve = curve.apply_rotation_on_x_axis(hull.cg, angle)
            else:
                leaned_curve = curve
            try:
                point = leaned_curve.eval_x(mid_x)
                all_points.append(point)
            except ValueError:
                continue

        # Get submerged polygon
        submerged = hull._get_points_below_waterline(all_points, waterline)

        # Plot all hull points
        y_all = [p.y for p in all_points]
        z_all = [p.z for p in all_points]
        ax.scatter(y_all, z_all, c="blue", s=50, label="Hull points", zorder=3)

        # Plot submerged polygon
        if len(submerged) >= 3:
            profile = Profile(mid_x, submerged)
            y_sub = [p.y for p in profile.points] + [profile.points[0].y]
            z_sub = [p.z for p in profile.points] + [profile.points[0].z]
            ax.fill(y_sub, z_sub, alpha=0.3, color="cyan", label="Submerged area")
            ax.plot(y_sub, z_sub, "c-", linewidth=2)

            # Calculate and plot centroid (CB)
            cy, cz = profile.calculate_centroid()
            ax.plot(cy, cz, "ro", markersize=12, label=f"CB (y={cy:.3f}m)", zorder=5)

        # Plot waterline
        ax.axhline(
            y=waterline,
            color="blue",
            linestyle="--",
            linewidth=2,
            label=f"Waterline ({waterline:.3f}m)",
        )

        # Plot CG (rotated position)
        cg_y_rot = hull.cg.y  # CG.y stays at 0 since we rotate around it
        cg_z_rot = hull.cg.z  # CG.z stays the same
        ax.plot(cg_y_rot, cg_z_rot, "g*", markersize=15, label=f"CG (z={cg_z_rot:.3f}m)", zorder=5)

        # Reference lines
        ax.axvline(x=0, color="gray", linestyle=":", alpha=0.5)
        ax.axhline(y=0, color="gray", linestyle=":", alpha=0.5)

        ax.set_xlabel("Y (m) - Starboard (+) / Port (-)")
        ax.set_ylabel("Z (m)")
        ax.set_title(f"Heel angle: {angle}°\nDisplacement: {displacement:.0f}kg")
        ax.legend(loc="upper right", fontsize=8)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-0.4, 0.4)
        ax.set_ylim(-0.1, 0.35)

    plt.suptitle(f"Submerged Profile at x={mid_x:.2f}m (mid-hull)\nHull: {hull.name}", fontsize=14)
    plt.tight_layout()
    plt.savefig("profile_visualization.png", dpi=120)
    print("Saved to profile_visualization.png")
    plt.show()


if __name__ == "__main__":
    visualize_profiles()
