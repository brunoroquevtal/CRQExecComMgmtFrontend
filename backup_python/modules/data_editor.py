"""
Módulo para edição de dados
"""
import pandas as pd
import streamlit as st
from datetime import datetime
from config import DATE_FORMAT, STATUS_OPCOES
from modules.calculations import (
    calculate_delay, update_status_by_delay,
    validate_datetime_string, parse_datetime_string
)
from modules.database import DatabaseManager
from modules.auth import can_edit_data


def render_data_editor(data_dict, db_manager):
    """
    Renderiza editor de dados interativo com abas por CRQ
    
    Args:
        data_dict: Dicionário com dataframes
        db_manager: Gerenciador de banco de dados
    """
    if not data_dict:
        st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um arquivo Excel primeiro.")
        return
    
    if db_manager is None:
        st.error("❌ Gerenciador de banco de dados não inicializado.")
        return
    
    # Obter CRQs disponíveis e ordenar
    crqs = sorted(list(data_dict.keys()))
    
    if not crqs:
        st.warning("⚠️ Nenhum CRQ encontrado nos dados.")
        return
    
    # Criar lista de nomes de abas com emojis
    from config import SEQUENCIAS
    tab_names = []
    tab_keys = []
    
    # Adicionar aba "Todas" primeiro
    tab_names.append("📋 Todas")
    tab_keys.append("TODAS")
    
    # Adicionar abas para cada CRQ
    for crq in crqs:
        crq_info = SEQUENCIAS.get(crq, {})
        emoji = crq_info.get("emoji", "📊")
        nome = crq_info.get("nome", crq)
        tab_names.append(f"{emoji} {nome}")
        tab_keys.append(crq)
    
    # Criar abas
    try:
        tabs = st.tabs(tab_names)
    except Exception as e:
        st.error(f"❌ Erro ao criar abas: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return
    
    # Processar cada aba - Streamlit renderiza todas, mas só mostra a ativa
    if len(tabs) != len(tab_keys):
        st.error(f"❌ Número de abas ({len(tabs)}) não corresponde ao número de chaves ({len(tab_keys)})")
        return
    
    for idx, tab in enumerate(tabs):
        with tab:
            try:
                if idx >= len(tab_keys):
                    st.error(f"❌ Índice de aba inválido: {idx}")
                    continue
                    
                if tab_keys[idx] == "TODAS":
                    # Aba "Todas" - mostrar todas as sequências juntas
                    render_editor_tab(data_dict, None, db_manager, "Todas")
                else:
                    # Aba de CRQ específica
                    crq_selecionado = tab_keys[idx]
                    if crq_selecionado in data_dict:
                        render_editor_tab(data_dict, crq_selecionado, db_manager, crq_selecionado)
                    else:
                        st.error(f"❌ CRQ '{crq_selecionado}' não encontrado nos dados carregados.")
                        st.info(f"CRQs disponíveis: {', '.join(data_dict.keys())}")
            except Exception as e:
                st.error(f"❌ Erro ao renderizar aba '{tab_names[idx] if idx < len(tab_names) else 'desconhecida'}': {str(e)}")
                import traceback
                with st.expander("Detalhes do erro"):
                    st.code(traceback.format_exc())


def render_editor_tab(data_dict, crq_selecionado, db_manager, tab_name):
    """
    Renderiza o conteúdo de uma aba do editor
    
    Args:
        data_dict: Dicionário com dataframes
        crq_selecionado: CRQ selecionado (None para "Todas")
        db_manager: Gerenciador de banco de dados
        tab_name: Nome da aba para usar nas keys
    """
    # Validar entrada
    if not data_dict:
        st.warning("⚠️ Nenhum dado disponível")
        return
    
    if db_manager is None:
        st.error("❌ Gerenciador de banco de dados não disponível")
        return
    
    # Preparar dataframe
    try:
        if crq_selecionado is None:
            # Combinar todos os CRQs
            all_dfs = []
            for crq, data in data_dict.items():
                if "dataframe" not in data:
                    st.warning(f"⚠️ CRQ '{crq}' não tem dataframe válido")
                    continue
                df = data["dataframe"].copy()
                all_dfs.append(df)
            if all_dfs:
                df = pd.concat(all_dfs, ignore_index=True)
            else:
                st.info("Nenhum dado disponível")
                return
        else:
            if crq_selecionado not in data_dict:
                st.error(f"❌ CRQ '{crq_selecionado}' não encontrado nos dados.")
                st.info(f"CRQs disponíveis: {', '.join(data_dict.keys())}")
                return
            if "dataframe" not in data_dict[crq_selecionado]:
                st.error(f"❌ CRQ '{crq_selecionado}' não tem dataframe válido.")
                return
            df = data_dict[crq_selecionado]["dataframe"].copy()
        
        if df is None or len(df) == 0:
            st.info("Nenhum dado disponível para este CRQ")
            return
        
        # Garantir que colunas sensíveis sejam string ANTES de qualquer processamento
        # Isso evita erros do PyArrow mesmo que as colunas não sejam exibidas
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
    except Exception as e:
        st.error(f"❌ Erro ao preparar dataframe: {str(e)}")
        import traceback
        with st.expander("Detalhes do erro"):
            st.code(traceback.format_exc())
        return
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filtro por Status:",
            ["Todos"] + STATUS_OPCOES,
            key=f"status_filter_{tab_name}"
        )
    
    with col2:
        busca = st.text_input(
            "Buscar por Atividade:",
            key=f"search_activity_{tab_name}"
        )
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if status_filter != "Todos":
        df_filtered = df_filtered[df_filtered["Status"] == status_filter]
    
    if busca:
        df_filtered = df_filtered[
            df_filtered["Atividade"].str.contains(busca, case=False, na=False)
        ]
    
    st.divider()
    
    # Preparar dataframe para exibição
    display_df = df_filtered.copy()
    
    # Converter colunas que podem ter tipos mistos para string ANTES de selecionar colunas
    # (para evitar erros do PyArrow)
    def convert_to_string_safe(val):
        if pd.isna(val) or val is None:
            return ""
        try:
            # Se for numérico, converter para string
            if isinstance(val, (int, float)):
                return str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
            return str(val)
        except:
            return ""
    
    # Converter colunas problemáticas para string
    for col in ["Grupo", "Tempo", "Atividade", "Observacoes"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(convert_to_string_safe)
    
    # Selecionar colunas para exibir (removendo colunas sensíveis: Executor, Localidade, Telefone)
    columns_to_show = [
        "Seq", "Atividade", "CRQ", "Grupo", "Status",
        "Inicio", "Fim",
        "Horario_Inicio_Real", "Horario_Fim_Real",
        "Is_Milestone",
        "Tempo", "Atraso_Minutos", "Observacoes", "Predecessoras"
    ]
    
    available_cols = [col for col in columns_to_show if col in display_df.columns]
    display_df = display_df[available_cols]
    
    # Formatar datas para exibição
    date_columns = ["Inicio", "Fim", "Horario_Inicio_Real", "Horario_Fim_Real"]
    for col in date_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: x.strftime(DATE_FORMAT) if pd.notna(x) and hasattr(x, 'strftime') else ""
            )
    
    # Formatar atraso
    if "Atraso_Minutos" in display_df.columns:
        from modules.calculations import format_delay
        display_df["Atraso"] = display_df["Atraso_Minutos"].apply(format_delay)
    
    # Garantir que Is_Milestone seja boolean
    if "Is_Milestone" in display_df.columns:
        display_df["Is_Milestone"] = display_df["Is_Milestone"].fillna(False).astype(bool)
        # Converter para texto para exibição
        display_df["Milestone"] = display_df["Is_Milestone"].apply(lambda x: "✓" if x else "")
    
    # Garantir que Predecessoras seja string
    if "Predecessoras" in display_df.columns:
        display_df["Predecessoras"] = display_df["Predecessoras"].fillna("").astype(str)
    
    st.markdown(f"**Total de atividades filtradas: {len(display_df)}**")
    
    # Verificar permissão de edição
    if not can_edit_data():
        st.warning("⚠️ Você não tem permissão para editar dados. Apenas visualização permitida.")
        st.dataframe(display_df, width='stretch', hide_index=True)
        return
    
    # Inicializar estado para seleção de linha
    selection_key = f"selected_row_{tab_name}"
    if selection_key not in st.session_state:
        st.session_state[selection_key] = None
    
    # Exibir tabela somente leitura e clicável
    st.markdown("### 📋 Tabela de Atividades (Somente Leitura)")
    st.info("💡 Clique em uma linha para editar a atividade")
    
    # Criar tabela somente leitura com seleção (st.dataframe é somente leitura por padrão)
    selected_rows = st.dataframe(
        display_df,
        width='stretch',
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=f"table_{tab_name}"
    )
    
    # Processar seleção
    if selected_rows.selection.rows:
        selected_index = selected_rows.selection.rows[0]
        st.session_state[selection_key] = selected_index
    elif st.session_state[selection_key] is not None:
        # Manter seleção mesmo se não houver seleção atual (para manter o formulário aberto)
        selected_index = st.session_state[selection_key]
    else:
        selected_index = None
    
    # Exibir formulário se houver linha selecionada
    if selected_index is not None:
        try:
            # Obter dados da linha selecionada do display_df
            row_data = display_df.iloc[selected_index].to_dict()
            seq = int(row_data["Seq"])
            
            # Determinar CRQ
            if crq_selecionado is None:
                seq_crq = row_data.get("CRQ", "")
            else:
                seq_crq = crq_selecionado
            
            # IMPORTANTE: O display_df mantém a mesma ordem de linhas do df_filtered
            # O selected_index é a posição da linha no display_df
            # Podemos usar esse índice diretamente no df_filtered, pois a ordem é preservada
            
            # Obter o índice real do df_filtered usando a posição selecionada
            # O display_df é criado a partir do df_filtered com a mesma ordem de linhas
            if selected_index < len(df_filtered):
                # Usar o índice pela posição (iloc) para garantir que pegamos a linha correta
                # mesmo com Seq duplicado
                original_idx = df_filtered.iloc[selected_index].name
            else:
                # Fallback: buscar por Seq + Atividade para garantir unicidade
                atividade = str(row_data.get("Atividade", ""))
                mask = (
                    (df_filtered["Seq"] == seq) &
                    (df_filtered["Atividade"].astype(str) == atividade)
                )
                matching_indices = df_filtered[mask].index.tolist()
                
                if len(matching_indices) > 0:
                    # Se há múltiplas correspondências, usar a posição relativa
                    if selected_index < len(matching_indices):
                        original_idx = matching_indices[selected_index]
                    else:
                        original_idx = matching_indices[0]
                else:
                    # Último fallback: buscar apenas por Seq
                    matching_indices = df_filtered[df_filtered["Seq"] == seq].index.tolist()
                    if len(matching_indices) > 0:
                        original_idx = matching_indices[0] if selected_index >= len(matching_indices) else matching_indices[selected_index]
                    else:
                        st.error("❌ Erro ao localizar atividade no dataframe original")
                        return
            
            # Renderizar formulário de edição
            render_edit_form(
                df_filtered, original_idx, seq, seq_crq, crq_selecionado,
                data_dict, db_manager, tab_name, selection_key
            )
        except Exception as e:
            st.error(f"❌ Erro ao processar seleção: {str(e)}")
            import traceback
            with st.expander("Detalhes do erro"):
                st.code(traceback.format_exc())


