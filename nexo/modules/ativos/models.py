"""
Modelos do módulo ATIVOS.

Este módulo mantém o cadastro independente dos ativos
operacionais utilizados pelo NEXO.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
)

from nexo.core.db import Base
from datetime import datetime

class Ativo(Base):

    __tablename__ = "ativos"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ========================================================
    # IDENTIFICAÇÃO
    # ========================================================

    nome = Column(
        String,
        nullable=False,
    )

    apelido = Column(
        String,
        nullable=False,
    )

    # Código utilizado pela integração SINAPSE.
    #
    # O valor será informado pelo SINAPSE e utilizado
    # como identificador de integração do ativo.

    id_local_operacao = Column(
        String,
        unique=True,
        index=True,
        nullable=True,
    )

    cor = Column(
        String,
        nullable=False,
        default="#0d6efd",
    )

    # ========================================================
    # CARACTERÍSTICAS OPERACIONAIS
    # ========================================================

    capacidade = Column(
        Float,
        nullable=False,
    )

    tipo = Column(
        String,
        nullable=True,
    )

    regiao = Column(
        String,
        nullable=True,
    )

    # ========================================================
    # EMPRESA
    # ========================================================

    empresa = Column(
        String,
        nullable=True,
    )

    logo = Column(
        String,
        nullable=True,
    )

    # ========================================================
    # STATUS
    # ========================================================

    ativo = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    # ========================================================
    # CONTROLE DE DATAS
    # ========================================================

    criado_em = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    atualizado_em = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )