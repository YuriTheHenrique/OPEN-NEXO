from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=[
        "nexo/modules/tetris/templates",
        "nexo/core/templates",
    ]
)

router = APIRouter()

router.mount(
    "/tetris/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="tetris-static"
)

@router.get("/tetris")
def tetris(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="tetris.html"
    )