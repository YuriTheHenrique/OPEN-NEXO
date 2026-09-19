"""Services layer for the dashboard module.

This file contains functions that encapsulate the database
queries and business logic used by the dashboard endpoints.
"""

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from nexo.modules.sinapse.models import Restricao
from nexo.modules.ativos.data import data_hoje
from nexo.modules.ativos.models import Ativo

import io
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

FUSO_OPERACIONAL = ZoneInfo("America/Sao_Paulo")

def filtro_dia_operacional(campo, data):
    """Filtra um campo UTC pelo dia operacional de Brasília."""

    if isinstance(data, str):
        data = date.fromisoformat(data)
    inicio_brt = datetime.combine(
        data,
        time.min,
        tzinfo=FUSO_OPERACIONAL
    )
    fim_brt = inicio_brt + timedelta(days=1)

    inicio_utc = inicio_brt.astimezone(timezone.utc).isoformat()
    fim_utc = fim_brt.astimezone(timezone.utc).isoformat()

    return (
        campo >= inicio_utc,
        campo < fim_utc
    )

def calcular_indicadores(db, data=None):

    if data is None:
        data = data_hoje()

    inicio, fim = filtro_dia_operacional(
        Restricao.dataCadastro,
        data
    )

    total = (
        db.query(Restricao)
        .filter(inicio, fim)
        .count()
    )

    pendentes = (
        db.query(Restricao)
        .filter(
            Restricao.status == "Pendente",
            inicio, fim
        )
        .count()
    )

    confirmadas = (
        db.query(Restricao)
        .filter(
            Restricao.status == "Confirmada",
            inicio, fim
        )
        .count()
    )

    canceladas = (
        db.query(Restricao)
        .filter(
            Restricao.status == "Cancelada",
            inicio, fim
        )
        .count()
    )

    ultima = (
        db.query(Restricao)
        .filter(inicio, fim)
        .order_by(Restricao.id.desc())
        .first()
    )

    return {
        "total": total,
        "pendentes": pendentes,
        "confirmadas": confirmadas,
        "canceladas": canceladas,
        "ultima_atualizacao": (
            ultima.dataAtualizacao
            if ultima
            else None
        )
    }


def listar_usinas_service(db, data=None):

    if data is None:
        data = data_hoje()

    inicio, fim = filtro_dia_operacional(
        Restricao.dataCadastro,
        data
    )

    restricoes = (
        db.query(Restricao)
        .filter(inicio, fim)
        .order_by(Restricao.id.desc())
        .all()
    )

    resultado = {}

    for r in restricoes:

        if r.usina not in resultado:

            resultado[r.usina] = {
                "usina": r.usina,
                "apelido": r.apelido,
                "capacidade": r.capacidade,
                "regiao": r.regiao,
                "tipo_geracao": r.tipo_geracao,
                "evento": r.evento,
                "potencia_observada": r.potencia_observada,
                "potencia_restricao": r.potencia_restricao,
                "status": r.status
            }

    return list(resultado.values())


def grafico_restricoes(db, data=None):

    if data is None:
        data = data_hoje()

    inicio, fim = filtro_dia_operacional(
        Restricao.dataCadastro,
        data
    )

    eventos = (
        db.query(Restricao)
        .filter(inicio, fim)
        .order_by(
            Restricao.dataCadastro.asc()
        )
        .all()
    )

    ativos = db.query(Ativo).all()
    ativos_map = {a.nome: a for a in ativos}
    ativos_map.update({
        a.apelido: a
        for a in ativos
        if a.apelido
    })

    resultado = []

    for evento in eventos:

        cadastro = (
            ativos_map.get(evento.usina)
            or ativos_map.get(evento.apelido)
        )

        if not cadastro:
            continue

        capacidade = float(
            cadastro.capacidade or 0.0
        )

        # Se for LIBERAÇÃO:
        # limite é 100% da usina e corte é zero.
        if evento.evento == "LIBERACAO":

            limite = capacidade
            restricao = 0.0

        elif evento.potencia_restricao is not None:

            limite = float(
                evento.potencia_restricao
            )

            restricao = max(
                0.0,
                round(capacidade - limite, 1)
            )

        else:
            continue

        resultado.append({
            "data": evento.dataCadastro,
            "usina": cadastro.apelido or evento.usina,
            "restricao": restricao,
            "limite": limite,
            "capacidade": capacidade
        })

    return resultado


