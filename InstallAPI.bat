@echo off
title NEXO - Configuracao do Ambiente

echo ==========================================
echo   NEXO - Núcleo de Execução Operacional
echo      Configuracao do ambiente Python
echo ==========================================
echo.
echo 2026 Yuri Henrique.
echo.

python --version
if errorlevel 1 (
    echo.
    echo Python nao encontrado.
    echo Instale o Python pela Microsoft Store e execute novamente.
    pause
    exit /b
)

echo.
echo Criando ambiente virtual...

python -m venv .venv

echo.
echo Ativando ambiente virtual...

call .venv\Scripts\activate.bat

echo.
echo Atualizando pip...

python -m pip install --upgrade pip

echo.
echo Instalando dependencias...

pip install -r requirements.txt

echo.
echo ==========================================
echo     Ambiente configurado com sucesso!
echo      Execute agora o arquivo run.bat
echo ==========================================

pause