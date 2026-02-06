"""
Módulo para componentes de UI reutilizáveis
"""
import pandas as pd
import streamlit as st
from config import STATUS_COLORS, STATUS_OPCOES


def render_status_card(title, value, delta=None, delta_color="normal"):
    """
    Renderiza um card de status
    
    Args:
        title: Título do card
        value: Valor principal
        delta: Valor delta (opcional)
        delta_color: Cor do delta
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )


def render_status_badge(status):
    """
    Renderiza um badge de status com cor
    
    Args:
        status: Status da atividade
        
    Returns:
        str: HTML do badge
    """
    color = STATUS_COLORS.get(status, "#6c757d")
    return f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">{status}</span>'


def render_sequence_status_card(sequencia, stats, total, milestones_count=0):
    """
    Renderiza card de status de um CRQ
    
    Args:
        sequencia: Nome do CRQ
        stats: Estatísticas do CRQ
        total: Total de atividades (sem milestones)
        milestones_count: Número de milestones
    """
    from config import SEQUENCIAS
    
    sequencia_info = SEQUENCIAS.get(sequencia, {})
    emoji = sequencia_info.get("emoji", "📊")
    nome = sequencia_info.get("nome", sequencia)
    
    with st.container():
        st.markdown(f"### {emoji} {nome} ({total} atividades)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pct = stats.get("pct_concluidas", 0)
            st.markdown(f"**✅ Concluídas**")
            st.markdown(f"{stats['concluidas']}/{total} ({pct:.1f}%)")
        
        with col2:
            pct = stats.get("pct_em_execucao", 0)
            st.markdown(f"**⏳ Em Execução**")
            st.markdown(f"{stats['em_execucao']}/{total} ({pct:.1f}%)")
        
        with col3:
            pct = stats.get("pct_planejadas", 0)
            st.markdown(f"**🟡 Planejadas**")
            st.markdown(f"{stats['planejadas']}/{total} ({pct:.1f}%)")
        
        with col4:
            pct = stats.get("pct_atrasadas", 0)
            st.markdown(f"**🔴 Atrasadas**")
            st.markdown(f"{stats['atrasadas']}/{total} ({pct:.1f}%)")
        
        st.divider()


def format_dataframe_for_display(df, columns_to_show=None):
    """
    Formata dataframe para exibição na tabela
    
    Args:
        df: DataFrame
        columns_to_show: Lista de colunas para mostrar
        
    Returns:
        DataFrame: DataFrame formatado
    """
    if df is None or len(df) == 0:
        return df
    
    display_df = df.copy()
    
    if columns_to_show:
        # Mostrar apenas colunas especificadas
        available_cols = [col for col in columns_to_show if col in display_df.columns]
        display_df = display_df[available_cols]
    
    # Formatar datas
    date_columns = ["Inicio", "Fim", "Horario_Inicio_Real", "Horario_Fim_Real"]
    for col in date_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: x.strftime("%d/%m/%Y %H:%M:%S") if pd.notna(x) and hasattr(x, 'strftime') else ""
            )
    
    # Formatar atraso
    if "Atraso_Minutos" in display_df.columns:
        from modules.calculations import format_delay
        display_df["Atraso"] = display_df["Atraso_Minutos"].apply(format_delay)
        if "Atraso_Minutos" in display_df.columns and "Atraso" in display_df.columns:
            # Manter apenas a coluna formatada
            display_df = display_df.drop(columns=["Atraso_Minutos"])
    
    return display_df


def render_loading_spinner(message="Carregando..."):
    """
    Renderiza spinner de carregamento
    
    Args:
        message: Mensagem a exibir
    """
    return st.spinner(message)


def show_success_message(message):
    """
    Mostra mensagem de sucesso
    
    Args:
        message: Mensagem a exibir
    """
    st.success(message)


def show_error_message(message):
    """
    Mostra mensagem de erro
    
    Args:
        message: Mensagem a exibir
    """
    st.error(message)


def show_warning_message(message):
    """
    Mostra mensagem de aviso
    
    Args:
        message: Mensagem a exibir
    """
    st.warning(message)


def show_info_message(message):
    """
    Mostra mensagem informativa
    
    Args:
        message: Mensagem a exibir
    """
    st.info(message)
