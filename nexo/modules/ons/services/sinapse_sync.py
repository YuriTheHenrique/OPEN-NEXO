"""
Serviço de sincronização de solicitações do SINAPSE via API do ONS.
"""

import logging
from typing import Any
from nexo.modules.ons.client import ons_client

logger = logging.getLogger("nexo.modules.ons.services.sinapse_sync")


def consultar_solicitacoes_sinapse(
    origens: str | None = None,
    destinos: str | None = None,
    data_inicio: str | None = None,
    limite: int = 100,
) -> dict[str, Any] | None:
    """
    Consulta a lista de solicitações registradas no SINAPSE através da API oficial do ONS.
    """
    params: dict[str, Any] = {"limite": limite}
    if origens:
        params["origem.codigo"] = origens
    if destinos:
        params["destino.codigo"] = destinos
    if data_inicio:
        params["dataDeCriacao"] = data_inicio

    res = ons_client.requisicao("GET", "/operacao/sinapse/solicitacoes", params=params)

    if res and res.status_code == 200:
        return res.json()

    logger.warning(
        f"Falha ao consultar solicitações do SINAPSE: {res.status_code if res else 'Sem resposta'}"
    )
    return None
