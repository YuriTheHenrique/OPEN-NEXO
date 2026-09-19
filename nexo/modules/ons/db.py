from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ONS_DB_URL = f"sqlite:///{DATA_DIR / 'ons.db'}"

engine_ons = create_engine(
    ONS_DB_URL,
    connect_args={"check_same_thread": False}
)

SessionLocalONS = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_ons
)

BaseONS = declarative_base()


def criar_tabelas_ons():
    """
    Cria todas as tabelas do módulo ONS no banco dedicado ons.db.
    """
    from nexo.modules.ons import models  # Garante o carregamento dos models
    BaseONS.metadata.create_all(bind=engine_ons)
