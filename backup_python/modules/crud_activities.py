"""
Módulo CRUD para gerenciamento completo de atividades
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from config import DATE_FORMAT, SEQUENCIAS, STATUS_OPCOES
from modules.calculations import calculate_delay, parse_datetime_string, validate_datetime_string


def render_crud_activities(data_dict, db_manager):
    """
    Renderiza interface CRUD completa para atividades
    
    Args:
        data_dict: Dicionário com dataframes por CRQ
        db_manager: Instância do DatabaseManager
    """
    st.header("🔧 CRUD de Atividades")
    st.caption("Criar, visualizar, editar e excluir atividades")
    
    # Tabs para diferentes operações
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "➕ Criar", "✏️ Editar", "🗑️ Excluir"])
    
    with tab1:
        render_list_activities(data_dict, db_manager)
    
    with tab2:
        render_create_activity(data_dict, db_manager)
    
    with tab3:
        render_edit_activity(data_dict, db_manager)
    
    with tab4:
        render_delete_activity(data_dict, db_manager)


def render_list_activities(data_dict, db_manager):
    """Lista todas as atividades com filtros"""
    st.subheader("📋 Listar Atividades")
    
    if not data_dict:
        st.warning("⚠️ Nenhum dado carregado.")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        crq_filtro = st.selectbox(
            "Filtrar por CRQ:",
            ["Todos"] + list(SEQUENCIAS.keys()),
            key="list_crq_filter"
        )
    
    with col2:
        status_filtro = st.selectbox(
            "Filtrar por Status:",
            ["Todos"] + STATUS_OPCOES,
            key="list_status_filter"
        )
    
    with col3:
        buscar_texto = st.text_input(
            "Buscar (Atividade, Executor, etc):",
            key="list_search"
        )
    
    # Coletar todas as atividades
    all_activities = []
    for sequencia, data in data_dict.items():
        if crq_filtro != "Todos" and sequencia != crq_filtro:
            continue
        
        df = data["dataframe"]
        for idx, row in df.iterrows():
            atividade_info = {
                "CRQ": sequencia,
                "Seq": row.get("Seq", ""),
                "Atividade": row.get("Atividade", ""),
                "Status": row.get("Status", ""),
                "Executor": row.get("Executor", ""),
                "Grupo": row.get("Grupo", ""),
                "Inicio": row.get("Inicio", ""),
                "Fim": row.get("Fim", ""),
                "Horario_Inicio_Real": row.get("Horario_Inicio_Real", ""),
                "Horario_Fim_Real": row.get("Horario_Fim_Real", ""),
                "Observacoes": row.get("Observacoes", ""),
                "Excel_Data_ID": row.get("Excel_Data_ID", 0)
            }
            
            # Aplicar filtros
            if status_filtro != "Todos" and atividade_info["Status"] != status_filtro:
                continue
            
            if buscar_texto:
                texto_busca = buscar_texto.lower()
                if (texto_busca not in str(atividade_info["Atividade"]).lower() and
                    texto_busca not in str(atividade_info["Executor"]).lower() and
                    texto_busca not in str(atividade_info["Grupo"]).lower()):
                    continue
            
            all_activities.append(atividade_info)
    
    if not all_activities:
        st.info("Nenhuma atividade encontrada com os filtros aplicados.")
        return
    
    # Criar DataFrame para exibição
    df_display = pd.DataFrame(all_activities)
    
    # Selecionar colunas para exibição
    display_cols = ["CRQ", "Seq", "Atividade", "Status", "Executor", "Grupo", 
                   "Inicio", "Fim", "Horario_Inicio_Real", "Horario_Fim_Real", "Observacoes"]
    
    # Garantir que todas as colunas existem
    available_cols = [col for col in display_cols if col in df_display.columns]
    df_display = df_display[available_cols]
    
    st.write(f"**Total de atividades encontradas: {len(df_display)}**")
    st.dataframe(df_display, use_container_width=True, hide_index=True)


def render_create_activity(data_dict, db_manager):
    """Cria nova atividade"""
    st.subheader("➕ Criar Nova Atividade")
    
    with st.form("form_create_activity"):
        col1, col2 = st.columns(2)
        
        with col1:
            crq_selecionado = st.selectbox(
                "CRQ:",
                list(SEQUENCIAS.keys()),
                key="create_crq"
            )
            
            seq = st.number_input(
                "Seq:",
                min_value=1,
                value=1,
                key="create_seq"
            )
            
            atividade = st.text_input(
                "Atividade:",
                key="create_atividade"
            )
            
            grupo = st.text_input(
                "Grupo:",
                key="create_grupo"
            )
            
            executor = st.text_input(
                "Executor:",
                key="create_executor"
            )
        
        with col2:
            status = st.selectbox(
                "Status:",
                STATUS_OPCOES,
                index=0,  # Planejado
                key="create_status"
            )
            
            inicio = st.text_input(
                "Início Planejado (DD/MM/YYYY HH:MM:SS):",
                key="create_inicio"
            )
            
            fim = st.text_input(
                "Fim Planejado (DD/MM/YYYY HH:MM:SS):",
                key="create_fim"
            )
            
            horario_inicio_real = st.text_input(
                "Horário Início Real (DD/MM/YYYY HH:MM:SS):",
                key="create_inicio_real"
            )
            
            horario_fim_real = st.text_input(
                "Horário Fim Real (DD/MM/YYYY HH:MM:SS):",
                key="create_fim_real"
            )
        
        observacoes = st.text_area(
            "Observações:",
            key="create_observacoes"
        )
        
        is_milestone = st.checkbox(
            "É Milestone?",
            key="create_milestone"
        )
        
        submitted = st.form_submit_button("➕ Criar Atividade", type="primary")
        
        if submitted:
            # Validações
            if not atividade.strip():
                st.error("❌ Atividade é obrigatória!")
                return
            
            # Validar datas se fornecidas
            if inicio and not validate_datetime_string(inicio):
                st.error(f"❌ Data de início inválida. Use o formato {DATE_FORMAT}")
                return
            
            if fim and not validate_datetime_string(fim):
                st.error(f"❌ Data de fim inválida. Use o formato {DATE_FORMAT}")
                return
            
            if horario_inicio_real and not validate_datetime_string(horario_inicio_real):
                st.error(f"❌ Horário início real inválido. Use o formato {DATE_FORMAT}")
                return
            
            if horario_fim_real and not validate_datetime_string(horario_fim_real):
                st.error(f"❌ Horário fim real inválido. Use o formato {DATE_FORMAT}")
                return
            
            # Calcular atraso se houver fim real e fim planejado
            atraso_minutos = 0
            if horario_fim_real and fim:
                fim_planejado_dt = parse_datetime_string(fim)
                fim_real_dt = parse_datetime_string(horario_fim_real)
                if fim_planejado_dt and fim_real_dt:
                    atraso_minutos = calculate_delay(fim_planejado_dt, fim_real_dt)
            
            try:
                # Inserir no excel_data
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                
                # Converter datas para string ISO
                inicio_str = None
                fim_str = None
                if inicio:
                    inicio_dt = parse_datetime_string(inicio)
                    if inicio_dt:
                        inicio_str = inicio_dt.isoformat()
                if fim:
                    fim_dt = parse_datetime_string(fim)
                    if fim_dt:
                        fim_str = fim_dt.isoformat()
                
                cursor.execute("""
                    INSERT INTO excel_data
                    (sequencia, seq, atividade, grupo, localidade, executor, 
                     telefone, inicio, fim, tempo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    crq_selecionado,
                    int(seq),
                    atividade.strip(),
                    grupo.strip() if grupo else "",
                    "",  # localidade
                    executor.strip() if executor else "",
                    "",  # telefone
                    inicio_str,
                    fim_str,
                    ""  # tempo
                ))
                
                excel_data_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                # Criar registro de controle
                db_manager.save_activity_control(
                    seq=int(seq),
                    sequencia=crq_selecionado,
                    status=status,
                    horario_inicio_real=horario_inicio_real.strip() if horario_inicio_real else None,
                    horario_fim_real=horario_fim_real.strip() if horario_fim_real else None,
                    atraso_minutos=atraso_minutos,
                    observacoes=observacoes.strip() if observacoes else None,
                    is_milestone=is_milestone,
                    excel_data_id=excel_data_id
                )
                
                st.success(f"✅ Atividade criada com sucesso! (Seq: {seq}, CRQ: {crq_selecionado})")
                
                # Recarregar dados
                saved_excel_data = db_manager.load_excel_data()
                if saved_excel_data:
                    control_data = db_manager.get_all_activities_control()
                    from modules.data_loader import merge_control_data
                    merged_data = merge_control_data(saved_excel_data, control_data)
                    st.session_state.data_dict = merged_data
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao criar atividade: {str(e)}")
                import traceback
                st.code(traceback.format_exc())


