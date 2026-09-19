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
echo ==========================================
echo.

call .venv\Scripts\activate.bat

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload