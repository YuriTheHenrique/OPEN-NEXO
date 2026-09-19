"""
Plugin do módulo ONS / SINtegre.
"""

from fastapi import FastAPI
from nexo.modules.ons.config_router import router as config_router
from nexo.modules.ons.db import criar_tabelas_ons

MODULE_INFO = {
    "codigo": "NEXO / ONS",
    "titulo": "ONS / SINtegre",
    "descricao": "Integração oficial com as APIs do Operador Nacional do Sistema.",
    "url": "/ons/config",
    "ordem": 40,
}


def setup_module(app: FastAPI, event_bus=None) -> None:
    """
    Inicializa o módulo ONS: cria as tabelas no ons.db e registra as rotas.
    """
    try:
        criar_tabelas_ons()
    except Exception as e:
        print(f"Aviso ao criar tabelas do ONS: {e}")

    app.include_router(config_router)
