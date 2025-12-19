import facebook

def post_to_facebook_page(page_id, page_access_token, message):
    """
    Publica uma mensagem de texto em uma Página do Facebook.

    Args:
        page_id (str): O ID da Página do Facebook.
        page_access_token (str): O Token de Acesso da Página que nunca expira.
        message (str): O texto a ser publicado.

    Returns:
        bool: True se a publicação for bem-sucedida, False caso contrário.
    """
    try:
        # Inicializa a API de Grafos com o token da página
        graph = facebook.GraphAPI(access_token=page_access_token, version="v18.0")
        
        # Publica no feed da página
        graph.put_object(parent_object=page_id, connection_name='feed', message=message)
        
        print(f"✅ Post publicado com sucesso na página {page_id}!")
        return True
    except facebook.GraphAPIError as e:
        print(f"❌ Erro ao publicar no Facebook: {e.result}")
        return False