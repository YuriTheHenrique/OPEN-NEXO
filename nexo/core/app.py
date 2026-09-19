import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from nexo.core.db import init_database
from nexo.core.logging import configure_logging
from nexo.core.events.bus import event_bus
from nexo.core.loader import inicializar_modulos, obter_background_tasks, obter_modulos_home, obter_integracoes_home
from nexo.core.backup import worker_backup_diario



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Coleta as tarefas dos módulos e inclui a rotina central de backup diário
    background_coroutines = obter_background_tasks()
    background_coroutines.append(worker_backup_diario)

    tasks = [asyncio.create_task(coro_fn()) for coro_fn in background_coroutines]

    try:
        yield
    finally:
        # Encerra todas as tarefas de forma limpa no desligamento do servidor
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


CORE_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(CORE_TEMPLATES_DIR))

def create_app() -> FastAPI:
    configure_logging()
    init_database()

    app = FastAPI(
        title="NEXO - Núcleo de Execução Operacional",
        description="Plataforma modular (fase 3: modular)",
        version="0.8",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Carrega dinamicamente todos os módulos/plugins (rotas, eventos, tabelas, etc.)
    inicializar_modulos(app, event_bus)

    # Monta arquivos estáticos globais se a pasta existir
    if Path("app/static").exists():
        app.mount(
            "/static",
            StaticFiles(directory="app/static"),
            name="static"
        )

    @app.get("/")
    def home(request: Request):
        modulos = obter_modulos_home()
        integracoes = obter_integracoes_home()
        return templates.TemplateResponse(
            request=request,
            name="home.html",
            context={
                "modulos": modulos,
                "integracoes": integracoes,
            }
        )

    return app
