import os
from pathlib import Path
from typing import Union
from typing import List, Dict, Optional, Tuple

from fastapi import APIRouter, HTTPException
from src.analysis.stability import create_stability_curve_points
from src.config import settings
from src.geometry.hull import Hull
from src.model.models import CreateHullModel, CurveModel, HullModel, HullSummaryModel, ProfileModel, StabilityAnalysisModel, StabilityAnalysisResultModel, StabilityPointModel
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
        with open(hull_file, 'r') as f:
            hull_data = f.read()
            hull_model = HullModel.model_validate_json(hull_data)
            hulls.append(HullSummaryModel(name=hull_model.name, 
                                          description=hull_model.description,
                                          length=round(hull_model.length,2), 
                                          beam=round(hull_model.beam,2),
                                          depth=round(hull_model.depth,2), 
                                          volume=round(hull_model.volume,2), 
                                          waterline=round(hull_model.waterline,2), 
                                          displacement=round(hull_model.displacement,2)))
    # Sort hulls by name alphabetically
    hulls.sort(key=lambda h: h.name.lower() if h.name else "")
    return hulls


@router.get("/{hull_name}")
def get_hull(hull_name: str)  -> HullModel:
    safe_filename = sanitize_filename(hull_name)
    file_path = settings.data_path
    os.makedirs(file_path, exist_ok=True)
    file_path = file_path / f"{safe_filename}.hull"
    with open(file_path, 'r') as f:
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
        hull.build(hull_model.model_dump())
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
        
        result = HullModel()
        result.name = hull.name
        result.description = hull.description
        result.units = hull.units
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
            result.curves.append(CurveModel(name=curve.name, mirrored=curve.mirrored, points=[(p.x, p.y, p.z) for p in curve.points]))
        for profile in hull.profiles:
            result.profiles.append(ProfileModel(station=profile.station, points=[(p.x, p.y, p.z) for p in profile.points])) 
        
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(result.model_dump_json(indent=2))
    return result

@router.put("/{hull_name}")
def update_hull(hull_name: str, hull_model: CreateHullModel) -> HullModel:
    if hull_name != hull_model.name:
        #rename the existing file to the new name if it exists
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
    hull.build(hull_model.model_dump())
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
    
    result = HullModel()
    result.name = hull.name
    result.description = hull.description
    result.units = hull.units
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
        result.curves.append(CurveModel(name=curve.name, mirrored=curve.mirrored, points=[(p.x, p.y, p.z) for p in curve.points]))
    for profile in hull.profiles:
        result.profiles.append(ProfileModel(station=profile.station, points=[(p.x, p.y, p.z) for p in profile.points])) 
    
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(result.model_dump_json(indent=2))

    return result

@router.delete("/{hull_name}")
def delete_hull(hull_name: str)  -> HullModel:
    safe_filename = sanitize_filename(hull_name)
    file_path = settings.data_path
    os.makedirs(file_path, exist_ok=True)
    file_path = file_path / f"{safe_filename}.hull"
    #delete the file if it exists
    if file_path.is_file():
        file_path.unlink()
        return {"detail": "Hull deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Hull not found.")

@router.post("/{hull_name}/stability")
def calculate_hull_stability(stability_analysis: StabilityAnalysisModel) -> StabilityAnalysisResultModel:
    safe_filename = sanitize_filename(stability_analysis.hull_name)
    file_path = settings.data_path / f"{safe_filename}.hull"
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Hull not found.")
    with open(file_path, 'r') as f:
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
        break_on_vanishing=stability_analysis.break_on_vanishing
    )
    result =  StabilityAnalysisResultModel(
        vanishing_angle=vanishing_angle,
        max_moment=max_moment,
        max_moment_angle=max_moment_angle,
    )
    
    for point in stability_points:
        result.stability_points.append(StabilityPointModel(
            angle=point["angle"],
            gz=point["gz"],
            moment=point["moment"],
            waterline=point["waterline"],
            displacement=point["displacement"]
        ))
    
    return result 