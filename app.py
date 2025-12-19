import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pandas as pd

import io
# Importa as funções que criamos para gerenciar a planilha
# import spreadsheet_manager as sm # Desativado para focar na lógica do Excel

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
# Carrega as variáveis de ambiente (você vai configurar isso no Render)
ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

# Validação para garantir que os tokens foram configurados no ambiente do Render
if not all([ACCESS_TOKEN, VERIFY_TOKEN, PHONE_NUMBER_ID]):
    print("❌ ERRO: As variáveis de ambiente WHATSAPP_ACCESS_TOKEN, WHATSAPP_VERIFY_TOKEN e WHATSAPP_PHONE_NUMBER_ID devem ser configuradas.")
    # Em um ambiente de produção real, você poderia fazer o app parar aqui.
    # exit(1)

# # Conecta-se à planilha ao iniciar o app (Desativado)
# planilha = sm.autenticar_e_abrir_planilha()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Assistente de Planilhas IA</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --background-color: #121212;
            --surface-color: #1e1e1e;
            --primary-text-color: #e0e0e0;
            --secondary-text-color: #b0b0b0;
            --accent-color: #8A2BE2; /* Roxo azulado */
            --user-bubble-color: #2a2a68;
            --bot-bubble-color: #333333;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--primary-text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .main-container {
            width: 100%;
            max-width: 800px;
            display: flex;
            flex-direction: column;
            height: calc(100vh - 40px);
        }
        h1 {
            color: var(--primary-text-color);
            text-align: center;
            background: linear-gradient(90deg, var(--accent-color), #4a90e2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .chat-container {
            flex-grow: 1;
            border: 1px solid #333;
            overflow-y: auto;
            padding: 20px;
            background-color: var(--surface-color);
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 18px;
            border-radius: 18px;
            max-width: 80%;
            line-height: 1.5;
            animation: fadeIn 0.5s ease-in-out;
        }
        .user { background-color: var(--user-bubble-color); margin-left: auto; border-bottom-right-radius: 4px; }
        .bot { background-color: var(--bot-bubble-color); margin-right: auto; border-bottom-left-radius: 4px; }
        .input-container { display: flex; }
        input[type="text"] {
            flex-grow: 1; padding: 15px; border: 1px solid #444; border-radius: 25px;
            background-color: var(--surface-color); color: var(--primary-text-color); font-size: 16px;
        }
        input[type="text"]:focus { outline: none; border-color: var(--accent-color); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="main-container">
        <h1>🤖 Assistente de Planilhas IA</h1>
        <div id="chat" class="chat-container"></div>
        <div class="input-container">
            <input type="text" id="message" placeholder="Digite 'vendas', 'estoque', 'ajuda'..." onkeypress="if(event.key === 'Enter') sendMessage()">
        </div>
    </div>
    <script>
        function addMessage(text, isUser) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user' : 'bot');
            div.innerHTML = text.replace(/\\n/g, '<br>').replace(/•/g, '<li>').replace(/📋|📊|❓/g, '');
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        async function sendMessage() {
            const input = document.getElementById('message');
            const message = input.value.trim();
            if (!message) return;
            addMessage(message, true);
            input.value = '';
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            });
            const data = await response.json();
            addMessage(data.response, false);
        }
        addMessage("👋 Olá! Sou seu assistente de planilhas. Digite 'ajuda' para ver os comandos!", false);
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    """Página inicial para verificar se o bot está online."""
    return HTML_TEMPLATE

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """Endpoint principal que recebe eventos do WhatsApp."""
    if request.method == "GET":
        # Processo de verificação do webhook (feito uma única vez)
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        else:
            print(f"❌ Falha na verificação do Webhook! Token recebido: '{request.args.get('hub.verify_token')}' | Token esperado: '{VERIFY_TOKEN}'")
            return "Erro de autenticação.", 403

    # Processa mensagens recebidas via POST
    data = request.get_json()
    print(f"📥 Dados recebidos no webhook (POST): {json.dumps(data, indent=2)}") # Adicionado para depuração

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
    
    print(f"💬 Mensagem WhatsApp recebida de {numero_usuario}: '{texto_mensagem}'")    
    
    resposta = processar_comando_bot(texto_mensagem, numero_usuario)

    # A resposta para o WhatsApp pode ser um texto ou um arquivo
    if isinstance(resposta, dict) and resposta.get("tipo") == "arquivo":
        enviar_documento_whatsapp(numero_usuario, resposta["media_id"], resposta["nome_arquivo"], resposta["legenda"])
    else:
        enviar_mensagem_whatsapp(numero_usuario, resposta)

