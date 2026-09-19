"""
Fila de comunicação do módulo COMMS.

A fila recebe eventos de restrições confirmadas e permite que
o processamento das comunicações aconteça de forma assíncrona,
sem bloquear o EventBus ou o SINAPSE.
"""

import asyncio
from typing import Any


class FilaComunicacao:

    def __init__(self):
        self.fila: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    def adicionar(self, evento: dict[str, Any]):
        self.fila.put_nowait(evento)

    async def obter(self) -> dict[str, Any]:
        return await self.fila.get()

    def concluir(self):
        self.fila.task_done()


fila_comunicacao = FilaComunicacao()