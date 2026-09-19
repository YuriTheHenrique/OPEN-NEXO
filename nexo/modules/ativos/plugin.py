from fastapi import FastAPI
from nexo.modules.ativos.config_router import router as ativos_router

def setup_module(app: FastAPI, event_bus):
    # O próprio módulo é responsável por anexar suas rotas ao FastAPI
    app.include_router(ativos_router, prefix="/ativos", tags=["Ativos"])
    # Se o módulo escutar eventos do core, ele se inscreve diretamente aqui
    # event_bus.subscribe("NOVO_ATIVO_CRIADO", ao_criar_ativo)

MODULE_INFO = {
    "codigo": "NEXO / ATIVOS",
    "titulo": "Ativos",
    "descricao": "Consulte, cadastre e configure os ativos utilizados pelo NEXO.",
    "url": "/ativos/config/pagina",
    "ordem": 2,
}