def historico_usina(
    db,
    usina: str,
    data=None
):
    """Retorna o histórico da usina na data selecionada."""

    if data is None:
        data = data_hoje()

    inicio, fim = filtro_dia_operacional(
        Restricao.dataCadastro,
        data
    )

    eventos = (
        db.query(Restricao)
        .filter(
            Restricao.usina == usina,
            inicio,
            fim
        )
        .order_by(
            Restricao.id.desc()
        )
        .limit(20)
        .all()
    )

    resultado = []

    for evento in eventos:

        resultado.append({
            "data": evento.dataCadastro,
            "status": evento.status,
            "potencia": evento.potencia_restricao
        })

    return resultado


def status_dashboard(db, data=None):
    """Retorna o status do dashboard para a data selecionada."""

    if data is None:
        data = data_hoje()

    inicio, fim = filtro_dia_operacional(
        Restricao.dataCadastro,
        data
    )

    eventos_recebidos = (
        db.query(Restricao)
        .filter(
            Restricao.evento == "RESTRICAO",
            Restricao.status == "Confirmada",
            inicio, fim
        )
        .count()
    )

    restricoes_registradas = (
        db.query(Restricao)
        .filter(
            Restricao.evento == "RESTRICAO",
            inicio, fim
        )
        .count()
    )

    ultima = (
        db.query(Restricao)
        .filter(inicio, fim)
        .order_by(Restricao.id.desc())
        .first()
    )

    usinas = (
        db.query(Restricao.usina)
        .filter(inicio, fim)
        .distinct()
        .count()
    )

    restricoes_confirmadas = (
        db.query(Restricao)
        .filter(
            Restricao.evento == "RESTRICAO",
            Restricao.status == "Confirmada",
            Restricao.dataCadastro.isnot(None),
            inicio, fim
        )
        .order_by(Restricao.dataCadastro.asc())
        .all()
    )

    todos_restricoes = (
        db.query(Restricao)
        .filter(
            Restricao.evento == "RESTRICAO",
            inicio, fim
        )
        .order_by(Restricao.dataCadastro.asc())
        .all()
    )

    intervalos = []

    for anterior, atual in zip(
        restricoes_confirmadas,
        restricoes_confirmadas[1:]
    ):
        try:
            data_anterior = datetime.fromisoformat(
                anterior.dataCadastro.replace("Z", "+00:00")
            )
            data_atual = datetime.fromisoformat(
                atual.dataCadastro.replace("Z", "+00:00")
            )
            diferenca = (
                data_atual - data_anterior
            ).total_seconds()

            if diferenca >= 0:
                intervalos.append(diferenca)

        except (ValueError, AttributeError):
            continue

    if intervalos:
        media_segundos = sum(intervalos) / len(intervalos)
        horas = int(media_segundos // 3600)
        minutos = int((media_segundos % 3600) // 60)
        segundos = int(media_segundos % 60)

        if horas:
            tempo_medio = f"{horas:02d}h {minutos:02d}m"
        else:
            tempo_medio = f"{minutos:02d}m {segundos:02d}s"
    else:
        tempo_medio = "--"

    return {
        "sistema": "ONLINE",
        "eventos_recebidos": eventos_recebidos,
        "usinas_monitoradas": usinas,
        "restricoes_registradas": restricoes_registradas,
        "ultimo_evento": (
            ultima.dataCadastro
            if ultima
            else None
        ),
        "tempo_resposta_medio": tempo_medio
    }


def obter_historico_detalhado(db, data=None, usina=None):
    """
    Retorna a lista completa de eventos e restrições para a tabela de auditoria,
    incluindo os dados originais recebidos do SINAPSE.
    """

    if data is None:
        data = data_hoje()

    campo_data = getattr(
        Restricao,
        "dataCadastro",
        getattr(Restricao, "data_cadastro", None)
    )

    query = db.query(Restricao)

    if campo_data is not None:
        inicio, fim = filtro_dia_operacional(
            campo_data,
            data
        )
        query = query.filter(inicio, fim)

    if usina and usina != "todas":
        query = query.filter(
            (Restricao.usina == usina) |
            (Restricao.apelido == usina)
        )

    if campo_data is not None:
        query = query.order_by(
            campo_data.desc()
        )

    eventos = query.all()

    ativos = db.query(Ativo).all()

    mapa_cap = {
        a.nome: float(a.capacidade or 0.0)
        for a in ativos
    }

    mapa_cap.update({
        a.apelido: float(a.capacidade or 0.0)
        for a in ativos
        if a.apelido
    })

    resultado = []

    for e in eventos:

        data_str = getattr(
            e,
            "dataCadastro",
            getattr(e, "data_cadastro", "")
        ) or ""

        cap = (
            mapa_cap.get(e.usina or "", 0.0)
            or mapa_cap.get(e.apelido or "", 0.0)
            or float(getattr(e, "capacidade", 0) or 0.0)
        )

        pot_restricao = getattr(
            e,
            "potencia_restricao",
            None
        )

        limite = (
            float(pot_restricao)
            if pot_restricao is not None
            else cap
        )

        corte = (
            max(0.0, cap - limite)
            if e.evento == "RESTRICAO"
            else 0.0
        )

        resultado.append({

            # Identificação
            "id": getattr(e, "id", 0),

            # Datas
            "data": str(data_str),
            "data_cadastro": str(data_str),
            "data_atualizacao": getattr(
                e,
                "dataAtualizacao",
                None
            ),
            "data_recebimento": getattr(
                e,
                "dataRecebimento",
                None
            ),

            # Usina
            "usina": (
                e.usina
                or e.apelido
                or "SISTEMA"
            ),

            "apelido": getattr(
                e,
                "apelido",
                None
            ),

            # Evento
            "evento": getattr(
                e,
                "evento",
                "RESTRICAO"
            ),

            "status": getattr(
                e,
                "status",
                "OK"
            ),

            # Potência
            "potencia_observada": getattr(
                e,
                "potencia_observada",
                None
            ),

            "potencia_restricao": round(
                limite,
                2
            ),

            "corte_mw": round(
                corte,
                2
            ),

            "capacidade": round(
                cap,
                2
            ),

            # Tempo
            "tempo_resposta": getattr(
                e,
                "tempo_resposta",
                None
            ),

            # Dados originais do SINAPSE
            "motivo": getattr(
                e,
                "motivo",
                None
            ),

            "informacao_adicional": getattr(
                e,
                "informacaoAdicional",
                None
            ),

            "mensagem": getattr(
                e,
                "mensagem",
                None
            ),

            # Origem / destino
            "origem": getattr(
                e,
                "origem",
                None
            ),

            "destino": getattr(
                e,
                "destino",
                None
            ),

            "id_local_operacao": getattr(
                e,
                "idLocalOperacao",
                None
            ),

            "codigo": getattr(
                e,
                "codigo",
                None
            ),
        })

    return resultado

def obter_dados_pdp_dashboard(
    data=None,
    usina=None
):
    """
    Consulta a programação diária (PDP)
    do ons.db para alimentar a Visão 2.
    """

    if data is None:
        data = data_hoje()

    try:

        from nexo.modules.ons.db import SessionLocalONS
        from nexo.modules.ons.models import ONSPDP

        db_ons = SessionLocalONS()

        query = (
            db_ons
            .query(ONSPDP)
            .filter(
                ONSPDP.data == data
            )
        )

        if usina and usina != "todas":

            query = query.filter(
                ONSPDP.codigo_usina == usina
            )

        registros = (
            query
            .order_by(
                ONSPDP.patamar_numero.asc()
            )
            .all()
        )

        labels = []
        valores = []
        tabela = []

        energia_total_mwh = 0.0
        pico_mw = 0.0

        for r in registros:

            hora = getattr(
                r,
                "patamar_hora",
                f"#{r.patamar_numero}"
            )

            val = float(
                getattr(
                    r,
                    "potencia_programada",
                    0.0
                )
                or 0.0
            )

            labels.append(hora)
            valores.append(val)

            energia_total_mwh += (
                val * 0.5
            )

            if val > pico_mw:
                pico_mw = val

            tabela.append({
                "numero": getattr(
                    r,
                    "patamar_numero",
                    0
                ),
                "hora": hora,
                "codigo_usina": getattr(
                    r,
                    "codigo_usina",
                    "--"
                ),
                "potencia_mw": round(
                    val,
                    2
                ),
            })

        db_ons.close()

        return {
            "labels": labels,
            "valores": valores,
            "tabela": tabela,
            "energia_total_mwh": round(
                energia_total_mwh,
                2
            ),
            "pico_mw": round(
                pico_mw,
                2
            ),
            "total_patamares": len(
                tabela
            ),
        }

    except Exception as err:

        return {
            "labels": [],
            "valores": [],
            "tabela": [],
            "energia_total_mwh": 0.0,
            "pico_mw": 0.0,
            "total_patamares": 0,
            "mensagem": (
                f"Aguardando dados: {str(err)}"
            ),
        }

def gerar_pdf_auditoria(db, data=None, usinas=None):
    if data is None:
        data = data_hoje()

    if isinstance(data, str):
        data = date.fromisoformat(data)

    if not usinas:
        usinas = ["todas"]

    eventos = obter_historico_detalhado(db, data, None)

    usinas_filtradas = [
        u for u in usinas
        if u and u != "todas"
    ]

    if usinas_filtradas:
        eventos = [
            e for e in eventos
            if e.get("usina") in usinas_filtradas
        ]

    eventos.sort(key=lambda e: e.get("data") or "")

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloAuditoria",
        parent=estilos["Heading1"],
        fontSize=16,
        leading=19,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    subtitulo = ParagraphStyle(
        "SubtituloAuditoria",
        parent=estilos["Normal"],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12
    )

    texto = ParagraphStyle(
        "TextoAuditoria",
        parent=estilos["Normal"],
        fontSize=7.5,
        leading=9
    )

    elementos = []

    elementos.append(
        Paragraph(
            "AUDITORIA DE EVENTOS E RESTRIÇÕES",
            titulo
        )
    )

    elementos.append(
        Paragraph(
            f"Data operacional: {data.strftime('%d/%m/%Y')}",
            subtitulo
        )
    )

    nome_usinas = (
        ", ".join(usinas_filtradas)
        if usinas_filtradas
        else "Todas as usinas"
    )

    elementos.append(
        Paragraph(
            f"<b>Usina(s):</b> {nome_usinas}",
            texto
        )
    )

    elementos.append(Spacer(1, 6 * mm))

    cabecalho = [
        "Hora",
        "Potência<br/>observada",
        "Restrição<br/>solicitada",
        "Corte",
        "Motivo",
        "Informação adicional"
    ]

    dados_tabela: list[list] = [cabecalho]

    for evento in eventos:
        if evento.get("evento") != "RESTRICAO":
            continue

        data_evento = evento.get("data")

        if data_evento:
            try:
                dt = datetime.fromisoformat(
                    str(data_evento).replace("Z", "+00:00")
                ).astimezone(FUSO_OPERACIONAL)
                hora = dt.strftime("%H:%M")
            except Exception:
                hora = str(data_evento)
        else:
            hora = "--"

        potencia_observada = evento.get("potencia_observada")
        potencia_restricao = evento.get("potencia_restricao")
        corte = evento.get("corte_mw") or 0

        potencia_observada_txt = (
            f"{float(potencia_observada):.2f} MW"
            if potencia_observada is not None else "--"
        )

        potencia_restricao_txt = (
            f"{float(potencia_restricao):.2f} MW"
            if potencia_restricao is not None else "--"
        )

        dados_tabela.append([
            hora,
            potencia_observada_txt,
            potencia_restricao_txt,
            f"{float(corte):.2f} MW",
            Paragraph(
                str(evento.get("motivo") or "--"),
                texto
            ),
            Paragraph(
                str(evento.get("informacao_adicional") or "--"),
                texto
            )
        ])

    if len(dados_tabela) == 1:
        dados_tabela.append([
            "--",
            "--",
            "--",
            "--",
            "Nenhuma restrição registrada",
            "--"
        ])

    tabela = Table(
        dados_tabela,
        colWidths=[
            16 * mm,
            26 * mm,
            28 * mm,
            20 * mm,
            44 * mm,
            52 * mm
        ],
        repeatRows=1
    )

    tabela.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#08314A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ALIGN", (0, 0), (3, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#F5F7F8")
            ]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5)
        ])
    )

    elementos.append(tabela)
    elementos.append(Spacer(1, 6 * mm))

    liberacoes = [
        e for e in eventos
        if e.get("evento") == "LIBERACAO"
    ]

    if liberacoes:
        ultima_liberacao = liberacoes[-1]
        data_liberacao = ultima_liberacao.get("data")

        try:
            dt = datetime.fromisoformat(
                str(data_liberacao).replace("Z", "+00:00")
            ).astimezone(FUSO_OPERACIONAL)
            hora_liberacao = dt.strftime("%H:%M")
        except Exception:
            hora_liberacao = "--"

        elementos.append(
            Paragraph(
                f"<b>{hora_liberacao}</b> — "
                "Liberação total de potência ativa",
                texto
            )
        )

    doc.build(elementos)

    buffer.seek(0)
    return buffer