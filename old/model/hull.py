import json
from pprint import pprint
from src.model.profile import Profile
from src.model.point import Point3D
from src.geometry.volume import calculate_volume_and_cg_between_profiles, calculate_volume_and_cg_between_profile_and_tip

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
        stern_tip_depth = data.get("stern_tip_depth", None)
        if stern_tip_depth is not None:
            self.stern_tip_depth = stern_tip_depth
            self.has_stern_tip = True
        else:
            self.has_stern_tip = False
        bow_tip_depth = data.get("bow_tip_depth", None)
        if bow_tip_depth is not None:
            self.bow_tip_depth = bow_tip_depth
            self.has_bow_tip = True
        else:
            self.has_bow_tip = False
        self.length = data.get("length", 5.00)

        for profile_data in data.get("profiles", []):
            profile = Profile()
            profile.initialize(profile_data)
            self._add_profile(profile)  

        volumes = []
        cgs = []
        for i in range(len(self.profiles) - 1):
            volume, cg = calculate_volume_and_cg_between_profiles(self.profiles[i], self.profiles[i+1])
            volumes.append(volume)
            cgs.append(cg)
        if self.has_stern_tip:
            volume, cg = calculate_volume_and_cg_between_profile_and_tip(self.profiles[0], 0, self.stern_tip_depth)
            volumes.append(volume)
            cgs.append(cg)            
        if self.has_bow_tip:
            volume, cg = calculate_volume_and_cg_between_profile_and_tip(self.profiles[-1], self.length, self.bow_tip_depth)
            volumes.append(volume)
            cgs.append(cg)
            
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
        "profiles": export_profiles
        }
    
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
    print(f"Hull Volume: {hull.volume:.4f}, Center of Gravity: {hull.cg} ")
    print("\nTo visualize, open src/research/profile_visualizer.html in a browser")