def render_edit_form(df_filtered, original_idx, seq, seq_crq, crq_selecionado,
                     data_dict, db_manager, tab_name, selection_key):
    """
    Renderiza formulário de edição para uma atividade
    
    Args:
        df_filtered: DataFrame filtrado
        original_idx: Índice original da linha
        seq: Número sequencial da atividade
        seq_crq: CRQ da atividade
        crq_selecionado: CRQ selecionado na aba (None para "Todas")
        data_dict: Dicionário com dataframes
        db_manager: Gerenciador de banco de dados
        tab_name: Nome da aba
        selection_key: Chave para armazenar seleção
    """
    st.divider()
    st.markdown("### ✏️ Editar Atividade")
    
    # Obter dados atuais
    row = df_filtered.loc[original_idx]
    atividade_nome = row.get("Atividade", "")
    
    st.markdown(f"**Atividade {seq}:** {atividade_nome}")
    
    # Inicializar valores do formulário
    form_key = f"form_{tab_name}_{seq}"
    
    # Obter valores atuais (apenas os editáveis)
    old_status = row.get("Status", "Planejado")
    old_inicio_real = row.get("Horario_Inicio_Real", "")
    old_fim_real = row.get("Horario_Fim_Real", "")
    old_observacoes = row.get("Observacoes", "")
    
    # Converter datas para string se necessário
    if old_inicio_real and pd.notna(old_inicio_real):
        if isinstance(old_inicio_real, str):
            old_inicio_real_str = old_inicio_real.strip()
        elif hasattr(old_inicio_real, 'strftime'):
            old_inicio_real_str = old_inicio_real.strftime(DATE_FORMAT)
        else:
            old_inicio_real_str = str(old_inicio_real).strip()
    else:
        old_inicio_real_str = ""
    
    if old_fim_real and pd.notna(old_fim_real):
        if isinstance(old_fim_real, str):
            old_fim_real_str = old_fim_real.strip()
        elif hasattr(old_fim_real, 'strftime'):
            old_fim_real_str = old_fim_real.strftime(DATE_FORMAT)
        else:
            old_fim_real_str = str(old_fim_real).strip()
    else:
        old_fim_real_str = ""
    
    # Mostrar hora atual fora do formulário
    hora_atual = datetime.now().strftime(DATE_FORMAT)
    col_hora1, col_hora2 = st.columns([3, 1])
    with col_hora1:
        st.markdown(f"**🕐 Hora Atual:** `{hora_atual}`")
    with col_hora2:
        if st.button("📋 Copiar Hora", key=f"copy_hora_{form_key}"):
            try:
                import pyperclip
                pyperclip.copy(hora_atual)
                st.success("✅ Hora copiada!")
            except:
                st.info(f"💡 Selecione e copie: `{hora_atual}`")
    
    # Formulário
    with st.form(key=form_key):
        new_status = st.selectbox(
            "Status:",
            STATUS_OPCOES,
            index=STATUS_OPCOES.index(old_status) if old_status in STATUS_OPCOES else 0,
            key=f"status_{form_key}"
        )
        
        new_inicio_real = st.text_input(
            "Horário Início Real:",
            value=old_inicio_real_str,
            help=f"Formato: {DATE_FORMAT}",
            key=f"inicio_{form_key}"
        )
        
        new_fim_real = st.text_input(
            "Horário Fim Real:",
            value=old_fim_real_str,
            help=f"Formato: {DATE_FORMAT}",
            key=f"fim_{form_key}"
        )
        
        new_observacoes = st.text_area(
            "Observações:",
            value=old_observacoes if old_observacoes else "",
            key=f"obs_{form_key}"
        )
        
        # Botões
        col_save, col_cancel, col_spacer = st.columns([1, 1, 4])
        
        with col_save:
            save_button = st.form_submit_button("💾 Salvar", use_container_width=True, type="primary")
        
        with col_cancel:
            cancel_button = st.form_submit_button("❌ Cancelar", use_container_width=True)
    
    # Processar ações
    if save_button:
        # Obter valores não editáveis do dataframe original (para manter no banco)
        row = df_filtered.loc[original_idx]
        old_is_milestone = row.get("Is_Milestone", False) if "Is_Milestone" in row else False
        old_predecessoras = row.get("Predecessoras", "") if "Predecessoras" in row else ""
        
        # Validar e salvar
        if validate_and_save_activity(
            df_filtered, original_idx, seq, seq_crq, crq_selecionado,
            old_status, new_status,
            new_inicio_real, new_fim_real,
            new_observacoes, old_is_milestone, old_predecessoras,
            data_dict, db_manager
        ):
            st.success("✅ Atividade salva com sucesso!")
            # Limpar seleção
            st.session_state[selection_key] = None
            st.rerun()
    
    if cancel_button:
        # Limpar seleção sem salvar
        st.session_state[selection_key] = None
        st.rerun()


