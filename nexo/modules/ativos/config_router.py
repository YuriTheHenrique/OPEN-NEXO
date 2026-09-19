"""
Rotas de configuração do módulo ATIVOS.
"""

from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from nexo.core.db import SessionLocal
from nexo.modules.ativos.service import (
    listar_ativos,
    obter_ativo,
    atualizar_ativo,
    criar_ativo,
    excluir_ativo,
)

router = APIRouter(
    prefix="/config",
    tags=["Ativos"],
)

templates = Jinja2Templates(
    directory=[
        "nexo/modules/ativos/templates",
        "nexo/core/templates",
    ]
)

# ============================================================
# BANCO DE DADOS
# ============================================================

def obter_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# ============================================================
# CONFIG
# ============================================================

@router.get(
    "/pagina",
    response_class=HTMLResponse,
)
def pagina_config(
    request: Request,
    db: Session = Depends(obter_db),
):
    """
    Exibe a página de configuração dos ativos.
    """

    ativos = listar_ativos(db)

    return templates.TemplateResponse(
        request=request,
        name="config.html",
        context={
            "ativos": ativos,
        },
    )

# ============================================================
# EDIÇÃO
# ============================================================

@router.get(
    "/{id_ativo}/editar",
    response_class=HTMLResponse,
)
def editar_ativo(
    id_ativo: int,
    request: Request,
    db: Session = Depends(obter_db),
):
    """
    Exibe a página de edição de um ativo.
    """

    ativo = obter_ativo(
        db,
        id_ativo,
    )

    if not ativo:
        raise HTTPException(
            status_code=404,
            detail="Ativo não encontrado.",
        )

    return templates.TemplateResponse(
        request=request,
        name="editar.html",
        context={
            "ativo": ativo,
        },
    )

@router.get(
    "/novo",
    response_class=HTMLResponse,
)
def novo_ativo_pagina(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="novo.html",
        context={},
    )

@router.post("/novo")
def criar_novo_ativo(
    nome: str = Form(...),
    apelido: str = Form(...),
    id_local_operacao: str = Form(""),
    capacidade: float = Form(...),
    tipo: str = Form(""),
    regiao: str = Form(""),
    empresa: str = Form(""),
    logo: str = Form(""),
    cor: str = Form(""),
    ativo_habilitado: bool = Form(False, alias="ativo"),
    db: Session = Depends(obter_db),
):
    criar_ativo(
        db,
        nome=nome.strip(),
        apelido=apelido.strip(),
        id_local_operacao=id_local_operacao.strip() or None,
        capacidade=capacidade,
        tipo=tipo.strip() or None,
        regiao=regiao.strip() or None,
        empresa=empresa.strip() or None,
        logo=logo.strip() or None,
        cor=cor.strip() or None,
        ativo=ativo_habilitado,
    )
    return {"ok": True, "mensagem": "Ativo cadastrado com sucesso."}

# ============================================================
# SALVAMENTO DA EDIÇÃO
# ============================================================

@router.post(
    "/{id_ativo}/editar",
)
def salvar_ativo(
    id_ativo: int,
    nome: str = Form(...),
    apelido: str = Form(...),
    id_local_operacao: str = Form(""),
    capacidade: float = Form(...),
    tipo: str = Form(""),
    regiao: str = Form(""),
    empresa: str = Form(""),
    logo: str = Form(""),
    cor: str = Form(""),
    ativo: bool = Form(False),
    db: Session = Depends(obter_db),
    ativo_habilitado: bool = Form(False, alias="ativo"),
):
    """
    Salva as alterações de um ativo.
    """

    ativo_obj = obter_ativo(
        db,
        id_ativo,
    )

    if not ativo_obj:
        raise HTTPException(
            status_code=404,
            detail="Ativo não encontrado.",
        )

    atualizar_ativo(
        db,
        ativo_obj,
        nome=nome.strip(),
        apelido=apelido.strip(),
        id_local_operacao=id_local_operacao.strip() or None,
        capacidade=capacidade,
        tipo=tipo.strip() or None,
        regiao=regiao.strip() or None,
        empresa=empresa.strip() or None,
        logo=logo.strip() or None,
        cor=cor.strip() or None,
        ativo=ativo_habilitado,
    )

    return {
        "ok": True,
        "mensagem": "Ativo atualizado com sucesso.",
    }

# ============================================================
# LISTAGEM
# ============================================================

@router.get("")
def consultar_ativos(
    db: Session = Depends(obter_db),
):
    """
    Retorna os ativos cadastrados no NEXO.
    """

    ativos = listar_ativos(db)

    return [
        {
            "id": ativo.id,
            "nome": ativo.nome,
            "apelido": ativo.apelido,
            "id_local_operacao": ativo.id_local_operacao,
            "capacidade": ativo.capacidade,
            "tipo": ativo.tipo,
            "regiao": ativo.regiao,
            "empresa": ativo.empresa,
            "logo": ativo.logo,
            "cor": ativo.cor,
            "ativo": ativo.ativo,
            "criado_em": ativo.criado_em,
            "atualizado_em": ativo.atualizado_em,
        }
        for ativo in ativos
    ]


# ============================================================
# CONSULTA INDIVIDUAL
# ============================================================

@router.get("/{id_ativo}")
def consultar_ativo(
    id_ativo: int,
    db: Session = Depends(obter_db),
):
    """
    Retorna um ativo específico.
    """

    ativo = obter_ativo(
        db,
        id_ativo,
    )

    if not ativo:
        raise HTTPException(
            status_code=404,
            detail="Ativo não encontrado.",
        )

    return {
        "id": ativo.id,
        "nome": ativo.nome,
        "apelido": ativo.apelido,
        "id_local_operacao": ativo.id_local_operacao,
        "capacidade": ativo.capacidade,
        "tipo": ativo.tipo,
        "regiao": ativo.regiao,
        "empresa": ativo.empresa,
        "logo": ativo.logo,
        "cor": ativo.cor,
        "ativo": ativo.ativo,
        "criado_em": ativo.criado_em,
        "atualizado_em": ativo.atualizado_em,
    }

@router.post(
    "/{id_ativo}/excluir",
)
def excluir_ativo_rota(
    id_ativo: int,
    db: Session = Depends(obter_db),
):
    ativo = obter_ativo(db, id_ativo)
    if not ativo:
        raise HTTPException(
            status_code=404,
            detail="Ativo não encontrado.",
        )

    excluir_ativo(db, ativo)
    return {"status": "ok"}
