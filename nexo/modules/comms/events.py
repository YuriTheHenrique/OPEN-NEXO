"""
Eventos do módulo COMMS.

Este arquivo conecta o COMMS ao EventBus central do NEXO.
"""

from nexo.core.events.bus import event_bus

from nexo.core.events.types import (COMMS_MENSAGEM_ENVIAR, SINAPSE_RESTRICAO_RECEBIDA)

from nexo.modules.comms.services import (processar_mensagem, receber_restricao)


## REGISTRO DO COMMS NO EVENT BUS
# Conecta o módulo COMMS ao barramento central.
# A partir deste registro, qualquer módulo do NEXO pode solicitar
# uma comunicação publicando o evento COMMS_MENSAGEM_ENVIAR.


def registrar_eventos():

    event_bus.subscribe(
        COMMS_MENSAGEM_ENVIAR,
        processar_mensagem
    )

    ## REGISTRO DAS RESTRIÇÕES NO COMMS
    # Permite que o COMMS receba as restrições publicadas pelo SINapse.
    # A partir desse evento, o COMMS poderá posteriormente decidir
    # quais restrições devem gerar mensagens e quais templates utilizar.

    event_bus.subscribe(
        SINAPSE_RESTRICAO_RECEBIDA,
        receber_restricao
    )