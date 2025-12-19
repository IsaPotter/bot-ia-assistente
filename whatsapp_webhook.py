from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from bot_ia import BotIA

def setup_whatsapp_routes(app):
    bot = BotIA()
    
    @app.route('/whatsapp', methods=['POST'])
    def whatsapp_webhook():
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        # Processar mensagem com o bot
        response_text = bot.processar_mensagem(incoming_msg)
        
        # Criar resposta do Twilio
        resp = MessagingResponse()
        msg = resp.message()
        msg.body(response_text)
        
        return str(resp)