"""
Serviço de sincronização de usinas e Programação Diária de Produção (PDP) via API do ONS.
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from nexo.modules.ons.client import ons_client
from nexo.modules.ons.models import ONSUsinaRepresentada, ONSPDP

logger = logging.getLogger("nexo.modules.ons.pdp_sync")


def sincronizar_catalogo_usinas_ons(db_ons: Session) -> list[dict]:

    res = ons_client.requisicao("GET", "/programacao/usina/ListarUsinasRepresentadas")
    if not res or res.status_code != 200:
        logger.warning("Não foi possível listar usinas representadas no ONS.")
        return []

    dados = res.json()
    usinas_ons = dados.get("Usinas", [])
    
    for item in usinas_ons:
        codigo = item.get("Codigo")
        nome = item.get("Nome")
        tipo = item.get("Tipo")

        if not codigo:
            continue

        usina_existente = db_ons.query(ONSUsinaRepresentada).filter_by(codigo=codigo).first()
        if usina_existente:
            usina_existente.nome = nome
            usina_existente.tipo = tipo
        else:
            db_ons.add(ONSUsinaRepresentada(codigo=codigo, nome=nome, tipo=tipo))

    db_ons.commit()
    logger.info(f"{len(usinas_ons)} usinas do ONS sincronizadas com sucesso.")
    return usinas_ons


def sincronizar_curva_pdp_dia(data_str: str, db_ons: Session, db_nexo: Session) -> int:
    """
    Coleta os 48 patamares de geração programada para as usinas ativas do NEXO.
    data_str formato: YYYY-MM-DD
    """
    from nexo.modules.ativos.models import Ativo

    data_dt = datetime.strptime(data_str, "%Y-%m-%d")
    
    # 1. Pega os códigos ONS das usinas cadastradas no nexo.db
    ativos = db_nexo.query(Ativo).filter(Ativo.ativo.is_(True)).all()
    codigos_ons = [str(getattr(a, "id_local_operacao")) for a in ativos if getattr(a, "id_local_operacao", None) is not None and str(getattr(a, "id_local_operacao")) != ""]

    if not codigos_ons:
        logger.info("Nenhum ativo com código ONS (id_local_operacao) cadastrado no NEXO.")
        return 0

    params = {
        "request.ano": data_dt.year,
        "request.mes": data_dt.month,
        "request.dia": data_dt.day,
        "request.numeroPaginacao": 1,
        "request.quantidadePagina": 100,
    }

    res = ons_client.requisicao("GET", "/programacao/usina/ListarGeracaoPropostaGET", params=params)
    if not res or res.status_code != 200:
        logger.warning(f"Falha ao consultar geração proposta PDP para {data_str}")
        return 0

    dados = res.json()
    # A estrutura retorna lista de itens de insumo com os patamares
    itens = dados.get("Itens", []) or dados.get("Insumos", []) or []
    salvos = 0

    for item in itens:
        codigo_usina = item.get("CodigoUsina") or item.get("Codigo")
        patamares = item.get("Patamares", [])

        for p in patamares:
            numero = p.get("PatamarNumero") or p.get("Numero")
            hora = p.get("PatamarHora") or p.get("Hora") or f"{numero}:00"
            valor = float(p.get("PatamarValor_PRE") or p.get("Valor") or 0.0)

            registro = (
                db_ons.query(ONSPDP)
                .filter_by(data=data_str, codigo_usina=codigo_usina, patamar_numero=numero)
                .first()
            )

            if registro:
                setattr(registro, "potencia_programada", valor)
            else:
                db_ons.add(
                    ONSPDP(
                        data=data_str,
                        codigo_usina=str(codigo_usina),
                        patamar_numero=int(numero),
                        patamar_hora=str(hora),
                        potencia_programada=float(valor),
                    )
                )

            salvos += 1

    db_ons.commit()
    logger.info(f"{salvos} patamares de PDP salvos no ons.db para a data {data_str}.")
    return salvos
