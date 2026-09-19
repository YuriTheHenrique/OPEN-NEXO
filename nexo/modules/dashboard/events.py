from nexo.modules.dashboard.state import registrar_evento

## RECEBIMENTO DE EVENTOS DO SINAPSE
# Recebe o evento operacional publicado pelo SINAPSE.
# O campo "evento" identifica o tipo da operação, por exemplo
# RESTRICAO ou LIBERACAO.


def nova_restricao(evento):
    print(
        f"[{evento['evento'].upper()}] "
        f"{evento['usina']} "
        f"{evento['status']}"
    )

    registrar_evento(evento)