@app.route("/chat", methods=["POST"])
def chat():
    """Endpoint para o chat do site."""
    data = request.get_json()
    texto_mensagem = data.get("message", "").lower()
    print(f"💬 Mensagem Web recebida: '{texto_mensagem}'")
    # Para o chat web, não precisamos enviar arquivos, apenas a confirmação em texto.
    resposta = processar_comando_bot(texto_mensagem, "web_user", enviar_arquivo=False)
    return jsonify({"response": resposta})

def processar_comando_bot(texto_mensagem, id_usuario, enviar_arquivo=True):
    """Função central que processa os comandos do bot."""
    if "ola" in texto_mensagem or "oi" in texto_mensagem:
        resposta = "🤖 Olá! Sou seu assistente de planilhas Excel!\n\nPosso ajudar com:\n📊 Criar planilhas de vendas, estoque, etc.\n\nDigite 'ajuda' para ver os comandos."
    elif "vendas" in texto_mensagem:
        resposta = criar_planilha_vendas(id_usuario, enviar_arquivo)
    elif "estoque" in texto_mensagem:
        resposta = criar_planilha_estoque(id_usuario, enviar_arquivo)
    elif "financeiro" in texto_mensagem or "gastos" in texto_mensagem:
        resposta = criar_planilha_financeiro(id_usuario, enviar_arquivo)
    elif "clientes" in texto_mensagem:
        resposta = criar_planilha_clientes(id_usuario, enviar_arquivo)
    elif "tarefas" in texto_mensagem:
        resposta = criar_planilha_tarefas(id_usuario, enviar_arquivo)
    elif "ajuda" in texto_mensagem or "help" in texto_mensagem:
        resposta = mostrar_ajuda()
    else:
        resposta = "🤔 Não entendi. Digite 'ajuda' para ver os comandos disponíveis ou me diga que tipo de planilha precisa!"
    return resposta

def enviar_mensagem_whatsapp(destinatario, texto):
    """Envia uma mensagem de texto para um número no WhatsApp."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
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

def upload_excel_para_whatsapp(df, nome_arquivo):
    """
    Converte um DataFrame para um arquivo Excel em memória e faz o upload para a API do WhatsApp.
    Retorna o ID da mídia se o upload for bem-sucedido.
    """
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    files = {
        'file': (nome_arquivo, buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
        'messaging_product': (None, 'whatsapp')
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        media_id = response.json().get("id")
        print(f"✅ Upload do arquivo '{nome_arquivo}' bem-sucedido. Media ID: {media_id}")
        return media_id
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro no upload do arquivo para o WhatsApp: {e.response.text}")
        return None

def enviar_documento_whatsapp(destinatario, media_id, nome_arquivo, legenda=""):
    """Envia um documento (usando media_id) para um número no WhatsApp."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "document",
        "document": {
            "id": media_id,
            "caption": legenda,
            "filename": nome_arquivo
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"✔️ Documento enviado para {destinatario}.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao enviar documento: {e.response.text}")

# --- FUNÇÕES DE CRIAÇÃO DE PLANILHAS (INTEGRADAS DO WhatsAppExcelBot) ---

def criar_planilha_vendas(id_usuario, enviar_arquivo=True):
    """Cria uma planilha de vendas e retorna uma mensagem de confirmação."""
    try:
        df = pd.DataFrame({
            'Data': [datetime.now().strftime('%d/%m/%Y')], 'Vendedor': ['João Silva'], 'Cliente': ['Empresa A'],
            'Produto': ['Produto X'], 'Quantidade': [5], 'Valor_Unitario': [50.0], 'Total': [250.0]
        })
        if enviar_arquivo:
            nome_arquivo = f"planilha_vendas_{datetime.now().strftime('%Y%m%d')}.xlsx"
            media_id = upload_excel_para_whatsapp(df, nome_arquivo)
            if media_id:
                return {"tipo": "arquivo", "media_id": media_id, "nome_arquivo": nome_arquivo, "legenda": "Aqui está sua planilha de vendas!"}
            else:
                return "❌ Desculpe, não consegui gerar sua planilha de vendas no momento."
        return "✅ Planilha de Vendas gerada com sucesso! (Em breve, o download estará disponível aqui)."
    except Exception as e:
        return f"❌ Erro ao processar planilha de vendas: {str(e)}"

def criar_planilha_estoque(id_usuario, enviar_arquivo=True):
    """Cria uma planilha de estoque e retorna uma mensagem de confirmação."""
    try:
        df = pd.DataFrame({
            'Codigo': ['001'], 'Produto': ['Notebook Dell'], 'Categoria': ['Informática'],
            'Estoque_Atual': [15], 'Estoque_Minimo': [5], 'Status': ['OK']
        })
        if enviar_arquivo:
            nome_arquivo = f"planilha_estoque_{datetime.now().strftime('%Y%m%d')}.xlsx"
            media_id = upload_excel_para_whatsapp(df, nome_arquivo)
            if media_id:
                return {"tipo": "arquivo", "media_id": media_id, "nome_arquivo": nome_arquivo, "legenda": "Aqui está sua planilha de controle de estoque!"}
            else:
                return "❌ Desculpe, não consegui gerar sua planilha de estoque no momento."
        return "✅ Planilha de Estoque gerada com sucesso!"
    except Exception as e:
        return f"❌ Erro ao processar planilha de estoque: {str(e)}"

