@echo off
title NEXO - WhatsApp Gateway

cd /d "%~dp0"

echo ==========================================
echo       NEXO - WHATSAPP GATEWAY
echo ==========================================
echo.

echo Iniciando Gateway...
echo.

set PATH=%CD%\tools\node;%PATH%
cd whatsapp-gateway
npm start dev

echo.
echo ==========================================
echo Gateway encerrado.
echo ==========================================
pause