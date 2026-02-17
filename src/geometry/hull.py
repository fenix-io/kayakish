import json
import numpy as np
from src.geometry.profile import Profile
from src.geometry.point import Point3D
from src.geometry.curve import Curve


class WaterlineCalculationError(Exception):
    """Raised when waterline calculation fails to converge.

    Or when hull geometry is inadequate.
    """

    pass


class Hull:
    name: str
    description: str | None = None
    target_waterline: float | None = None
    target_weight: float | None = None
    target_payload: float | None = None
    waterline: float | None = None
    file_name: str | None = None

    def __init__(self):
        self.curves: list[Curve] = []
        self.profiles: list[Profile] = []

    def _add_spline(self, spline: Curve):
        self.curves.append(spline)

    def as_dict(self):
        return self.__dict__

    def length(self):
        return self.max_x - self.min_x

    def beam(self):
        return self.max_y - self.min_y

    def depth(self):
        return self.max_z - self.min_z

    def wetted_surface_area(self, waterline: float = None, step: float = 0.05) -> float:
        """Calculate the total wetted surface area of the hull below the waterline.

        The wetted surface area is the total area of hull surface in contact with water,
        calculated by integrating the wetted perimeter along the hull length using the
        trapezoidal rule.

        Args:
            waterline: The z-coordinate of the waterline. If None, uses self.waterline.
            step: The longitudinal step size for integration in meters. Default 0.05 m.

        Returns:
            float: Wetted surface area in square meters (m²)

        Raises:
            ValueError: If waterline is not set or invalid

        Example:
            >>> hull.wetted_surface_area()  # Uses hull.waterline
            2.345  # m²
            >>> hull.wetted_surface_area(waterline=0.15)  # Custom waterline
            2.456  # m²
        """
        if waterline is None:
            waterline = self.waterline
        if waterline is None or waterline <= 0:
            raise ValueError(
                f"Invalid waterline: {waterline}. "
                "Ensure waterline is calculated before calling wetted_surface_area()."
            )

        x = self.min_x
        perimeters = []
        stations = []

        # Calculate wetted perimeter at each station
        while x <= self.max_x:
            points = []
            for curve in self.curves:
                try:
                    point = curve.eval_x(x)
                    points.append(point)
                except ValueError:
                    continue

            if len(points) >= 3:
                # Get points below waterline
                points_below = self._get_points_below_waterline(points, waterline)
                profile = Profile(x, points_below)

                if profile.is_valid():
                    perimeter = profile.wetted_perimeter()
                    perimeters.append(perimeter)
                    stations.append(x)

            x += step

        if len(perimeters) < 2:
            return 0.0

        # Integrate wetted perimeter along hull length using trapezoidal rule
        # S_w = ∫ P_w(x) dx ≈ Σ [(P_w(i) + P_w(i+1)) / 2] * Δx
        wetted_area = 0.0
        for i in range(len(perimeters) - 1):
            avg_perimeter = (perimeters[i] + perimeters[i + 1]) / 2.0
            dx = stations[i + 1] - stations[i]
            wetted_area += avg_perimeter * dx

        return wetted_area

    def waterline_length(self, waterline: float = None, step: float = 0.05) -> float:
        """Calculate the waterline length (LWL) of the hull.

        The waterline length is the longitudinal distance from the forward-most to the
        aft-most point where the hull intersects the waterline. This is typically less
        than the overall length (LOA).

        Args:
            waterline: The z-coordinate of the waterline. If None, uses self.waterline.
            step: The longitudinal step size for sampling in meters. Default 0.05 m.

        Returns:
            float: Waterline length in meters (m)

        Raises:
            ValueError: If waterline is not set or invalid

        Example:
            >>> hull.waterline_length()
            4.850  # m
        """
        if waterline is None:
            waterline = self.waterline
        if waterline is None or waterline <= 0:
            raise ValueError(
                f"Invalid waterline: {waterline}. "
                "Ensure waterline is calculated before calling waterline_length()."
            )

        x = self.min_x
        forward_x = None  # Forward-most station with waterline intersection
        aft_x = None  # Aft-most station with waterline intersection

        # Find forward-most and aft-most stations where hull intersects waterline
        while x <= self.max_x:
            points = []
            for curve in self.curves:
                try:
                    point = curve.eval_x(x)
                    points.append(point)
                except ValueError:
                    continue

            if len(points) >= 3:
                # Check if any points are below waterline (hull intersects waterline here)
                has_submerged = any(p.z <= waterline for p in points)
                has_emerged = any(p.z > waterline for p in points)

                # Hull intersects waterline if it has both submerged and emerged points
                if has_submerged and has_emerged:
                    if aft_x is None:
                        aft_x = x  # First intersection (aft)
                    forward_x = x  # Keep updating (last intersection will be forward)

            x += step

        if aft_x is None or forward_x is None:
            return 0.0

        return forward_x - aft_x

    def waterline_beam(self, waterline: float = None, step: float = 0.05) -> float:
        """Calculate the maximum beam (width) of the hull at the waterline.

        The waterline beam (BWL) is the maximum transverse width of the hull measured
        at the waterline, from port to starboard.

        Args:
            waterline: The z-coordinate of the waterline. If None, uses self.waterline.
            step: The longitudinal step size for sampling in meters. Default 0.05 m.

        Returns:
            float: Waterline beam in meters (m)

        Raises:
            ValueError: If waterline is not set or invalid

        Example:
            >>> hull.waterline_beam()
            0.545  # m
        """
        if waterline is None:
            waterline = self.waterline
        if waterline is None or waterline <= 0:
            raise ValueError(
                f"Invalid waterline: {waterline}. "
                "Ensure waterline is calculated before calling waterline_beam()."
            )

        x = self.min_x
        max_beam = 0.0

        # Find maximum beam at waterline across all stations
        while x <= self.max_x:
            points = []
            for curve in self.curves:
                try:
                    point = curve.eval_x(x)
                    points.append(point)
                except ValueError:
                    continue

            if len(points) >= 3:
                # Find points at or near the waterline
                # We look for points within a small tolerance of the waterline,
                # or interpolate between points above and below
                waterline_y_coords = []

                n = len(points)
                for i in range(n):
                    p1 = points[i]
                    p2 = points[(i + 1) % n]

                    # If point is at waterline, add it
                    if abs(p1.z - waterline) < 1e-6:
                        waterline_y_coords.append(abs(p1.y))

                    # If edge crosses waterline, interpolate
                    if (p1.z < waterline < p2.z) or (p2.z < waterline < p1.z):
                        t = (waterline - p1.z) / (p2.z - p1.z)
                        intersect_y = p1.y + t * (p2.y - p1.y)
                        waterline_y_coords.append(abs(intersect_y))

                # Calculate beam at this station
                if len(waterline_y_coords) >= 2:
                    station_beam = max(waterline_y_coords) * 2  # Port to starboard
                    max_beam = max(max_beam, station_beam)

            x += step

        return max_beam

    def initialize_from_data(self, data: dict):
        self.name = data.get("name", "KAYAK HULL")
        self.description = data.get("description", "KAYAK HULL")
        self.target_waterline = data.get("target_waterline", 0.1)
        self.target_weight = data.get("target_weight", 100)
        self.target_payload = data.get("target_payload", 100)
        self.volume = data.get("volume", 0.0)
        if data.get("cg"):
            self.cg = Point3D(data["cg"][0], data["cg"][1], data["cg"][2])
        else:
            self.cg = None
        self.waterline = data.get("waterline", 0.0)
        if data.get("cb"):
            self.cb = Point3D(data["cb"][0], data["cb"][1], data["cb"][2])
        else:
            self.cb = None
        self.displacement = data.get("displacement", 0.0)
        self.min_x = data.get("min_x", 0.0)
        self.max_x = data.get("max_x", 0.0)
        self.min_y = data.get("min_y", 0.0)
        self.max_y = data.get("max_y", 0.0)
        self.min_z = data.get("min_z", 0.0)
        self.max_z = data.get("max_z", 0.0)
        for curve_data in data.get("curves", []):
            name = curve_data.get("name", "Unnamed Curve")
            points = [Point3D(p[0], p[1], p[2]) for p in curve_data.get("points", [])]
            mirrored = curve_data.get("mirrored", False)
            self._add_spline(Curve(name, points, mirrored=mirrored))
        for profile_data in data.get("profiles", []):
            station = profile_data.get("station", 0.0)
            points = [Point3D(p[0], p[1], p[2]) for p in profile_data.get("points", [])]
            self.profiles.append(Profile(station, points))

    def build(self, data: dict):
        self.name = data.get("name", "KAYAK HULL")
        self.description = data.get("description", "KAYAK HULL")
        self.target_waterline = data.get("target_waterline", 0.1)
        self.target_weight = data.get("target_weight", 100)
        self.target_payload = data.get("target_payload", 100)

        self.min_x = float("inf")
        self.max_x = float("-inf")
        self.min_y = float("inf")
        self.max_y = float("-inf")
        self.min_z = float("inf")
        self.max_z = float("-inf")

        for spline_data in data.get("curves", []):
            name = spline_data["name"] = spline_data.get("name", "Unnamed Curve")
            points = []
            oposite = []
            y = 0.0
            for point in spline_data.get("points", []):
                p = Point3D(point[0], point[1], point[2])
                self._update_min_max(p)
                points.append(p)
                y += point[1]

            spline = Curve(name, points, mirrored=False)
            self._add_spline(spline)
            if y != 0:
                for point in spline_data.get("points", []):
                    p = Point3D(point[0], -point[1], point[2])
                    self._update_min_max(p)
                    oposite.append(p)

                spline_oposite = Curve("Mirror of " + name, oposite, mirrored=True)
                self._add_spline(spline_oposite)

        volume, cg = self._calculate_profiles_volume_and_cg()
        self.volume = volume
        self.cg = cg
        weight = self.target_payload + self.target_weight
        waterline, cb, displacement = self._calculate_waterline(weight, angle=0.0)
        self.waterline = waterline
        self.cb = cb
        self.displacement = displacement

    def _calculate_profiles_volume_and_cg(self):
        x = self.min_x
        step = 0.05
        profiles = []
        volumes = []
        cgs = []
        while x <= self.max_x:
            points = self._get_points_at(x)
            if len(points) >= 3:
                profile = Profile(x, points)
                if profile.is_valid():
                    volume, cg = profile.calculate_volume_and_cg(step)
                    if volume > 0:
                        profiles.append(profile)
                        volumes.append(volume)
                        cgs.append(cg)
            x += step

        self.profiles = profiles  # Store profiles for potential visualization or further analysis

        # Calculate total volume
        volume = sum(volumes)

        # Check if we have valid volume
        if volume == 0:
            raise WaterlineCalculationError(
                "Hull has zero volume. The geometry may be degenerate "
                "or incorrectly defined. Check that curves define a "
                "valid 3D shape with non-zero cross-sections."
            )

        # Calculate weighted CG
        cgx = 0.0
        cgy = 0.0
        cgz = 0.0
        for i in range(len(volumes)):
            cgx += volumes[i] * cgs[i].x
            cgy += volumes[i] * cgs[i].y
            cgz += volumes[i] * cgs[i].z

        # Divide by total volume
        cgx /= volume
        cgy /= volume
        cgz /= volume

        self.volume = volume
        self.cg = Point3D(cgx, cgy, cgz)
        return volume, Point3D(cgx, cgy, cgz)

    def _update_min_max(self, point: Point3D):
        if point.x < self.min_x:
            self.min_x = point.x
        if point.x > self.max_x:
            self.max_x = point.x
        if point.y < self.min_y:
            self.min_y = point.y
        if point.y > self.max_y:
            self.max_y = point.y
        if point.z < self.min_z:
            self.min_z = point.z
        if point.z > self.max_z:
            self.max_z = point.z

    def _get_points_at(
        self,
        x: float,
    ) -> list[Point3D]:
        points = []
        for curve in self.curves:
            try:
                point = curve.eval_x(x)
                points.append(point)
            except ValueError:
                continue
        return points

    def _calculate_waterline(self, weight: float, angle: float = 0.0):
        waterline = self.waterline or self.target_waterline or self.depth() / 3
        max_iterations = 50  # Prevent infinite loops
        iteration = 0

        while 0 < waterline and waterline <= self.depth() and iteration < max_iterations:
            iteration += 1
            x = self.min_x
            step = 0.05
            profiles = []
            volumes = []
            cgs = []

            while x <= self.max_x:
                points = []
                for curve in self.curves:
                    if angle != 0.0:
                        leaned_curve = curve.apply_rotation_on_x_axis(self.cg, angle)
                    else:
                        leaned_curve = curve
                    try:
                        point = leaned_curve.eval_x(x)
                        points.append(point)
                    except ValueError:
                        continue

                if len(points) >= 3:
                    points = self._get_points_below_waterline(points, waterline)
                    profile = Profile(x, points)
                    if profile.is_valid():
                        volume, cg = profile.calculate_volume_and_cg(step)
                        if volume > 0:
                            profiles.append(profile)
                            volumes.append(volume)
                            cgs.append(cg)
                x += step

            # Calculate total volume
            volume = sum(volumes)

            # Check if we have a valid volume
            if volume == 0:
                raise WaterlineCalculationError(
                    f"Unable to calculate waterline: Hull has "
                    f"insufficient volume at waterline {waterline:.3f}m. "
                    f"The hull geometry may be too small or incorrectly "
                    f"defined."
                )

            # Calculate weighted CG
            cgx = 0.0
            cgy = 0.0
            cgz = 0.0
            for i in range(len(volumes)):
                cgx += volumes[i] * cgs[i].x
                cgy += volumes[i] * cgs[i].y
                cgz += volumes[i] * cgs[i].z

            # Divide by total volume
            cgx /= volume
            cgy /= volume
            cgz /= volume

            cb = Point3D(cgx, cgy, cgz)

            displacement = volume * 1000  # Assuming density of water is 1000 kg/m³
            diff = weight - displacement
            if abs(diff) > 1:  # assume a tolerance of 0.1 kg in the calculation
                increment = (
                    diff / weight * waterline
                )  # Adjust waterline proportionally to the difference in weight
                waterline += increment  # add the increment to the waterline to try to match the target weight
            else:
                break

        # If we exited due to bounds or iterations, raise an exception
        if not locals().get("cb"):
            if iteration >= max_iterations:
                raise WaterlineCalculationError(
                    f"Waterline calculation did not converge after "
                    f"{max_iterations} iterations. Target weight: "
                    f"{weight:.1f}kg, Hull volume: {self.volume:.4f}m³, "
                    f"Maximum displacement at full depth: "
                    f"{self.volume * 1000:.1f}kg. The target weight may "
                    f"exceed the hull's buoyancy capacity."
                )
            elif waterline <= 0 or waterline > self.depth():
                max_displacement = self.volume * 1000
                raise WaterlineCalculationError(
                    f"Waterline calculation went out of bounds "
                    f"(waterline: {waterline:.3f}m, "
                    f"depth: {self.depth():.3f}m). Target weight: "
                    f"{weight:.1f}kg, Maximum possible displacement: "
                    f"{max_displacement:.1f}kg. The hull geometry cannot "
                    f"support the requested weight."
                )

        return waterline, cb, displacement

    def _get_points_below_waterline(self, points: list[Point3D], waterline: float) -> list[Point3D]:
        """Get points below the waterline, including intersection points.

        Points must first be sorted in circular order around their centroid
        before calculating waterline intersections.
        """
        if len(points) < 3:
            return []

        # Sort points in circular order around centroid (same as Profile.sort_points)
        cy = sum(p.y for p in points) / len(points)
        cz = sum(p.z for p in points) / len(points)
        sorted_points = sorted(points, key=lambda p: np.arctan2(p.z - cz, p.y - cy))

        below_points = []
        n = len(sorted_points)

        for i in range(n):
            p1 = sorted_points[i]
            p2 = sorted_points[(i + 1) % n]  # Next point (wrap around)

            if p1.z <= waterline:
                below_points.append(p1)

            # Check if edge crosses waterline
            if (p1.z < waterline < p2.z) or (p2.z < waterline < p1.z):
                # Edge crosses the waterline, find intersection
                t = (waterline - p1.z) / (p2.z - p1.z)
                intersect_y = p1.y + t * (p2.y - p1.y)
                below_points.append(Point3D(p1.x, intersect_y, waterline))

        return below_points


