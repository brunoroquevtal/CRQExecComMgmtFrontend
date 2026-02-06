"""
Módulo de autenticação e controle de acesso
"""
import streamlit as st


# Usuários do sistema
USUARIOS = {
    "visualizador": {
        "senha": "visual123",
        "nome": "Visualizador",
        "tipo": "visualizador",
        "permissoes": ["dashboard"]
    },
    "admin": {
        "senha": "admin123",
        "nome": "Administrador",
        "tipo": "administrador",
        "permissoes": ["dashboard", "dados", "mensagem", "configuracoes"]
    },
    "lider": {
        "senha": "lider123",
        "nome": "Líder da Mudança",
        "tipo": "lider",
        "permissoes": ["dashboard", "dados", "mensagem"]
    }
}


def init_session_auth():
    """Inicializa variáveis de autenticação no session_state"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "usuario_atual" not in st.session_state:
        st.session_state.usuario_atual = None
    if "tipo_usuario" not in st.session_state:
        st.session_state.tipo_usuario = None


def login(usuario, senha):
    """
    Realiza login do usuário
    
    Args:
        usuario: Nome de usuário
        senha: Senha do usuário
        
    Returns:
        bool: True se login bem-sucedido, False caso contrário
    """
    usuario_lower = usuario.lower()
    
    if usuario_lower in USUARIOS:
        if USUARIOS[usuario_lower]["senha"] == senha:
            st.session_state.authenticated = True
            st.session_state.usuario_atual = USUARIOS[usuario_lower]["nome"]
            # Salvar a chave do usuário (admin, lider, visualizador) em vez do tipo
            st.session_state.tipo_usuario = usuario_lower
            return True
    
    return False


def logout():
    """Realiza logout do usuário"""
    st.session_state.authenticated = False
    st.session_state.usuario_atual = None
    st.session_state.tipo_usuario = None


def is_authenticated():
    """Verifica se usuário está autenticado"""
    return st.session_state.get("authenticated", False)


def get_user_type():
    """Retorna o tipo do usuário atual"""
    return st.session_state.get("tipo_usuario", None)


def get_user_name():
    """Retorna o nome do usuário atual"""
    return st.session_state.get("usuario_atual", "Usuário")


def has_permission(page):
    """
    Verifica se usuário tem permissão para acessar uma página
    
    Args:
        page: Nome da página (dashboard, dados, mensagem, configuracoes)
        
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    if not is_authenticated():
        return False
    
    tipo = get_user_type()
    if tipo is None:
        return False
    
    usuario_info = USUARIOS.get(tipo, {})
    permissoes = usuario_info.get("permissoes", [])
    
    return page in permissoes


def can_edit_data():
    """
    Verifica se usuário pode editar dados
    
    Returns:
        bool: True se pode editar, False caso contrário
    """
    tipo = get_user_type()
    # tipo_usuario é a chave do dicionário (admin, lider, visualizador)
    return tipo in ["admin", "lider"]


def render_login_page():
    """Renderiza página de login"""
    st.title("🔐 Login - Janela de Mudança TI")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Faça login para continuar")
        
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário:", key="login_usuario")
            senha = st.text_input("🔑 Senha:", type="password", key="login_senha")
            
            submit = st.form_submit_button("Entrar", width='stretch')
            
            if submit:
                if login(usuario, senha):
                    st.success(f"✅ Bem-vindo, {get_user_name()}!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos!")

