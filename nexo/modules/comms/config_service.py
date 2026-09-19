"""
Serviço de configuração do módulo COMMS.

Centraliza a leitura e gravação das configurações e templates
persistidos no banco de dados.
"""

from typing import Optional

from nexo.core.db import SessionLocal

from nexo.modules.comms.models import (
    CommsConfig,
    CommsTemplate,
)


# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================

def obter_config() -> CommsConfig:
    """
    Retorna a configuração atual do COMMS.

    Caso ainda não exista uma configuração no banco,
    cria a configuração padrão.
    """

    db = SessionLocal()

    try:
        config = db.query(CommsConfig).first()

        if config is None:
            config = CommsConfig(
                ativo=False,
                tempo_espera=5,
            )

            db.add(config)
            db.commit()
            db.refresh(config)

        return config

    finally:
        db.close()


def salvar_config(
    ativo: bool,
    tempo_espera: int,
) -> CommsConfig:
    """
    Atualiza a configuração geral do COMMS.
    """

    db = SessionLocal()

    try:
        config = db.query(CommsConfig).first()

        if config is None:
            config = CommsConfig()

            db.add(config)

        config.ativo = ativo
        config.tempo_espera = tempo_espera

        db.commit()
        db.refresh(config)

        return config

    finally:
        db.close()


def comms_ativo() -> bool:
    """
    Retorna True quando o COMMS está habilitado.
    """

    config = obter_config()

    return config.ativo


def obter_tempo_espera() -> int:
    """
    Retorna o tempo de espera configurado para o COMMS.
    """

    config = obter_config()

    return config.tempo_espera


# ============================================================
# TEMPLATES
# ============================================================

def obter_template(
    tipo_evento: str,
    id_local_operacao: Optional[str] = None,
) -> Optional[str]:
    """
    Obtém o template correspondente ao evento.

    Primeiro procura um template específico para a usina.

    Caso não exista, procura o template padrão.
    """

    db = SessionLocal()

    try:

        if id_local_operacao:
            template = (
                db.query(CommsTemplate)
                .filter(
                    CommsTemplate.tipo_evento == tipo_evento,
                    CommsTemplate.id_local_operacao
                    == id_local_operacao,
                )
                .first()
            )

            if template:
                return template.template

        template = (
            db.query(CommsTemplate)
            .filter(
                CommsTemplate.tipo_evento == tipo_evento,
                CommsTemplate.id_local_operacao.is_(None),
            )
            .first()
        )

        if template:
            return template.template

        return None

    finally:
        db.close()


def salvar_template(
    tipo_evento: str,
    template: str,
    id_local_operacao: Optional[str] = None,
) -> CommsTemplate:
    """
    Cria ou atualiza um template.

    id_local_operacao=None representa o template padrão.
    """

    db = SessionLocal()

    try:

        consulta = (
            db.query(CommsTemplate)
            .filter(
                CommsTemplate.tipo_evento == tipo_evento,
            )
        )

        if id_local_operacao is None:
            consulta = consulta.filter(
                CommsTemplate.id_local_operacao.is_(None)
            )
        else:
            consulta = consulta.filter(
                CommsTemplate.id_local_operacao
                == id_local_operacao
            )

        registro = consulta.first()

        if registro is None:
            registro = CommsTemplate(
                tipo_evento=tipo_evento,
                id_local_operacao=id_local_operacao,
                template=template,
            )

            db.add(registro)

        else:
            registro.template = template

        db.commit()
        db.refresh(registro)

        return registro

    finally:
        db.close()

# ============================================================
# INICIALIZAÇÃO
# ============================================================

def inicializar_config():
    """
    Garante que a configuração inicial do COMMS exista no banco.

    Não sobrescreve configurações já existentes.
    """

    db = SessionLocal()

    try:
        config = db.query(CommsConfig).first()

        if config is None:
            config = CommsConfig(
                ativo=False,
                tempo_espera=5,
            )

            db.add(config)

        # ----------------------------------------------------
        # Template padrão de restrição
        # ----------------------------------------------------

        template_restricao = (
            db.query(CommsTemplate)
            .filter(
                CommsTemplate.tipo_evento == "RESTRICAO",
                CommsTemplate.id_local_operacao.is_(None),
            )
            .first()
        )

        if template_restricao is None:
            db.add(
                CommsTemplate(
                    tipo_evento="RESTRICAO",
                    id_local_operacao=None,
                    template=(
                        "*{apelido}*;\n"
                        "Às {hora} {origem} solicita restrição "
                        "de potência em {potencia_restricao} MW;\n"
                        "Geração anterior: "
                        "{potencia_observada} MW;\n"
                        "Motivo: {motivo};"
                    ),
                )
            )

        # ----------------------------------------------------
        # Template padrão de liberação total
        # ----------------------------------------------------

        template_liberacao = (
            db.query(CommsTemplate)
            .filter(
                CommsTemplate.tipo_evento == "LIBERACAO_TOTAL",
                CommsTemplate.id_local_operacao.is_(None),
            )
            .first()
        )

        if template_liberacao is None:
            db.add(
                CommsTemplate(
                    tipo_evento="LIBERACAO_TOTAL",
                    id_local_operacao=None,
                    template=(
                        "Às {hora} {origem} solicita o FIM "
                        "da restrição de potência ativa."
                    ),
                )
            )

        db.commit()

    finally:
        db.close()