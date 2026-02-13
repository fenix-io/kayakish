from src.model.model import Hull
from .profile import Profile
class PreparedHull:
    name: str
    description: str | None = None
    units:  str | None = "metric"
    target_waterline: float | None = None
    target_payload: float | None = None
    profiles: list[Profile]
    
    def add_profile(self, profile: Profile):
        if not hasattr(self, 'profiles'):
            self.profiles = []
        self.profiles.append(profile)

    def to_json(self):
        return PreparedHull()

def prepare_hull(hull: Hull):
    # Dummy implementation of hull preparation
    prep = PreparedHull()
    
    for profile in hull.profiles:
        target_profile = Profile(station=profile.station)
        for pt in profile.port_points:
            target_profile.add_point(profile.station, pt.y, pt.z)
        target_profile.sort_points()
        target_profile.auto_complete_starboard()
        target_profile.auto_complete_circular()
        prep.add_profile(target_profile)
    
    prep.name = hull.metadata.name
    prep.description = hull.metadata.description
    prep.units = hull.metadata.units
    prep.target_waterline = hull.metadata.target_waterline
    prep.target_payload = hull.metadata.target_payload
    
    return prep