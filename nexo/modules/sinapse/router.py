from fastapi import APIRouter, Body, Depends
from typing import Any

from nexo.modules.sinapse.dependencies import get_db
from nexo.modules.sinapse import services


router = APIRouter()


@router.post("/sinapse")
def receber_evento(
    evento: Any = Body(...),
    db=Depends(get_db)
):
    return services.process_eventos(db, evento)