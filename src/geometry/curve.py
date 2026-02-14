
from typing import List
from src.geometry.point import Point3D
from src.geometry.spline import Spline3D

class Curve(Spline3D):
    def __init__(self, name: str, points: List[Point3D], bc_type='natural', parametrization='auto', mirrored=False):
        super().__init__(name, points, bc_type, parametrization)
        self.mirrored = mirrored  # Indicates if this curve is a mirrored version of another curve
        