"""
Cliente HTTP do WhatsApp Gateway.

O COMMS utiliza este módulo apenas para entregar
mensagens ao Gateway local.
"""

import requests

from typing import Any

from nexo.modules.comms.logger import (
    log_info,
    log_warn,
    log_error,
)


GATEWAY_URL = (
    "http://127.0.0.1:8100/messages"
)

GATEWAY_STATUS_URL = (
    "http://127.0.0.1:8100/status"
)

GATEWAY_QR_URL = (
    "http://127.0.0.1:8100/qr"
)

GATEWAY_RECONNECT_URL = (
    "http://127.0.0.1:8100/reconnect"
)

GATEWAY_RESET_URL = (
    "http://127.0.0.1:8100/reset"
)

# ============================================================
# ENVIO PARA O WHATSAPP GATEWAY
# ============================================================

def enviar_mensagem(
    grupo: str,
    mensagem: str,
) -> bool:
    """
    Envia uma mensagem para o WhatsApp Gateway.

    Retorna True quando o Gateway aceita a mensagem
    e False quando ocorre qualquer falha de comunicação
    ou resposta HTTP diferente de 2xx.
    """

    log_info(
        "Enviando mensagem ao Gateway. "
        f"Grupo: {grupo}."
    )

    try:

        resposta = requests.post(
            GATEWAY_URL,
            json={
                "grupo": grupo,
                "mensagem": mensagem,
            },
            timeout=5,
        )

        # ----------------------------------------------------
        # GATEWAY ACEITOU
        # ----------------------------------------------------

        if 200 <= resposta.status_code < 300:

            log_info(
                "Gateway aceitou a mensagem. "
                f"Grupo: {grupo}. "
                f"HTTP {resposta.status_code}."
            )

            return True

        # ----------------------------------------------------
        # GATEWAY RECUSOU
        # ----------------------------------------------------

        log_warn(
            "Gateway recusou a mensagem. "
            f"Grupo: {grupo}. "
            f"HTTP {resposta.status_code}."
        )

        return False

    # --------------------------------------------------------
    # FALHA DE COMUNICAÇÃO
    # --------------------------------------------------------

    except requests.RequestException as erro:

        log_error(
            "Falha ao comunicar com o Gateway. "
            f"Grupo: {grupo}.",
            erro,
        )

        return False

# ============================================================
# STATUS DO WHATSAPP GATEWAY
# ============================================================

def obter_status_gateway() -> dict[str, Any] | None:
    """
    Consulta o estado atual do WhatsApp Gateway.

    Retorna os dados do Gateway quando a comunicação
    é possível. Retorna None quando ocorre uma falha.
    """

    try:

        resposta = requests.get(
            GATEWAY_STATUS_URL,
            timeout=5,
        )

        dados = resposta.json()

        if resposta.status_code == 200:

            log_info(
                "Gateway WhatsApp consultado. "
                f"Status: "
                f"{dados.get('whatsapp', {}).get('status')}."
            )

            return dados

        log_warn(
            "Gateway WhatsApp retornou estado "
            f"não saudável. "
            f"HTTP {resposta.status_code}."
        )

        return dados

    except requests.RequestException as erro:

        log_error(
            "Falha ao consultar o status "
            "do WhatsApp Gateway.",
            erro,
        )

        return None

    except ValueError as erro:

        log_error(
            "Gateway WhatsApp retornou uma "
            "resposta JSON inválida.",
            erro,
        )

        return None

# ============================================================
# COLETAR QRCODE DO WHATSAPP GATEWAY
# ============================================================

