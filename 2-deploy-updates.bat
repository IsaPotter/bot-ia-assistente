@echo off
echo 🚀 Fazendo deploy de atualizacoes para o Heroku...

if not defined HEROKU_APP_NAME (
    echo ❌ ERRO: A variavel de ambiente HEROKU_APP_NAME nao foi definida.
    echo    Execute: setx HEROKU_APP_NAME "seu-nome-de-app-unico" e reinicie o terminal.
    pause
    exit /b
)

echo.
echo 1️⃣ Adicionando alteracoes ao Git...
git add .
git commit -m "Atualizacao do bot"

echo.
echo 2️⃣ Fazendo deploy para o app existente: %HEROKU_APP_NAME%...
git push heroku main

echo.
echo ✅ Deploy concluido!
for /f "tokens=*" %%i in ('heroku apps:info -a %HEROKU_APP_NAME% --json ^| findstr "web_url"') do (
    set WEB_URL=%%i
)
set WEB_URL=%WEB_URL:*"web_url": "%
set WEB_URL=%WEB_URL%",%
echo 📱 Seu bot foi atualizado em: %WEB_URL%

pause