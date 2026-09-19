"""
Plugin do módulo SINAPSE.
"""

from fastapi import FastAPI
from nexo.modules.sinapse.router import router

INTEGRACAO_INFO = {
    "titulo": "Integração",
    "subtitulo": "Endpoint disponível para integração com o SINAPSE.",
    "label": "API SINAPSE",
    "path": "sinapse",
}

def init_plugin(app: FastAPI):
    app.include_router(router)
