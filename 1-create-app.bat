@echo off
echo 🚀 Configurando e criando o App Heroku pela primeira vez...

if not defined HEROKU_APP_NAME (
    echo ❌ ERRO: A variavel de ambiente HEROKU_APP_NAME nao foi definida.
    echo    Execute: setx HEROKU_APP_NAME "seu-nome-de-app-unico" e reinicie o terminal.
    pause
    exit /b
)

echo.
echo 1️⃣ Fazendo login no Heroku...
heroku login

echo.
echo 2️⃣ Criando app Heroku com o nome: %HEROKU_APP_NAME%
heroku create %HEROKU_APP_NAME%

echo.
echo 3️⃣ Inicializando Git e fazendo o primeiro commit...
git init
git add .
git commit -m "Commit inicial: configuracao do bot"

echo.
echo 4️⃣ Fazendo o primeiro deploy para o app %HEROKU_APP_NAME%...
git push heroku main

echo.
echo ✅ Configuracao e deploy inicial concluidos!
for /f "tokens=*" %%i in ('heroku apps:info -a %HEROKU_APP_NAME% --json ^| findstr "web_url"') do (
    set WEB_URL=%%i
)
set WEB_URL=%WEB_URL:*"web_url": "%
set WEB_URL=%WEB_URL%",%
echo 📱 Seu bot esta disponivel em: %WEB_URL%
echo 🔧 Configure o webhook no Meta Business com essa URL + /webhook

pause