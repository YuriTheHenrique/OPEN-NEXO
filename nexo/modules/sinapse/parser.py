"""
Parser de mensagens recebidas do ONS / SINAPSE.
"""

import re
from nexo.modules.ativos.data import USINAS


def extrair_usina(mensagem: str) -> str | None:
    if "|" not in mensagem:
        return None
    return mensagem.split("|")[0].strip()


def extrair_potencia_observada(mensagem: str) -> int | None:
    resultado = re.search(r"Ponto de Partida:\s*(\d+)", mensagem)
    if resultado:
        return int(resultado.group(1))
    return None


def extrair_potencia_restricao(mensagem: str) -> int | None:
    resultado = re.search(r"Limitar em\s*(\d+)", mensagem)
    if resultado:
        return int(resultado.group(1))
    return None


def extrair_tipo_geracao(mensagem: str) -> str | None:
    if "Fotovoltaica" in mensagem:
        return "Fotovoltaica"
    if "Eólica" in mensagem:
        return "Eólica"
    return None


def identificar_evento(mensagem: str) -> str:
    if "Liberação Total" in mensagem or "Liberacao Total" in mensagem:
        return "LIBERACAO"
    if "Limitar em" in mensagem:
        return "RESTRICAO"
    return "DESCONHECIDO"


def buscar_usina(nome: str | None, db=None):
    if not nome:
        return None

    if db is not None:
        try:
            from nexo.modules.ativos.models import Ativo
            ativo = (
                db.query(Ativo)
                .filter((Ativo.nome == nome) | (Ativo.apelido == nome))
                .first()
            )
            if ativo:
                return ativo
        except Exception:
            pass

    return USINAS.get(nome)



def parse_mensagem(mensagem: str, db=None) -> dict:
    usina = extrair_usina(mensagem)
    cadastro = buscar_usina(usina, db=db)
    evento = identificar_evento(mensagem)
    potencia_obs = extrair_potencia_observada(mensagem)
    potencia_rest = extrair_potencia_restricao(mensagem)

    # Se for LIBERAÇÃO, a potência liberada (teto permitido) é 100% da usina cadastrada
    if evento == "LIBERACAO" and cadastro and getattr(cadastro, "capacidade", None) is not None:
        potencia_rest = float(cadastro.capacidade)

    return {
        "usina": usina,
        "apelido": cadastro.apelido if (cadastro and cadastro.apelido) else usina,
        "capacidade": cadastro.capacidade if cadastro else None,
        "regiao": cadastro.regiao if cadastro else None,
        "tipo_geracao": cadastro.tipo if cadastro else extrair_tipo_geracao(mensagem),
        "potencia_observada": potencia_obs,
        "potencia_restricao": potencia_rest,
        "evento": evento,
    }
