import json
from pprint import pprint
import numpy as np
from src.geometry.profile import Profile
from src.geometry.point import Point3D
from src.geometry.spline import Spline3D

class Hull:
    name: str
    description: str | None = None
    units:  str | None = "metric"
    target_waterline: float | None = None
    target_weight: float | None = None
    target_payload: float | None = None
    waterline: float | None = None

    curves: list[Spline3D] = []     
    # profiles: list[Profile] = []
    
    def __init__(self):
       pass
    
    def _add_spline(self, spline: Spline3D):
        self.curves.append(spline)

    def as_dict(self):
        return self.__dict__

    def length(self):
        return self.max_x - self.min_x

    def beam(self):
        return (self.max_y - self.min_y)
    
    def depth(self):
        return self.max_z - self.min_z

    def initialize(self, data: dict):
        self.name = data.get("metadata", {}).get("name", "KAYAK HULL")
        self.description = data.get("metadata", {}).get("description", "KAYAK HULL")
        self.units = data.get("metadata", {}).get("units", "metric")
        self.target_waterline = data.get("metadata", {}).get("target_waterline", 0.1)
        self.target_weight = data.get("metadata", {}).get("target_weight", 100)
        self.target_payload = data.get("metadata", {}).get("target_payload", 100)

        self.min_x = float('inf')
        self.max_x = float('-inf')
        self.min_y = float('inf')
        self.max_y = float('-inf')
        self.min_z = float('inf')
        self.max_z = float('-inf')

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

            spline = Spline3D(name, points)
            self._add_spline(spline)  
            if y != 0:
                for point in spline_data.get("points", []):
                    p = Point3D(point[0], -point[1], point[2])
                    self._update_min_max(p)
                    oposite.append(p)
                
                spline_oposite = Spline3D("opposite " + name, oposite)
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
        step = 0.01
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
            
        # Calculate total volume
        volume = sum(volumes)
        
        # Calculate weighted CG
        cgx = 0.0
        cgy = 0.0
        cgz = 0.0   
        for i in range(len(volumes)):
            cgx += (volumes[i] * cgs[i].x)
            cgy += (volumes[i] * cgs[i].y)
            cgz += (volumes[i] * cgs[i].z)
        
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

    def _get_points_at(self, x: float, ) -> list[Point3D]:
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
 
        while 0 < waterline and waterline <= self.depth():
            x = self.min_x
            step = 0.01
            profiles = []
            volumes = []
            cgs = []

            while x <= self.max_x:
                points = []
                for curve in self.curves:
                    if  angle != 0.0:
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
            
            # Calculate weighted CG
            cgx = 0.0
            cgy = 0.0
            cgz = 0.0   
            for i in range(len(volumes)):
                cgx += (volumes[i] * cgs[i].x)
                cgy += (volumes[i] * cgs[i].y)
                cgz += (volumes[i] * cgs[i].z)
            
            # Divide by total volume
            cgx /= volume
            cgy /= volume
            cgz /= volume
            
            cb = Point3D(cgx, cgy, cgz) 
            
            displacement = volume * 1000  # Assuming density of water is 1000 kg/m³
            diff = weight - displacement
            if abs(diff) > 1:  # assume a tolerance of 0.1 kg in the calculation
                increment = diff/weight * waterline # Adjust waterline proportionally to the difference in weight
                waterline += increment  # add the increment to the waterline to try to match the target weight 
            else: 
                break
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
    with open(file_path, 'r') as file:
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
    file_path = 'data/k01.json'
    data = read_file(file_path)
    # pprint(data)

    hull = Hull()
    hull.initialize(data)    
    print(f"Hull Name: {hull.name}")
    print(f"Hull Description: {hull.description}")
    print(f"Hull Units: {hull.units}")
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