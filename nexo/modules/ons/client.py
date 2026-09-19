"""
Cliente HTTP para comunicação com as APIs do ONS / SINtegre.
"""

import logging
import requests
from typing import Any

from nexo.modules.ons.config import carregar_config

logger = logging.getLogger("nexo.modules.ons.client")


class ONSClient:
    """
    Cliente centralizado para autenticação e requisições nas APIs do ONS.
    """

    def __init__(self):
        self.config = carregar_config()
        self.base_url = self.config.get("base_url", "https://integra.ons.org.br/api").rstrip("/")
        self.token: str | None = None

    def recarregar_config(self):
        """Recarrega as configurações a partir do JSON."""
        self.config = carregar_config()
        self.base_url = self.config.get("base_url", "https://integra.ons.org.br/api").rstrip("/")

    def autenticar(self) -> bool:
        """
        Realiza login no ONS via POST /autenticar e obtém o token JWT.
        """
        self.recarregar_config()
        usuario = self.config.get("usuario")
        senha = self.config.get("senha")

        if not usuario or not senha:
            logger.warning("Credenciais do ONS não configuradas no config.json.")
            return False

        url = f"{self.base_url}/autenticar"
        payload = {"usuario": usuario, "senha": senha}

        try:
            res = requests.post(url, json=payload, timeout=20)
            if res.status_code == 200:
                dados = res.json()
                self.token = (
                    dados.get("token")
                    or dados.get("accessToken")
                    or dados.get("access_token")
                )
                logger.info("Autenticação no ONS realizada com sucesso.")
                return True
            else:
                logger.error(f"Falha na autenticação ONS ({res.status_code}): {res.text}")
                self.token = None
                return False
        except Exception as e:
            logger.error(f"Erro de conexão ao autenticar no ONS: {e}")
            self.token = None
            return False

    def requisicao(
        self,
        metodo: str,
        endpoint: str,
        params: dict | None = None,
        json_data: Any = None,
        timeout: int = 30,
    ) -> requests.Response | None:
        """
        Executa uma requisição HTTP autenticada com tratamento e renovação de token.
        """
        if not self.token:
            if not self.autenticar():
                return None

        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            res = requests.request(
                method=metodo,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=timeout,
            )

            # Se o token expirou (401), tenta autenticar novamente uma vez
            if res.status_code == 401:
                logger.info("Token JWT do ONS expirado. Renovando autenticação...")
                if self.autenticar():
                    headers["Authorization"] = f"Bearer {self.token}"
                    res = requests.request(
                        method=metodo,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json_data,
                        timeout=timeout,
                    )

            return res
        except Exception as e:
            logger.error(f"Erro na requisição ONS para {url}: {e}")
            return None


# Instância global compartilhada (Singleton)
ons_client = ONSClient()
