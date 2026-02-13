import os
from pathlib import Path
from typing import Union
from typing import List, Dict, Optional, Tuple

from fastapi import APIRouter, HTTPException
from src.model.model import Hull
from src.utils.filename import sanitize_filename

router = APIRouter()

@router.get("/")
def hull_list() -> List[Hull]:
    return [{"name": "My hull"}]


@router.get("/{hull_id}")
def get_hull(hull_id: int, q: Union[str, None] = None)  -> Hull:
    return [{"name": "My hull"}]

@router.post("/")
def create_hull(hull: Hull) -> Hull:
    safe_filename = sanitize_filename(hull.file_name or hull.metadata.name)
    file_path = Path("data") / f"{safe_filename}.json"
    prep_file_path = Path("data") / f"{safe_filename}_ready.json"
    
    if file_path.is_file():
        raise HTTPException(status_code=409, detail="A hull with this name already exists.")    
    else:
        prepared_hull = prepare_hull( hull)
        
        hull.file_name = str(file_path)
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(hull.model_dump_json(indent=2))
        with open(prep_file_path, 'w') as f:
            f.write(prepared_hull.to_json(indent=2))
    return hull