def read_file(file_path: str) -> dict:
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


# def export_profile_for_visualization(profiles: list, output_file: str):
#     """Export profile data in format suitable for HTML visualization"""
#     export_profiles = [{
#             "station": profile.station,
#             "center": {
#                 "x": profile.center.x,
#                 "y": profile.center.y,
#                 "z": profile.center.z
#             },
#             "data_points": [
#                 {"x": p.x, "y": p.y, "z": p.z} for p in profile.data_points
#             ],
#             "points": [
#                 {"x": p.x, "y": p.y, "z": p.z} for p in profile.points
#             ]
#         } for profile in profiles]

#     export_data = {
#         "profiles": export_profiles
#         }

#     with open(output_file, 'w') as f:
#         json.dump(export_data, f, indent=2)

#     print(f"Profile data exported to {output_file}")
#     return export_data

if __name__ == "__main__":
    file_path = "data/k01.json"
    data = read_file(file_path)
    # pprint(data)

    hull = Hull()
    hull.build(data)
    print(f"Hull Name: {hull.name}")
    print(f"Hull Description: {hull.description}")
    print(f"Hull Target Waterline: {hull.target_waterline}")
    print(f"Hull Target Weight: {hull.target_weight}")
    print(f"Hull Target Payload: {hull.target_payload}")
    print(f"Hull Length: {hull.length():.3f} m")
    print(f"Hull Beam: {hull.beam():.3f} m")
    print(f"Hull Depth: {hull.depth():.3f} m")
    print(f"Hull Volume: {hull.volume:.6f} m³")
    print(f"Hull Center of Gravity: {hull.cg}")
    print(f"Hull Waterline: {hull.waterline:.3f} m")
    print(f"Hull Center of Buoyancy: {hull.cb}")
    print(f"Hull Displacement: {hull.displacement:.2f} kg")

    # print(json.dumps(hull.as_dict(), indent=2))

    # profile = hull.profiles

    # # Export for visualization
    # export_profile_for_visualization(hull.profiles, 'src/research/profile_export.json')
    # print(f"Hull Volume: {hull.volume:.4f}, Center of Gravity: {hull.cg} ")
    # print("\nTo visualize, open src/research/profile_visualizer.html in a browser")
