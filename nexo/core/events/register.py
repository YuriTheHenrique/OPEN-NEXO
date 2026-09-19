from nexo.core.events.bus import event_bus
from nexo.core.events.types import SINAPSE_RESTRICAO_RECEBIDA

from nexo.modules.dashboard.events import nova_restricao
from nexo.modules.comms.events import registrar_eventos as registrar_eventos_comms

def register_events():
    event_bus.subscribe(
        SINAPSE_RESTRICAO_RECEBIDA,
        nova_restricao
    )

    ## REGISTRO DO MÓDULO COMMS
    # Inicializa os listeners responsáveis pelas solicitações
    # de comunicação do NEXO.

    registrar_eventos_comms()