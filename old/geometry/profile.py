import numpy as np
from typing import List
from src.geometry.point import Point3D


class Profile:

    station: float = 0.0   
    points: List[Point3D] = []
    data_points: List[Point3D] = []
    
    def __init__(self, station: float = 0.0):
        self.station = station
        self.points = []
        self.data_points = []
    
    def add_point(self, x: float, y: float, z: float):
        self.data_points.append(Point3D(x, y, z))
        
    def get_points(self) -> List[Point3D]:
        return self.data_points
    
    def to_json(self) -> str:
        points_list = [{"x": p.x, "y": p.y, "z": p.z} for p in self.data_points]
        return {"points": points_list}
    
    def sort_points(self):
        if not self.data_points:
            return
        self.data_points.sort(key=lambda p: (p.z, -p.y, p.x), reverse=True)

    def auto_complete_starboard(self):
        if not self.data_points:
            return
        st_points = []
        for pt in reversed(self.data_points):
            if pt.y != 0.0:
                st_points.append(Point3D(pt.x, -pt.y, pt.z))
        
        self.data_points.extend(st_points)
        
    def auto_complete_circular(self):
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
        
        # Calculate center of mass
        sum_y = sum(pt.y for pt in self.data_points)
        sum_z = sum(pt.z for pt in self.data_points)
        n     = len(self.data_points) 
        center_y = sum_y / n
        center_z = sum_z / n
        angle = np.radians(90.0)   # Start from vertical up
        increment = np.radians(3.0)    # 3 degree increments
       
        
        for side in range(0, 360 // 3): 
            # we should break at first instersection because a center ray can not intersect multiple times
            for i in range(len(self.data_points)-1):
                p1 = self.data_points[i]
                p2 = self.data_points[i+1]
                # Calulate intersection of ray from center at angle with line segment p1-p2
                
                dy = p2.y - p1.y
                dz = p2.z - p1.z
                if dy == 0 and dz == 0:
                    continue
                # Line segment parametric equations
                def line_y(t): return p1.y + t * dy
                def line_z(t): return p1.z + t * dz
                
                # Solve for intersection
                denom = dy * np.cos(angle) + dz * np.sin(angle)
                if denom == 0:
                    continue
                t = ((center_y - p1.y) * np.cos(angle) + (center_z - p1.z) * np.sin(angle)) / denom 
                if 0.0 <= t <= 1.0:
                    intersect_y = line_y(t)
                    intersect_z = line_z(t)

                    self.points.append(Point3D(self.station, intersect_y, intersect_z))
                    break
                
            angle += increment