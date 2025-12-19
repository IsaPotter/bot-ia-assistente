import pandas as pd
from datetime import datetime, timedelta
import json

class AssistenteRedesSociais:
    def __init__(self):
        self.posts_agendados = []
        self.campanhas = []
        self.metricas = {
            'instagram': {'seguidores': 15420, 'engajamento': 4.2, 'alcance': 8500},
            'facebook': {'seguidores': 8930, 'engajamento': 3.1, 'alcance': 5200},
            'twitter': {'seguidores': 3250, 'engajamento': 2.8, 'alcance': 2100},
            'linkedin': {'seguidores': 1890, 'engajamento': 5.5, 'alcance': 1200}
        }
        
    def processar_comando_redes(self, mensagem):
        mensagem = mensagem.lower().strip()
        
        if "agendar post" in mensagem:
            return self.agendar_post()
            
        elif "métricas" in mensagem or "analytics" in mensagem:
            return self.gerar_metricas()
            
        elif "campanha" in mensagem:
            return self.criar_campanha()
            
        elif "hashtags" in mensagem:
            return self.sugerir_hashtags()
            
        elif "conteúdo" in mensagem:
            return self.sugerir_conteudo()
            
        elif "relatório redes" in mensagem:
            return self.gerar_relatorio_redes()
            
        elif "posts agendados" in mensagem:
            return self.listar_posts_agendados()
            
        else:
            return "📱 **REDES SOCIAIS**\n\n• 'agendar post' - Agendar publicação\n• 'métricas' - Ver analytics\n• 'campanha' - Criar campanha\n• 'hashtags' - Sugestões de hashtags\n• 'conteúdo' - Ideias de conteúdo\n• 'relatório redes' - Relatório completo\n• 'posts agendados' - Ver agenda"
    
    def agendar_post(self):
        post = {
            'id': len(self.posts_agendados) + 1,
            'data': (datetime.now() + timedelta(hours=2)).strftime('%d/%m/%Y %H:%M'),
            'plataforma': 'Instagram, Facebook',
            'tipo': 'Imagem + Texto',
            'status': 'Agendado'
        }
        self.posts_agendados.append(post)
        
        return f"✅ **POST AGENDADO**\n\n📅 Data: {post['data']}\n📱 Plataformas: {post['plataforma']}\n📝 Tipo: {post['tipo']}\n🆔 ID: {post['id']}\n\n📌 Post agendado com sucesso!"
    
    def gerar_metricas(self):
        resultado = "📊 **MÉTRICAS DAS REDES SOCIAIS**\n\n"
        
        for rede, dados in self.metricas.items():
            resultado += f"📱 **{rede.upper()}**\n"
            resultado += f"👥 Seguidores: {dados['seguidores']:,}\n"
            resultado += f"💝 Engajamento: {dados['engajamento']}%\n"
            resultado += f"👁️ Alcance: {dados['alcance']:,}\n\n"
        
        total_seguidores = sum(dados['seguidores'] for dados in self.metricas.values())
        resultado += f"🎯 **TOTAL GERAL**\n👥 Seguidores: {total_seguidores:,}"
        
        return resultado
    
    def criar_campanha(self):
        campanha = {
            'id': len(self.campanhas) + 1,
            'nome': 'Campanha Black Friday',
            'inicio': datetime.now().strftime('%d/%m/%Y'),
            'fim': (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y'),
            'orcamento': 'R$ 2.500,00',
            'objetivo': 'Aumentar vendas'
        }
        self.campanhas.append(campanha)
        
        return f"🚀 **CAMPANHA CRIADA**\n\n📝 Nome: {campanha['nome']}\n📅 Período: {campanha['inicio']} - {campanha['fim']}\n💰 Orçamento: {campanha['orcamento']}\n🎯 Objetivo: {campanha['objetivo']}\n🆔 ID: {campanha['id']}\n\n✅ Campanha configurada!"
    
    def sugerir_hashtags(self):
        hashtags = {
            'Negócios': '#empreendedorismo #business #startup #inovacao #sucesso',
            'Marketing': '#marketing #digitalmarketing #socialmedia #branding #publicidade',
            'Vendas': '#vendas #blackfriday #promocao #desconto #oferta',
            'Lifestyle': '#lifestyle #motivacao #inspiracao #dicas #qualidadedevida',
            'Tecnologia': '#tecnologia #inovacao #digital #tech #futuro'
        }
        
        resultado = "🏷️ **SUGESTÕES DE HASHTAGS**\n\n"
        for categoria, tags in hashtags.items():
            resultado += f"📂 **{categoria}**\n{tags}\n\n"
        
        return resultado
    
    def sugerir_conteudo(self):
        ideias = [
            "📸 Bastidores da empresa",
            "💡 Dicas do seu nicho",
            "🎉 Depoimentos de clientes",
            "📊 Dados e estatísticas",
            "🔥 Tendências do mercado",
            "❓ Perguntas para engajamento",
            "🎯 Cases de sucesso",
            "📚 Conteúdo educativo"
        ]
        
        resultado = "💡 **IDEIAS DE CONTEÚDO**\n\n"
        for i, ideia in enumerate(ideias, 1):
            resultado += f"{i}. {ideia}\n"
        
        resultado += "\n🎨 **FORMATOS:**\n• Carrossel\n• Stories\n• Reels\n• IGTV\n• Posts simples"
        
        return resultado
    
    def gerar_relatorio_redes(self):
        # Dados para planilha
        dados_relatorio = {
            'Rede_Social': ['Instagram', 'Facebook', 'Twitter', 'LinkedIn'],
            'Seguidores': [15420, 8930, 3250, 1890],
            'Engajamento_%': [4.2, 3.1, 2.8, 5.5],
            'Alcance': [8500, 5200, 2100, 1200],
            'Posts_Mes': [25, 20, 30, 15],
            'Crescimento_%': [12.5, 8.3, 15.2, 22.1]
        }
        
        df = pd.DataFrame(dados_relatorio)
        
        return f"📈 **RELATÓRIO REDES SOCIAIS**\n\n📊 Planilha gerada com:\n• 4 redes sociais\n• Métricas de engajamento\n• Dados de crescimento\n• Análise de alcance\n\n📎 Relatório Excel criado!\n\n🎯 **DESTAQUES:**\n🥇 Maior engajamento: LinkedIn (5.5%)\n📈 Maior crescimento: LinkedIn (22.1%)\n👥 Mais seguidores: Instagram (15.420)"
    
    def listar_posts_agendados(self):
        if not self.posts_agendados:
            return "📅 Nenhum post agendado no momento.\n\nDigite 'agendar post' para criar um!"
        
        resultado = "📅 **POSTS AGENDADOS**\n\n"
        for post in self.posts_agendados:
            resultado += f"🆔 {post['id']} - {post['data']}\n📱 {post['plataforma']}\n📝 {post['tipo']}\n\n"
        
        return resultado