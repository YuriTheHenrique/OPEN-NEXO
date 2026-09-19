import importlib
import pkgutil
from pathlib import Path
from fastapi import FastAPI
import logging
import nexo.modules

logger = logging.getLogger("nexo.core.loader")

def descobrir_modulos():
    # Suporta pacotes normais e namespace packages no Windows e Linux
    caminhos = list(nexo.modules.__path__)
    modulos = []
    for info in pkgutil.iter_modules(caminhos):
        if info.ispkg:
            modulos.append(info.name)
    return modulos

def carregar_modelos_bd():
    # Descobre e importa models.py de cada módulo antes da criação das tabelas no banco
    for nome in descobrir_modulos():
        try:
            importlib.import_module(f"nexo.modules.{nome}.models")
            logger.info(f"Modelos SQLAlchemy carregados para o módulo: {nome}")
        except ModuleNotFoundError:
            pass

def inicializar_modulos(app: FastAPI, event_bus):
    # Executa a função setup_module de cada plugin registrado
    for nome in descobrir_modulos():
        try:
            modulo = importlib.import_module(f"nexo.modules.{nome}.plugin")

            if hasattr(modulo, "init_plugin"):
                modulo.init_plugin(app)
                logger.info(f"Plugin '{nome}' inicializado com sucesso.")

            elif hasattr(modulo, "setup_module"):
                modulo.setup_module(app=app, event_bus=event_bus)
                logger.info(f"Plugin '{nome}' inicializado com sucesso.")
        except ModuleNotFoundError:
            logger.warning(f"Módulo '{nome}' não possui plugin.py implementado.")
        except Exception as erro:
            logger.error(f"Erro ao inicializar o plugin '{nome}': {erro}", exc_info=True)

def obter_background_tasks():
    # Coleta todas as corrotinas de background dos módulos para rodar no lifespan do FastAPI
    tasks = []
    for nome in descobrir_modulos():
        try:
            modulo = importlib.import_module(f"nexo.modules.{nome}.plugin")
            if hasattr(modulo, "get_background_tasks"):
                tasks.extend(modulo.get_background_tasks())
        except Exception as erro:
            logger.error(f"Erro ao obter tasks do módulo '{nome}': {erro}", exc_info=True)
    return tasks

def obter_modulos_home():
    """
    Descobre e retorna os metadados dos módulos ativos para exibir os cards na Home.
    """
    modulos_home = []
    caminhos = list(nexo.modules.__path__)

    for info in pkgutil.iter_modules(caminhos):
        if info.ispkg:
            try:
                mod = importlib.import_module(f"nexo.modules.{info.name}.plugin")
                if hasattr(mod, "MODULE_INFO"):
                    dados = getattr(mod, "MODULE_INFO")
                    if not dados.get("ocultar_home", False):
                        modulos_home.append(dados)
            except Exception as erro:
                logger.warning(f"Não foi possível obter MODULE_INFO de {info.name}: {erro}")

    modulos_home.sort(key=lambda m: m.get("ordem", 99))
    return modulos_home

def obter_integracoes_home():
    """
    Descobre e retorna as informações de integrações/APIs expostas pelos módulos para a Home.
    """
    integracoes = []
    caminhos = list(nexo.modules.__path__)

    for info in pkgutil.iter_modules(caminhos):
        if info.ispkg:
            try:
                mod = importlib.import_module(f"nexo.modules.{info.name}.plugin")
                if hasattr(mod, "INTEGRACAO_INFO"):
                    integracoes.append(getattr(mod, "INTEGRACAO_INFO"))
            except Exception as erro:
                logger.warning(f"Não foi possível obter INTEGRACAO_INFO de {info.name}: {erro}")

    return integracoes
