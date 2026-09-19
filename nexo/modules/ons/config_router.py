"""
Rotas de configuração e status do módulo ONS / SINtegre.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from nexo.modules.ons.config import carregar_config, salvar_config
from nexo.modules.ons.client import ons_client
from nexo.modules.ons.services.sinapse_sync import consultar_solicitacoes_sinapse

router = APIRouter(
    prefix="/ons/config",
    tags=["ONS"],
)

templates = Jinja2Templates(
    directory=[
        "nexo/modules/ons/templates",
        "nexo/core/templates",
    ]
)


@router.get("", response_class=HTMLResponse)
@router.get("/pagina", response_class=HTMLResponse)
def config_pagina(request: Request):
    """
    Renderiza a interface de configuração do conector ONS.
    """
    config = carregar_config()
    config_exibicao = config.copy()
    if config_exibicao.get("senha"):
        config_exibicao["senha_mascarada"] = "••••••••••••"

    return templates.TemplateResponse(
        request=request,
        name="config.html",
        context={"config": config_exibicao},
    )


@router.post("/salvar")
async def salvar_configuracoes(request: Request):
    """
    Salva as configurações do ONS no config.json.
    """
    try:
        dados = await request.json()
        config_atual = carregar_config()

        config_atual["base_url"] = dados.get("base_url", "https://api.ons.org.br").strip()
        config_atual["usuario"] = dados.get("usuario", "").strip()

        nova_senha = dados.get("senha", "").strip()
        if nova_senha and nova_senha != "••••••••••••":
            config_atual["senha"] = nova_senha

        config_atual["intervalo_sincronizacao_segundos"] = int(
            dados.get("intervalo_sincronizacao_segundos", 300)
        )
        config_atual["ativo"] = bool(dados.get("ativo", True))

        salvar_config(config_atual)
        ons_client.recarregar_config()
        ons_client.token = None  # Força nova autenticação

        return JSONResponse({"sucesso": True, "mensagem": "Configurações salvas com sucesso."})
    except Exception as e:
        return JSONResponse(
            {"sucesso": False, "mensagem": f"Erro ao salvar configurações: {str(e)}"},
            status_code=400,
        )


@router.post("/testar")
def testar_conexao():
    """
    Testa a autenticação e uma consulta simples no ONS.
    """
    try:
        ons_client.token = None
        sucesso_auth = ons_client.autenticar()

        if not sucesso_auth:
            return JSONResponse({
                "sucesso": False,
                "mensagem": "Falha na autenticação. Verifique usuário e senha do SINtegre.",
            })

        res_sinapse = consultar_solicitacoes_sinapse(limite=1)
        if res_sinapse and res_sinapse.get("success"):
            return JSONResponse({
                "sucesso": True,
                "mensagem": "Conexão com a API do ONS validada com sucesso! Token JWT e endpoint SINAPSE operacionais.",
            })

        return JSONResponse({
            "sucesso": True,
            "mensagem": "Autenticado com sucesso no ONS (Token JWT obtido).",
        })
    except Exception as e:
        return JSONResponse({
            "sucesso": False,
            "mensagem": f"Erro durante o teste de conexão: {str(e)}",
        })
