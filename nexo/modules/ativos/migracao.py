"""
Migração inicial dos ativos para o banco de dados do NEXO.

Este script copia os ativos atualmente definidos em data.py
para a tabela "ativos".

A migração é segura para execução repetida:
ativos já existentes não são alterados.
"""

from nexo.core.db import SessionLocal
from nexo.modules.ativos.data import USINAS
from nexo.modules.ativos.models import Ativo


def migrar_ativos():
    """
    Migra os ativos definidos em data.py para o banco.

    Registros existentes são preservados.
    """

    db = SessionLocal()

    criados = 0
    ignorados = 0

    try:

        print("")
        print("=" * 60)
        print("ATIVOS -> MIGRAÇÃO INICIAL")
        print("=" * 60)

        for chave, usina in USINAS.items():

            # ------------------------------------------------
            # VERIFICA SE O ATIVO JÁ EXISTE
            # ------------------------------------------------

            ativo_existente = (
                db.query(Ativo)
                .filter(
                    Ativo.nome == usina.nome
                )
                .first()
            )

            if ativo_existente:

                print(
                    f"[IGNORADO] {usina.nome} "
                    f"(já existe no banco)"
                )

                ignorados += 1

                continue

            # ------------------------------------------------
            # CRIA O ATIVO
            # ------------------------------------------------

            ativo = Ativo(
                nome=usina.nome,
                apelido=usina.apelido,
                id_local_operacao=None,
                capacidade=usina.capacidade,
                tipo=usina.tipo,
                regiao=usina.regiao,
                empresa=usina.empresa,
                logo=usina.logo,
                ativo=usina.ativa,
                cor=usina.cor,
            )

            db.add(ativo)

            print(
                f"[CRIADO] {usina.nome}"
            )

            criados += 1

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        db.commit()

        print("")
        print("-" * 60)
        print(
            f"Processamento concluído. "
            f"{len(USINAS)} ativo(s) processado(s)."
        )
        print(
            f"  Criados:   {criados}"
        )
        print(
            f"  Ignorados: {ignorados}"
        )
        print("-" * 60)
        print("")

    except Exception:

        db.rollback()

        print("")
        print(
            "[ERRO] A migração falhou. "
            "Nenhuma alteração foi confirmada no banco."
        )
        print("")

        raise

    finally:

        db.close()


if __name__ == "__main__":
    migrar_ativos()