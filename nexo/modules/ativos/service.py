"""
Serviços do módulo ATIVOS.

Centraliza as operações de leitura e alteração
dos ativos cadastrados no NEXO.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from nexo.modules.ativos.models import Ativo


# ============================================================
# CONSULTAS
# ============================================================

def listar_ativos(
    db: Session,
    apenas_ativos: bool = False,
) -> list[Ativo]:
    """
    Retorna os ativos cadastrados.

    Por padrão, retorna ativos ativos e inativos.
    Quando apenas_ativos=True, retorna somente os ativos
    atualmente habilitados.
    """

    consulta = select(Ativo)

    if apenas_ativos:
        consulta = consulta.where(
            Ativo.ativo.is_(True)
        )

    consulta = consulta.order_by(
        Ativo.apelido
    )

    return list(
        db.scalars(consulta).all()
    )


def obter_ativo(
    db: Session,
    id_ativo: int,
) -> Ativo | None:
    """
    Retorna um ativo pelo ID interno do NEXO.
    """

    return db.get(
        Ativo,
        id_ativo,
    )


def obter_ativo_por_id_local_operacao(
    db: Session,
    id_local_operacao: str,
) -> Ativo | None:
    """
    Retorna um ativo pelo código de integração
    utilizado pelo SINAPSE.
    """

    consulta = (
        select(Ativo)
        .where(
            Ativo.id_local_operacao
            == id_local_operacao
        )
    )

    return db.scalars(
        consulta
    ).first()


# ============================================================
# CRIAÇÃO
# ============================================================

def criar_ativo(
    db: Session,
    *,
    nome: str,
    apelido: str,
    capacidade: float,
    tipo: str | None = None,
    regiao: str | None = None,
    empresa: str | None = None,
    logo: str | None = None,
    cor: str | None = None,
    id_local_operacao: str | None = None,
    ativo: bool = True,
) -> Ativo:
    """
    Cria um novo ativo no cadastro do NEXO tratando strings vazias como None.
    """
    novo_ativo = Ativo(
        nome=nome.strip() if nome else "",
        apelido=apelido.strip() if apelido else "",
        capacidade=float(capacidade) if capacidade else 0.0,
        tipo=tipo.strip() if (tipo and tipo.strip()) else None,
        regiao=regiao.strip() if (regiao and regiao.strip()) else None,
        empresa=empresa.strip() if (empresa and empresa.strip()) else None,
        logo=logo.strip() if (logo and logo.strip()) else None,
        cor=cor.strip() if (cor and cor.strip()) else None,
        id_local_operacao=id_local_operacao.strip() if (id_local_operacao and id_local_operacao.strip()) else None,
        ativo=ativo,
    )

    db.add(novo_ativo)
    db.commit()
    db.refresh(novo_ativo)

    return novo_ativo




# ============================================================
# ATUALIZAÇÃO
# ============================================================

def atualizar_ativo(
    db: Session,
    ativo_obj: Ativo,
    **dados,
) -> Ativo:
    """
    Atualiza os dados de um ativo existente.

    Somente campos existentes no model serão alterados.
    """

    campos_permitidos = {
        "nome",
        "apelido",
        "capacidade",
        "tipo",
        "regiao",
        "empresa",
        "logo",
        "cor",
        "ativo",
        "id_local_operacao",
    }

    for campo, valor in dados.items():

        if campo not in campos_permitidos:
            continue

        setattr(
            ativo_obj,
            campo,
            valor,
        )

    db.commit()
    db.refresh(ativo_obj)

    return ativo_obj

# ============================================================
# EXCLUSÃO
# ============================================================

def excluir_ativo(
    db: Session,
    ativo: Ativo,
) -> bool:
    """
    Remove um ativo do banco de dados do NEXO.
    """
    db.delete(ativo)
    db.commit()
    return True
