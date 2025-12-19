import pandas as pd
import io
import base64
from datetime import datetime
import json

class AssistenteAtendimento:
    def __init__(self):
        self.atendimentos = []
        self.clientes = {}
        
    def processar_mensagem(self, mensagem):
        mensagem = mensagem.lower().strip()
        
        if any(palavra in mensagem for palavra in ["olá", "oi", "bom dia", "boa tarde"]):
            return "👋 Olá! Sou seu assistente virtual de atendimento. Posso ajudar com:\n\n📊 Gerar planilhas Excel\n📋 Registrar atendimentos\n👥 Gerenciar clientes\n📈 Relatórios\n\nComo posso ajudar?"
            
        elif "planilha" in mensagem or "excel" in mensagem:
            return self.menu_planilhas()
            
        elif "vendas" in mensagem:
            return self.gerar_planilha_vendas()
            
        elif "clientes" in mensagem:
            return self.gerar_planilha_clientes()
            
        elif "estoque" in mensagem:
            return self.gerar_planilha_estoque()
            
        elif "financeiro" in mensagem:
            return self.gerar_planilha_financeiro()
            
        elif "registrar atendimento" in mensagem:
            return self.registrar_atendimento()
            
        elif "relatório" in mensagem:
            return self.gerar_relatorio()
            
        else:
            return "🤖 Comandos disponíveis:\n• 'planilha' - Menu de planilhas\n• 'vendas' - Planilha de vendas\n• 'clientes' - Planilha de clientes\n• 'estoque' - Planilha de estoque\n• 'financeiro' - Planilha financeira\n• 'registrar atendimento' - Novo atendimento\n• 'relatório' - Relatório geral"
    
    def menu_planilhas(self):
        return "📊 **PLANILHAS DISPONÍVEIS**\n\n1️⃣ Vendas - Digite 'vendas'\n2️⃣ Clientes - Digite 'clientes'\n3️⃣ Estoque - Digite 'estoque'\n4️⃣ Financeiro - Digite 'financeiro'\n\nQual planilha deseja gerar?"
    
    def gerar_planilha_vendas(self):
        # Dados de exemplo
        dados_vendas = {
            'Data': ['2024-12-01', '2024-12-02', '2024-12-03', '2024-12-04'],
            'Cliente': ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Lima'],
            'Produto': ['iPhone 15', 'MacBook Air', 'AirPods', 'iPad'],
            'Quantidade': [1, 1, 2, 1],
            'Valor_Unitario': [1299.99, 2899.99, 199.99, 899.99],
            'Total': [1299.99, 2899.99, 399.98, 899.99]
        }
        
        df = pd.DataFrame(dados_vendas)
        
        # Converter para Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Vendas', index=False)
        
        excel_data = output.getvalue()
        
        return f"✅ **PLANILHA DE VENDAS GERADA**\n\n📊 Total de vendas: {len(dados_vendas['Data'])}\n💰 Faturamento: R$ {sum(dados_vendas['Total']):.2f}\n\n📎 Planilha Excel criada com sucesso!\n(Em produção, seria enviada como anexo)"
    
    def gerar_planilha_clientes(self):
        dados_clientes = {
            'ID': [1, 2, 3, 4, 5],
            'Nome': ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Lima', 'Carlos Souza'],
            'Email': ['joao@email.com', 'maria@email.com', 'pedro@email.com', 'ana@email.com', 'carlos@email.com'],
            'Telefone': ['11999999999', '11888888888', '11777777777', '11666666666', '11555555555'],
            'Cidade': ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasília'],
            'Status': ['Ativo', 'Ativo', 'Inativo', 'Ativo', 'Ativo']
        }
        
        df = pd.DataFrame(dados_clientes)
        
        return f"✅ **PLANILHA DE CLIENTES GERADA**\n\n👥 Total de clientes: {len(dados_clientes['ID'])}\n✅ Clientes ativos: {dados_clientes['Status'].count('Ativo')}\n❌ Clientes inativos: {dados_clientes['Status'].count('Inativo')}\n\n📎 Planilha Excel criada com sucesso!"
    
    def gerar_planilha_estoque(self):
        dados_estoque = {
            'Codigo': ['P001', 'P002', 'P003', 'P004', 'P005'],
            'Produto': ['iPhone 15 Pro', 'MacBook Air M2', 'AirPods Pro', 'iPad Air', 'Apple Watch'],
            'Categoria': ['Smartphone', 'Notebook', 'Fone', 'Tablet', 'Smartwatch'],
            'Quantidade': [25, 15, 50, 30, 40],
            'Preco_Custo': [1000.00, 2200.00, 150.00, 650.00, 300.00],
            'Preco_Venda': [1299.99, 2899.99, 199.99, 899.99, 399.99],
            'Status': ['Em Estoque', 'Baixo Estoque', 'Em Estoque', 'Em Estoque', 'Em Estoque']
        }
        
        df = pd.DataFrame(dados_estoque)
        
        return f"✅ **PLANILHA DE ESTOQUE GERADA**\n\n📦 Total de produtos: {len(dados_estoque['Codigo'])}\n⚠️ Produtos com baixo estoque: 1\n💰 Valor total em estoque: R$ {sum(p*q for p,q in zip(dados_estoque['Preco_Custo'], dados_estoque['Quantidade'])):.2f}\n\n📎 Planilha Excel criada com sucesso!"
    
    def gerar_planilha_financeiro(self):
        dados_financeiro = {
            'Data': ['2024-12-01', '2024-12-02', '2024-12-03', '2024-12-04', '2024-12-05'],
            'Tipo': ['Receita', 'Despesa', 'Receita', 'Despesa', 'Receita'],
            'Categoria': ['Vendas', 'Fornecedor', 'Vendas', 'Aluguel', 'Vendas'],
            'Descricao': ['Venda iPhone', 'Compra produtos', 'Venda MacBook', 'Aluguel loja', 'Venda AirPods'],
            'Valor': [1299.99, -800.00, 2899.99, -2500.00, 399.98],
            'Saldo': [1299.99, 499.99, 3399.98, 899.98, 1299.96]
        }
        
        df = pd.DataFrame(dados_financeiro)
        
        receitas = sum(v for v in dados_financeiro['Valor'] if v > 0)
        despesas = sum(v for v in dados_financeiro['Valor'] if v < 0)
        saldo = receitas + despesas
        
        return f"✅ **PLANILHA FINANCEIRA GERADA**\n\n💰 Total receitas: R$ {receitas:.2f}\n💸 Total despesas: R$ {abs(despesas):.2f}\n📊 Saldo atual: R$ {saldo:.2f}\n\n📎 Planilha Excel criada com sucesso!"
    
    def registrar_atendimento(self):
        atendimento = {
            'id': len(self.atendimentos) + 1,
            'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'status': 'Em andamento'
        }
        self.atendimentos.append(atendimento)
        
        return f"✅ **ATENDIMENTO REGISTRADO**\n\n🆔 ID: {atendimento['id']}\n📅 Data: {atendimento['data']}\n📋 Status: {atendimento['status']}\n\nAtendimento iniciado com sucesso!"
    
    def gerar_relatorio(self):
        return f"📊 **RELATÓRIO GERAL**\n\n👥 Atendimentos hoje: {len(self.atendimentos)}\n📈 Planilhas geradas: Disponível\n💼 Status do sistema: Online\n⏰ Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n✅ Sistema funcionando normalmente!"