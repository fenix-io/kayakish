"""
KayakHull class for defining and managing kayak hull geometry.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel

class YZPointModel(BaseModel):
    y: float
    z: float

class ProfileModel(BaseModel):
    station: float
    port_points: List[YZPoint] 

class MetadataModel(BaseModel):
    name: str
    description: str | None = None
    units:  str | None = "metric"
    target_waterline: float | None = None
    target_payload: float | None = None

class HullModel(BaseModel):
    metadata: MetadataModel | None = None
    profiles: List[ProfileModel] = [] 
    file_name: str | None = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "metadata" : {
                        "name": "Kayak 001",
                        "description": "Kayak 001",
                        "units": "metric",
                        "target_waterline": 0.1,
                        "target_payload": 100.0
                    },
                    "profiles": [
                        {
                            "station": 0.0,
                            "port_points": [
                                {"y": 0.0, "z": 0.30}
                            ]
                        },
                        {
                            "station": 1.0,
                            "port_points": [
                                {"y": 0.00, "z": 0.30},
                                {"y": 0.18, "z": 0.28},
                                {"y": 0.12, "z": 0.15},
                                {"y": 0.09, "z": 0.05},
                                {"y": 0.00, "z": 0.00}
                            ]
                        },
                        {
                            "station": 3.0,
                            "port_points": [
                                {"y": 0.00, "z": 0.30},
                                {"y": 0.30, "z": 0.28},
                                {"y": 0.20, "z": 0.15},
                                {"y": 0.15, "z": 0.05},
                                {"y": 0.00, "z": 0.00}
                            ]
                        },
                        {
                            "station": 4.0,
                            "port_points": [
                                {"y": 0.00, "z": 0.35},
                                {"y": 0.28, "z": 0.28},
                                {"y": 0.18, "z": 0.15},
                                {"y": 0.12, "z": 0.05},
                                {"y": 0.00, "z": 0.00}
                            ]
                        },
                        {
                            "station": 5.0,
                            "port_points": [
                                {"y": 0.0, "z": 0.30}
                            ]
                        }                        
                    ]
                }
            ]
        }
    }

    
