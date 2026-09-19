from dataclasses import dataclass
from datetime import datetime

#data de hoje por enquanto, depois adicinar filtro e remover
def data_hoje():

    return datetime.now().strftime("%Y-%m-%d")

#gestão de ativos

@dataclass
class Usina:
    nome: str
    apelido: str
    capacidade: float
    empresa: str
    logo: str
    tipo: str
    regiao: str
    ativa: bool = True
    cor: str = "#0d6efd"   # Bootstrap Primary


USINAS = {

}