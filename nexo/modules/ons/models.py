"""
Modelos de dados dedicados para o módulo ONS.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from datetime import datetime
from nexo.modules.ons.db import BaseONS


class ONSUsinaRepresentada(BaseONS):
    """
    Catálogo oficial de usinas representadas pela empresa no ONS.
    """
    __tablename__ = "ons_usinas_representadas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False) # Ex: IYSDF, IYCBS
    nome = Column(String(150), nullable=False)                           # Ex: CJF SOL DO FUTURO
    tipo = Column(String(20), nullable=True)                             # Ex: UFV, UEE
    empresa_codigo = Column(String(20), nullable=True)                   # Ex: IY
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ONSPDP(BaseONS):
    """
    Programação Diária de Produção (PDP) emitida pelo ONS patamar a patamar.
    """
    __tablename__ = "ons_pdp"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(String(10), nullable=False, index=True)          # Formato YYYY-MM-DD
    codigo_usina = Column(String(50), nullable=False, index=True)  # Ex: IYSDF
    patamar_numero = Column(Integer, nullable=False)               # 1 a 48
    patamar_hora = Column(String(10), nullable=False)              # "00:00", "00:30", etc.
    potencia_programada = Column(Float, nullable=False, default=0.0) # MW
    data_coleta = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("data", "codigo_usina", "patamar_numero", name="uix_pdp_data_usina_patamar"),
    )


class ONSSolicitacao(BaseONS):
    """
    Solicitações e restrições do SINAPSE coletadas via API oficial do ONS.
    """
    __tablename__ = "ons_solicitacoes"

    id = Column(String(100), primary_key=True, index=True)
    data_criacao = Column(String(50), nullable=True, index=True)
    data_atualizacao = Column(String(50), nullable=True)
    origem_codigo = Column(String(20), nullable=True)
    origem_nome = Column(String(100), nullable=True)
    destino_codigo = Column(String(20), nullable=True)
    destino_nome = Column(String(100), nullable=True)
    mensagem = Column(String(500), nullable=True)
    data_sincronizacao = Column(DateTime, default=datetime.utcnow)
    informacao_adicional = Column(String(1000), nullable=True)
    motivo = Column(String(500), nullable=True)
    detalhe_impedimento = Column(String(1000), nullable=True)
    local_codigo = Column(String(50), nullable=True)
    local_nome = Column(String(150), nullable=True)
    status_codigo = Column(Integer, nullable=True)
    status_nome = Column(String(100), nullable=True)
    sistema_origem = Column(String(100), nullable=True)
    tags = Column(String(500), nullable=True)
