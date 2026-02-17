import os
from typing import List
import numpy as np

from fastapi import APIRouter, HTTPException
from src.analysis.stability import create_stability_curve_points
from src.analysis.resistance import (
    calculate_resistance_curve,
    calculate_hull_speed,
    WATER_DENSITY_FRESH,
    WATER_DENSITY_SALT,
)
from src.analysis.hull_parameters import (
    calculate_block_coefficient,
    calculate_prismatic_coefficient,
    calculate_midship_coefficient,
    calculate_waterplane_coefficient,
)
from src.config import settings
from src.geometry.hull import Hull, WaterlineCalculationError
from src.model.models import (
    CreateHullModel,
    CurveModel,
    HullModel,
    HullSummaryModel,
    ProfileModel,
    ResistanceAnalysisModel,
    ResistanceAnalysisResultModel,
    ResistancePointModel,
    StabilityAnalysisModel,
    StabilityAnalysisResultModel,
    StabilityPointModel,
)
from src.utils.filename import sanitize_filename

router = APIRouter()


@router.get("/")
def hull_list() -> List[HullSummaryModel]:
    file_path = settings.data_path
    os.makedirs(file_path, exist_ok=True)
    # get the list of diles in path that ends with .hull
    hull_files = [f for f in file_path.iterdir() if f.is_file() and f.suffix == ".hull"]
    hulls = []
    for hull_file in hull_files:
        with open(hull_file, "r") as f:
            hull_data = f.read()
            hull_model = HullModel.model_validate_json(hull_data)
            hulls.append(
                HullSummaryModel(
                    name=hull_model.name,
                    description=hull_model.description,
                    length=round(hull_model.length, 2),
                    beam=round(hull_model.beam, 2),
                    depth=round(hull_model.depth, 2),
                    volume=round(hull_model.volume, 2),
                    waterline=round(hull_model.waterline, 2),
                    displacement=round(hull_model.displacement, 2),
                )
            )
    # Sort hulls by name alphabetically
    hulls.sort(key=lambda h: h.name.lower() if h.name else "")
    return hulls


@router.get("/{hull_name}")
def get_hull(hull_name: str) -> HullModel:
    safe_filename = sanitize_filename(hull_name)
    file_path = settings.data_path
    os.makedirs(file_path, exist_ok=True)
    file_path = file_path / f"{safe_filename}.hull"
    with open(file_path, "r") as f:
        hull_data = f.read()
        hull_model = HullModel.model_validate_json(hull_data)
    return hull_model


@router.post("/")
def create_hull(hull_model: CreateHullModel) -> HullModel:
    safe_filename = sanitize_filename(hull_model.name)
    file_path = settings.data_path / f"{safe_filename}.hull"
    # prep_file_path = Path("data") / f"{safe_filename}_ready.json"

    if file_path.is_file():
        raise HTTPException(status_code=409, detail="A hull with this name already exists.")
    else:
        hull = Hull()
        try:
            hull.build(hull_model.model_dump())
        except WaterlineCalculationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        # print(f"Hull Name: {hull.name}")
        # print(f"Hull Description: {hull.description}")
        # print(f"Hull Target Waterline: {hull.target_waterline}")
        # print(f"Hull Target Weight: {hull.target_weight}")
        # print(f"Hull Target Payload: {hull.target_payload}")
        # print(f"Hull Length: {hull.length():.3f} m")
        # print(f"Hull Beam: {hull.beam():.3f} m")
        # print(f"Hull Depth: {hull.depth():.3f} m")
        # print(f"Hull Volume: {hull.volume:.6f} m³")
        # print(f"Hull Center of Gravity: {hull.cg}")
        # print(f"Hull Waterline: {hull.waterline:.3f} m")
        # print(f"Hull Center of Buoyancy: {hull.cb}")
        # print(f"Hull Displacement: {hull.displacement:.2f} kg")

        result = HullModel()
        result.name = hull.name
        result.description = hull.description
        result.target_waterline = hull.target_waterline
        result.target_weight = hull.target_weight
        result.target_payload = hull.target_payload
        result.length = hull.length()
        result.beam = hull.beam()
        result.depth = hull.depth()
        result.volume = hull.volume
        result.cg = (hull.cg.x, hull.cg.y, hull.cg.z) if hull.cg else None
        result.waterline = hull.waterline
        result.cb = (hull.cb.x, hull.cb.y, hull.cb.z) if hull.cb else None
        result.min_x = hull.min_x
        result.max_x = hull.max_x
        result.min_y = hull.min_y
        result.max_y = hull.max_y
        result.min_z = hull.min_z
        result.max_z = hull.max_z
        result.displacement = hull.displacement
        for curve in hull.curves:
            result.curves.append(
                CurveModel(
                    name=curve.name,
                    mirrored=curve.mirrored,
                    points=[(p.x, p.y, p.z) for p in curve.points],
                )
            )
        for profile in hull.profiles:
            result.profiles.append(
                ProfileModel(
                    station=profile.station, points=[(p.x, p.y, p.z) for p in profile.points]
                )
            )

        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(result.model_dump_json(indent=2))
    return result


@router.put("/{hull_name}")
def update_hull(hull_name: str, hull_model: CreateHullModel) -> HullModel:
    if hull_name != hull_model.name:
        # rename the existing file to the new name if it exists
        old_safe_filename = sanitize_filename(hull_name)
        old_file_path = settings.data_path / f"{old_safe_filename}.hull"
        new_safe_filename = sanitize_filename(hull_model.name)
        new_file_path = settings.data_path / f"{new_safe_filename}.hull"
        if old_file_path.is_file():
            old_file_path.rename(new_file_path)
        else:
            raise HTTPException(status_code=404, detail="Hull not found.")
        file_path = new_file_path
    else:
        file_path = settings.data_path / f"{sanitize_filename(hull_name)}.hull"
        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="Hull not found.")

    # prep_file_path = Path("data") / f"{safe_filename}_ready.json"
    hull = Hull()
    try:
        hull.build(hull_model.model_dump())
    except WaterlineCalculationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # print(f"Hull Name: {hull.name}")
    # print(f"Hull Description: {hull.description}")
    # print(f"Hull Target Waterline: {hull.target_waterline}")
    # print(f"Hull Target Weight: {hull.target_weight}")
    # print(f"Hull Target Payload: {hull.target_payload}")
    # print(f"Hull Length: {hull.length():.3f} m")
    # print(f"Hull Beam: {hull.beam():.3f} m")
    # print(f"Hull Depth: {hull.depth():.3f} m")
    # print(f"Hull Volume: {hull.volume:.6f} m³")
    # print(f"Hull Center of Gravity: {hull.cg}")
    # print(f"Hull Waterline: {hull.waterline:.3f} m")
    # print(f"Hull Center of Buoyancy: {hull.cb}")
    # print(f"Hull Displacement: {hull.displacement:.2f} kg")

    result = HullModel()
    result.name = hull.name
    result.description = hull.description
    result.target_waterline = hull.target_waterline
    result.target_weight = hull.target_weight
    result.target_payload = hull.target_payload
    result.length = hull.length()
    result.beam = hull.beam()
    result.depth = hull.depth()
    result.volume = hull.volume
    result.cg = (hull.cg.x, hull.cg.y, hull.cg.z) if hull.cg else None
    result.waterline = hull.waterline
    result.cb = (hull.cb.x, hull.cb.y, hull.cb.z) if hull.cb else None
    result.min_x = hull.min_x
    result.max_x = hull.max_x
    result.min_y = hull.min_y
    result.max_y = hull.max_y
    result.min_z = hull.min_z
    result.max_z = hull.max_z
    result.displacement = hull.displacement
    for curve in hull.curves:
        result.curves.append(
            CurveModel(
                name=curve.name,
                mirrored=curve.mirrored,
                points=[(p.x, p.y, p.z) for p in curve.points],
            )
        )
    for profile in hull.profiles:
        result.profiles.append(
            ProfileModel(station=profile.station, points=[(p.x, p.y, p.z) for p in profile.points])
        )

    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, "w") as f:
        f.write(result.model_dump_json(indent=2))

    return result


@router.delete("/{hull_name}")
def delete_hull(hull_name: str) -> HullModel:
    safe_filename = sanitize_filename(hull_name)
    file_path = settings.data_path
    os.makedirs(file_path, exist_ok=True)
    file_path = file_path / f"{safe_filename}.hull"
    # delete the file if it exists
    if file_path.is_file():
        file_path.unlink()
        return {"detail": "Hull deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Hull not found.")


@router.post("/{hull_name}/stability")
def calculate_hull_stability(
    stability_analysis: StabilityAnalysisModel,
) -> StabilityAnalysisResultModel:
    safe_filename = sanitize_filename(stability_analysis.hull_name)
    file_path = settings.data_path / f"{safe_filename}.hull"
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Hull not found.")
    with open(file_path, "r") as f:
        hull_data = f.read()
        hull_model = HullModel.model_validate_json(hull_data)
        hull = Hull()
        hull.initialize_from_data(hull_model.model_dump())
    vanishing_angle, max_moment, max_moment_angle, stability_points = create_stability_curve_points(
        hull,
        paddler_cg_z=stability_analysis.paddler_cg_z,
        paddler_weight=stability_analysis.paddler_weight,
        hull_weight=stability_analysis.hull_weight,
        max_angle=stability_analysis.max_angle,
        step=stability_analysis.step,
        break_on_vanishing=stability_analysis.break_on_vanishing,
    )
    result = StabilityAnalysisResultModel(
        vanishing_angle=vanishing_angle,
        max_moment=max_moment,
        max_moment_angle=max_moment_angle,
    )

    for point in stability_points:
        result.stability_points.append(
            StabilityPointModel(
                angle=point["angle"],
                gz=point["gz"],
                moment=point["moment"],
                waterline=point["waterline"],
                displacement=point["displacement"],
            )
        )

    return result


@router.post("/{hull_name}/resistance")
def calculate_hull_resistance(
    resistance_analysis: ResistanceAnalysisModel,
) -> ResistanceAnalysisResultModel:
    """Calculate resistance and performance characteristics for a hull.

    This endpoint computes:
    - Resistance vs speed curves (total, frictional, residuary)
    - Power requirements (effective and paddler power)
    - Hull form coefficients
    - Waterline dimensions and wetted surface area
    - Hull speed estimate

    Args:
        resistance_analysis: ResistanceAnalysisModel with analysis parameters

    Returns:
        ResistanceAnalysisResultModel with complete resistance analysis

    Raises:
        HTTPException: 404 if hull not found, 400 if parameters invalid
    """
    safe_filename = sanitize_filename(resistance_analysis.hull_name)
    file_path = settings.data_path / f"{safe_filename}.hull"

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Hull not found.")

    # Load hull
    with open(file_path, "r") as f:
        hull_data = f.read()
        hull_model = HullModel.model_validate_json(hull_data)
        hull = Hull()
        hull.initialize_from_data(hull_model.model_dump())

    # Validate parameters
    if resistance_analysis.min_speed < 0:
        raise HTTPException(status_code=400, detail="Minimum speed must be non-negative.")
    if resistance_analysis.max_speed <= resistance_analysis.min_speed:
        raise HTTPException(
            status_code=400,
            detail="Maximum speed must be greater than minimum speed.",
        )
    if resistance_analysis.speed_step <= 0:
        raise HTTPException(status_code=400, detail="Speed step must be positive.")
    if resistance_analysis.water_type not in ["fresh", "salt"]:
        raise HTTPException(status_code=400, detail="Water type must be 'fresh' or 'salt'.")
    if not (0 < resistance_analysis.propulsion_efficiency <= 1):
        raise HTTPException(
            status_code=400,
            detail="Propulsion efficiency must be between 0 and 1.",
        )

    # Calculate hull parameters
    waterline_length = hull.waterline_length()
    waterline_beam = hull.waterline_beam()
    wetted_surface = hull.wetted_surface_area()

    # Calculate hull form coefficients
    try:
        block_coeff = calculate_block_coefficient(hull)
        prismatic_coeff = calculate_prismatic_coefficient(hull)
        midship_coeff = calculate_midship_coefficient(hull)
        waterplane_coeff = calculate_waterplane_coefficient(hull)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to calculate hull form coefficients: {str(e)}",
        )

    # Calculate hull speed
    hull_speed_ms = calculate_hull_speed(waterline_length)
    hull_speed_kmh = hull_speed_ms * 3.6
    hull_speed_knots = hull_speed_ms * 1.94384

    # Generate speed range
    speed_range = np.arange(
        resistance_analysis.min_speed,
        resistance_analysis.max_speed + resistance_analysis.speed_step,
        resistance_analysis.speed_step,
    )

    # Select water density
    water_density = (
        WATER_DENSITY_SALT if resistance_analysis.water_type == "salt" else WATER_DENSITY_FRESH
    )

    # Calculate resistance curve
    resistance_results = calculate_resistance_curve(
        speed_range=speed_range.tolist(),
        waterline_length=waterline_length,
        wetted_surface=wetted_surface,
        prismatic_coefficient=prismatic_coeff,
        water_density=water_density,
        roughness_allowance=resistance_analysis.roughness_allowance,
        propulsion_efficiency=resistance_analysis.propulsion_efficiency,
    )

    # Build result
    result = ResistanceAnalysisResultModel(
        hull_speed_ms=hull_speed_ms,
        hull_speed_kmh=hull_speed_kmh,
        hull_speed_knots=hull_speed_knots,
        waterline_length=waterline_length,
        waterline_beam=waterline_beam,
        wetted_surface=wetted_surface,
        block_coefficient=block_coeff,
        prismatic_coefficient=prismatic_coeff,
        midship_coefficient=midship_coeff,
        waterplane_coefficient=waterplane_coeff,
    )

    # Convert resistance results to response models
    for res in resistance_results:
        point = ResistancePointModel(
            speed=res.speed,
            speed_kmh=res.speed * 3.6,
            speed_knots=res.speed * 1.94384,
            froude_number=res.froude_number,
            reynolds_number=res.reynolds_number,
            friction_coefficient=res.friction_coefficient,
            residuary_coefficient=res.residuary_coefficient,
            frictional_resistance=res.frictional_resistance,
            residuary_resistance=res.residuary_resistance,
            total_resistance=res.total_resistance,
            effective_power=res.effective_power,
            paddler_power=res.paddler_power,
        )
        result.resistance_points.append(point)

    return result
