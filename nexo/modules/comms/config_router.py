"""
Rotas de configuração do módulo COMMS.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from nexo.modules.comms.config_service import (
    obter_config,
    salvar_config,
    obter_template,
    salvar_template,
)

from nexo.modules.comms.gateway import (
    obter_status_gateway,
    obter_qr_gateway,
    reconectar_gateway,
    resetar_gateway,
)

router = APIRouter(
    prefix="/comms/config",
    tags=["COMMS"],
)

templates = Jinja2Templates(
    directory=[
        "nexo/modules/comms/templates",
        "nexo/core/templates",
    ]
)


# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================

@router.get("")
def consultar_config():

    config = obter_config()

    return {
        "ativo": config.ativo,
        "tempo_espera": config.tempo_espera,
    }


@router.get("/page")
def pagina_config(request: Request):

    config = obter_config()

    template_restricao = obter_template(
        tipo_evento="RESTRICAO"
    )

    template_liberacao = obter_template(
        tipo_evento="LIBERACAO_TOTAL"
    )

    return templates.TemplateResponse(
        request,
        "config.html",
        {
            "request": request,
            "config": config,
            "template_restricao": template_restricao,
            "template_liberacao": template_liberacao,
        },
    )


@router.post("/page")
def salvar_config_pagina(
    ativo: bool = Form(False),
    tempo_espera: int = Form(5),
):

    salvar_config(
        ativo=ativo,
        tempo_espera=tempo_espera,
    )

    return RedirectResponse(
        url="/comms/config/page",
        status_code=303,
    )


# ============================================================
# TEMPLATES
# ============================================================

@router.get("/template/{tipo_evento}")
def consultar_template(
    tipo_evento: str,
):

    template = obter_template(
        tipo_evento=tipo_evento,
    )

    return {
        "tipo_evento": tipo_evento,
        "template": template,
    }


@router.get(
    "/template/{tipo_evento}/{id_local_operacao}"
)
def consultar_template_usina(
    tipo_evento: str,
    id_local_operacao: str,
):

    template = obter_template(
        tipo_evento=tipo_evento,
        id_local_operacao=id_local_operacao,
    )

    return {
        "tipo_evento": tipo_evento,
        "id_local_operacao": id_local_operacao,
        "template": template,
    }


@router.post("/page/template")
def salvar_template_pagina(
    tipo_evento: str = Form(...),
    template: str = Form(...),
    id_local_operacao: str = Form(""),
):

    salvar_template(
        tipo_evento=tipo_evento,
        template=template,
        id_local_operacao=id_local_operacao or None,
    )

    return RedirectResponse(
        url="/comms/config/page",
        status_code=303,
    )

# ============================================================
# TEMPLATES ESPECÍFICOS POR ATIVO
# ============================================================

@router.get("/template-ativo/{tipo_evento}/{id_local_operacao}")
def consultar_template_ativo(
    tipo_evento: str,
    id_local_operacao: str,
):
    template = obter_template(
        tipo_evento=tipo_evento,
        id_local_operacao=id_local_operacao,
    )

    return {
        "ok": True,
        "tipo_evento": tipo_evento,
        "id_local_operacao": id_local_operacao,
        "template": template or "",
    }


@router.post("/template-ativo")
def salvar_template_ativo(
    tipo_evento: str = Form(...),
    template: str = Form(...),
    id_local_operacao: str = Form(...),
):
    if not id_local_operacao.strip():
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "erro": "O ativo deve ser informado.",
            },
        )

    salvar_template(
        tipo_evento=tipo_evento,
        template=template,
        id_local_operacao=id_local_operacao.strip(),
    )

    return {
        "ok": True,
        "mensagem": "Template do ativo salvo com sucesso.",
    }

# ============================================================
# WHATSAPP GATEWAY
# ============================================================

@router.get("/whatsapp/status")
def consultar_status_whatsapp():

    status = obter_status_gateway()

    if status is None:
        return {
            "ok": False,
            "disponivel": False,
            "erro": "WhatsApp Gateway indisponível.",
        }

    return status

@router.get("/whatsapp/qr")
def consultar_qr_whatsapp():

    qr = obter_qr_gateway()

    if qr is None:
        return {
            "ok": False,
            "disponivel": False,
            "erro": "WhatsApp Gateway indisponível.",
        }

    return qr

# ============================================================
# CONTROLE DA CONEXÃO WHATSAPP
# ============================================================

@router.post("/whatsapp/reconectar")
def reconectar_whatsapp():

    resultado = reconectar_gateway()

    if resultado is None:
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "erro": "WhatsApp Gateway indisponível.",
            },
        )

    return resultado


@router.post("/whatsapp/resetar")
def resetar_whatsapp():

    resultado = resetar_gateway()

    if resultado is None:
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "erro": "WhatsApp Gateway indisponível.",
            },
        )

    return resultado