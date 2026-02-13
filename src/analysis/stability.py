import numpy as np
from src.geometry.hull import Hull, read_file
from src.geometry.point import Point3D

def create_stability_curve(weights: list[float], hull: Hull) -> list[tuple[float, float, float]]:
    """Calculate stability curve points for a range of weights.
    
    Args:
        weights: List of weights to evaluate (in kg)
        hull: The Hull object to analyze"""
    stability_points = []
    angle_degrees = -3.0
    weight = sum(weights)
    for step in range(3, 87, 3):
        print(f"\nCalculando estabilidad para peso total: {weight:.2f} kg, ángulo: {angle_degrees:.1f}°")
        angle =np.radians(angle_degrees)
        waterline, cb, displacement = hull._calculate_waterline(weight, angle=angle_degrees)
        cbz = (hull.cg.z - hull.cb.z) * np.cos(angle)
        cby = (hull.cg.z - hull.cb.z) * np.sin(angle) 
        metacenter_x = hull.cg.x
        metacenter_y = cb.y
        metacenter_z = -(cbz + cb.y) / np.tan(angle)  # Vertical distance from CB to metacenter
        metacenter = Point3D(metacenter_x, metacenter_y, metacenter_z)
        keel_x = hull.cg.x
        keel_y = -hull.cg.z * np.sin(angle)  # Adjust keel y position based on angle
        keel_z = hull.cg.z - (hull.cg.z * np.cos(angle))   # Adjust keel z position based on angle
        
        keel = Point3D(keel_x, keel_y, keel_z)
        km = keel.distance_to(metacenter)
        gm = hull.cg.distance_to(metacenter)
        stability_points.append((angle_degrees, km, gm, km-gm))
        if km< gm:
            print(f"¡Inestabilidad detectada! KM ({km:.3f} m) es menor que GM ({gm:.3f} m)")
            break
        angle_degrees -= 3.0  # Increment angle for next point (simulate tilting the hull)
        
    return stability_points


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
    
    stability_curve = create_stability_curve([hull.target_weight, hull.target_payload], hull)
    print("\nStability Curve (Angle, KM, GM, KM-GM):", stability_curve)