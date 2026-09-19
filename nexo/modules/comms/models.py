"""
Models de persistência do módulo COMMS.
"""

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from nexo.core.db import Base


class CommsConfig(Base):
    """
    Configuração geral do módulo COMMS.
    """

    __tablename__ = "comms_config"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    ativo: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    tempo_espera: Mapped[int] = mapped_column(
        default=5,
        nullable=False,
    )


class CommsTemplate(Base):
    """
    Templates de mensagens utilizados pelo COMMS.

    Quando id_local_operacao for None,
    o template representa o modelo padrão.
    """

    __tablename__ = "comms_templates"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    id_local_operacao: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        index=True,
    )

    tipo_evento: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    template: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )