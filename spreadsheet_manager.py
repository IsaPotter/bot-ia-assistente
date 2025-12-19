import gspread
import pandas as pd
from datetime import datetime
import os
import json

# Constantes
NOME_DA_PLANILHA = os.environ.get("GOOGLE_SHEET_NAME", "Nome da Sua Planilha")  # Nome da planilha via variável de ambiente ou padrão
ARQUIVO_CREDENCIAL = "credentials.json"    # Arquivo JSON que você baixou

def autenticar_e_abrir_planilha():
    """Autentica com a API do Google e abre a planilha desejada."""
    try:
        # Prioriza a variável de ambiente para o deploy no Render
        google_creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if google_creds_json:
            print("🔑 Autenticando com credenciais da variável de ambiente...")
            creds_dict = json.loads(google_creds_json)
            gc = gspread.service_account_from_dict(creds_dict)
        else:
            # Usa o arquivo local para desenvolvimento
            print("🔑 Autenticando com arquivo credentials.json local...")
            gc = gspread.service_account(filename=ARQUIVO_CREDENCIAL)

        planilha = gc.open(NOME_DA_PLANILHA).sheet1
        print(f"✅ Conectado com sucesso à planilha '{NOME_DA_PLANILHA}'")
        return planilha
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo '{ARQUIVO_CREDENCIAL}' não encontrado. Configure a variável de ambiente 'GOOGLE_CREDENTIALS_JSON' no Render.")
        return None
    except Exception as e:
        print(f"❌ Erro ao conectar com a planilha: {e}")
        return None

def carregar_posts_agendados(planilha):
    """Carrega todos os posts da planilha em um DataFrame do Pandas."""
    if not planilha:
        return pd.DataFrame()
        
    dados = planilha.get_all_records()
    df = pd.DataFrame(dados)
    
    if df.empty:
        print("⚠️ A planilha está vazia.")
        return df

    # Converte a coluna de data para o formato datetime
    df['data_agendamento'] = pd.to_datetime(df['data_agendamento'], format='%d/%m/%Y %H:%M')
    return df

def encontrar_posts_para_publicar(df):
    """Filtra a lista de posts para encontrar os que estão pendentes e no horário."""
    agora = datetime.now()
    
    # Filtra posts com status "Pendente" e cuja data de agendamento já passou
    posts_prontos = df[
        (df['status'].str.lower() == 'pendente') &
        (df['data_agendamento'] <= agora)
    ]
    
    return posts_prontos.to_dict('records')

def marcar_como_publicado(planilha, texto_do_post):
    """Encontra uma linha pelo texto do post e atualiza seu status para 'Publicado'."""
    try:
        # Encontra a célula que contém o texto do post
        celula = planilha.find(texto_do_post)
        # Atualiza a célula na coluna 4 (D), que é a coluna de 'status'
        planilha.update_cell(celula.row, 4, "Publicado")
        print(f"✅ Status atualizado para 'Publicado' para o post: '{texto_do_post[:30]}...'")
    except gspread.exceptions.CellNotFound:
        print(f"⚠️ Não foi possível encontrar o post para atualizar o status: '{texto_do_post[:30]}...'")

def adicionar_post_na_planilha(planilha, post_info):
    """Adiciona uma nova linha na planilha com os dados do post."""
    try:
        nova_linha = [
            post_info.get('plataforma'),
            post_info.get('texto_do_post'),
            post_info.get('data_agendamento'),
            'Pendente'  # Status inicial
        ]
        planilha.append_row(nova_linha)
        print(f"✅ Novo post adicionado à planilha: '{post_info.get('texto_do_post')[:30]}...'")
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar post na planilha: {e}")
        return False

# --- Exemplo de como usar as funções ---
if __name__ == "__main__":
    planilha_ws = autenticar_e_abrir_planilha()
    
    if planilha_ws:
        dataframe_posts = carregar_posts_agendados(planilha_ws)
        
        if not dataframe_posts.empty:
            print(f"\n🔍 Verificando posts agendados para agora ({datetime.now().strftime('%H:%M')})...")
            posts_a_publicar = encontrar_posts_para_publicar(dataframe_posts)
            
            if posts_a_publicar:
                print(f" encontrado(s) {len(posts_a_publicar)} post(s) para publicar!")
                for post in posts_a_publicar:
                    print(f"  -> Plataforma: {post['plataforma']}, Texto: {post['texto_do_post']}")
                    marcar_como_publicado(planilha_ws, post['texto_do_post'])
            else:
                print("   Nenhum post para publicar no momento.")