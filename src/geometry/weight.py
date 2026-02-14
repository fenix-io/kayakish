import json
from pprint import pprint
import numpy as np


class Weight:
    weight: float = 0.0
    cg: tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    def __init__(self, weight: float = 0.0, cg: tuple[float, float, float] = (0.0, 0.0, 0.0)):
        self.weight = weight
        self.cg = cg
        
    def to_json(self) -> str:
        return json.dumps({
            "weight": self.weight,
            "cg": self.cg
        })