ULTIMOS_EVENTOS = []


def registrar_evento(evento):
    ULTIMOS_EVENTOS.append(evento)

    if len(ULTIMOS_EVENTOS) > 100:
        ULTIMOS_EVENTOS.pop(0)


def listar_eventos():
    return ULTIMOS_EVENTOS