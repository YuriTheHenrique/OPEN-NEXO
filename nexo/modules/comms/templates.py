"""
Templates de mensagens do módulo COMMS.

Este módulo centraliza a obtenção dos modelos de mensagem
utilizados pelo COMMS.

Inicialmente os templates ficam em memória.
Posteriormente os templates poderão ser carregados
de configuração persistente e editados pela interface.
"""

from typing import Any

from nexo.modules.comms.config import TEMPLATE_RESTRICAO_PADRAO

# ============================================================
# TEMPLATES ESPECÍFICOS POR USINA
# ============================================================

# A chave utiliza o idLocalOperacao recebido pelo SINAPSE.

TEMPLATES_USINAS: dict[str, str] = {
    # Exemplo:
    #
    # "MGVST1": (
    #     "*{apelido}*;\n"
    #     f"Às {hora} {origem};\n"
    #     "Limite: {potencia_restricao} MW;\n"
    #     "Geração anterior: {potencia_observada} MW;\n"
    #     "Motivo: {motivo};"
    # ),
}


# ============================================================
# OBTENÇÃO DO TEMPLATE
# ============================================================

def obter_template(evento: dict[str, Any]) -> str:
    """
    Retorna o template correspondente ao evento.

    Para restrições, procura primeiro um template específico
    para a usina através do idLocalOperacao.

    Caso não exista, utiliza o template padrão.
    """

    id_local_operacao = evento.get("idLocalOperacao")

    if id_local_operacao:
        template = TEMPLATES_USINAS.get(id_local_operacao)

        if template:
            return template

    return TEMPLATE_RESTRICAO_PADRAO