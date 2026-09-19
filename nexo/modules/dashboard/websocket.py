import asyncio
import json

from fastapi import WebSocket


class DashboardWebSocketManager:

    def __init__(self):
        self.connections: dict[
            WebSocket,
            tuple[asyncio.Queue, asyncio.AbstractEventLoop]
        ] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        self.connections[websocket] = (queue, loop)

        print(
            f"DASHBOARD WS -> conectado "
            f"({len(self.connections)} cliente(s))"
        )

        return queue

    def disconnect(self, websocket: WebSocket):

        self.connections.pop(websocket, None)

        print(
            f"DASHBOARD WS -> desconectado "
            f"({len(self.connections)} cliente(s))"
        )

    def publicar(self, dados):

        if not self.connections:
            return

        mensagem = json.dumps(
            dados,
            ensure_ascii=False,
            default=str
        )

        for websocket, (queue, loop) in list(
            self.connections.items()
        ):

            try:

                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    mensagem
                )

            except Exception as erro:

                print(
                    f"Erro ao notificar dashboard: {erro}"
                )


dashboard_ws = DashboardWebSocketManager()