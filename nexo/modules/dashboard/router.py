from pathlib import Path
import asyncio
import datetime
from fastapi import APIRouter, Request, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from nexo.core.events.bus import event_bus
from nexo.core.events.types import SINAPSE_RESTRICAO_RECEBIDA
from nexo.modules.dashboard.websocket import dashboard_ws

from nexo.modules.dashboard.dependencies import get_db
from nexo.modules.dashboard import services
from nexo.modules.sinapse.models import Restricao
from nexo.modules.ativos.data import data_hoje
from nexo.modules.ativos.models import Ativo
from app.database import SessionLocal

router = APIRouter()

templates = Jinja2Templates(
    directory=[
        "nexo/modules/dashboard/templates",
        "nexo/core/templates",
    ]
)


STATIC_DIR = Path(__file__).resolve().parent / "static"

router.mount(
    "/dashboard/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="dashboard_static"
)

@router.websocket("/api/dashboard/ws")
async def dashboard_websocket(websocket: WebSocket):

    queue = await dashboard_ws.connect(websocket)

    async def enviar_mensagens():

        while True:

            mensagem = await queue.get()

            await websocket.send_text(mensagem)

    tarefa_envio = asyncio.create_task(
        enviar_mensagens()
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        pass

    except Exception as erro:

        print(
            f"DASHBOARD WS -> erro: {erro}"
        )

    finally:

        tarefa_envio.cancel()

        try:
            await tarefa_envio
        except asyncio.CancelledError:
            pass

        dashboard_ws.disconnect(websocket)

def notificar_dashboard(dados):

    dashboard_ws.publicar({
        "tipo": "sinapse.restricao.recebida",
        "dados": dados
    })

event_bus.subscribe(
    SINAPSE_RESTRICAO_RECEBIDA,
    notificar_dashboard
)

@router.get("/dashboard")
def dashboard(request: Request, db=Depends(get_db)):
    indicadores = services.calcular_indicadores(db)
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"indicadores": indicadores})


@router.get("/indicadores")
def indicadores(db=Depends(get_db)):
    return services.calcular_indicadores(db)


@router.get("/restricoes")
def listar_restricoes(db=Depends(get_db)):
    restricoes = db.query(Restricao).all()
    return restricoes


@router.get("/usinas")
def listar_usinas(db=Depends(get_db)):
    return services.listar_usinas_service(db)


@router.get("/api/usinas")
def api_usinas(
    data: datetime.date | None = Query(None),
    db=Depends(get_db)
):
    if data is None:
        data_filtro = data_hoje()
    else:
        data_filtro = data

    ativos = db.query(Ativo).filter(Ativo.ativo == True).all()
    resultado = []

    inicio, fim = services.filtro_dia_operacional(
        Restricao.dataCadastro,
        data_filtro
    )

    for ativo in ativos:
        ultima = (
            db.query(Restricao)
            .filter(
                (Restricao.usina == ativo.nome) | (Restricao.apelido == ativo.apelido),
                inicio,
                fim
            )
            .order_by(Restricao.id.desc())
            .first()
        )
        if ultima:
            resultado.append({
                "usina": ativo.nome,
                "apelido": ativo.apelido,
                "capacidade": ativo.capacidade,
                "regiao": ativo.regiao,
                "tipo_geracao": ultima.tipo_geracao or ativo.tipo,
                "evento": ultima.evento,
                "status": ultima.status,
                "id_evento": ultima.id,
                "potencia_observada": ultima.potencia_observada,
                "potencia_restricao": ultima.potencia_restricao,
                "dataAtualizacao": ultima.dataAtualizacao,
                "dataRecebimento": ultima.dataRecebimento,
                "dataCadastro": ultima.dataCadastro,
                "empresa": ativo.empresa,
                "logo": ativo.logo
            })
        else:
            resultado.append({
                "usina": ativo.nome,
                "apelido": ativo.apelido,
                "capacidade": ativo.capacidade,
                "regiao": ativo.regiao,
                "tipo_geracao": ativo.tipo,
                "empresa": ativo.empresa,
                "logo": ativo.logo,
                "evento": "NORMAL",
                "status": "Sem restrição",
                "potencia_observada": None,
                "potencia_restricao": None,
                "dataAtualizacao": None,
                "dataCadastro": None,
                "dataRecebimento": None
            })
    return resultado



@router.get("/api/grafico/restricoes")
def grafico_restricoes(
    data: datetime.date | None = Query(None),
    db=Depends(get_db)
):
    
    return services.grafico_restricoes(
        db,
        data
    )


@router.get("/api/status")
def status_dashboard(
    data: datetime.date | None = Query(None)
):

    db = SessionLocal()

    try:
        return services.status_dashboard(
            db,
            data
        )

    finally:
        db.close()


@router.get("/api/historico/{usina}")
def historico_usina(
    usina: str,
    data: datetime.date | None = Query(None)
):

    db = SessionLocal()

    try:
        return services.historico_usina(
            db,
            usina,
            data
        )

    finally:
        db.close()

@router.get(
    "/api/dashboard/historico",
    tags=["Dashboard"]
)
def api_historico(
    data: str | None = Query(default=None),
    usina: str | None = Query(default=None),
    db=Depends(get_db)
):
    return services.obter_historico_detalhado(db, data, usina)

@router.get(
    "/api/dashboard/auditoria/pdf",
    tags=["Dashboard"]
)
def pdf_auditoria(
    data: datetime.date | None = Query(default=None),
    usina: list[str] | None = Query(default=None),
    db=Depends(get_db)
):
    pdf = services.gerar_pdf_auditoria(
        db,
        data,
        usina
    )

    data_arquivo = data or data_hoje()

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'inline; filename="auditoria_{data_arquivo}.pdf"'
        }
    )

@router.get(
    "/api/dashboard/pdp",
    tags=["Dashboard"]
)
@router.get(
    "/api/pdp",
    tags=["Dashboard"]
)
def api_pdp(
    data: str | None = Query(default=None),
    usina: str | None = Query(default=None),
):
    return services.obter_dados_pdp_dashboard(data, usina)