def criar_planilha_financeiro(id_usuario, enviar_arquivo=True):
    """Cria uma planilha financeira e retorna uma mensagem de confirmação."""
    try:
        df = pd.DataFrame({
            'Data': ['01/12/2024'], 'Tipo': ['Receita'], 'Categoria': ['Vendas'],
            'Descricao': ['Venda produtos'], 'Valor': [5000.0], 'Saldo': [5000.0]
        })
        if enviar_arquivo:
            nome_arquivo = f"planilha_financeira_{datetime.now().strftime('%Y%m%d')}.xlsx"
            media_id = upload_excel_para_whatsapp(df, nome_arquivo)
            if media_id:
                return {"tipo": "arquivo", "media_id": media_id, "nome_arquivo": nome_arquivo, "legenda": "Aqui está sua planilha de controle financeiro!"}
            else:
                return "❌ Desculpe, não consegui gerar sua planilha financeira no momento."
        return "✅ Planilha Financeira gerada com sucesso!"
    except Exception as e:
        return f"❌ Erro ao processar planilha financeira: {str(e)}"

def criar_planilha_clientes(id_usuario, enviar_arquivo=True):
    """Cria uma planilha de clientes e retorna uma mensagem de confirmação."""
    try:
        df = pd.DataFrame({
            'ID': [1], 'Nome': ['João Silva'], 'Email': ['joao@email.com'],
            'Telefone': ['11999999999'], 'Status': ['Ativo']
        })
        if enviar_arquivo:
            nome_arquivo = f"planilha_clientes_{datetime.now().strftime('%Y%m%d')}.xlsx"
            media_id = upload_excel_para_whatsapp(df, nome_arquivo)
            if media_id:
                return {"tipo": "arquivo", "media_id": media_id, "nome_arquivo": nome_arquivo, "legenda": "Aqui está sua planilha de clientes!"}
            else:
                return "❌ Desculpe, não consegui gerar sua planilha de clientes no momento."
        return "✅ Planilha de Clientes gerada com sucesso!"
    except Exception as e:
        return f"❌ Erro ao processar planilha de clientes: {str(e)}"

def criar_planilha_tarefas(id_usuario, enviar_arquivo=True):
    """Cria uma planilha de tarefas e a envia para o usuário."""
    try:
        df = pd.DataFrame({
            'Tarefa': ['Desenvolver novo recurso X', 'Corrigir bug na página de login', 'Reunião de alinhamento semanal'],
            'Responsável': ['Ana', 'Carlos', 'Equipe'],
            'Prazo': [(datetime.now() + timedelta(days=5)).strftime('%d/%m/%Y'), (datetime.now() + timedelta(days=2)).strftime('%d/%m/%Y'), (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')],
            'Status': ['A Fazer', 'Em Andamento', 'A Fazer'],
            'Prioridade': ['Alta', 'Urgente', 'Média']
        })
        if enviar_arquivo:
            nome_arquivo = f"planilha_tarefas_{datetime.now().strftime('%Y%m%d')}.xlsx"
            media_id = upload_excel_para_whatsapp(df, nome_arquivo)
            if media_id:
                return {"tipo": "arquivo", "media_id": media_id, "nome_arquivo": nome_arquivo, "legenda": "Aqui está sua planilha de gerenciamento de tarefas!"}
            else:
                return "❌ Desculpe, não consegui gerar sua planilha de tarefas no momento."
        return "✅ Planilha de Tarefas gerada com sucesso!"
    except Exception as e:
        return f"❌ Erro ao processar planilha de tarefas: {str(e)}"

def mostrar_ajuda():
    """Retorna a mensagem de ajuda com os comandos."""
    return """📋 **COMANDOS DISPONÍVEIS:**

📊 **CRIAR PLANILHAS:**
• "vendas" - Para criar um modelo de controle de vendas.
• "estoque" - Para criar um modelo de gestão de estoque.
• "financeiro" - Para criar um modelo de controle financeiro.
• "clientes" - Para criar um modelo de base de clientes.
• "tarefas" - Para criar um modelo de gestão de tarefas.

❓ **AJUDA:**
• "ajuda" - Para ver este menu de comandos.

Exemplo: Digite "vendas" para receber as instruções da planilha de vendas!"""

if __name__ == "__main__":
    # A porta é definida pelo Render, então usamos a variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)