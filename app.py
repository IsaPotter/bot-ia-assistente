import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

# Importa as funções que criamos para gerenciar a planilha
import spreadsheet_manager as sm

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
# Carrega as variáveis de ambiente (você vai configurar isso no Render)
ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")

# Conecta-se à planilha ao iniciar o app
planilha = sm.autenticar_e_abrir_planilha()

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """Endpoint principal que recebe eventos do WhatsApp."""
    if request.method == "GET":
        # Processo de verificação do webhook (feito uma única vez)
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        else:
            return "Erro de autenticação.", 403

    # Processa mensagens recebidas via POST
    data = request.get_json()
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                if "messages" in change.get("value", {}):
                    for message in change["value"]["messages"]:
                        if message["type"] == "text":
                            processar_mensagem_whatsapp(message)
    return "OK", 200

def processar_mensagem_whatsapp(message):
    """Analisa a mensagem recebida e decide o que fazer."""
    numero_usuario = message["from"]
    texto_mensagem = message["text"]["body"].lower()
    
    print(f"💬 Mensagem recebida de {numero_usuario}: '{texto_mensagem}'")

    # --- LÓGICA DO BOT ---
    # Verifica se a mensagem é um comando para agendar post
    if texto_mensagem.startswith("agendar"):
        try:
            # Exemplo de comando: "agendar instagram: Meu post de hoje para amanhã às 10:00"
            partes = texto_mensagem.split(":", 1)
            plataforma = partes[0].replace("agendar", "").strip()
            texto_post = partes[1].strip()

            # Tenta extrair data e hora da mensagem (lógica simplificada)
            # Para uma solução robusta, seria necessário usar bibliotecas de NLP
            data_agendamento = datetime.now() + timedelta(minutes=5) # Padrão: 5 min a partir de agora
            if "amanhã" in texto_post:
                data_agendamento = datetime.now() + timedelta(days=1)
            
            # Formata a data para a planilha
            data_formatada = data_agendamento.strftime('%d/%m/%Y %H:%M')

            post_info = {
                "plataforma": plataforma,
                "texto_do_post": texto_post,
                "data_agendamento": data_formatada,
            }

            # Adiciona na planilha
            if sm.adicionar_post_na_planilha(planilha, post_info):
                resposta = f"✅ Agendado! Seu post para '{plataforma}' foi salvo."
            else:
                resposta = "❌ Ocorreu um erro ao salvar seu post na planilha."
            
            enviar_mensagem_whatsapp(numero_usuario, resposta)

        except Exception as e:
            print(f"Erro ao processar comando: {e}")
            enviar_mensagem_whatsapp(numero_usuario, "❌ Comando inválido. Use o formato: `agendar <plataforma>: <texto>`")
    else:
        # Resposta padrão se não for um comando conhecido
        resposta_padrao = "Olá! Para agendar um post, envie: `agendar <plataforma>: <texto do post>`"
        enviar_mensagem_whatsapp(numero_usuario, resposta_padrao)

def enviar_mensagem_whatsapp(destinatario, texto):
    """Envia uma mensagem de texto para um número no WhatsApp."""
    url = f"https://graph.facebook.com/v18.0/me/messages" # Use a versão mais recente da API
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "text": {"body": texto},
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"✔️ Mensagem enviada para {destinatario}: '{texto}'")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao enviar mensagem: {e.response.text}")

if __name__ == "__main__":
    # A porta é definida pelo Render, então usamos a variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)