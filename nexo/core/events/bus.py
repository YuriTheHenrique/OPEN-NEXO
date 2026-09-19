from collections import defaultdict
from typing import Callable, Any


class EventBus:

    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, evento: str, callback: Callable):
        self.listeners[evento].append(callback)

        print(
            f"SUBSCRIBE -> {evento} -> {callback.__name__}"
        )

    def publish(self, evento: str, dados: Any):
        callbacks = self.listeners.get(evento, [])

        for callback in callbacks:
            try:
                callback(dados)
            except Exception as erro:
                print(
                    f"Erro ao processar evento {evento}: {erro}"
                )


event_bus = EventBus()