def render_edit_activity(data_dict, db_manager):
    """Edita atividade existente"""
    st.subheader("✏️ Editar Atividade")
    
    if not data_dict:
        st.warning("⚠️ Nenhum dado carregado.")
        return
    
    # Seleção de atividade
    col1, col2 = st.columns(2)
    
    with col1:
        crq_selecionado = st.selectbox(
            "Selecione a CRQ:",
            list(SEQUENCIAS.keys()),
            key="edit_crq"
        )
    
    with col2:
        if crq_selecionado in data_dict:
            df = data_dict[crq_selecionado]["dataframe"]
            atividades_opcoes = []
            for idx, row in df.iterrows():
                seq = row.get("Seq", "")
                atividade = row.get("Atividade", "")
                atividades_opcoes.append(f"Seq {seq}: {atividade}")
            
            if not atividades_opcoes:
                st.warning("Nenhuma atividade encontrada nesta CRQ.")
                return
            
            atividade_selecionada = st.selectbox(
                "Selecione a atividade:",
                atividades_opcoes,
                key="edit_atividade_select"
            )
            
            # Extrair seq da seleção
            seq_selecionado = int(atividade_selecionada.split(":")[0].replace("Seq", "").strip())
            
            # Buscar dados da atividade
            atividade_row = None
            excel_data_id = 0
            for idx, row in df.iterrows():
                if int(row.get("Seq", 0)) == seq_selecionado:
                    atividade_row = row
                    excel_data_id = row.get("Excel_Data_ID", 0)
                    break
            
            if atividade_row is None:
                st.error("Atividade não encontrada.")
                return
            
            # Formulário de edição
            with st.form("form_edit_activity"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("Seq:", value=str(seq_selecionado), disabled=True, key="edit_seq_display")
                    atividade = st.text_input(
                        "Atividade:",
                        value=str(atividade_row.get("Atividade", "")),
                        key="edit_atividade"
                    )
                    grupo = st.text_input(
                        "Grupo:",
                        value=str(atividade_row.get("Grupo", "")),
                        key="edit_grupo"
                    )
                    executor = st.text_input(
                        "Executor:",
                        value=str(atividade_row.get("Executor", "")),
                        key="edit_executor"
                    )
                
                with col2:
                    status = st.selectbox(
                        "Status:",
                        STATUS_OPCOES,
                        index=STATUS_OPCOES.index(atividade_row.get("Status", "Planejado")) if atividade_row.get("Status", "Planejado") in STATUS_OPCOES else 0,
                        key="edit_status"
                    )
                    
                    inicio = st.text_input(
                        "Início Planejado:",
                        value=str(atividade_row.get("Inicio", "")) if pd.notna(atividade_row.get("Inicio", "")) else "",
                        key="edit_inicio"
                    )
                    
                    fim = st.text_input(
                        "Fim Planejado:",
                        value=str(atividade_row.get("Fim", "")) if pd.notna(atividade_row.get("Fim", "")) else "",
                        key="edit_fim"
                    )
                
                horario_inicio_real = st.text_input(
                    "Horário Início Real:",
                    value=str(atividade_row.get("Horario_Inicio_Real", "")) if pd.notna(atividade_row.get("Horario_Inicio_Real", "")) else "",
                    key="edit_inicio_real"
                )
                
                horario_fim_real = st.text_input(
                    "Horário Fim Real:",
                    value=str(atividade_row.get("Horario_Fim_Real", "")) if pd.notna(atividade_row.get("Horario_Fim_Real", "")) else "",
                    key="edit_fim_real"
                )
                
                observacoes = st.text_area(
                    "Observações:",
                    value=str(atividade_row.get("Observacoes", "")),
                    key="edit_observacoes"
                )
                
                is_milestone = st.checkbox(
                    "É Milestone?",
                    value=bool(atividade_row.get("Is_Milestone", False)),
                    key="edit_milestone"
                )
                
                submitted = st.form_submit_button("💾 Salvar Alterações", type="primary")
                
                if submitted:
                    # Validações
                    if not atividade.strip():
                        st.error("❌ Atividade é obrigatória!")
                        return
                    
                    # Validar datas
                    if inicio and not validate_datetime_string(inicio):
                        st.error(f"❌ Data de início inválida. Use o formato {DATE_FORMAT}")
                        return
                    
                    if fim and not validate_datetime_string(fim):
                        st.error(f"❌ Data de fim inválida. Use o formato {DATE_FORMAT}")
                        return
                    
                    if horario_inicio_real and not validate_datetime_string(horario_inicio_real):
                        st.error(f"❌ Horário início real inválido. Use o formato {DATE_FORMAT}")
                        return
                    
                    if horario_fim_real and not validate_datetime_string(horario_fim_real):
                        st.error(f"❌ Horário fim real inválido. Use o formato {DATE_FORMAT}")
                        return
                    
                    # Calcular atraso
                    atraso_minutos = 0
                    if horario_fim_real and fim:
                        fim_planejado_dt = parse_datetime_string(fim)
                        fim_real_dt = parse_datetime_string(horario_fim_real)
                        if fim_planejado_dt and fim_real_dt:
                            atraso_minutos = calculate_delay(fim_planejado_dt, fim_real_dt)
                    
                    try:
                        # Atualizar excel_data
                        conn = db_manager.get_connection()
                        cursor = conn.cursor()
                        
                        inicio_str = None
                        fim_str = None
                        if inicio:
                            inicio_dt = parse_datetime_string(inicio)
                            if inicio_dt:
                                inicio_str = inicio_dt.isoformat()
                        if fim:
                            fim_dt = parse_datetime_string(fim)
                            if fim_dt:
                                fim_str = fim_dt.isoformat()
                        
                        cursor.execute("""
                            UPDATE excel_data
                            SET atividade = ?, grupo = ?, executor = ?, inicio = ?, fim = ?
                            WHERE id = ?
                        """, (
                            atividade.strip(),
                            grupo.strip() if grupo else "",
                            executor.strip() if executor else "",
                            inicio_str,
                            fim_str,
                            excel_data_id
                        ))
                        
                        conn.commit()
                        conn.close()
                        
                        # Atualizar controle
                        db_manager.save_activity_control(
                            seq=int(seq_selecionado),
                            sequencia=crq_selecionado,
                            status=status,
                            horario_inicio_real=horario_inicio_real.strip() if horario_inicio_real else None,
                            horario_fim_real=horario_fim_real.strip() if horario_fim_real else None,
                            atraso_minutos=atraso_minutos,
                            observacoes=observacoes.strip() if observacoes else None,
                            is_milestone=is_milestone,
                            excel_data_id=excel_data_id if excel_data_id > 0 else None
                        )
                        
                        st.success("✅ Atividade atualizada com sucesso!")
                        
                        # Recarregar dados
                        saved_excel_data = db_manager.load_excel_data()
                        if saved_excel_data:
                            control_data = db_manager.get_all_activities_control()
                            from modules.data_loader import merge_control_data
                            merged_data = merge_control_data(saved_excel_data, control_data)
                            st.session_state.data_dict = merged_data
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao atualizar atividade: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())


