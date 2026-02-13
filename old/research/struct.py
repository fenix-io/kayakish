import json
from pprint import pprint
import numpy as np
from typing import List
from src.geometry.point import Point3D

class Profile:
    max_depth: float = -999999999
    min_depth: float = 999999999 
    center: Point3D
    station: float = 0.0   
    points: List[Point3D] = []
    data_points: List[Point3D] = []
    
    def __init__(self):
        self.station = 0
        self.min_depth = 999999999
        self.max_depth = -999999999
        self.center = Point3D(0.0, 0.0, 0.0)
        self.points = []
        self.data_points = []

    def initialize(self, data: dict):
        self.station = data.get("station", 0.0)
        for pt in data.get("port_points", []):
            self.min_depth = min(self.min_depth, pt[1])
            self.max_depth = max(self.max_depth, pt[1])
            self._add_point(self.station, pt[0], pt[1])
        self.center = Point3D(self.station, 0.0, (self.min_depth + self.max_depth) / 2)
        self.data_points.sort(key=lambda p: (p.z, -p.y, p.x), reverse=True)
        self._auto_complete_full_semi_circle()    

    def _add_point(self, x: float, y: float, z: float):
        self.data_points.append(Point3D(x, y, z))

    def as_dict(self):
        return self.__dict__
    
    def _auto_complete_full_semi_circle(self):
        """ This function calaculate the mass center of the profile,
        the radius from the center each 3 degrees, starting from the vertical up,
        and then find the points around the circle at each 3 degree interval 
        where they intersect the profile lines.
        """
        if not self.data_points:
            return
        if len(self.data_points) <= 1:
            return
        self.points = []
        
        tolerance = 0.00001
        deg_increment = 3.0    # 3 degree increments
        deg_current = 90.0
        # Calculate center of mass
           # Start from vertical up
        increment = np.radians(deg_increment)    # 3 degree increments
        num_steps = int(180 / deg_increment) + 1
        center_y = self.center.y
        center_z = self.center.z
        
        data_points = []
        points = []
        for i in range(len(self.data_points)):
            data_points.append(Point3D(self.data_points[i].x, self.data_points[i].y, self.data_points[i].z - center_z)) 
        
        for step in range(0, num_steps):
            if deg_current == 90:
                y = data_points[0].y
                z = data_points[0].z
                points.append(Point3D(np.round(self.station, 3), np.round(y, 3), np.round(z + center_z, 3)))
            elif deg_current == -90:
                y = data_points[-1].y
                z = data_points[-1].z
                points.append(Point3D(np.round(self.station, 3), np.round(y, 3), np.round(z + center_z, 3)))
            else:
                angle = np.radians(deg_current)
                m1 = np.tan(angle)  # slope of the ray from center
                # we should break at first instersection because a center ray can not intersect multiple times
                for i in range(len(data_points)-1):
                    p1 = data_points[i]
                    p2 = data_points[i+1]

                    m2 = (p2.z - p1.z) / (p2.y - p1.y) if (p2.y - p1.y) != 0 else None 
                    if m2 is not None:
                        b2 = p1.z - m2 * p1.y
                        intersect_y = b2 / (m1 - m2)
                        if abs(deg_current) == 90 and abs(intersect_y) < tolerance:
                            intersect_y = 0
                        intersect_z = m1 * intersect_y
                    else:
                        intersect_y = p1.y
                        intersect_z = m1 * intersect_y
                    
                    # Check if intersection is within segment bounds
                    if (min(p1.y, p2.y) - tolerance <= intersect_y <= max(p1.y, p2.y) + tolerance) and (min(p1.z, p2.z) -tolerance <= intersect_z <= max(p1.z, p2.z) + tolerance):
                        points.append(Point3D(np.round(self.station, 3), np.round(intersect_y, 3), np.round(intersect_z + center_z, 3)))
                        break

                
            deg_current -= deg_increment

        for pt in points:
            self.points.append(pt)
        for pt in reversed(points):
            if np.abs(pt.y) > tolerance:
                self.points.append(Point3D(pt.x, -pt.y, pt.z))

class Hull:
    name: str
    description: str | None = None
    units:  str | None = "metric"
    target_waterline: float | None = None
    target_payload: float | None = None
    profiles: list[Profile]
    stern_tip_depth: float 
    bow_tip_depth: float
    length: float
    
    def __init__(self):
        self.stern_tip_depth = 0.25
        self.bow_tip_depth = 0.25
        self.length = 5.00
    
    def _add_profile(self, profile: Profile):
        if not hasattr(self, 'profiles'):
            self.profiles = []
        self.profiles.append(profile)

    def as_dict(self):
        return self.__dict__

    def initialize(self, data: dict):
        self.name = data.get("metadata", {}).get("name", "KAYAK HULL")
        self.description = data.get("metadata", {}).get("description", "KAYAK HULL")
        self.units = data.get("metadata", {}).get("units", "metric")
        self.target_waterline = data.get("metadata", {}).get("target_waterline", 0.1)
        self.target_payload = data.get("metadata", {}).get("target_payload", 100)
        self.stern_tip_depth = data.get("stern_tip_depth", 0.25)
        self.bow_tip_depth = data.get("bow_tip_depth", 0.25)
        self.length = data.get("length", 5.00)

        for profile_data in data.get("profiles", []):
            profile = Profile()
            profile.initialize(profile_data)
            self._add_profile(profile)  


def read_file(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def export_profile_for_visualization(profiles: list, output_file: str):
    """Export profile data in format suitable for HTML visualization"""
    export_profiles = [{
            "station": profile.station,
            "center": {
                "x": profile.center.x,
                "y": profile.center.y,
                "z": profile.center.z
            },
            "data_points": [
                {"x": p.x, "y": p.y, "z": p.z} for p in profile.data_points
            ],
            "points": [
                {"x": p.x, "y": p.y, "z": p.z} for p in profile.points
            ]
        } for profile in profiles]
    
    export_data = { 
        "profiles": export_profiles}
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"Profile data exported to {output_file}")
    return export_data

if __name__ == "__main__":
    file_path = 'src/research/struct.json'
    data = read_file(file_path)
    # pprint(data)

    hull = Hull()
    hull.initialize(data)    
    
    profile = hull.profiles
    
    # Export for visualization
    export_profile_for_visualization(hull.profiles, 'src/research/profile_export.json')
    print("\nTo visualize, open src/research/profile_visualizer.html in a browser")