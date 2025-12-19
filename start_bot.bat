@echo off
echo 🚀 Iniciando WhatsApp Bot...
echo.

echo 1️⃣ Executando bot...
start python whatsapp_meta.py

echo.
echo 2️⃣ Aguarde 5 segundos...
timeout /t 5 /nobreak >nul

echo.
echo 3️⃣ Iniciando Ngrok...
echo Baixe ngrok.exe em: https://ngrok.com/download
echo.
echo Execute: ngrok http 5004
echo.
echo 4️⃣ Use a URL gerada no Meta Business:
echo https://abc123.ngrok.io/webhook
echo.
echo ✅ Bot rodando em: http://localhost:5004
pause