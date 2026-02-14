from typing import Union
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.routes.hull import router 

app = FastAPI()

# Include API routers FIRST
app.include_router(router, prefix="/hulls", tags=["Hulls"])

# Mount static files LAST (acts as catch-all for unmatched routes)
# This allows /hulls/* to be handled by the router above, while serving static files for everything else
visualization_dir = Path(__file__).parent.parent / "visualization"
if visualization_dir.exists():
    app.mount("/", StaticFiles(directory=str(visualization_dir), html=True), name="visualization")
else:
    print(f"Warning: Visualization directory '{visualization_dir}' not found. Static files will not be served.")

