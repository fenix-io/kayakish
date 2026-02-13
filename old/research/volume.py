"""
Volume calculation utilities for research purposes.
"""

import numpy as np
from typing import Tuple
from src.model.profile import Profile
from src.model.point import Point3D
from src.geometry.volume import tetrahedron_volume, slice_volume

def _calculate_volume_and_cg(profile_1: Profile, profile_2: Profile) -> Tuple[np.float64, Point3D]:
    # This function will calculate the volumen and center of gravity of the volume between two profiles at a given waterline.
    st_points = profile_1.points
    st_cg = profile_1.center
    
    end_points = profile_2.points
    end_cg = profile_2.center
    
    count = len(st_points)
    volumes = []
    cgs = []
    full_volume = 0.0
    for i in range(count - 1):
        j = (i + 1) % count
        points = []
        points.append( end_cg)
        points.append( end_points[i])
        points.append( end_points[j])
        
        points.append( st_cg)
        points.append( st_points[i]), 
        points.append( st_points[j])

        volume, cg = slice_volume(points)
        volumes.append(volume) 
        cgs.append(cg)
        full_volume += volume
    
    cgx = 0.0
    cgy = 0.0
    cgz = 0.0   
    for i in range(count - 1):
        cgx = (volumes[i] * cgs[i].x) / full_volume
        cgy = (volumes[i] * cgs[i].y) / full_volume
        cgz = (volumes[i] * cgs[i].z) / full_volume

    return full_volume, Point3D(cgx, cgy, cgz)    
        
        
if __name__ == "__main__":
    # Example usage
    points = []
    
    points.append( Point3D(20, 0, 0))
    points.append( Point3D(20, 10, 0))
    points.append( Point3D(20, 10, 4))
    
    points.append( Point3D(0, 0, 0))
    points.append( Point3D(0, 10, 0)), 
    points.append( Point3D(0, 10, 4))
    
    volume, cg = slice_volume(points)
    print(f"Total Volume: {volume:.4f}, Centroid: {cg} ")