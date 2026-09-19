"""
Configurações do módulo ONS / SINtegre.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("nexo.modules.ons.config")

CONFIG_FILE = Path(__file__).resolve().parent / "config.json"

CONFIG_PADRAO = {
    "base_url": "https://api.ons.org.br",
    "usuario": "",
    "senha": "",
    "intervalo_sincronizacao_segundos": 300,
    "ativo": True,
}


def carregar_config() -> dict:
    """
    Carrega o arquivo de configuração JSON do ONS.
    Se não existir, cria o arquivo com a estrutura padrão.
    """
    if not CONFIG_FILE.exists():
        salvar_config(CONFIG_PADRAO)
        return CONFIG_PADRAO.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar {CONFIG_FILE}: {e}")
        return CONFIG_PADRAO.copy()


def salvar_config(dados: dict) -> None:
    """
    Salva os dados no arquivo config.json.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao salvar {CONFIG_FILE}: {e}")