def render_delete_activity(data_dict, db_manager):
    """Exclui atividade"""
    st.subheader("🗑️ Excluir Atividade")
    st.warning("⚠️ **Atenção:** Esta ação é irreversível!")
    
    if not data_dict:
        st.warning("⚠️ Nenhum dado carregado.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        crq_selecionado = st.selectbox(
            "Selecione a CRQ:",
            list(SEQUENCIAS.keys()),
            key="delete_crq"
        )
    
    with col2:
        if crq_selecionado in data_dict:
            df = data_dict[crq_selecionado]["dataframe"]
            atividades_opcoes = []
            for idx, row in df.iterrows():
                seq = row.get("Seq", "")
                atividade = row.get("Atividade", "")
                atividades_opcoes.append(f"Seq {seq}: {atividade}")
            
            if not atividades_opcoes:
                st.warning("Nenhuma atividade encontrada nesta CRQ.")
                return
            
            atividade_selecionada = st.selectbox(
                "Selecione a atividade para excluir:",
                atividades_opcoes,
                key="delete_atividade_select"
            )
            
            # Extrair seq
            seq_selecionado = int(atividade_selecionada.split(":")[0].replace("Seq", "").strip())
            
            # Buscar dados
            atividade_row = None
            excel_data_id = 0
            for idx, row in df.iterrows():
                if int(row.get("Seq", 0)) == seq_selecionado:
                    atividade_row = row
                    excel_data_id = row.get("Excel_Data_ID", 0)
                    break
            
            if atividade_row is not None:
                st.info(f"""
                **Atividade selecionada:**
                - Seq: {seq_selecionado}
                - Atividade: {atividade_row.get('Atividade', '')}
                - Status: {atividade_row.get('Status', '')}
                - CRQ: {crq_selecionado}
                """)
                
                if st.button("🗑️ Excluir Atividade", type="primary", key="btn_delete_activity"):
                    try:
                        conn = db_manager.get_connection()
                        cursor = conn.cursor()
                        
                        # Excluir de activity_control
                        cursor.execute("""
                            DELETE FROM activity_control
                            WHERE seq = ? AND sequencia = ? AND excel_data_id = ?
                        """, (seq_selecionado, crq_selecionado, excel_data_id))
                        control_removidos = cursor.rowcount
                        
                        # Excluir de excel_data
                        cursor.execute("""
                            DELETE FROM excel_data
                            WHERE id = ?
                        """, (excel_data_id,))
                        excel_removidos = cursor.rowcount
                        
                        conn.commit()
                        conn.close()
                        
                        st.success(f"✅ Atividade excluída com sucesso! ({control_removidos} controle, {excel_removidos} excel)")
                        
                        # Recarregar dados
                        saved_excel_data = db_manager.load_excel_data()
                        if saved_excel_data:
                            control_data = db_manager.get_all_activities_control()
                            from modules.data_loader import merge_control_data
                            merged_data = merge_control_data(saved_excel_data, control_data)
                            st.session_state.data_dict = merged_data
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao excluir atividade: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
