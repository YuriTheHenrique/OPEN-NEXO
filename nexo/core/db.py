"""
Banco de dados central do NEXO.

Todos os módulos devem importar Base, SessionLocal e engine apenas deste arquivo.
"""

from app.database import engine, SessionLocal, Base
from nexo.core.loader import carregar_modelos_bd

def init_database():
    # Carrega dinamicamente todos os models.py dos módulos antes de criar as tabelas
    carregar_modelos_bd()
    Base.metadata.create_all(bind=engine)

__all__ = [
    "engine",
    "SessionLocal",
    "Base",
]
