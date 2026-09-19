from fastapi import FastAPI
from nexo.modules.dashboard.router import router as dashboard_router
from nexo.modules.dashboard.events import nova_restricao
from nexo.core.events.types import SINAPSE_RESTRICAO_RECEBIDA

def setup_module(app: FastAPI, event_bus):
    # Registra rotas do painel visual e assina eventos de restrição em tempo real
    app.include_router(dashboard_router)
    event_bus.subscribe(SINAPSE_RESTRICAO_RECEBIDA, nova_restricao)

MODULE_INFO = {
    "codigo": "NEXO / SINAPSE",
    "titulo": "Dashboard",
    "descricao": "Visualização operacional das restrições, eventos e indicadores das usinas.",
    "url": "/dashboard",
    "ordem": 1,
}
