"""
Estruturas de mensagem do módulo COMMS.

Este arquivo define o formato padrão utilizado pelo NEXO
para solicitar o envio de uma comunicação.

Os módulos de origem trabalham com esta estrutura sem
precisar conhecer a implementação do canal de comunicação.
"""

from dataclasses import dataclass
from typing import Any


## ESTRUTURA PADRÃO DE MENSAGEM
# Representa uma solicitação de comunicação dentro do NEXO.
# O canal e o destino ficam separados do conteúdo para permitir
# que a mesma estrutura seja utilizada por WhatsApp, e-mail,
# Teams ou outros canais futuramente.


@dataclass
class MensagemComms:

    canal: str
    destino: str
    mensagem: str
    dados: dict[str, Any] | None = None