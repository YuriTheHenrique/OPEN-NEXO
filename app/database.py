import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker


# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Diretório onde ficam os bancos de dados
DATABASE_DIR = BASE_DIR / "nexo" / "data"

try:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
except OSError as e:
    raise RuntimeError(
        f"Não foi possível criar o diretório do banco de dados: {DATABASE_DIR}"
    ) from e


# Banco padrão do NEXO
DATABASE_PATH = DATABASE_DIR / "nexo.db"

# Permite trocar facilmente para PostgreSQL futuramente
# Exemplo:
# DATABASE_URL=postgresql://usuario:senha@servidor/nexo
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_PATH}"
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Configurações específicas para SQLite.

    São ignoradas automaticamente caso o NEXO utilize
    PostgreSQL no futuro.
    """
    if engine.dialect.name != "sqlite":
        return

    cursor = dbapi_connection.cursor()

    # Habilita integridade referencial
    cursor.execute("PRAGMA foreign_keys=ON;")

    # Melhor concorrência entre leitura e escrita
    cursor.execute("PRAGMA journal_mode=WAL;")

    # Melhor equilíbrio entre desempenho e segurança
    cursor.execute("PRAGMA synchronous=NORMAL;")

    cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()