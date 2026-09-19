@echo off
title NEXO - Núcleo de Execução Operacional

echo ==========================================
echo   NEXO - Núcleo de Execução Operacional
echo      Configuracao do ambiente Python
echo ==========================================
echo.
echo Yuri Henrique.
echo.
echo ==========================================
echo.
echo Dashboard:
echo https://127.0.0.1:8000/dashboard
echo.
echo API:
echo https://127.0.0.1:8000/sinapse
echo.
echo Docs:
echo https://127.0.0.1:8000/docs
echo.
echo Pressione CTRL+C para encerrar.
echo.
echo Cloudflared: cloudflared tunnel --url http://127.0.0.1:8000
echo ==========================================
echo.

call .venv\Scripts\activate.bat

echo python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000