from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Restricao(Base):

    __tablename__ = "restricoes"

    id = Column(Integer, primary_key=True, index=True)

    codigo = Column(String)

    dataAtualizacao = Column(String)
    
    dataCadastro = Column(String)

    dataRecebimento = Column(String)

    destino = Column(String)
    idLocalOperacao = Column(String)

    informacaoAdicional = Column(String)
    mensagem = Column(String)

    motivo = Column(String)
    origem = Column(String)

    status = Column(String)


    # Dados extraídos pelo NEXO

    usina = Column(String)
    apelido = Column(String)
    capacidade = Column(Integer)
    regiao = Column(String)
    tipo_geracao = Column(String)

    potencia_observada = Column(Integer)
    potencia_restricao = Column(Integer)

    evento = Column(String)
