import re

from .assets import USINAS

def extrair_usina(mensagem: str):

    if "|" not in mensagem:
        return None

    return mensagem.split("|")[0].strip()

def extrair_potencia_observada(mensagem: str):

    resultado = re.search(
        r"Ponto de Partida:\s*(\d+)",
        mensagem
    )

    if resultado:
        return int(resultado.group(1))

    return None

def extrair_potencia_restricao(mensagem: str):

    resultado = re.search(
        r"Limitar em\s*(\d+)",
        mensagem
    )

    if resultado:
        return int(resultado.group(1))

    return None

def extrair_tipo_geracao(mensagem: str):

    if "Fotovoltaica" in mensagem:
        return "Fotovoltaica"

    if "Eólica" in mensagem:
        return "Eólica"

    return None

def identificar_evento(mensagem: str):

    if "Liberação Total" in mensagem:
        return "LIBERACAO"

    if "Limitar em" in mensagem:
        return "RESTRICAO"

    return "DESCONHECIDO"

def buscar_usina(nome):

    return USINAS.get(nome)

def parse_mensagem(mensagem):

    usina = extrair_usina(mensagem)

    cadastro = buscar_usina(usina)

    return {

    "usina": usina,

    "apelido": cadastro.apelido if cadastro else usina,

    "capacidade": cadastro.capacidade if cadastro else None,

    "regiao": cadastro.regiao if cadastro else None,

    "tipo_geracao": cadastro.tipo if cadastro else None,

    "potencia_observada":
        extrair_potencia_observada(mensagem),

    "potencia_restricao":
        extrair_potencia_restricao(mensagem),

    "evento":
        identificar_evento(mensagem)

}