def validate_and_save_activity(df_filtered, original_idx, seq, seq_crq, crq_selecionado,
                                old_status, new_status,
                                new_inicio_real, new_fim_real,
                                new_observacoes, old_is_milestone, old_predecessoras,
                                data_dict, db_manager):
    """
    Valida e salva uma atividade
    
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    import streamlit as st  # Garantir que st está disponível
    
    # Normalizar strings vazias
    if new_inicio_real is None or (isinstance(new_inicio_real, str) and new_inicio_real.strip() == ""):
        new_inicio_real = ""
    if new_fim_real is None or (isinstance(new_fim_real, str) and new_fim_real.strip() == ""):
        new_fim_real = ""
    
    # Validar transições de status
    if new_status in ["Concluído", "Atrasado", "Adiantado"] and old_status not in ["Em Execução", "Concluído", "Atrasado", "Adiantado"]:
        st.error(f"⚠️ Para alterar o status para '{new_status}', a atividade deve estar em 'Em Execução' primeiro.")
        return False
    
    # Preencher automaticamente horários baseado na mudança de status
    hora_atual = datetime.now().strftime(DATE_FORMAT)
    old_inicio_real_value = df_filtered.loc[original_idx, "Horario_Inicio_Real"]
    old_fim_real_value = df_filtered.loc[original_idx, "Horario_Fim_Real"]
    
    # Converter valores antigos para string se necessário
    if old_inicio_real_value and pd.notna(old_inicio_real_value):
        if isinstance(old_inicio_real_value, str):
            old_inicio_real_str = old_inicio_real_value.strip()
        elif hasattr(old_inicio_real_value, 'strftime'):
            old_inicio_real_str = old_inicio_real_value.strftime(DATE_FORMAT)
        else:
            old_inicio_real_str = str(old_inicio_real_value).strip()
    else:
        old_inicio_real_str = ""
    
    # Preencher automaticamente horários baseado na mudança de status
    if old_status != new_status:
        # Caso 1: Mudou de "Planejado" para "Em Execução" - preencher Horário Início Real
        if old_status == "Planejado" and new_status == "Em Execução":
            if not new_inicio_real or new_inicio_real.strip() == "":
                new_inicio_real = hora_atual
            if not new_fim_real or new_fim_real.strip() == "":
                new_fim_real = ""
        
        # Caso 2: Mudou de "Em Execução" para "Concluído", "Atrasado" ou "Adiantado" - preencher Horário Fim Real
        elif old_status == "Em Execução" and new_status in ["Concluído", "Atrasado", "Adiantado"]:
            if not new_fim_real or new_fim_real.strip() == "":
                new_fim_real = hora_atual
            if old_inicio_real_str:
                new_inicio_real = old_inicio_real_str
            elif not new_inicio_real or new_inicio_real.strip() == "":
                new_inicio_real = hora_atual
        
        # Caso 3: Qualquer outra mudança de status
        else:
            if not new_inicio_real or new_inicio_real.strip() == "":
                if old_inicio_real_str:
                    new_inicio_real = old_inicio_real_str
                else:
                    new_inicio_real = hora_atual
    
    # Validar datas (apenas se não estiverem vazias)
    if new_inicio_real and new_inicio_real.strip():
        if not validate_datetime_string(new_inicio_real):
            st.error(f"Data inválida: {new_inicio_real}. Use o formato {DATE_FORMAT}")
            return False
    
    if new_fim_real and new_fim_real.strip():
        if not validate_datetime_string(new_fim_real):
            st.error(f"Data inválida: {new_fim_real}. Use o formato {DATE_FORMAT}")
            return False
    
    # Validar que fim >= início
    if new_inicio_real and new_fim_real:
        inicio_dt = parse_datetime_string(new_inicio_real)
        fim_dt = parse_datetime_string(new_fim_real)
        
        if inicio_dt and fim_dt and fim_dt < inicio_dt:
            st.error("Horário Fim Real deve ser maior ou igual ao Horário Início Real")
            return False
    
    # Calcular atraso
    atraso_minutos = 0
    if new_fim_real:
        fim_planejado = df_filtered.loc[original_idx, "Fim"]
        if pd.notna(fim_planejado):
            atraso_minutos = calculate_delay(fim_planejado, new_fim_real)
    
    # Atualizar status se necessário
    # IMPORTANTE: Se o usuário escolheu "Concluído", manter "Concluído" mesmo se houver atraso
    # Só alterar automaticamente se o status não foi explicitamente escolhido como "Concluído"
    # ou se houver atraso positivo (atrasado)
    if new_status == "Concluído":
        # Se o usuário escolheu "Concluído", só mudar para "Atrasado" se houver atraso positivo
        # Não mudar para "Adiantado" se o usuário escolheu "Concluído"
        if atraso_minutos > 0:
            new_status = "Atrasado"
        # Se atraso_minutos < 0 (adiantado) ou == 0, manter "Concluído" como o usuário escolheu
    
    # Converter strings vazias para None
    horario_inicio_real_final = new_inicio_real.strip() if new_inicio_real and new_inicio_real.strip() else None
    horario_fim_real_final = new_fim_real.strip() if new_fim_real and new_fim_real.strip() else None
    observacoes_final = new_observacoes.strip() if new_observacoes and new_observacoes.strip() else None
    # Manter valores não editáveis (predecessoras e milestone) do original
    predecessoras_final = old_predecessoras.strip() if old_predecessoras and old_predecessoras.strip() else None
    is_milestone_final = bool(old_is_milestone) if old_is_milestone is not None else False
    
    # Obter excel_data_id da linha para identificar unicamente
    excel_data_id = df_filtered.loc[original_idx, "Excel_Data_ID"] if "Excel_Data_ID" in df_filtered.columns else 0
    if pd.isna(excel_data_id):
        excel_data_id = 0
    else:
        excel_data_id = int(excel_data_id)
    
    # Salvar no banco de dados (FONTE ÚNICA DE VERDADE)
    # Usar excel_data_id para garantir que atualizamos apenas a linha correta
    db_manager.save_activity_control(
        seq=seq,
        sequencia=seq_crq,
        status=new_status,
        horario_inicio_real=horario_inicio_real_final,
        horario_fim_real=horario_fim_real_final,
        atraso_minutos=atraso_minutos,
        observacoes=observacoes_final,
        is_milestone=is_milestone_final,
        predecessoras=predecessoras_final,
        excel_data_id=excel_data_id if excel_data_id > 0 else None
    )
    
    # IMPORTANTE: Após salvar no banco, atualizar st.session_state.data_dict
    # Isso garante que todas as sessões vejam as mesmas mudanças
    # Recarregar do banco (fonte única de verdade) e atualizar session_state
    import streamlit as st
    saved_excel_data = db_manager.load_excel_data()
    if saved_excel_data:
        control_data = db_manager.get_all_activities_control()
        from modules.data_loader import merge_control_data
        # Recarregar do banco e atualizar session_state
        merged_data = merge_control_data(saved_excel_data, control_data)
        st.session_state.data_dict = merged_data
        # Também atualizar o data_dict local para exibição imediata
        data_dict.clear()
        data_dict.update(merged_data)
    
    # Atualizar dataframe em memória (para exibição imediata)
    if crq_selecionado is None:
        # Na aba "Todas", atualizar o dataframe correto
        if seq_crq in data_dict:
            df_crq = data_dict[seq_crq]["dataframe"]
            mask = (df_crq["Seq"] == seq)
            if mask.any():
                idx_crq = df_crq[mask].index[0]
                df_crq.loc[idx_crq, "Status"] = new_status
                df_crq.loc[idx_crq, "Horario_Inicio_Real"] = horario_inicio_real_final
                df_crq.loc[idx_crq, "Horario_Fim_Real"] = horario_fim_real_final
                df_crq.loc[idx_crq, "Atraso_Minutos"] = atraso_minutos
                df_crq.loc[idx_crq, "Observacoes"] = observacoes_final if observacoes_final else ""
                if "Is_Milestone" in df_crq.columns:
                    df_crq.loc[idx_crq, "Is_Milestone"] = is_milestone_final
                if "Predecessoras" in df_crq.columns:
                    df_crq.loc[idx_crq, "Predecessoras"] = predecessoras_final if predecessoras_final else ""
                data_dict[seq_crq]["dataframe"] = df_crq
    else:
        # Atualizar dataframe do CRQ específico
        df = data_dict[crq_selecionado]["dataframe"]
        df.loc[original_idx, "Status"] = new_status
        df.loc[original_idx, "Horario_Inicio_Real"] = horario_inicio_real_final
        df.loc[original_idx, "Horario_Fim_Real"] = horario_fim_real_final
        df.loc[original_idx, "Atraso_Minutos"] = atraso_minutos
        df.loc[original_idx, "Observacoes"] = observacoes_final if observacoes_final else ""
        if "Is_Milestone" in df.columns:
            df.loc[original_idx, "Is_Milestone"] = is_milestone_final
        if "Predecessoras" in df.columns:
            df.loc[original_idx, "Predecessoras"] = predecessoras_final if predecessoras_final else ""
        data_dict[crq_selecionado]["dataframe"] = df
    
    return True
