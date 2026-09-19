import requests
import random
import time
from datetime import datetime, timedelta


URL = "http://localhost:8000/sinapse"


def agora():
    return datetime.utcnow().isoformat() + "Z"


def novo_codigo():
    return (
        datetime.now().strftime("%Y%m%d%H%M%S")
        + "-"
        + "".join(
            random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            for _ in range(6)
        )
    )


def horario_simulado(horario):
    """
    Cria um timestamp UTC para o horário informado,
    usando a data de hoje.
    """

    hoje = datetime.now().date()

    hora, minuto = map(int, horario.split(":"))

    data = datetime(
        hoje.year,
        hoje.month,
        hoje.day,
        hora,
        minuto
    )

    # Brasil UTC-3
    data_utc = data + timedelta(hours=3)

    return data_utc.isoformat() + "Z"


def evento_restricao(
    codigo,
    usina,
    origem,
    partida,
    limite,
    tipo="Eólica",
    status="pendente",
    tempo=None
):

    if tempo is None:
        tempo = agora()

    return {
        "dataAtualizacao": tempo,
        "codigo": codigo,
        "origem": origem,
        "destino": "",
        "mensagem":
            f"{usina} | "
            f"(Ponto de Partida: {partida} MW) "
            f"Limitar em {limite} MW a Geração {tipo}",
        "status": status,
        "dataCadastro": tempo,
        "motivo": "Energético (Controle de Frequência)",
        "informacaoAdicional": "",
        "idLocalOperacao": "SIMULADO"
    }


def evento_liberacao(
    codigo,
    usina,
    origem,
    tipo,
    tempo=None
):

    if tempo is None:
        tempo = agora()

    return {
        "dataAtualizacao": tempo,
        "codigo": codigo,
        "origem": origem,
        "destino": "",
        "mensagem":
            f"{usina} | Liberação Total de Geração {tipo}",
        "status": "finalizada",
        "dataCadastro": tempo,
        "motivo": "Energético (Controle de Frequência)",
        "informacaoAdicional": "",
        "idLocalOperacao": "SIMULADO"
    }


def enviar(evento):

    resposta = requests.post(
        URL,
        json=[evento],
        verify=False,
        timeout=10
    )

    print(
        resposta.status_code,
        resposta.text
    )


def simular_patamar(
    usina,
    origem,
    partida,
    limite,
    tipo,
    horario
):

    codigo = novo_codigo()
    tempo = horario_simulado(horario)

    print("\n==============================")
    print("NOVO PATAMAR")
    print("==============================")
    print(f"Usina:    {usina}")
    print(f"Horário:  {horario}")
    print(f"Partida:  {partida} MW")
    print(f"Limite:   {limite} MW")
    print(f"Código:   {codigo}")
    print("==============================")

    # 1 - chegada da restrição
    enviar(
        evento_restricao(
            codigo,
            usina,
            origem,
            partida,
            limite,
            tipo,
            "pendente",
            tempo
        )
    )

    time.sleep(2)

    # 2 - operador confirma
    enviar(
        evento_restricao(
            codigo,
            usina,
            origem,
            partida,
            limite,
            tipo,
            "confirmada",
            tempo
        )
    )


def simular_liberacao(
    usina,
    origem,
    tipo
):

    codigo = novo_codigo()
    tempo = agora()

    print("\n==============================")
    print("LIBERAÇÃO TOTAL")
    print("==============================")
    print(f"Usina: {usina}")
    print("==============================")

    enviar(
        evento_liberacao(
            codigo,
            usina,
            origem,
            tipo,
            tempo
        )
    )


if __name__ == "__main__":

    # ============================================================
    # 10 PATAMARES - MESMOS HORÁRIOS PARA AS DUAS PLANTAS
    # ============================================================

    horarios = [
        "06:00",
        "07:30",
        "09:00",
        "10:30",
        "12:00",
        "14:00",
        "16:00",
        "18:00",
        "20:00",
        "22:00"
    ]


    # ============================================================
    # VENTO NORTE
    # Máximo: 80 MW
    # ============================================================

    vento_norte = [
        (25, 20),
        (35, 28),
        (45, 35),
        (55, 42),
        (65, 50),
        (72, 58),
        (80, 65),
        (70, 55),
        (60, 45),
        (40, 30)
    ]


    # ============================================================
    # SERRA AZUL
    # Máximo: 180 MW
    # ============================================================

    serra_azul = [
        (60, 45),
        (80, 60),
        (110, 85),
        (135, 100),
        (155, 120),
        (180, 140),
        (170, 130),
        (150, 115),
        (120, 90),
        (80, 60)
    ]


    # ============================================================
    # PATAMARES - VENTO NORTE
    # ============================================================

    for horario, (partida, limite) in zip(
        horarios,
        vento_norte
    ):

        simular_patamar(
            "Conj. Vento Norte",
            "NE",
            partida,
            limite,
            "Eólica",
            horario
        )

        time.sleep(1)


    # ============================================================
    # PATAMARES - SERRA AZUL
    # ============================================================

    for horario, (partida, limite) in zip(
        horarios,
        serra_azul
    ):

        simular_patamar(
            "Complexo Serra Azul",
            "SE",
            partida,
            limite,
            "Fotovoltaica",
            horario
        )

        time.sleep(1)


    # ============================================================
    # LIBERAÇÃO TOTAL
    # SOMENTE APÓS OS 10 PATAMARES DAS DUAS PLANTAS
    # ============================================================

    simular_liberacao(
        "Conj. Vento Norte",
        "NE",
        "Eólica"
    )

    time.sleep(2)

    simular_liberacao(
        "Complexo Serra Azul",
        "SE",
        "Fotovoltaica"
    )