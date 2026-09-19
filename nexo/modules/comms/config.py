"""
Configurações do módulo COMMS.
"""

TEMPO_ESPERA_COMUNICACAO = 5

# ============================================================
# TEMPLATE PADRÃO DE RESTRIÇÃO
# ============================================================

TEMPLATE_RESTRICAO_PADRAO = (
    "*{apelido}*;\n"
    "Às {hora} {origem} solicita restrição "
    "de potência em {potencia_restricao} MW;\n"
    "Geração anterior: {potencia_observada} MW;\n"
    "Motivo: {motivo};"
)


# ============================================================
# TEMPLATE DE LIBERAÇÃO TOTAL
# ============================================================

TEMPLATE_LIBERACAO_TOTAL = (
    "Às {hora} {origem} "
    "solicita o FIM da restrição de potência ativa."
)


# ============================================================
# TEMPLATES ESPECÍFICOS POR USINA
# ============================================================

TEMPLATES_USINAS = {
    "MGVST1": (
        "*{apelido}*;\n"
        "Às {hora}\n"
        "Origem: {origem}\n"
        "Limite: {potencia_restricao} MW\n"
        "Geração anterior: {potencia_observada} MW\n"
        "Motivo: {motivo};"
    ),
}