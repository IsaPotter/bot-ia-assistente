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

@app.route("/")
def index():
    """Página inicial para verificar se o bot está online."""
    return "<h1>🤖 Seu assistente de WhatsApp está no ar!</h1><p>O webhook está configurado para receber eventos em /webhook.</p>"

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
    
    print(f"💬 Mensagem recebida de {numero_usuario}: '{texto_mensagem}'")    
    
    # --- LÓGICA DO BOT DE EXCEL ---
    # A lógica do WhatsAppExcelBot foi integrada aqui.
    if "ola" in texto_mensagem or "oi" in texto_mensagem:
        resposta = "🤖 Olá! Sou seu assistente de planilhas Excel!\n\nPosso ajudar com:\n📊 Criar planilhas de vendas, estoque, etc.\n\nDigite 'ajuda' para ver os comandos."
    elif "vendas" in texto_mensagem:
        resposta = criar_planilha_vendas(numero_usuario)
    elif "estoque" in texto_mensagem:
        resposta = criar_planilha_estoque(numero_usuario)
    elif "financeiro" in texto_mensagem or "gastos" in texto_mensagem:
        resposta = criar_planilha_financeiro(numero_usuario)
    elif "clientes" in texto_mensagem:
        resposta = criar_planilha_clientes(numero_usuario)
    elif "ajuda" in texto_mensagem or "help" in texto_mensagem:
        resposta = mostrar_ajuda()
    else:
        resposta = "🤔 Não entendi. Digite 'ajuda' para ver os comandos disponíveis ou me diga que tipo de planilha precisa!"

    enviar_mensagem_whatsapp(numero_usuario, resposta)

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

def criar_planilha_vendas(numero_usuario):
    """Cria uma planilha de vendas e retorna uma mensagem de confirmação."""
    try:
        df = pd.DataFrame({
            'Data': [datetime.now().strftime('%d/%m/%Y')], 'Vendedor': ['João Silva'], 'Cliente': ['Empresa A'],
            'Produto': ['Produto X'], 'Quantidade': [5], 'Valor_Unitario': [50.0], 'Total': [250.0]
        })
        nome_arquivo = f"planilha_vendas_{datetime.now().strftime('%Y%m%d')}.xlsx"
        media_id = upload_excel_para_whatsapp(df, nome_arquivo)
        if media_id:
            enviar_documento_whatsapp(numero_usuario, media_id, nome_arquivo, "Aqui está sua planilha de vendas!")
            return "Enviei a planilha para você! ✅" # Retorna uma resposta de texto simples
        else:
            return "❌ Desculpe, não consegui gerar sua planilha de vendas no momento."
    except Exception as e:
        return f"❌ Erro ao processar planilha de vendas: {str(e)}"

def criar_planilha_estoque(numero_usuario):
    """Cria uma planilha de estoque e retorna uma mensagem de confirmação."""
    try:
        df = pd.DataFrame({
            'Codigo': ['001'], 'Produto': ['Notebook Dell'], 'Categoria': ['Informática'],
            'Estoque_Atual': [15], 'Estoque_Minimo': [5], 'Status': ['OK']
        })
        nome_arquivo = f"planilha_estoque_{datetime.now().strftime('%Y%m%d')}.xlsx"
        media_id = upload_excel_para_whatsapp(df, nome_arquivo)
        if media_id:
            enviar_documento_whatsapp(numero_usuario, media_id, nome_arquivo, "Aqui está sua planilha de controle de estoque!")
            return "Enviei a planilha para você! ✅"
        else:
            return "❌ Desculpe, não consegui gerar sua planilha de estoque no momento."
    except Exception as e:
        return f"❌ Erro ao processar planilha de estoque: {str(e)}"

def criar_planilha_financeiro(numero_usuario):
    """Cria uma planilha financeira e retorna uma mensagem de confirmação."""
    try:
        df = pd.DataFrame({
            'Data': ['01/12/2024'], 'Tipo': ['Receita'], 'Categoria': ['Vendas'],
            'Descricao': ['Venda produtos'], 'Valor': [5000.0], 'Saldo': [5000.0]
        })
        nome_arquivo = f"planilha_financeira_{datetime.now().strftime('%Y%m%d')}.xlsx"
        media_id = upload_excel_para_whatsapp(df, nome_arquivo)
        if media_id:
            enviar_documento_whatsapp(numero_usuario, media_id, nome_arquivo, "Aqui está sua planilha de controle financeiro!")
            return "Enviei a planilha para você! ✅"
        else:
            return "❌ Desculpe, não consegui gerar sua planilha financeira no momento."
    except Exception as e:
        return f"❌ Erro ao processar planilha financeira: {str(e)}"

def criar_planilha_clientes(numero_usuario):
    """Cria uma planilha de clientes e retorna uma mensagem de confirmação."""
    try:
        df = pd.DataFrame({
            'ID': [1], 'Nome': ['João Silva'], 'Email': ['joao@email.com'],
            'Telefone': ['11999999999'], 'Status': ['Ativo']
        })
        nome_arquivo = f"planilha_clientes_{datetime.now().strftime('%Y%m%d')}.xlsx"
        media_id = upload_excel_para_whatsapp(df, nome_arquivo)
        if media_id:
            enviar_documento_whatsapp(numero_usuario, media_id, nome_arquivo, "Aqui está sua planilha de clientes!")
            return "Enviei a planilha para você! ✅"
        else:
            return "❌ Desculpe, não consegui gerar sua planilha de clientes no momento."
    except Exception as e:
        return f"❌ Erro ao processar planilha de clientes: {str(e)}"

def mostrar_ajuda():
    """Retorna a mensagem de ajuda com os comandos."""
    return """📋 **COMANDOS DISPONÍVEIS:**

📊 **CRIAR PLANILHAS:**
• "vendas" - Para criar um modelo de controle de vendas.
• "estoque" - Para criar um modelo de gestão de estoque.
• "financeiro" - Para criar um modelo de controle financeiro.
• "clientes" - Para criar um modelo de base de clientes.

❓ **AJUDA:**
• "ajuda" - Para ver este menu de comandos.

Exemplo: Digite "vendas" para receber as instruções da planilha de vendas!"""

if __name__ == "__main__":
    # A porta é definida pelo Render, então usamos a variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)