from fastapi import FastAPI
from nexo.modules.tetris.router import router as tetris_router

def setup_module(app: FastAPI, event_bus):
    # Registra a rota do Tetris dos operadores
    app.include_router(tetris_router)

MODULE_INFO = {
    "ocultar_home": True
}
