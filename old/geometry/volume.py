"""
Volume calculation utilities for research purposes.
"""

import numpy as np
from typing import Tuple
from src.model.profile import Profile
from src.model.point import Point3D

def tetrahedron_volume(
    p0: Tuple[np.float64, np.float64, np.float64],
    p1: Tuple[np.float64, np.float64, np.float64],
    p2: Tuple[np.float64, np.float64, np.float64],
    p3: Tuple[np.float64, np.float64, np.float64]
) -> Tuple[np.float64, Point3D]:
    """
    Calculate the volume of a tetrahedron defined by four 3D points.
    
    The volume is calculated using the scalar triple product formula:
    V = |det(B)| / 6
    
    Where B is a 3x3 matrix formed by the vectors from one vertex to the other three:
    v1 = p1 - p0
    v2 = p2 - p0
    v3 = p3 - p0
    
    Args:
        p0: First point (x, y, z) - reference vertex
        p1: Second point (x, y, z)
        p2: Third point (x, y, z)
        p3: Fourth point (x, y, z)
    
    Returns:
        Volume of the tetrahedron in cubic units
    
    Example:
        >>> p0 = (0, 0, 0)
        >>> p1 = (1, 0, 0)
        >>> p2 = (0, 1, 0)
        >>> p3 = (0, 0, 1)
        >>> volume = tetrahedron_volume(p0, p1, p2, p3)
        >>> print(f"{volume:.4f}")  # Should be 1/6 ≈ 0.1667
        0.1667
    """
    cg = Point3D((p0[0] + p1[0] + p2[0] + p3[0])/4.0, (p0[1] + p1[1] + p2[1] + p3[1])/4.0, (p0[2] + p1[2] + p2[2] + p3[2])/4.0)  # Centroid of the tetrahedron
    
    # Convert points to numpy arrays
    p0 = np.array(p0)
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)
    
    # Create vectors from p0 to the other three points
    v1 = p1 - p0
    v2 = p2 - p0
    v3 = p3 - p0
    
    # Create matrix with vectors as columns and calculate determinant
    # The volume is the absolute value of det divided by 6
    matrix = np.column_stack([v1, v2, v3])
    det = np.linalg.det(matrix)
    
    volume = abs(det) / 6.0
    
    return volume, cg

def slice_volume(points: list)->Tuple[np.float64, Point3D]:
    # Example usage
    p0 = (points[0].x, points[0].y, points[0].z)
    p1 = (points[1].x, points[1].y, points[1].z)
    p2 = (points[2].x, points[2].y, points[2].z)   
    
    p3 = (points[3].x, points[3].y, points[3].z)
    p4 = (points[4].x, points[4].y, points[4].z)
    p5 = (points[5].x, points[5].y, points[5].z)
    
    v1, cg1 = tetrahedron_volume(p0, p1, p2, p3)
    print(f"Tetrahedron Volume: {v1:.4f}, {cg1}") 
    
    v2, cg2 = tetrahedron_volume(p1, p2, p3, p4)
    print(f"Tetrahedron Volume: {v2:.4f}, {cg2}") 

    v3, cg3 = tetrahedron_volume(p2, p3, p4, p5)
    print(f"Tetrahedron Volume: {v3:.4f}, {cg3}") 

    volume = v1 + v2 + v3
    cgx = ((v1 * cg1.x) + (v2 * cg2.x) + (v3 * cg3.x)) / volume
    cgy = ((v1 * cg1.y) + (v2 * cg2.y) + (v3 * cg3.y)) / volume
    cgz = ((v1 * cg1.z) + (v2 * cg2.z) + (v3 * cg3.z)) / volume
    
    return volume, Point3D(cgx, cgy, cgz)

def calculate_volume_and_cg_between_profiles(profile_1: Profile, profile_2: Profile) -> Tuple[np.float64, Point3D]:
    # This function will calculate the volumen and center of gravity of the volume between two profiles at a given waterline.
    st_points = profile_1.points
    st_cg = profile_1.center
    
    end_points = profile_2.points
    end_cg = profile_2.center
    
    count = len(st_points)
    volumes = []
    cgs = []
    volume = 0.0
    for i in range(count):
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
    
    volume = sum(volumes)
    
    cgx = 0.0
    cgy = 0.0
    cgz = 0.0   
    for i in range(count):
        cgx += (volumes[i] * cgs[i].x)
        cgy += (volumes[i] * cgs[i].y)
        cgz += (volumes[i] * cgs[i].z)
    
    # Divide by total volume
    cgx /= volume
    cgy /= volume
    cgz /= volume

    return volume, Point3D(cgx, cgy, cgz)    

def calculate_volume_and_cg_between_profile_and_tip(profile_1: Profile, tip_offset:float, tip_depth: float) -> Tuple[np.float64, Point3D]:
    # This function will calculate the volumen and center of gravity of the volume between a profiles a tip
    st_points = profile_1.points
    st_cg = profile_1.center
    
    count = len(st_points)
    volumes = []
    cgs = []
    volume = 0.0
    for i in range(count):
        j = (i + 1) % count
        p0 = (tip_offset, 0, tip_depth)
        p1 = (st_points[i].x, 0, st_cg.z)
        p2 = (st_points[i].x, st_points[i].y, st_points[i].z)
        p3 = (st_points[j].x, st_points[j].y, st_points[j].z)
        vi, cgi = tetrahedron_volume(p0, p1, p2, p3)
        
        volumes.append(vi)
        cgs.append(cgi) 

    volume = sum(volumes)
    cgx = 0.0
    cgy = 0.0
    cgz = 0.0   
    for i in range(count):
        cgx += (volumes[i] * cgs[i].x)
        cgy += (volumes[i] * cgs[i].y)
        cgz += (volumes[i] * cgs[i].z)
    
    # Divide by total volume
    cgx /= volume
    cgy /= volume
    cgz /= volume

    return volume, Point3D(cgx, cgy, cgz)    

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