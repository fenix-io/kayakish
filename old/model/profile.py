import json
from pprint import pprint
import numpy as np
from typing import List
from src.model.point import Point3D

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
        self.tolerance = 0.00001
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
        pts = reversed(self.data_points)
        for pt in pts:
            if np.abs(pt.y) > self.tolerance:
                self.data_points.append(Point3D(pt.x, -pt.y, pt.z))    

    def _add_point(self, x: float, y: float, z: float):
        self.data_points.append(Point3D(x, y, z))

    def as_dict(self):
        return self.__dict__
    
    def _auto_complete_full_semi_circle(self):
        """ This function calculate the mass center of the profile,
        the radius from the center each 3 degrees, starting from the vertical up,
        and then find the points around the circle at each 3 degree interval 
        where they intersect the profile lines.
        """
        if not self.data_points:
            return
        if len(self.data_points) <= 1:
            return
        self.points = []
        
        
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
                        if abs(deg_current) == 90 and abs(intersect_y) < self.tolerance:
                            intersect_y = 0
                        intersect_z = m1 * intersect_y
                    else:
                        intersect_y = p1.y
                        intersect_z = m1 * intersect_y
                    
                    # Check if intersection is within segment bounds
                    if (min(p1.y, p2.y) - self.tolerance <= intersect_y <= max(p1.y, p2.y) + self.tolerance) and (min(p1.z, p2.z) -self.tolerance <= intersect_z <= max(p1.z, p2.z) + self.tolerance):
                        points.append(Point3D(np.round(self.station, 3), np.round(intersect_y, 3), np.round(intersect_z + center_z, 3)))
                        break

            deg_current -= deg_increment

        for pt in points:
            self.points.append(pt)
            
        for pt in reversed(points):
            if np.abs(pt.y) > self.tolerance:
                self.points.append(Point3D(pt.x, -pt.y, pt.z))
        
    def get_data_points(self, center:Point3D, rotation:float, waterline:float) -> List[Point3D]:
        """ Get the profile points rotated around the center point by rotation angle (degrees),
        and shifted vertically to the waterline.
        """
        points = []
        temp = []
        for pt in self.data_points:
            # Shift to origin
            shifted_pt = Point3D(pt.x - center.x, pt.y - center.y, pt.z - center.z)
            # Rotate around Z axis
            rotated_pt = shifted_pt.rotate_z(rotation)
            # Shift back and apply waterline
            final_pt = Point3D(rotated_pt.x + center.x, rotated_pt.y + center.y, rotated_pt.z + center.z)
            temp.append(final_pt)
        
        for i in range(len(temp)):
            j = (i + 1) % len(temp)
            if temp[i].z <= waterline:
                points.append(temp[i])
                if temp[j].z > waterline:
                    # Interpolate to find intersection with waterline
                    t = (waterline - temp[i].z) / (temp[j].z - temp[i].z)
                    intersect_x = temp[i].x + t * (temp[j].x - temp[i].x)
                    intersect_y = temp[i].y + t * (temp[j].y - temp[i].y)
                    points.append(Point3D(intersect_x, intersect_y, waterline))
            else:
                if temp[j].z <= waterline:
                    # Interpolate to find intersection with waterline
                    t = (waterline - temp[i].z) / (temp[j].z - temp[i].z)
                    intersect_x = temp[i].x + t * (temp[j].x - temp[i].x)
                    intersect_y = temp[i].y + t * (temp[j].y - temp[i].y)
                    points.append(Point3D(intersect_x, intersect_y, waterline))

        return points
    
    def get_all_points(self, center:Point3D, rotation:float, waterline:float) -> List[Point3D]:
       
        points = self.get_data_points(center, rotation, waterline)
        if not points:
            return
        if len(points) <= 1:
            return
        points = []
        
        
        deg_increment = 3.0    # 3 degree increments
        deg_current = 90.0
        # Calculate center of mass
        # Start from vertical up
        increment = np.radians(deg_increment)    # 3 degree increments
        num_steps = int(180 / deg_increment) + 1
        center_y = center.y
        center_z = center.z
        
        data_points = []
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
                        if abs(deg_current) == 90 and abs(intersect_y) < self.tolerance:
                            intersect_y = 0
                        intersect_z = m1 * intersect_y
                    else:
                        intersect_y = p1.y
                        intersect_z = m1 * intersect_y
                    
                    # Check if intersection is within segment bounds
                    if (min(p1.y, p2.y) - self.tolerance <= intersect_y <= max(p1.y, p2.y) + self.tolerance) and (min(p1.z, p2.z) -self.tolerance <= intersect_z <= max(p1.z, p2.z) + self.tolerance):
                        points.append(Point3D(np.round(self.station, 3), np.round(intersect_y, 3), np.round(intersect_z + center_z, 3)))
                        break

            deg_current -= deg_increment

        for pt in points:
            self.points.append(pt)
            
        for pt in reversed(points):
            if np.abs(pt.y) > self.tolerance:
                self.points.append(Point3D(pt.x, -pt.y, pt.z))
