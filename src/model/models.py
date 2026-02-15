"""
KayakHull class for defining and managing kayak hull geometry.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field


class CurveModel(BaseModel):
    name: str
    mirrored: bool | None = False
    points: List[Tuple[float, float, float]]


class ProfileModel(BaseModel):
    station: float = 0.0
    points: List[Tuple[float, float, float]] = Field(default_factory=list)


class CreateHullModel(BaseModel):
    name: str
    description: str | None = None
    target_waterline: float | None = None
    target_payload: float | None = None
    target_weight: float | None = None
    curves: List[CurveModel] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Kayak 001",
                    "description": "Kayak 001",
                    "target_waterline": 0.1,
                    "target_payload": 90.0,
                    "target_weight": 10.0,
                    "curves": [
                        {
                            "name": "starboard gunnel",
                            "points": [
                                [0.00, 0.00, 0.30],
                                [1.00, 0.18, 0.28],
                                [2.00, 0.30, 0.28],
                                [3.00, 0.30, 0.28],
                                [4.00, 0.14, 0.28],
                                [5.00, 0.00, 0.30],
                            ],
                        },
                        {
                            "name": "starboard chime",
                            "points": [
                                [0.20, 0.00, 0.16],
                                [1.00, 0.12, 0.12],
                                [2.00, 0.22, 0.11],
                                [3.00, 0.22, 0.11],
                                [4.00, 0.10, 0.12],
                                [4.70, 0.00, 0.16],
                            ],
                        },
                        {
                            "name": "keel",
                            "points": [
                                [0.00, 0.00, 0.30],
                                [0.20, 0.00, 0.16],
                                [0.50, 0.00, 0.00],
                                [4.20, 0.00, 0.00],
                                [4.70, 0.00, 0.16],
                                [5.00, 0.00, 0.30],
                            ],
                        },
                    ],
                }
            ]
        }
    }


class HullSummaryModel(BaseModel):
    name: str | None = None
    description: str | None = None
    length: float | None = None
    beam: float | None = None
    depth: float | None = None
    volume: float | None = None
    waterline: float | None = None
    displacement: float | None = None


class HullModel(BaseModel):
    name: str | None = None
    description: str | None = None
    target_waterline: float | None = None
    target_payload: float | None = None
    target_weight: float | None = None
    curves: List[CurveModel] = Field(default_factory=list)
    file_name: str | None = None
    length: float | None = None
    beam: float | None = None
    depth: float | None = None
    volume: float | None = None
    cg: Tuple[float, float, float] | None = None
    cb: Tuple[float, float, float] | None = None
    waterline: float | None = None
    displacement: float | None = None
    profiles: List[ProfileModel] = Field(default_factory=list)
    min_x: float | None = None
    max_x: float | None = None
    min_y: float | None = None
    max_y: float | None = None
    min_z: float | None = None
    max_z: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Kayak 001",
                    "description": "Kayak 001",
                    "target_waterline": 0.1,
                    "target_payload": 90.0,
                    "target_weight": 10.0,
                    "length": 5.000,
                    "beam": 0.600,
                    "depth": 0.300,
                    "volume": 0.339441,
                    "cg": [2.431, 0.000, 0.175],
                    "waterline": 0.134,
                    "cb": [2.439, -0.000, 0.089],
                    "displacement": 100.91,
                    "file_name": "kayak001",
                    "min_x": 0.000,
                    "max_x": 5.000,
                    "min_y": -0.300,
                    "max_y": 0.300,
                    "min_z": 0.000,
                    "max_z": 0.300,
                    "curves": [
                        {
                            "name": "starboard gunnel",
                            "points": [
                                [0.00, 0.00, 0.30],
                                [1.00, 0.18, 0.28],
                                [2.00, 0.30, 0.28],
                                [3.00, 0.30, 0.28],
                                [4.00, 0.14, 0.28],
                                [5.00, 0.00, 0.30],
                            ],
                        },
                        {
                            "name": "starboard chime",
                            "points": [
                                [0.20, 0.00, 0.16],
                                [1.00, 0.12, 0.12],
                                [2.00, 0.22, 0.11],
                                [3.00, 0.22, 0.11],
                                [4.00, 0.10, 0.12],
                                [4.70, 0.00, 0.16],
                            ],
                        },
                        {
                            "name": "keel",
                            "points": [
                                [0.00, 0.00, 0.30],
                                [0.20, 0.00, 0.16],
                                [0.50, 0.00, 0.00],
                                [4.20, 0.00, 0.00],
                                [4.70, 0.00, 0.16],
                                [5.00, 0.00, 0.30],
                            ],
                        },
                    ],
                    "profiles": [],
                }
            ]
        }
    }


class StabilityPointModel(BaseModel):
    angle: float | None = None
    gz: float | None = None
    moment: float | None = None
    waterline: float | None = None
    displacement: float | None = None


class StabilityAnalysisResultModel(BaseModel):
    vanishing_angle: float | None = None
    max_moment: float | None = None
    max_moment_angle: float | None = None
    stability_points: List[StabilityPointModel] = Field(default_factory=list)


class StabilityAnalysisModel(BaseModel):
    hull_name: str
    paddler_weight: float | None = None
    paddler_cg_z: float = 0.25
    hull_weight: float | None = None
    max_angle: float = 90
    step: float = 3
    break_on_vanishing: bool = False
