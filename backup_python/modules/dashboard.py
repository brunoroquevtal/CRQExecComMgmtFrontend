"""
Módulo para componentes do dashboard
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from modules.calculations import (
    calculate_statistics, get_activities_by_status,
    get_delayed_activities, get_next_activities,
    get_milestones
)
from modules.ui import render_status_card, render_sequence_status_card


def render_main_indicators(stats):
    """
    Renderiza indicadores principais (cards)
    
    Args:
        stats: Estatísticas calculadas
    """
    st.subheader("📊 Indicadores Principais")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    geral = stats["geral"]
    
    with col1:
        render_status_card("Total de Atividades", geral["total"])
    
    with col2:
        pct = geral.get("pct_concluidas", 0)
        render_status_card(
            "✅ Concluídas",
            f"{geral['concluidas']} ({pct:.1f}%)",
            delta=None
        )
    
    with col3:
        pct = geral.get("pct_em_execucao", 0)
        render_status_card(
            "⏳ Em Execução",
            f"{geral['em_execucao']} ({pct:.1f}%)",
            delta=None
        )
    
    with col4:
        pct = geral.get("pct_planejadas", 0)
        render_status_card(
            "🟡 Planejadas",
            f"{geral['planejadas']} ({pct:.1f}%)",
            delta=None
        )
    
    with col5:
        pct = geral.get("pct_atrasadas", 0)
        render_status_card(
            "🔴 Atrasadas",
            f"{geral['atrasadas']} ({pct:.1f}%)",
            delta="negative" if geral['atrasadas'] > 0 else None
        )
    
    st.divider()


def render_burndown_chart(data_dict, crq_filtro=None):
    """
    Renderiza gráfico Burndown com tempo no eixo horizontal
    Apenas atividades "Concluídas" reduzem o trabalho restante.
    Outros status (Em Execução, Atrasado, Adiantado) são tratados como "Planejado".
    
    Args:
        data_dict: Dicionário com dataframes
        crq_filtro: CRQ específico para filtrar (None para todas)
    """
    import pandas as pd
    from datetime import datetime
    from config import SEQUENCIAS, DATE_FORMAT
    from modules.calculations import parse_datetime_string
    
    # Filtro por CRQ
    col1, col2 = st.columns([1, 3])
    with col1:
        crqs_disponiveis = ["Todas"] + sorted(list(data_dict.keys()))
        crq_selecionado = st.selectbox(
            "Filtrar por CRQ:",
            crqs_disponiveis,
            key="burndown_crq_filter",
            index=0
        )
    
    # Determinar qual CRQ usar
    if crq_selecionado == "Todas":
        crqs_para_processar = sorted(list(data_dict.keys()))
    else:
        if crq_selecionado in data_dict:
            crqs_para_processar = [crq_selecionado]
        else:
            st.warning(f"CRQ '{crq_selecionado}' não encontrado")
            return
    
    # Coletar todas as atividades e calcular totais
    all_activities = []
    total_atividades = 0
    
    for crq in crqs_para_processar:
        if crq not in data_dict:
            continue
        
        df = data_dict[crq]["dataframe"].copy()
        
        # Excluir milestones das contagens
        if "Is_Milestone" in df.columns:
            df = df[df["Is_Milestone"].fillna(False) == False]
        
        total_atividades += len(df)
        
        # Coletar atividades concluídas com data de fim real
        for _, row in df.iterrows():
            status = row.get("Status", "Planejado")
            if status == "Concluído":
                horario_fim_real = row.get("Horario_Fim_Real")
                if horario_fim_real and pd.notna(horario_fim_real) and str(horario_fim_real).strip():
                    try:
                        # Tentar parsear a data
                        if isinstance(horario_fim_real, str):
                            dt = parse_datetime_string(horario_fim_real)
                        elif hasattr(horario_fim_real, 'to_pydatetime'):
                            dt = horario_fim_real.to_pydatetime()
                        elif isinstance(horario_fim_real, datetime):
                            dt = horario_fim_real
                        else:
                            continue
                        
                        if dt:
                            all_activities.append({
                                'data': dt,
                                'crq': crq
                            })
                    except:
                        continue
    
    if total_atividades == 0:
        st.info("Não há atividades para exibir")
        return
    
    # Ordenar atividades por data
    all_activities.sort(key=lambda x: x['data'])
    
    # Calcular burndown ao longo do tempo
    if not all_activities:
        # Se não há atividades concluídas, mostrar apenas o total
        timestamps = [datetime.now()]
        restantes = [total_atividades]
        concluidas = [0]
    else:
        # Criar pontos temporais: início (total) + cada conclusão
        timestamps = []
        restantes = []
        concluidas = []
        
        # Ponto inicial: todas as atividades ainda pendentes
        if all_activities:
            # Usar a primeira data de conclusão ou data atual como início
            primeira_data = all_activities[0]['data']
            timestamps.append(primeira_data)
            restantes.append(total_atividades)
            concluidas.append(0)
        
        # Adicionar pontos para cada atividade concluída
        concluidas_count = 0
        for activity in all_activities:
            concluidas_count += 1
            timestamps.append(activity['data'])
            restantes.append(total_atividades - concluidas_count)
            concluidas.append(concluidas_count)
        
        # Adicionar ponto final (atual)
        timestamps.append(datetime.now())
        restantes.append(total_atividades - concluidas_count)
        concluidas.append(concluidas_count)
    
    # Criar gráfico Burndown
    fig = go.Figure()
    
    # Linha do trabalho restante (real)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=restantes,
        mode='lines+markers',
        name='Trabalho Restante (Real)',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=8, color='#dc3545'),
        hovertemplate='<b>%{x|%d/%m/%Y %H:%M:%S}</b><br>Trabalho Restante: %{y} atividades<extra></extra>',
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.1)'
    ))
    
    # Linha do trabalho total (inicial) - constante
    if timestamps:
        fig.add_trace(go.Scatter(
            x=[timestamps[0], timestamps[-1]],
            y=[total_atividades, total_atividades],
            mode='lines',
            name='Total de Atividades',
            line=dict(color='#6c757d', width=2, dash='dash'),
            hovertemplate='Total: %{y} atividades<extra></extra>'
        ))
    
    # Linha das concluídas acumuladas (para referência)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=concluidas,
        mode='lines+markers',
        name='Concluídas (Acumulado)',
        line=dict(color='#28a745', width=2),
        marker=dict(size=6, color='#28a745'),
        hovertemplate='<b>%{x|%d/%m/%Y %H:%M:%S}</b><br>Concluídas: %{y} atividades<extra></extra>'
    ))
    
    # Configurar layout
    titulo = f'📉 Gráfico Burndown - Trabalho Restante ao Longo do Tempo'
    if crq_selecionado != "Todas":
        crq_info = SEQUENCIAS.get(crq_selecionado, {})
        nome_crq = crq_info.get("nome", crq_selecionado)
        titulo += f' ({nome_crq})'
    
    fig.update_layout(
        title={
            'text': titulo,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Data/Hora",
        yaxis_title="Quantidade de Atividades",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        yaxis=dict(
            rangemode='tozero',
            gridcolor='lightgray',
            gridwidth=1
        ),
        xaxis=dict(
            gridcolor='lightgray',
            gridwidth=1,
            type='date',
            tickformat='%d/%m/%Y %H:%M'
        ),
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Adicionar informações adicionais
    st.info("ℹ️ **Como funciona o Burndown:**\n"
           "- Apenas atividades **Concluídas** reduzem o trabalho restante\n"
           "- Status como Em Execução, Atrasado e Adiantado são tratados como Planejado (não reduzem o total)\n"
           "- O trabalho restante = Total - Concluídas")


def render_gantt_chart(data_dict):
    """
    Renderiza gráfico de Gantt mostrando CRQs no eixo vertical e horários no horizontal
    Mostra barras planejadas e reais, com linha vertical indicando data/hora atual
    
    Args:
        data_dict: Dicionário com dataframes por CRQ
    """
    from modules.calculations import parse_datetime_string
    from config import SEQUENCIAS
    from datetime import datetime, timezone, timedelta
    
    st.subheader("📊 Gráfico de Gantt - CRQs vs Horários")
    
    # Data/hora atual (GMT-3)
    gmt_minus_3 = timezone(timedelta(hours=-3))
    agora = datetime.now(gmt_minus_3)
    agora_naive = agora.replace(tzinfo=None) if agora.tzinfo else agora
    
    # Coletar dados de todas as atividades por CRQ
    gantt_data = []
    
    for sequencia, data in data_dict.items():
        df = data["dataframe"]
        
        # Filtrar apenas atividades (não milestones)
        if "Is_Milestone" in df.columns:
            df_activities = df[df["Is_Milestone"].fillna(False) != True].copy()
        else:
            df_activities = df.copy()
        
        # Calcular início e fim planejados e reais para o CRQ (uma barra por CRQ)
        # Início planejado: menor data de início entre todas as atividades
        # Fim planejado: maior data de fim entre todas as atividades
        # Início real: menor data de início real entre todas as atividades
        # Fim real: maior data de fim real entre todas as atividades
        # Também coletar informações sobre atividades em execução e adiantadas
        inicio_planejado_min = None
        fim_planejado_max = None
        inicio_real_min = None
        fim_real_max = None
        
        # Para atividades em execução: calcular período de execução
        inicio_execucao_min = None
        fim_execucao_max = None  # Será agora ou fim_real, o que vier primeiro
        
        # Para atividades adiantadas: verificar se há parte após a linha do tempo
        tem_adiantadas = False
        fim_adiantada_max = None
        
        for idx, row in df_activities.iterrows():
            # Datas planejadas
            inicio_planejado = row.get("Inicio")
            fim_planejado = row.get("Fim")
            
            if pd.notna(inicio_planejado):
                if isinstance(inicio_planejado, (datetime, pd.Timestamp)):
                    inicio_dt = inicio_planejado.to_pydatetime() if isinstance(inicio_planejado, pd.Timestamp) else inicio_planejado
                else:
                    inicio_dt = parse_datetime_string(str(inicio_planejado))
                if inicio_dt:
                    # Remover timezone se existir
                    if inicio_dt.tzinfo is not None:
                        inicio_dt = inicio_dt.replace(tzinfo=None)
                    if inicio_planejado_min is None or inicio_dt < inicio_planejado_min:
                        inicio_planejado_min = inicio_dt
            
            if pd.notna(fim_planejado):
                if isinstance(fim_planejado, (datetime, pd.Timestamp)):
                    fim_dt = fim_planejado.to_pydatetime() if isinstance(fim_planejado, pd.Timestamp) else fim_planejado
                else:
                    fim_dt = parse_datetime_string(str(fim_planejado))
                if fim_dt:
                    # Remover timezone se existir
                    if fim_dt.tzinfo is not None:
                        fim_dt = fim_dt.replace(tzinfo=None)
                    if fim_planejado_max is None or fim_dt > fim_planejado_max:
                        fim_planejado_max = fim_dt
            
            # Datas reais
            inicio_real = row.get("Horario_Inicio_Real")
            fim_real = row.get("Horario_Fim_Real")
            status = str(row.get("Status", "")).strip()
            
            # Para atividades concluídas ou adiantadas, sempre considerar o fim_real
            # mesmo que seja anterior à hora atual (mostra que foi cumprida)
            is_concluida_ou_adiantada = status in ["Concluído", "Atrasado", "Adiantado"]
            is_em_execucao = status == "Em Execução" or status == "Adiantado"
            is_adiantada = status == "Adiantado"
            
            if pd.notna(inicio_real):
                if isinstance(inicio_real, (datetime, pd.Timestamp)):
                    inicio_dt = inicio_real.to_pydatetime() if isinstance(inicio_real, pd.Timestamp) else inicio_real
                elif isinstance(inicio_real, str):
                    inicio_dt = parse_datetime_string(inicio_real)
                else:
                    inicio_dt = None
                if inicio_dt:
                    # Remover timezone se existir
                    if inicio_dt.tzinfo is not None:
                        inicio_dt = inicio_dt.replace(tzinfo=None)
                    if inicio_real_min is None or inicio_dt < inicio_real_min:
                        inicio_real_min = inicio_dt
            
            if pd.notna(fim_real):
                if isinstance(fim_real, (datetime, pd.Timestamp)):
                    fim_dt = fim_real.to_pydatetime() if isinstance(fim_real, pd.Timestamp) else fim_real
                elif isinstance(fim_real, str):
                    fim_dt = parse_datetime_string(fim_real)
                else:
                    fim_dt = None
                if fim_dt:
                    # Remover timezone se existir
                    if fim_dt.tzinfo is not None:
                        fim_dt = fim_dt.replace(tzinfo=None)
                    # Sempre considerar o fim_real, especialmente para atividades concluídas/adiantadas
                    # mesmo que seja anterior à hora atual (mostra que foi cumprida)
                    if fim_real_max is None or fim_dt > fim_real_max:
                        fim_real_max = fim_dt
                    
                    # Se é adiantada, marcar para barra tracejada
                    if is_adiantada:
                        tem_adiantadas = True
                        if fim_adiantada_max is None or fim_dt > fim_adiantada_max:
                            fim_adiantada_max = fim_dt
            
            # Coletar informações sobre atividades em execução
            if is_em_execucao and inicio_dt:  # inicio_dt foi calculado acima
                if inicio_execucao_min is None or inicio_dt < inicio_execucao_min:
                    inicio_execucao_min = inicio_dt
                
                # Fim de execução: se tem fim_real, usar ele; senão, será agora (será calculado depois)
                if fim_dt:  # fim_dt foi calculado acima se existe
                    if fim_execucao_max is None or fim_dt > fim_execucao_max:
                        fim_execucao_max = fim_dt
            elif is_concluida_ou_adiantada:
                # Se está concluída/adiantada mas não tem fim_real, usar o fim planejado como referência
                # para garantir que a barra seja mostrada
                if pd.notna(fim_planejado):
                    if isinstance(fim_planejado, (datetime, pd.Timestamp)):
                        fim_dt = fim_planejado.to_pydatetime() if isinstance(fim_planejado, pd.Timestamp) else fim_planejado
                    else:
                        fim_dt = parse_datetime_string(str(fim_planejado))
                    if fim_dt:
                        if fim_dt.tzinfo is not None:
                            fim_dt = fim_dt.replace(tzinfo=None)
                        if fim_real_max is None or fim_dt > fim_real_max:
                            fim_real_max = fim_dt
        
        # Adicionar dados do CRQ se tiver pelo menos uma data
        # Uma única entrada por CRQ com o range completo (início mínimo ao fim máximo)
        if inicio_planejado_min or fim_planejado_max or inicio_real_min or fim_real_max:
            gantt_data.append({
                "CRQ": sequencia,
                "Inicio_Planejado": inicio_planejado_min,
                "Fim_Planejado": fim_planejado_max,
                "Inicio_Real": inicio_real_min,
                "Fim_Real": fim_real_max,
                "Inicio_Execucao": inicio_execucao_min,
                "Fim_Execucao": fim_execucao_max,  # Será ajustado para agora se necessário
                "Tem_Adiantadas": tem_adiantadas,
                "Fim_Adiantada": fim_adiantada_max
            })
    
    if not gantt_data:
        st.info("ℹ️ Não há dados suficientes para gerar o gráfico de Gantt. É necessário ter atividades com datas planejadas ou reais.")
        return
    
    # Criar gráfico de Gantt
    fig = go.Figure()
    
    # Ordenar CRQs
    crqs_ordenados = sorted([d["CRQ"] for d in gantt_data])
    
    # Preparar dados para o gráfico
    y_positions = list(range(len(crqs_ordenados)))
    y_labels = []
    
    # Encontrar range de datas para o eixo X
    # IMPORTANTE: Incluir TODAS as datas reais, mesmo que sejam anteriores à hora atual
    # Isso garante que atividades concluídas/adiantadas sejam sempre visíveis
    todas_datas = []
    for d in gantt_data:
        if d["Inicio_Planejado"]:
            todas_datas.append(d["Inicio_Planejado"])
        if d["Fim_Planejado"]:
            todas_datas.append(d["Fim_Planejado"])
        if d["Inicio_Real"]:
            todas_datas.append(d["Inicio_Real"])
        if d["Fim_Real"]:
            # Sempre incluir fim_real, mesmo que seja anterior à hora atual
            # Isso mostra que a atividade foi cumprida (concluída/adiantada)
            todas_datas.append(d["Fim_Real"])
    
    if not todas_datas:
        st.info("ℹ️ Não há datas válidas para gerar o gráfico de Gantt.")
        return
    
    # Converter para datetime se necessário e normalizar timezone
    todas_datas_dt = []
    for dt in todas_datas:
        if isinstance(dt, pd.Timestamp):
            dt_py = dt.to_pydatetime()
        elif isinstance(dt, datetime):
            dt_py = dt
        else:
            continue
        
        # Remover timezone se existir para normalizar comparações
        if dt_py.tzinfo is not None:
            dt_py = dt_py.replace(tzinfo=None)
        
        todas_datas_dt.append(dt_py)
    
    min_date = min(todas_datas_dt)
    max_date = max(todas_datas_dt)
    
    # Adicionar margem de 10% em cada lado
    date_range = (max_date - min_date).total_seconds()
    margin = date_range * 0.1
    min_date = min_date - timedelta(seconds=margin)
    max_date = max_date + timedelta(seconds=margin)
    
    # Remover timezone de agora para comparar
    agora_naive = agora.replace(tzinfo=None) if agora.tzinfo else agora
    
    # Garantir que a data atual esteja no range (se estiver fora, expandir o range)
    if agora_naive < min_date:
        min_date = agora_naive - timedelta(hours=1)
    elif agora_naive > max_date:
        max_date = agora_naive + timedelta(hours=1)
    
    # Adicionar linha vertical para data/hora atual (sempre mostrar)
    # Usar add_shape em vez de add_vline para melhor compatibilidade com datetime
    fig.add_shape(
        type="line",
        x0=agora_naive,
        x1=agora_naive,
        y0=-0.5,
        y1=len(crqs_ordenados) - 0.5,
        line=dict(color="red", width=3, dash="dash"),
    )
    
    # Adicionar anotação separada
    fig.add_annotation(
        x=agora_naive,
        y=len(crqs_ordenados) - 0.5,
        text=f"Agora: {agora.strftime('%d/%m/%Y %H:%M:%S')}",
        showarrow=False,
        font=dict(size=12, color="red"),
        bgcolor="white",
        bordercolor="red",
        borderwidth=1,
        xshift=10
    )
    
    # Adicionar barras para cada CRQ
    for i, crq in enumerate(crqs_ordenados):
        crq_info = SEQUENCIAS.get(crq, {})
        emoji = crq_info.get("emoji", "📋")
        nome = crq_info.get("nome", crq)
        y_labels.append(f"{emoji} {nome}")
        
        # Encontrar dados do CRQ
        crq_data = next((d for d in gantt_data if d["CRQ"] == crq), None)
        if not crq_data:
            continue
        
        # Barra planejada
        if crq_data["Inicio_Planejado"] and crq_data["Fim_Planejado"]:
            inicio_p = crq_data["Inicio_Planejado"]
            fim_p = crq_data["Fim_Planejado"]
            
            # Converter para datetime se necessário e remover timezone
            if isinstance(inicio_p, pd.Timestamp):
                inicio_p = inicio_p.to_pydatetime()
            if isinstance(fim_p, pd.Timestamp):
                fim_p = fim_p.to_pydatetime()
            
            # Remover timezone se existir
            if isinstance(inicio_p, datetime) and inicio_p.tzinfo is not None:
                inicio_p = inicio_p.replace(tzinfo=None)
            if isinstance(fim_p, datetime) and fim_p.tzinfo is not None:
                fim_p = fim_p.replace(tzinfo=None)
            
            fig.add_trace(go.Scatter(
                x=[inicio_p, fim_p, fim_p, inicio_p, inicio_p],
                y=[i-0.2, i-0.2, i+0.2, i+0.2, i-0.2],
                fill='toself',
                fillcolor='rgba(0, 123, 255, 0.6)',
                line=dict(color='#007bff', width=2),
                name='Planejado',
                showlegend=(i == 0),
                hovertemplate=f'<b>{nome}</b><br>Planejado: {inicio_p.strftime("%d/%m/%Y %H:%M:%S")} - {fim_p.strftime("%d/%m/%Y %H:%M:%S")}<extra></extra>',
                mode='lines'
            ))
        
        # Barra real
        if crq_data["Inicio_Real"] and crq_data["Fim_Real"]:
            inicio_r = crq_data["Inicio_Real"]
            fim_r = crq_data["Fim_Real"]
            
            # Converter para datetime se necessário e remover timezone
            if isinstance(inicio_r, pd.Timestamp):
                inicio_r = inicio_r.to_pydatetime()
            if isinstance(fim_r, pd.Timestamp):
                fim_r = fim_r.to_pydatetime()
            
            # Remover timezone se existir
            if isinstance(inicio_r, datetime) and inicio_r.tzinfo is not None:
                inicio_r = inicio_r.replace(tzinfo=None)
            if isinstance(fim_r, datetime) and fim_r.tzinfo is not None:
                fim_r = fim_r.replace(tzinfo=None)
            
            # Verificar se há parte adiantada (fim_r > agora_naive)
            tem_parte_adiantada = crq_data.get("Tem_Adiantadas", False) and fim_r > agora_naive
            
            if tem_parte_adiantada:
                # Dividir a barra: parte sólida até agora, parte tracejada após agora
                # Parte sólida (até agora)
                if inicio_r < agora_naive:
                    fig.add_trace(go.Scatter(
                        x=[inicio_r, agora_naive, agora_naive, inicio_r, inicio_r],
                        y=[i-0.2, i-0.2, i+0.2, i+0.2, i-0.2],
                        fill='toself',
                        fillcolor='rgba(40, 167, 69, 0.6)',
                        line=dict(color='#28a745', width=2),
                        name='Real',
                        showlegend=(i == 0),
                        hovertemplate=f'<b>{nome}</b><br>Real: {inicio_r.strftime("%d/%m/%Y %H:%M:%S")} - {agora_naive.strftime("%d/%m/%Y %H:%M:%S")}<extra></extra>',
                        mode='lines'
                    ))
                
                # Parte tracejada (após agora - adiantada)
                fig.add_trace(go.Scatter(
                    x=[agora_naive, fim_r, fim_r, agora_naive, agora_naive],
                    y=[i-0.2, i-0.2, i+0.2, i+0.2, i-0.2],
                    fill='toself',
                    fillcolor='rgba(40, 167, 69, 0.3)',
                    line=dict(color='#28a745', width=2, dash='dash'),
                    name='Real (Adiantada)',
                    showlegend=(i == 0),
                    hovertemplate=f'<b>{nome}</b><br>Real (Adiantada): {agora_naive.strftime("%d/%m/%Y %H:%M:%S")} - {fim_r.strftime("%d/%m/%Y %H:%M:%S")}<extra></extra>',
                    mode='lines'
                ))
            else:
                # Barra sólida normal
                fig.add_trace(go.Scatter(
                    x=[inicio_r, fim_r, fim_r, inicio_r, inicio_r],
                    y=[i-0.2, i-0.2, i+0.2, i+0.2, i-0.2],
                    fill='toself',
                    fillcolor='rgba(40, 167, 69, 0.6)',
                    line=dict(color='#28a745', width=2),
                    name='Real',
                    showlegend=(i == 0),
                    hovertemplate=f'<b>{nome}</b><br>Real: {inicio_r.strftime("%d/%m/%Y %H:%M:%S")} - {fim_r.strftime("%d/%m/%Y %H:%M:%S")}<extra></extra>',
                    mode='lines'
                ))
        
        # Barra laranja tracejada para atividades em execução
        if crq_data.get("Inicio_Execucao"):
            inicio_exec = crq_data["Inicio_Execucao"]
            fim_exec = crq_data.get("Fim_Execucao")
            
            # Converter para datetime se necessário
            if isinstance(inicio_exec, pd.Timestamp):
                inicio_exec = inicio_exec.to_pydatetime()
            if fim_exec and isinstance(fim_exec, pd.Timestamp):
                fim_exec = fim_exec.to_pydatetime()
            
            # Remover timezone se existir
            if isinstance(inicio_exec, datetime) and inicio_exec.tzinfo is not None:
                inicio_exec = inicio_exec.replace(tzinfo=None)
            if fim_exec and isinstance(fim_exec, datetime) and fim_exec.tzinfo is not None:
                fim_exec = fim_exec.replace(tzinfo=None)
            
            # Fim de execução: usar fim_exec se existir, senão usar agora
            fim_exec_final = fim_exec if fim_exec else agora_naive
            
            # Só mostrar se o fim for maior que o início
            if fim_exec_final > inicio_exec:
                fig.add_trace(go.Scatter(
                    x=[inicio_exec, fim_exec_final, fim_exec_final, inicio_exec, inicio_exec],
                    y=[i-0.15, i-0.15, i+0.15, i+0.15, i-0.15],
                    fill='toself',
                    fillcolor='rgba(255, 165, 0, 0.4)',
                    line=dict(color='#ff8c00', width=2, dash='dash'),
                    name='Em Execução',
                    showlegend=(i == 0),
                    hovertemplate=f'<b>{nome}</b><br>Em Execução: {inicio_exec.strftime("%d/%m/%Y %H:%M:%S")} - {fim_exec_final.strftime("%d/%m/%Y %H:%M:%S")}<extra></extra>',
                    mode='lines'
                ))
    
    # Configurar layout
    fig.update_layout(
        title={
            'text': '📊 Gráfico de Gantt - CRQs vs Horários',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Data/Hora",
        yaxis_title="CRQ",
        yaxis=dict(
            tickmode='array',
            tickvals=y_positions,
            ticktext=y_labels,
            autorange="reversed"  # Inverter para ter o primeiro CRQ no topo
        ),
        xaxis=dict(
            type='date',
            tickformat='%d/%m/%Y %H:%M',
            range=[min_date, max_date]
        ),
        height=max(400, len(crqs_ordenados) * 100),
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Informações adicionais
    st.caption(f"💡 Linha vermelha vertical indica a data/hora atual: {agora.strftime('%d/%m/%Y %H:%M:%S')} (GMT-3)")
    
    st.divider()
    
    # Lista de atividades que deveriam estar em execução e não estão
    render_activities_execution_status(data_dict, agora_naive)


def render_activities_execution_status(data_dict, agora):
    """
    Renderiza lista de atividades que deveriam estar em execução e não estão,
    e atividades em execução indicando se estão adiantadas
    
    Args:
        data_dict: Dicionário com dataframes por CRQ
        agora: Data/hora atual (datetime sem timezone)
    """
    from datetime import datetime
    from config import SEQUENCIAS
    from modules.calculations import parse_datetime_string
    
    st.subheader("📋 Status de Execução das Atividades")
    
    atividades_atrasadas = []  # Deveriam estar em execução mas não estão
    atividades_em_execucao = []  # Estão em execução (com indicação de adiantamento)
    
    for sequencia, data in data_dict.items():
        df = data["dataframe"]
        
        # Filtrar apenas atividades (não milestones)
        if "Is_Milestone" in df.columns:
            df_activities = df[df["Is_Milestone"].fillna(False) != True].copy()
        else:
            df_activities = df.copy()
        
        crq_info = SEQUENCIAS.get(sequencia, {})
        emoji = crq_info.get("emoji", "📋")
        nome_crq = crq_info.get("nome", sequencia)
        
        for idx, row in df_activities.iterrows():
            status = str(row.get("Status", "")).strip()
            atividade = str(row.get("Atividade", "")).strip()
            seq = row.get("Seq", "")
            
            # Datas planejadas
            inicio_planejado = row.get("Inicio")
            
            # Data de início real
            inicio_real = row.get("Horario_Inicio_Real")
            
            # Converter datas para datetime
            inicio_planejado_dt = None
            if pd.notna(inicio_planejado):
                if isinstance(inicio_planejado, (datetime, pd.Timestamp)):
                    inicio_planejado_dt = inicio_planejado.to_pydatetime() if isinstance(inicio_planejado, pd.Timestamp) else inicio_planejado
                else:
                    inicio_planejado_dt = parse_datetime_string(str(inicio_planejado))
                if inicio_planejado_dt and inicio_planejado_dt.tzinfo is not None:
                    inicio_planejado_dt = inicio_planejado_dt.replace(tzinfo=None)
            
            inicio_real_dt = None
            if pd.notna(inicio_real):
                if isinstance(inicio_real, (datetime, pd.Timestamp)):
                    inicio_real_dt = inicio_real.to_pydatetime() if isinstance(inicio_real, pd.Timestamp) else inicio_real
                elif isinstance(inicio_real, str):
                    inicio_real_dt = parse_datetime_string(inicio_real)
                if inicio_real_dt and inicio_real_dt.tzinfo is not None:
                    inicio_real_dt = inicio_real_dt.replace(tzinfo=None)
            
            # Verificar se deveria estar em execução
            if inicio_planejado_dt and inicio_planejado_dt <= agora:
                # Já passou do horário planejado de início
                if status not in ["Em Execução", "Concluído", "Atrasado", "Adiantado"]:
                    # Deveria estar em execução mas não está
                    atividades_atrasadas.append({
                        "CRQ": nome_crq,
                        "Emoji": emoji,
                        "Seq": seq,
                        "Atividade": atividade,
                        "Inicio_Planejado": inicio_planejado_dt,
                        "Status": status
                    })
                elif status == "Em Execução" or status == "Adiantado":
                    # Está em execução, verificar se está adiantada
                    is_adiantada = False
                    if inicio_real_dt and inicio_planejado_dt:
                        if inicio_real_dt < inicio_planejado_dt:
                            is_adiantada = True
                    
                    atividades_em_execucao.append({
                        "CRQ": nome_crq,
                        "Emoji": emoji,
                        "Seq": seq,
                        "Atividade": atividade,
                        "Inicio_Planejado": inicio_planejado_dt,
                        "Inicio_Real": inicio_real_dt,
                        "Is_Adiantada": is_adiantada
                    })
    
    # Exibir atividades que deveriam estar em execução e não estão
    if atividades_atrasadas:
        st.markdown("#### 🚨 Atividades que Deveriam Estar em Execução")
        
        # Agrupar por CRQ
        for sequencia_key, sequencia_info in SEQUENCIAS.items():
            crq_atrasadas = [a for a in atividades_atrasadas if a["CRQ"] == sequencia_info["nome"]]
            if crq_atrasadas:
                emoji = sequencia_info["emoji"]
                nome = sequencia_info["nome"]
                st.markdown(f"**{emoji} {nome}**")
                
                for ativ in crq_atrasadas:
                    inicio_str = ativ["Inicio_Planejado"].strftime("%d/%m/%Y %H:%M:%S") if ativ["Inicio_Planejado"] else "N/A"
                    st.markdown(f"  - Seq {ativ['Seq']}: {ativ['Atividade']} (Início planejado: {inicio_str}, Status: {ativ['Status']})")
        
        st.divider()
    else:
        st.info("✅ Todas as atividades que deveriam estar em execução já estão em execução ou concluídas.")
        st.divider()
    
    # Exibir atividades em execução com indicação de adiantamento
    if atividades_em_execucao:
        st.markdown("#### ⏳ Atividades em Execução")
        
        # Agrupar por CRQ
        for sequencia_key, sequencia_info in SEQUENCIAS.items():
            crq_execucao = [a for a in atividades_em_execucao if a["CRQ"] == sequencia_info["nome"]]
            if crq_execucao:
                emoji = sequencia_info["emoji"]
                nome = sequencia_info["nome"]
                st.markdown(f"**{emoji} {nome}**")
                
                for ativ in crq_execucao:
                    inicio_planejado_str = ativ["Inicio_Planejado"].strftime("%d/%m/%Y %H:%M:%S") if ativ["Inicio_Planejado"] else "N/A"
                    inicio_real_str = ativ["Inicio_Real"].strftime("%d/%m/%Y %H:%M:%S") if ativ["Inicio_Real"] else "N/A"
                    
                    if ativ["Is_Adiantada"]:
                        st.markdown(f"  - ✅ Seq {ativ['Seq']}: {ativ['Atividade']} (Adiantada - Início real: {inicio_real_str}, Planejado: {inicio_planejado_str})")
                    else:
                        st.markdown(f"  - ⏳ Seq {ativ['Seq']}: {ativ['Atividade']} (Início real: {inicio_real_str}, Planejado: {inicio_planejado_str})")
        
        st.divider()
    else:
        st.info("ℹ️ Não há atividades em execução no momento.")


def render_activities_tables(data_dict):
    """
    Renderiza tabelas de detalhes
    
    Args:
        data_dict: Dicionário com dataframes
    """
    import pandas as pd
    
    # Função para garantir que colunas sensíveis sejam string
    def ensure_string_columns(df):
        """Garante que colunas sensíveis sejam string para evitar erros do PyArrow"""
        if df is None or len(df) == 0:
            return df
        
        def safe_str_convert(val):
            if pd.isna(val) or val is None:
                return ""
            try:
                if isinstance(val, (int, float)):
                    return str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
                return str(val)
            except:
                return ""
        
        for col in ["Telefone", "Grupo", "Localidade", "Executor", "Tempo", "Atividade"]:
            if col in df.columns:
                df[col] = df[col].apply(safe_str_convert)
        
        return df
    
    st.subheader("📋 Tabelas de Detalhes")
    
    # Tabela 1: Atividades em Execução (segmentada por CRQ)
    st.markdown("#### ⏳ Atividades em Execução")
    exec_df = get_activities_by_status(data_dict, "Em Execução")
    exec_df = ensure_string_columns(exec_df)
    
    if len(exec_df) > 0:
        # Agrupar por CRQ
        if "CRQ" in exec_df.columns:
            for crq in sorted(exec_df["CRQ"].unique()):
                crq_df = exec_df[exec_df["CRQ"] == crq].copy()
                from config import SEQUENCIAS
                crq_info = SEQUENCIAS.get(crq, {})
                emoji = crq_info.get("emoji", "📊")
                nome = crq_info.get("nome", crq)
                
                st.markdown(f"**{emoji} {nome}** ({len(crq_df)} atividades)")
                display_cols = ["Seq", "Atividade", "CRQ", "Grupo", "Tempo", "Horario_Inicio_Real"]
                available_cols = [col for col in display_cols if col in crq_df.columns]
                crq_display = crq_df[available_cols].sort_values("Seq")
                st.dataframe(crq_display, width='stretch', hide_index=True)
                st.divider()
        else:
            display_cols = ["Seq", "Atividade", "CRQ", "Grupo", "Tempo", "Horario_Inicio_Real"]
            available_cols = [col for col in display_cols if col in exec_df.columns]
            exec_display = exec_df[available_cols].sort_values("Seq")
            st.dataframe(exec_display, width='stretch', hide_index=True)
    else:
        st.info("Não há atividades em execução no momento")
    
    st.divider()
    
    # Tabela 2: Atividades Atrasadas (segmentada por CRQ)
    st.markdown("#### 🚨 Atividades Atrasadas")
    delayed_df = get_delayed_activities(data_dict)
    delayed_df = ensure_string_columns(delayed_df)
    
    if len(delayed_df) > 0:
        from modules.calculations import format_delay
        delayed_display = delayed_df.copy()
        delayed_display["Atraso"] = delayed_display["Atraso_Minutos"].apply(format_delay)
        
        # Agrupar por CRQ
        if "CRQ" in delayed_display.columns:
            for crq in sorted(delayed_display["CRQ"].unique()):
                crq_df = delayed_display[delayed_display["CRQ"] == crq].copy()
                from config import SEQUENCIAS
                crq_info = SEQUENCIAS.get(crq, {})
                emoji = crq_info.get("emoji", "📊")
                nome = crq_info.get("nome", crq)
                
                st.markdown(f"**{emoji} {nome}** ({len(crq_df)} atividades)")
                display_cols = ["Seq", "Atividade", "CRQ", "Grupo", "Atraso", "Observacoes"]
                available_cols = [col for col in display_cols if col in crq_df.columns]
                # Ordenar antes de filtrar colunas (usando Atraso_Minutos que existe no DataFrame original)
                if "Atraso_Minutos" in crq_df.columns:
                    crq_df_sorted = crq_df.sort_values("Atraso_Minutos", ascending=False)
                else:
                    crq_df_sorted = crq_df
                crq_display = crq_df_sorted[available_cols]
                st.dataframe(crq_display, width='stretch', hide_index=True)
                st.divider()
        else:
            display_cols = ["Seq", "Atividade", "CRQ", "Grupo", "Atraso", "Observacoes"]
            available_cols = [col for col in display_cols if col in delayed_display.columns]
            # Ordenar antes de filtrar colunas (usando Atraso_Minutos que existe no DataFrame original)
            if "Atraso_Minutos" in delayed_display.columns:
                delayed_display_sorted = delayed_display.sort_values("Atraso_Minutos", ascending=False)
            else:
                delayed_display_sorted = delayed_display
            delayed_display_final = delayed_display_sorted[available_cols]
            st.dataframe(delayed_display_final, width='stretch', hide_index=True)
    else:
        st.info("Não há atividades atrasadas")
    
    st.divider()
    
    # Tabela 3: Próximas Atividades (segmentada por CRQ)
    st.markdown("#### 📅 Próximas Atividades a Executar")
    next_df = get_next_activities(data_dict, limit=10)
    next_df = ensure_string_columns(next_df)
    
    if len(next_df) > 0:
        # Agrupar por CRQ
        if "CRQ" in next_df.columns:
            for crq in sorted(next_df["CRQ"].unique()):
                crq_df = next_df[next_df["CRQ"] == crq].copy()
                from config import SEQUENCIAS
                crq_info = SEQUENCIAS.get(crq, {})
                emoji = crq_info.get("emoji", "📊")
                nome = crq_info.get("nome", crq)
                
                st.markdown(f"**{emoji} {nome}** ({len(crq_df)} atividades)")
                display_cols = ["Seq", "Atividade", "CRQ", "Grupo", "Inicio"]
                available_cols = [col for col in display_cols if col in crq_df.columns]
                crq_display = crq_df[available_cols].sort_values("Inicio")
                
                # Formatar data
                if "Inicio" in crq_display.columns:
                    crq_display["Inicio"] = crq_display["Inicio"].apply(
                        lambda x: x.strftime("%d/%m/%Y %H:%M:%S") if pd.notna(x) and hasattr(x, 'strftime') else ""
                    )
                
                st.dataframe(crq_display, width='stretch', hide_index=True)
                st.divider()
        else:
            display_cols = ["Seq", "Atividade", "CRQ", "Grupo", "Inicio"]
            available_cols = [col for col in display_cols if col in next_df.columns]
            next_display = next_df[available_cols].sort_values("Inicio")
            
            # Formatar data
            if "Inicio" in next_display.columns:
                next_display["Inicio"] = next_display["Inicio"].apply(
                    lambda x: x.strftime("%d/%m/%Y %H:%M:%S") if pd.notna(x) and hasattr(x, 'strftime') else ""
                )
            
            st.dataframe(next_display, width='stretch', hide_index=True)
    else:
        st.info("Não há próximas atividades planejadas")
    
    st.divider()


def render_sequence_status_cards(stats):
    """
    Renderiza cards de status por CRQ
    
    Args:
        stats: Estatísticas calculadas
    """
    st.subheader("📊 Status por CRQ")
    
    from config import SEQUENCIAS
    
    for sequencia_key, sequencia_info in SEQUENCIAS.items():
        if sequencia_key in stats["por_sequencia"]:
            seq_stats = stats["por_sequencia"][sequencia_key]
            # Usar total real (sem milestones) em vez do config
            total = seq_stats["total"]
            render_sequence_status_card(sequencia_key, seq_stats, total)


def render_full_dashboard(data_dict):
    """
    Renderiza dashboard completo
    
    Args:
        data_dict: Dicionário com dataframes
    """
    if not data_dict:
        st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um arquivo Excel primeiro.")
        return
    
    # Calcular estatísticas
    stats = calculate_statistics(data_dict)
    
    # Indicadores principais
    render_main_indicators(stats)
    
    st.divider()
    
    # Tabelas de detalhes
    render_activities_tables(data_dict)
    
    # Status por CRQ
    render_sequence_status_cards(stats)
    
    st.divider()
    
    # Gráfico de Gantt (CRQs vs Horários)
    render_gantt_chart(data_dict)