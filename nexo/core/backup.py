"""
Rotina de backup automático do banco de dados SQLite do NEXO.
"""

import asyncio
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("nexo.core.backup")

# Diretório onde os backups serão guardados
BACKUPS_DIR = Path("backups")
BACKUPS_DIR.mkdir(exist_ok=True)


def realizar_backup_sqlite(db_path: str = "nexo.db") -> Path | None:
    """
    Realiza um snapshot seguro do SQLite utilizando a API nativa de backup.
    """
    origem_path = Path(db_path)
    if not origem_path.exists():
        # Fallback para o nome legado se existir
        if Path("sinapse.db").exists():
            origem_path = Path("sinapse.db")
        else:
            logger.warning("Banco de dados SQLite não encontrado para backup.")
            return None

    hoje = datetime.now().strftime("%Y-%m-%d")
    destino_path = BACKUPS_DIR / f"nexo_backup_{hoje}.db"

    try:
        con_origem = sqlite3.connect(str(origem_path))
        con_destino = sqlite3.connect(str(destino_path))

        with con_destino:
            con_origem.backup(con_destino)

        con_origem.close()
        con_destino.close()

        logger.info(f"Backup diário concluído com sucesso: {destino_path}")
        return destino_path
    except Exception as e:
        logger.error(f"Erro ao realizar backup do SQLite: {e}")
        return None


async def worker_backup_diario():
    """
    Tarefa em segundo plano que executa o backup uma vez ao dia.
    """
    # Executa um backup inicial seguro ao subir o sistema
    await asyncio.to_thread(realizar_backup_sqlite)

    while True:
        # Aguarda 24 horas (86400 segundos) para o próximo backup
        await asyncio.sleep(86400)
        await asyncio.to_thread(realizar_backup_sqlite)
