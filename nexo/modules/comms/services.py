"""
Serviços principais do módulo COMMS.

Este arquivo concentra o processamento das solicitações
de comunicação recebidas pelo módulo.
"""

from nexo.modules.comms.logger import (
    log_info,
    log_warn,
    log_error,
)

import asyncio
from typing import Any

from nexo.modules.comms.message import MensagemComms
from nexo.modules.comms.queue import fila_comunicacao

from nexo.modules.comms.config_service import (
    obter_config,
    obter_template,
)

from nexo.modules.comms.gateway import (
    enviar_mensagem,
    obter_grupos,
)


# ============================================================
# PROCESSADOR DE MENSAGENS DO COMMS
# ============================================================

def processar_mensagem(dados: Any):

    mensagem = MensagemComms(
        canal=dados["canal"],
        destino=dados["destino"],
        mensagem=dados.get("mensagem", ""),
        dados=dados.get("dados"),
    )

    return mensagem


# ============================================================
# GERADOR DE MENSAGENS
# ============================================================

def gerar_mensagem(evento: dict[str, Any]) -> str:
    """
    Gera a mensagem de comunicação a partir de um evento
    operacional recebido pelo COMMS.

    Os templates são carregados diretamente do banco de dados.
    """

    tipo_evento = evento.get("evento")

    id_local_operacao = evento.get(
        "idLocalOperacao"
    )

    # --------------------------------------------------------
    # HORÁRIO
    # --------------------------------------------------------

    data_recebimento = evento.get(
        "dataRecebimento",
        "",
    )

    if not data_recebimento:
        return ""

    hora = data_recebimento[11:16]

    hora_formatada = (
        hora[:2] + "h" + hora[3:] + "min"
    )

    # --------------------------------------------------------
    # LIBERAÇÃO TOTAL
    # --------------------------------------------------------

    if tipo_evento == "LIBERACAO":

        template = obter_template(
            tipo_evento="LIBERACAO_TOTAL",
            id_local_operacao=id_local_operacao,
        )

        if not template:
            log_error(
                "Nenhum template encontrado "
                "para LIBERACAO_TOTAL."
            )
            return ""

        return template.format(
            hora=hora,
            hora_formatada=hora_formatada,
            origem=evento.get(
                "origem",
                "",
            ),
            apelido=evento.get(
                "apelido",
                "",
            ),
            apelido_maiusculo=evento.get(
                "apelido",
                "",
            ).upper(),
            capacidade=evento.get(
                "capacidade",
                "",
            ),
            tipo_geracao=evento.get(
                "tipo_geracao",
                "",
            ),
            regiao=evento.get(
                "regiao",
                "",
            ),
            motivo=evento.get(
                "motivo",
                "",
            ),
            potencia_restricao=evento.get(
                "potencia_restricao",
                "",
            ),
            potencia_observada=evento.get(
                "potencia_observada",
                "",
            ),
            informacao_adicional=evento.get(
                "informacaoAdicional",
                "",
            ),
        )

    # --------------------------------------------------------
    # RESTRIÇÃO
    # --------------------------------------------------------

    if tipo_evento == "RESTRICAO":

        apelido = evento.get(
            "apelido",
            "",
        )

        informacao_adicional = evento.get(
            "informacaoAdicional",
            "",
        ).strip()

        if informacao_adicional:
            informacao_formatada = (
                f"Informação: "
                f"{informacao_adicional}\n"
            )
        else:
            informacao_formatada = ""

        template = obter_template(
            tipo_evento="RESTRICAO",
            id_local_operacao=id_local_operacao,
        )

        if not template:
            log_error(
                "Nenhum template encontrado "
                "para RESTRICAO."
            )
            return ""

        return template.format(
            apelido=apelido,
            apelido_maiusculo=apelido.upper(),
            hora=hora,
            hora_formatada=hora_formatada,
            origem=evento.get(
                "origem",
                "",
            ),
            potencia_restricao=evento.get(
                "potencia_restricao",
                "",
            ),
            potencia_observada=evento.get(
                "potencia_observada",
                "",
            ),
            capacidade=evento.get(
                "capacidade",
                "",
            ),
            tipo_geracao=evento.get(
                "tipo_geracao",
                "",
            ),
            regiao=evento.get(
                "regiao",
                "",
            ),
            motivo=evento.get(
                "motivo",
                "",
            ),
            informacao_adicional=informacao_formatada,
        )

    # --------------------------------------------------------
    # EVENTO DESCONHECIDO
    # --------------------------------------------------------

    log_warn(
        "Tipo de evento desconhecido: "
        f"{tipo_evento}"
    )

    return ""


# ============================================================
# RECEBIMENTO DE RESTRIÇÕES
# ============================================================

def receber_restricao(
    evento: dict[str, Any],
):
    """
    Recebe um evento confirmado pelo SINAPSE
    e coloca a comunicação na fila.
    """

    # O COMMS só deve agir quando o SINAPSE informar
    # que esta confirmação acabou de acontecer.

    if not evento.get(
        "confirmada_agora",
        False,
    ):
        return

    id_local_operacao = evento.get(
        "idLocalOperacao",
        "",
    )

    log_info(
        "Restrição confirmada recebida. "
        f"Usina: {id_local_operacao}."
    )

    # Coloca a confirmação na fila sem bloquear
    # o EventBus.

    fila_comunicacao.adicionar(evento)


# ============================================================
# WORKER DA FILA DE COMUNICAÇÃO
# ============================================================

async def processar_fila_comunicacao():

    while True:

        evento = await fila_comunicacao.obter()

        try:

            config = obter_config()

            # ------------------------------------------------
            # COMMS DESLIGADO
            # ------------------------------------------------

            if not config.ativo:
                continue

            # ------------------------------------------------
            # TEMPO DE ESPERA
            # ------------------------------------------------

            if config.tempo_espera > 0:

                await asyncio.sleep(
                    config.tempo_espera
                )

            # ------------------------------------------------
            # GERA MENSAGEM
            # ------------------------------------------------

            mensagem = gerar_mensagem(
                evento
            )

            if not mensagem:
                continue

            # ------------------------------------------------
            # IDENTIFICA OS GRUPOS
            # ------------------------------------------------

            id_local_operacao = evento.get(
                "idLocalOperacao"
            )

            if not id_local_operacao:

                log_warn(
                    "Evento sem idLocalOperacao. "
                    "Mensagem não enviada."
                )

                continue

            grupos = obter_grupos(
                id_local_operacao
            )

            if not grupos:

                log_warn(
                    "Nenhum grupo configurado para "
                    f"{id_local_operacao}. "
                    "Mensagem não enviada."
                )

                continue

            # ------------------------------------------------
            # ENVIA PARA TODOS OS GRUPOS
            # ------------------------------------------------

            resultados = []

            for grupo in grupos:

                enviada = enviar_mensagem(
                    grupo=grupo,
                    mensagem=mensagem,
                )

                resultados.append(
                    enviada
                )

            # ------------------------------------------------
            # LOG
            # ------------------------------------------------

            log_info(
                "Mensagem processada. "
                f"Usina: {id_local_operacao}. "
                f"Grupos: {len(grupos)}."
            )

            for indice, enviada in enumerate(
                resultados,
                start=1,
            ):
                if enviada:
                    log_info(
                        f"Grupo {indice}: Gateway aceitou."
                    )
                else:
                    log_warn(
                        f"Grupo {indice}: Gateway recusou."
                    )

        finally:

            fila_comunicacao.concluir()