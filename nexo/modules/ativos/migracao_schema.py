"""
Migração do schema da tabela ATIVOS.

Adiciona colunas que foram incorporadas ao model
depois da criação inicial da tabela.
"""

from sqlalchemy import inspect, text

from nexo.core.db import engine


def migrar_schema_ativos():
    """
    Atualiza a estrutura da tabela ativos sem apagar dados.
    """

    inspector = inspect(engine)

    colunas = {
        coluna["name"]
        for coluna in inspector.get_columns("ativos")
    }

    alteracoes = []

    # --------------------------------------------------------
    # COR
    # --------------------------------------------------------

    if "cor" not in colunas:

        alteracoes.append(
            """
            ALTER TABLE ativos
            ADD COLUMN cor VARCHAR
            """
        )

    # --------------------------------------------------------
    # CRIADO_EM
    # --------------------------------------------------------

    if "criado_em" not in colunas:

        alteracoes.append(
            """
            ALTER TABLE ativos
            ADD COLUMN criado_em DATETIME
            """
        )

    # --------------------------------------------------------
    # ATUALIZADO_EM
    # --------------------------------------------------------

    if "atualizado_em" not in colunas:

        alteracoes.append(
            """
            ALTER TABLE ativos
            ADD COLUMN atualizado_em DATETIME
            """
        )

    # --------------------------------------------------------
    # NADA PARA FAZER
    # --------------------------------------------------------

    if not alteracoes:

        print(
            "ATIVOS -> Schema já está atualizado."
        )

        return

    # --------------------------------------------------------
    # APLICA ALTERAÇÕES
    # --------------------------------------------------------

    with engine.begin() as conexao:

        for sql in alteracoes:

            conexao.execute(
                text(sql)
            )

    print(
        "ATIVOS -> Schema atualizado com sucesso."
    )

    for sql in alteracoes:

        print(
            f"  + {sql.strip()}"
        )


if __name__ == "__main__":

    migrar_schema_ativos()