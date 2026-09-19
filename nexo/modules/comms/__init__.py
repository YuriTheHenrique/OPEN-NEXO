"""
COMMS - Communication Module

Módulo responsável pelas comunicações externas do NEXO.

O COMMS recebe solicitações de comunicação através do EventBus
e posteriormente encaminha essas mensagens para os canais
configurados, como WhatsApp, e-mail, Teams e outros.

Os módulos de origem não precisam conhecer a implementação
dos canais de comunicação.
"""
