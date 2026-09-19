"""
Logger do módulo COMMS.

Mantém um arquivo de log separado por dia para o módulo
de comunicação do NEXO.
"""

from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO
# ============================================================

DIRETORIO_LOGS = (
    Path(__file__).resolve().parents[3]
    / "logs"
    / "comms"
)


# ============================================================
# ARQUIVO DO DIA
# ============================================================

def obter_arquivo_log() -> Path:
    """
    Retorna o arquivo de log correspondente ao dia atual.
    """

    DIRETORIO_LOGS.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = datetime.now().strftime(
        "%Y-%m-%d"
    )

    return DIRETORIO_LOGS / f"{data}.log"


# ============================================================
# ESCRITA
# ============================================================

def _registrar(
    nivel: str,
    mensagem: str,
):
    """
    Registra uma mensagem no log diário do COMMS.
    """

    agora = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    linha = (
        f"{agora} "
        f"[{nivel}] "
        f"[COMMS] "
        f"{mensagem}\n"
    )

    arquivo = obter_arquivo_log()

    with arquivo.open(
        "a",
        encoding="utf-8",
    ) as log:
        log.write(linha)


# ============================================================
# NÍVEIS
# ============================================================

def log_info(mensagem: str):
    _registrar(
        "INFO",
        mensagem,
    )


def log_warn(mensagem: str):
    _registrar(
        "WARN",
        mensagem,
    )


def log_error(
    mensagem: str,
    erro: Exception | None = None,
):
    if erro is not None:
        mensagem = (
            f"{mensagem} "
            f"Erro: {erro}"
        )

    _registrar(
        "ERROR",
        mensagem,
    )