def obter_qr_gateway() -> dict[str, Any] | None:
    """
    Consulta o QR Code atual do WhatsApp Gateway.

    Retorna os dados do Gateway quando a comunicação
    é possível. Retorna None quando ocorre uma falha.
    """

    try:

        resposta = requests.get(
            GATEWAY_QR_URL,
            timeout=5,
        )

        if not (
            200 <= resposta.status_code < 300
        ):
            log_warn(
                "Gateway WhatsApp recusou consulta "
                f"ao QR Code. "
                f"HTTP {resposta.status_code}."
            )

            return None

        dados = resposta.json()

        return dados

    except requests.RequestException as erro:

        log_error(
            "Falha ao consultar o QR Code "
            "do WhatsApp Gateway.",
            erro,
        )

        return None

    except ValueError as erro:

        log_error(
            "Gateway WhatsApp retornou uma "
            "resposta JSON inválida para o QR Code.",
            erro,
        )

        return None

# ============================================================
# CONTROLE DA CONEXÃO WHATSAPP
# ============================================================

def reconectar_gateway() -> dict[str, Any] | None:
    """
    Solicita ao WhatsApp Gateway uma reinicialização
    da conexão, mantendo a sessão autenticada.
    """

    try:

        resposta = requests.post(
            GATEWAY_RECONNECT_URL,
            timeout=10,
        )

        if not (
            200 <= resposta.status_code < 300
        ):
            log_warn(
                "Gateway WhatsApp recusou "
                "a reconexão. "
                f"HTTP {resposta.status_code}."
            )

            return None

        dados = resposta.json()

        log_info(
            "Reconexão do WhatsApp Gateway "
            "solicitada com sucesso."
        )

        return dados

    except requests.RequestException as erro:

        log_error(
            "Falha ao solicitar reconexão "
            "do WhatsApp Gateway.",
            erro,
        )

        return None

    except ValueError as erro:

        log_error(
            "Gateway WhatsApp retornou uma "
            "resposta JSON inválida na reconexão.",
            erro,
        )

        return None


def resetar_gateway() -> dict[str, Any] | None:
    """
    Solicita ao WhatsApp Gateway o reset completo
    da sessão autenticada.

    O Gateway removerá o diretório de autenticação
    e iniciará um novo pareamento por QR Code.
    """

    try:

        resposta = requests.post(
            GATEWAY_RESET_URL,
            timeout=10,
        )

        if not (
            200 <= resposta.status_code < 300
        ):
            log_warn(
                "Gateway WhatsApp recusou "
                "o reset da sessão. "
                f"HTTP {resposta.status_code}."
            )

            return None

        dados = resposta.json()

        log_warn(
            "Reset da sessão do WhatsApp Gateway "
            "solicitado com sucesso."
        )

        return dados

    except requests.RequestException as erro:

        log_error(
            "Falha ao solicitar reset da sessão "
            "do WhatsApp Gateway.",
            erro,
        )

        return None

    except ValueError as erro:

        log_error(
            "Gateway WhatsApp retornou uma "
            "resposta JSON inválida no reset.",
            erro,
        )

        return None

# ============================================================
# GRUPOS WHATSAPP POR USINA
# ============================================================

# Código do SINapse no lugar da usina - é o código interno da usina no ONS
# da pra pegar em um post do sinapse, ou usando reverse no post pelo site
# pelo SINtegre da pra coletar também, basta ter o nome do agente, exemplo:
# Nome: Conj. Vento Grande
# código interno: VENGR233
#
# Para enviar a mensagem, o código deve estar cadastrado no módulo ativos.

GRUPOS_USINAS = {

    # Usina envia para DOIS grupos.
    "USINADUPLA": [
        "xxxxxxxxx-xxxxxxxxx@g.us",
        "xxxxxxxxxxxxxxx@g.us",
    ],

    # Usina envia para grupo.
    "USINA1": [
        "xxxxxxxxxxxxx-xxxxxxx@g.us",
    ],

    "USINA2": [
        "xxxxxxxxxxxxx-xxxxxxx@g.us",
    ],

}


# ============================================================
# OBTÉM OS GRUPOS DA USINA
# ============================================================

def obter_grupos(
    id_local_operacao: str,
) -> list[str]:
    """
    Retorna todos os grupos WhatsApp associados
    à usina.
    """

    return GRUPOS_USINAS.get(
        id_local_operacao,
        [],
    )