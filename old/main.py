from typing import Union

from fastapi import FastAPI

from src.routes.hull import router 

app = FastAPI()

app.include_router(router, prefix="/hulls", tags=["Hulls"])


