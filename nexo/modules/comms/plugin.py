from fastapi import FastAPI
from nexo.modules.comms.config_router import router as comms_router
from nexo.modules.comms.config_service import inicializar_config
from nexo.modules.comms.events import registrar_eventos
from nexo.modules.comms.services import processar_fila_comunicacao

def setup_module(app: FastAPI, event_bus):
    # Inicializa configurações padrão, registra rotas e ouvintes do EventBus
    inicializar_config()
    app.include_router(comms_router)
    registrar_eventos()

def get_background_tasks():
    # Retorna o worker de envio de mensagens do WhatsApp para o lifespan executar
    return [processar_fila_comunicacao]

MODULE_INFO = {
    "codigo": "NEXO / COMMS",
    "titulo": "Comunicações",
    "descricao": "Configure os canais e parâmetros de comunicação operacional.",
    "url": "/comms/config/page",
    "ordem": 3,
}
