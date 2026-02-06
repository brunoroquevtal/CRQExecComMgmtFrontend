"""
Aplicação Principal - Janela de Mudança TI
Aplicação web interativa para gerenciamento de janelas de mudança de TI
"""
import streamlit as st
import pyperclip
import json
import pandas as pd
import requests
import os
from datetime import datetime
from modules.database import DatabaseManager
from modules.data_loader import load_excel_file, merge_control_data, validate_excel_structure
from modules.dashboard import render_full_dashboard
from modules.data_editor import render_data_editor
from modules.message_builder import build_whatsapp_message
from modules.calculations import calculate_statistics
from modules.crud_activities import render_crud_activities
from modules.auth import (
    init_session_auth, is_authenticated, has_permission,
    can_edit_data, get_user_name, get_user_type, render_login_page, logout
)
from config import DATE_FORMAT, SEQUENCIAS

# URL da API (pode ser configurada via variável de ambiente)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


# Configuração da página
st.set_page_config(
    page_title="Janela de Mudança TI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar autenticação
init_session_auth()

# Inicializar banco de dados
if "db_manager" not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

# Inicializar session_state
if "data_dict" not in st.session_state:
    st.session_state.data_dict = {}
    st.session_state.current_file = None
    # Tentar carregar dados persistidos do banco apenas se não houver dados em memória
    try:
        saved_excel_data = st.session_state.db_manager.load_excel_data()
        if saved_excel_data:
            # Mesclar com dados de controle
            control_data = st.session_state.db_manager.get_all_activities_control()
            from modules.data_loader import merge_control_data
            st.session_state.data_dict = merge_control_data(saved_excel_data, control_data)
            st.session_state.current_file = "Dados persistidos do banco"
        else:
            # Se não houver dados no banco, inicializar vazio
            st.session_state.data_dict = {}
            st.session_state.current_file = None
    except Exception as e:
        # Se houver erro ao carregar, mostrar erro mas continuar
        import traceback
        print(f"Erro ao carregar dados do banco na inicialização: {str(e)}")
        print(traceback.format_exc())
        st.session_state.data_dict = {}
        st.session_state.current_file = None

# Sempre tentar recarregar dados do banco se data_dict estiver vazio mas deveria ter dados
# (isso garante que mesmo se a sessão for reiniciada, os dados sejam carregados)
if not st.session_state.data_dict and st.session_state.current_file is None:
    try:
        saved_excel_data = st.session_state.db_manager.load_excel_data()
        if saved_excel_data:
            control_data = st.session_state.db_manager.get_all_activities_control()
            from modules.data_loader import merge_control_data
            st.session_state.data_dict = merge_control_data(saved_excel_data, control_data)
            st.session_state.current_file = "Dados persistidos do banco"
    except Exception as e:
        # Silenciar erro aqui para não mostrar na interface
        pass

if "has_unsaved_changes" not in st.session_state:
    st.session_state.has_unsaved_changes = False

if "current_file" not in st.session_state:
    st.session_state.current_file = None

# Verificar autenticação
if not is_authenticated():
    render_login_page()
    st.stop()


def load_data_from_excel(uploaded_file, show_success_message=True, use_api=True):
    """
    Carrega dados do Excel via API ou processamento local
    
    Args:
        uploaded_file: Arquivo Excel carregado via Streamlit
        show_success_message: Se deve mostrar mensagem de sucesso
        use_api: Se True, usa o endpoint da API; se False, processa localmente
    """
    try:
        if use_api:
            # Usar endpoint da API
            return load_data_from_excel_via_api(uploaded_file, show_success_message)
        else:
            # Processamento local (método antigo)
            return load_data_from_excel_local(uploaded_file, show_success_message)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False


def load_data_from_excel_via_api(uploaded_file, show_success_message=True):
    """Carrega dados do Excel via endpoint da API"""
    try:
        with st.spinner("Enviando arquivo Excel para a API..."):
            url = f"{API_BASE_URL}/upload-excel"
            
            # Preparar arquivo para upload
            files = {
                'file': (uploaded_file.name, uploaded_file.getvalue(), 
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            # Fazer upload via API
            response = requests.post(url, files=files, timeout=300)
            
            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get('detail', error_msg)
                except:
                    pass
                st.error(f"❌ Erro na API: {error_msg}")
                return False
            
            result = response.json()
            
            if not result.get('success', False):
                st.error(f"❌ Erro ao processar arquivo: {result.get('message', 'Erro desconhecido')}")
                return False
            
            # Mostrar estatísticas
            total_saved = result.get('total_saved', 0)
            control_created = result.get('control_created', 0)
            sequencias = result.get('sequencias', [])
            
            if total_saved == 0:
                st.warning("⚠️ Nenhum registro foi salvo no banco. Verifique os dados do Excel.")
                return False
            
            # Recarregar dados do banco para atualizar a interface
            saved_excel_data = st.session_state.db_manager.load_excel_data()
            
            if not saved_excel_data:
                st.error("❌ Erro: Dados foram salvos mas não puderam ser recarregados do banco.")
                return False
            
            # Carregar dados de controle do banco
            control_data = st.session_state.db_manager.get_all_activities_control()
            
            # Mesclar dados do banco
            merged_data = merge_control_data(saved_excel_data, control_data)
            
            # Salvar no session_state
            st.session_state.data_dict = merged_data
            st.session_state.current_file = uploaded_file.name
            
            # Limpar cache do Excel
            load_excel_file.clear()
            
            if show_success_message:
                st.success(f"✅ Dados carregados via API com sucesso! ({total_saved} registros salvos, {control_created} controles criados, {len(sequencias)} CRQs: {', '.join(sequencias)})")
            st.rerun()
            return True
    
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Não foi possível conectar à API em {API_BASE_URL}")
        st.info("💡 Tente usar o processamento local ou verifique se a API está rodando.")
        # Fallback para processamento local
        return load_data_from_excel_local(uploaded_file, show_success_message)
    except requests.exceptions.Timeout:
        st.error("❌ Timeout ao enviar arquivo para a API. O arquivo pode ser muito grande.")
        return False
    except Exception as e:
        st.error(f"Erro ao enviar arquivo para API: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        # Fallback para processamento local
        return load_data_from_excel_local(uploaded_file, show_success_message)


def load_data_from_excel_local(uploaded_file, show_success_message=True):
    """Carrega dados do Excel processando localmente (método antigo)"""
    try:
        with st.spinner("Carregando dados do Excel (processamento local)..."):
            # Limpar cache antes de carregar novo arquivo
            load_excel_file.clear()
            
            # Carregar dados do Excel (temporário, apenas para salvar no banco)
            excel_data = load_excel_file(uploaded_file)
            
            if not excel_data:
                st.error("Erro ao carregar arquivo Excel")
                return False
            
            # Contar total de registros antes de salvar
            total_rows = sum(len(data["dataframe"]) for data in excel_data.values())
            
            # Salvar dados do Excel no banco (FONTE ÚNICA DE VERDADE)
            total_saved = st.session_state.db_manager.save_excel_data(excel_data, uploaded_file.name)
            
            if total_saved == 0:
                st.warning("⚠️ Nenhum registro foi salvo no banco. Verifique os dados do Excel.")
                return False
            
            # Verificar se todos os registros foram salvos
            if total_saved != total_rows:
                st.warning(f"⚠️ Aviso: {total_rows} registros foram carregados, mas apenas {total_saved} foram salvos no banco. Alguns registros podem ter sido filtrados (Seq inválido, etc.)")
            
            # IMPORTANTE: Agora sempre recarregar do banco (não usar dados do Excel em memória)
            # Isso garante que todas as sessões vejam os mesmos dados
            saved_excel_data = st.session_state.db_manager.load_excel_data()
            
            if not saved_excel_data:
                st.error("❌ Erro: Dados foram salvos mas não puderam ser recarregados do banco.")
                return False
            
            # Carregar dados de controle do banco
            control_data = st.session_state.db_manager.get_all_activities_control()
            
            # Mesclar dados do banco (não do Excel em memória)
            merged_data = merge_control_data(saved_excel_data, control_data)
            
            # Salvar no session_state
            st.session_state.data_dict = merged_data
            st.session_state.current_file = uploaded_file.name
            
            # Inicializar dados de controle no banco se necessário
            for sequencia, data in merged_data.items():
                df = data["dataframe"]
                for _, row in df.iterrows():
                    seq = int(row["Seq"])
                    excel_data_id = row.get("Excel_Data_ID", 0) if "Excel_Data_ID" in row else 0
                    if pd.isna(excel_data_id):
                        excel_data_id = 0
                    else:
                        excel_data_id = int(excel_data_id)
                    
                    # Buscar usando excel_data_id se disponível
                    if excel_data_id and excel_data_id > 0:
                        existing = st.session_state.db_manager.get_activity_control(seq, sequencia, excel_data_id)
                    else:
                        existing = st.session_state.db_manager.get_activity_control(seq, sequencia)
                    
                    if not existing:
                        # Obter valor de Is_Milestone do dataframe (já detectado na importação)
                        is_milestone = row.get("Is_Milestone", False) if "Is_Milestone" in row else False
                        st.session_state.db_manager.save_activity_control(
                            seq=seq,
                            sequencia=sequencia,
                            status="Planejado",
                            is_milestone=is_milestone,
                            excel_data_id=excel_data_id if excel_data_id > 0 else None
                        )
            
            # Limpar cache do Excel após salvar no banco (não precisamos mais dele)
            load_excel_file.clear()
            
            if show_success_message:
                st.success(f"✅ Dados carregados e persistidos com sucesso! ({total_saved} registros, {len(merged_data)} CRQs)")
            st.rerun()
            return True
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False


def export_state():
    """Exporta estado atual para JSON"""
    if not st.session_state.data_dict:
        st.warning("Nenhum dado para exportar")
        return None
    
    export_data = {}
    
    for sequencia, data in st.session_state.data_dict.items():
        df = data["dataframe"]
        export_data[sequencia] = df.to_dict("records")
    
    return json.dumps(export_data, indent=2, default=str)


# Sidebar
with st.sidebar:
    st.title("🚀 Janela de Mudança TI")
    
    # Informações do usuário
    tipo_usuario = get_user_type()
    tipo_display = {
        "admin": "Administrador",
        "lider": "Líder da Mudança",
        "visualizador": "Visualizador"
    }.get(tipo_usuario, tipo_usuario.title() if tipo_usuario else "Desconhecido")
    st.info(f"👤 {get_user_name()}\n🔑 {tipo_display}")
    
    if st.button("🚪 Sair", width='stretch'):
        logout()
        st.rerun()
    
    st.divider()
    
    # Menu de navegação baseado em permissões
    st.subheader("📊 Navegação")
    
    pages_available = []
    if has_permission("dashboard"):
        pages_available.append("Dashboard")
    if has_permission("dados"):
        pages_available.append("Dados")
    if has_permission("mensagem"):
        pages_available.append("Comunicação")
    # CRUD Atividades - apenas para administradores
    if get_user_type() == "admin":
        pages_available.append("CRUD Atividades")
    if has_permission("configuracoes"):
        pages_available.append("Configurações")
    # API Upload - apenas para administradores
    if get_user_type() == "admin":
        pages_available.append("API Upload")
    
    if pages_available:
        page = st.radio(
            "Selecione a página:",
            pages_available,
            key="page_selector"
        )
    else:
        st.warning("Sem permissões de acesso")
        page = None
        st.stop()
    
    st.divider()
    
    # Gerenciamento de arquivo (apenas para administradores)
    if get_user_type() == "admin":
        st.subheader("📁 Gerenciamento de Arquivo")
        
        uploaded_file = st.file_uploader(
            "Carregar arquivo Excel",
            type=["xlsx", "xls"],
            key="file_uploader"
        )
        
        # Verificar se é um novo arquivo (não o mesmo que já está carregado)
        file_uploaded_key = "last_uploaded_file_name"
        if file_uploaded_key not in st.session_state:
            st.session_state[file_uploaded_key] = None
        
        if uploaded_file is not None:
            # Verificar se é um arquivo novo
            is_new_file = st.session_state[file_uploaded_key] != uploaded_file.name
            
            # Opção para escolher entre API ou processamento local
            use_api = st.checkbox("🌐 Usar API para processamento", value=True, 
                                 help="Se marcado, o arquivo será enviado para a API. Se desmarcado, será processado localmente.")
            
            if st.button("📥 Carregar Dados", width='stretch'):
                if validate_excel_structure(uploaded_file):
                    load_data_from_excel(uploaded_file, use_api=use_api)
                    st.session_state[file_uploaded_key] = uploaded_file.name
                else:
                    st.error("Arquivo Excel inválido. Verifique a estrutura do arquivo.")
        
        if st.session_state.current_file:
            st.info(f"📄 Arquivo atual: {st.session_state.current_file}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Atualizar", width='stretch'):
                    # Limpar cache e recarregar
                    load_excel_file.clear()
                    # Só recarregar se houver um arquivo selecionado E for diferente do atual
                    if uploaded_file is not None and uploaded_file.name != st.session_state.current_file:
                        load_data_from_excel(uploaded_file, use_api=True)
                        st.session_state[file_uploaded_key] = uploaded_file.name
                    else:
                        # Se não houver arquivo novo, apenas recarregar do banco (sem salvar Excel novamente)
                        saved_excel_data = st.session_state.db_manager.load_excel_data()
                        if saved_excel_data:
                            control_data = st.session_state.db_manager.get_all_activities_control()
                            from modules.data_loader import merge_control_data
                            st.session_state.data_dict = merge_control_data(saved_excel_data, control_data)
                            st.success("✅ Dados atualizados do banco!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Nenhum dado encontrado no banco.")
            
            with col2:
                if st.button("🔄 Recarregar do Banco", width='stretch', help="Recarrega os dados do banco de dados"):
                    try:
                        saved_excel_data = st.session_state.db_manager.load_excel_data()
                        if saved_excel_data:
                            control_data = st.session_state.db_manager.get_all_activities_control()
                            from modules.data_loader import merge_control_data
                            st.session_state.data_dict = merge_control_data(saved_excel_data, control_data)
                            st.session_state.current_file = "Dados persistidos do banco"
                            st.success("✅ Dados recarregados do banco com sucesso!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Nenhum dado encontrado no banco.")
                    except Exception as e:
                        st.error(f"❌ Erro ao recarregar dados: {str(e)}")
            
            with col3:
                if st.button("🗑️ Limpar Cache", width='stretch'):
                    load_excel_file.clear()
                    st.session_state.data_dict = {}
                    st.session_state.current_file = None
                    st.success("✅ Cache limpo!")
                    st.rerun()
        
        # Opção para limpar todos os dados e reimportar
        st.divider()
        st.subheader("⚠️ Gerenciamento de Dados")
        
        # Remover seqs específicos
        with st.expander("🗑️ Remover Sequências Específicas"):
            st.caption("Remova registros específicos por seq e CRQ")
            
            # Selecionar CRQ
            crq_opcoes = list(SEQUENCIAS.keys())
            crq_selecionado = st.selectbox(
                "Selecione a CRQ:",
                crq_opcoes,
                key="remover_crq"
            )
            
            # Input para seqs (separados por vírgula ou quebra de linha)
            seqs_input = st.text_area(
                "Digite os seqs para remover (um por linha ou separados por vírgula):",
                height=100,
                key="remover_seqs_input",
                help="Exemplo: 999093\n999094\n999095"
            )
            
            if st.button("🗑️ Remover Sequências", type="primary", key="btn_remover_seqs"):
                if seqs_input.strip():
                    # Processar input: separar por vírgula ou quebra de linha
                    seqs_raw = seqs_input.replace(",", "\n").split("\n")
                    seqs_para_remover = []
                    
                    for seq_str in seqs_raw:
                        seq_str = seq_str.strip()
                        if seq_str:
                            try:
                                seqs_para_remover.append(int(seq_str))
                            except ValueError:
                                st.error(f"❌ Seq inválido: {seq_str}")
                                st.stop()
                    
                    if seqs_para_remover:
                        # Executar remoção
                        try:
                            conn = st.session_state.db_manager.get_connection()
                            cursor = conn.cursor()
                            
                            # Contar registros antes
                            placeholders = ','.join(['?'] * len(seqs_para_remover))
                            params = seqs_para_remover + [crq_selecionado]
                            
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM activity_control 
                                WHERE seq IN ({placeholders}) AND sequencia = ?
                            """, params)
                            activity_antes = cursor.fetchone()[0]
                            
                            cursor.execute(f"""
                                SELECT COUNT(*) FROM excel_data 
                                WHERE seq IN ({placeholders}) AND sequencia = ?
                            """, params)
                            excel_antes = cursor.fetchone()[0]
                            
                            if activity_antes == 0 and excel_antes == 0:
                                st.warning("⚠️ Nenhum registro encontrado para remover com os seqs informados.")
                            else:
                                # Remover
                                cursor.execute(f"""
                                    DELETE FROM activity_control 
                                    WHERE seq IN ({placeholders}) AND sequencia = ?
                                """, params)
                                activity_removidos = cursor.rowcount
                                
                                cursor.execute(f"""
                                    DELETE FROM excel_data 
                                    WHERE seq IN ({placeholders}) AND sequencia = ?
                                """, params)
                                excel_removidos = cursor.rowcount
                                
                                conn.commit()
                                conn.close()
                                
                                st.success(f"✅ Remoção concluída!")
                                st.info(f"""
                                **Registros removidos:**
                                - activity_control: {activity_removidos}
                                - excel_data: {excel_removidos}
                                - **Total:** {activity_removidos + excel_removidos}
                                """)
                                
                                # Recarregar dados do banco
                                saved_excel_data = st.session_state.db_manager.load_excel_data()
                                if saved_excel_data:
                                    control_data = st.session_state.db_manager.get_all_activities_control()
                                    merged_data = merge_control_data(saved_excel_data, control_data)
                                    st.session_state.data_dict = merged_data
                                
                                st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Erro ao remover registros: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                    else:
                        st.warning("⚠️ Nenhum seq válido encontrado")
                else:
                    st.warning("⚠️ Digite pelo menos um seq para remover")
        
        st.warning("**Atenção:** A ação abaixo irá apagar TODOS os dados do banco (atividades e controles) e permitir uma nova importação.")
        
        if st.button("🗑️ Limpar Todos os Dados e Reimportar", width='stretch', type="secondary"):
            with st.spinner("Limpando todos os dados..."):
                # Limpar todos os dados do banco
                excel_count, control_count, success = st.session_state.db_manager.clear_all_data()
                # Limpar cache do Streamlit
                load_excel_file.clear()
                # Limpar session_state completamente
                st.session_state.data_dict = {}
                st.session_state.current_file = None
                st.session_state.has_unsaved_changes = False
                # Limpar todas as chaves relacionadas a processamento
                keys_to_remove = [key for key in list(st.session_state.keys()) if key.startswith("processing_") or key.startswith("last_hash_")]
                for key in keys_to_remove:
                    if key in st.session_state:
                        del st.session_state[key]
            
            if success:
                st.success(f"✅ Todos os dados foram apagados do banco! ({excel_count} registros Excel, {control_count} controles deletados). Agora você pode importar um novo arquivo Excel.")
            else:
                st.error("⚠️ Erro ao limpar alguns dados. Tente novamente.")
            st.rerun()
        
        # Exportar/Importar dados completos (para transferência entre máquinas)
        st.divider()
        st.subheader("🔄 Transferência de Dados entre Máquinas")
        st.info("💡 Use esta funcionalidade para transferir todos os dados (Excel + controles) entre máquinas de diferentes colaboradores.")
        
        col_export, col_import = st.columns(2)
        
        with col_export:
            st.markdown("#### 📤 Exportar Dados")
            if st.button("💾 Exportar Todos os Dados", width='stretch', type="primary"):
                try:
                    export_data = st.session_state.db_manager.export_all_data()
                    if export_data:
                        export_json = json.dumps(export_data, indent=2, default=str, ensure_ascii=False)
                        excel_count = export_data["metadata"]["excel_count"]
                        control_count = export_data["metadata"]["control_count"]
                        
                        st.success(f"✅ Dados exportados com sucesso! ({excel_count} registros Excel, {control_count} controles)")
                        
                        # Criar nome do arquivo com data/hora
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"backup_janela_mudanca_{timestamp}.json"
                        
                        st.download_button(
                            label="📥 Baixar Arquivo de Backup",
                            data=export_json,
                            file_name=filename,
                            mime="application/json",
                            key="download_backup"
                        )
                    else:
                        st.warning("⚠️ Nenhum dado encontrado para exportar.")
                except Exception as e:
                    st.error(f"❌ Erro ao exportar dados: {str(e)}")
                    import traceback
                    with st.expander("Detalhes do erro"):
                        st.code(traceback.format_exc())
        
        with col_import:
            st.markdown("#### 📥 Importar Dados")
            uploaded_backup = st.file_uploader(
                "Selecione o arquivo de backup (.json)",
                type=["json"],
                key="backup_uploader"
            )
            
            if uploaded_backup is not None:
                if st.button("📥 Importar Dados do Backup", width='stretch', type="primary"):
                    try:
                        # Ler arquivo JSON
                        import_data = json.load(uploaded_backup)
                        
                        # Validar estrutura
                        if "excel_data" not in import_data or "control_data" not in import_data:
                            st.error("❌ Arquivo de backup inválido. Estrutura não reconhecida.")
                        else:
                            with st.spinner("Importando dados..."):
                                # Limpar cache
                                load_excel_file.clear()
                                
                                # Importar dados
                                excel_imported, control_imported, success = st.session_state.db_manager.import_all_data(import_data)
                                
                                if success:
                                    # Recarregar dados do banco para o session_state
                                    saved_excel_data = st.session_state.db_manager.load_excel_data()
                                    if saved_excel_data:
                                        control_data = st.session_state.db_manager.get_all_activities_control()
                                        from modules.data_loader import merge_control_data
                                        st.session_state.data_dict = merge_control_data(saved_excel_data, control_data)
                                        st.session_state.current_file = "Dados importados do backup"
                                    
                                    st.success(f"✅ Dados importados com sucesso! ({excel_imported} registros Excel, {control_imported} controles)")
                                    st.info("🔄 A página será recarregada para exibir os dados importados.")
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao importar alguns dados. Verifique o arquivo de backup.")
                    except json.JSONDecodeError:
                        st.error("❌ Erro: Arquivo JSON inválido.")
                    except Exception as e:
                        st.error(f"❌ Erro ao importar dados: {str(e)}")
                        import traceback
                        with st.expander("Detalhes do erro"):
                            st.code(traceback.format_exc())
        
        # Exportar estado (mantido para compatibilidade)
        if st.session_state.data_dict:
            st.divider()
            st.subheader("💾 Exportar Estado (Legado)")
            st.caption("⚠️ Esta opção exporta apenas o estado em memória. Para transferência completa entre máquinas, use a opção acima.")
            
            export_json = export_state()
            if export_json:
                st.download_button(
                    label="📤 Exportar Estado (JSON)",
                    data=export_json,
                    file_name=f"estado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    width='stretch'
                )
    else:
        # Para outros usuários, apenas mostrar arquivo atual se existir
        if st.session_state.current_file:
            st.info(f"📄 Arquivo atual: {st.session_state.current_file}")
            st.caption("💡 Apenas administradores podem carregar novos arquivos")
    
    # Indicador de mudanças não salvas
    if st.session_state.has_unsaved_changes:
        st.warning("⚠️ Há alterações não salvas")
    
    st.divider()
    st.markdown("**Versão:** 1.1.0")
    st.markdown("**Desenvolvido com Streamlit**")
    
    # Informações de acesso
    if can_edit_data():
        st.success("✅ Permissão de edição ativa")
    else:
        st.info("👁️ Modo visualização apenas")


# IMPORTANTE: O banco de dados é a FONTE ÚNICA DE VERDADE
# Sempre carregar do banco, não confiar no session_state ou cache
# Isso garante que todas as sessões vejam os mesmos dados
try:
    saved_excel_data = st.session_state.db_manager.load_excel_data()
    if saved_excel_data:
        # Sempre recarregar do banco (ignorar cache e session_state)
        control_data = st.session_state.db_manager.get_all_activities_control()
        from modules.data_loader import merge_control_data
        merged_data = merge_control_data(saved_excel_data, control_data)
        
        # Verificar se os dados mudaram (comparar contagem de registros)
        current_count = sum(len(data["dataframe"]) for data in st.session_state.data_dict.values()) if st.session_state.data_dict else 0
        new_count = sum(len(data["dataframe"]) for data in merged_data.values())
        
        # Sempre atualizar se os dados mudaram OU se não há dados em memória
        # Isso garante sincronização entre sessões
        if current_count != new_count or not st.session_state.data_dict:
            st.session_state.data_dict = merged_data
            if not st.session_state.current_file or st.session_state.current_file == "Dados persistidos do banco":
                st.session_state.current_file = "Dados persistidos do banco"
    elif not saved_excel_data:
        # Se não há dados no banco, limpar session_state
        # (pode ter sido limpo em outra sessão)
        if st.session_state.data_dict:
            st.session_state.data_dict = {}
            st.session_state.current_file = None
except Exception as e:
    # Logar erro mas não mostrar na interface a cada renderização
    import traceback
    print(f"Erro ao verificar banco: {str(e)}")
    print(traceback.format_exc())

# Conteúdo principal
if page == "Dashboard":
    st.header("📊 Dashboard Executivo")
    
    if st.session_state.data_dict:
        render_full_dashboard(st.session_state.data_dict)
    else:
        st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um arquivo Excel primeiro na sidebar.")

elif page == "Dados":
    st.header("✏️ Editor de Dados")
    
    if not can_edit_data():
        st.error("❌ Você não tem permissão para editar dados. Apenas usuários Administrador e Líder da Mudança podem editar.")
        st.info("💡 Use a página Dashboard para visualizar os dados.")
    elif st.session_state.data_dict:
        render_data_editor(st.session_state.data_dict, st.session_state.db_manager)
    else:
        st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um arquivo Excel primeiro na sidebar.")

elif page == "Comunicação":
    st.header("💬 Comunicação")
    
    if st.session_state.data_dict:
        message = build_whatsapp_message(st.session_state.data_dict)
        
        # Exibir mensagem
        st.text_area(
            "Mensagem para WhatsApp:",
            value=message,
            height=400,
            key="whatsapp_message"
        )
        
        # Botão para copiar
        if st.button("📋 Copiar Mensagem", width='stretch'):
            pyperclip.copy(message)
            st.success("✅ Mensagem copiada para a área de transferência!")
    else:
        st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um arquivo Excel primeiro na sidebar.")

elif page == "CRUD Atividades":
    # Verificar se é administrador - dupla verificação de segurança
    if get_user_type() != "admin":
        st.error("❌ Você não tem permissão para acessar esta página. Apenas administradores podem acessar o CRUD de Atividades.")
        st.info("💡 Faça login como administrador para acessar esta funcionalidade.")
        st.stop()
    
    # Verificar se há dados carregados
    if not st.session_state.data_dict:
        st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um arquivo Excel primeiro na sidebar.")
    else:
        render_crud_activities(st.session_state.data_dict, st.session_state.db_manager)
    st.header("💬 Comunicação")
    
    if st.session_state.data_dict:
        # Gerar mensagem
        message = build_whatsapp_message(st.session_state.data_dict)
        
        # Botão para copiar
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("📋 Copiar para Clipboard", width='stretch'):
                try:
                    pyperclip.copy(message)
                    st.success("✅ Mensagem copiada para clipboard!")
                except Exception as e:
                    # Fallback: mostrar código para copiar manualmente
                    st.warning("⚠️ Não foi possível copiar automaticamente. Use o código abaixo:")
                    st.code(message, language=None)
                    st.info("💡 Selecione o texto acima e pressione Ctrl+C para copiar")
        
        st.divider()
        
        # Preview da mensagem
        st.subheader("📄 Preview da Mensagem de Comunicação")
        st.markdown("---")
        # Mostrar mensagem formatada (markdown preserva quebras de linha com dois espaços)
        st.markdown(message.replace("\n", "  \n"))  # Dois espaços antes do \n força quebra no markdown
        st.markdown("---")
        
        # Estatísticas rápidas
        st.subheader("📈 Estatísticas Rápidas")
        stats = calculate_statistics(st.session_state.data_dict)
        geral = stats["geral"]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", geral["total"])
        with col2:
            st.metric("Concluídas", geral["concluidas"], f"{geral.get('pct_concluidas', 0):.1f}%")
        with col3:
            st.metric("Em Execução", geral["em_execucao"], f"{geral.get('pct_em_execucao', 0):.1f}%")
        with col4:
            st.metric("Atrasadas", geral["atrasadas"], f"{geral.get('pct_atrasadas', 0):.1f}%")
        
        st.info("💡 A mensagem é atualizada automaticamente conforme os dados são editados.")
    
    else:
        st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um arquivo Excel primeiro na sidebar.")

elif page == "API Upload":
    st.header("🌐 Upload via API")
    
    st.markdown("""
    ### 📤 Endpoint para Upload de Arquivo Excel
    
    Use este endpoint para fazer upload de arquivo Excel via script Python, curl ou qualquer cliente HTTP.
    """)
    
    # Mostrar URL da API
    st.subheader("🔗 URL do Endpoint")
    api_url = f"{API_BASE_URL}/upload-excel"
    st.code(api_url, language="text")
    
    # Verificar se API está disponível
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API está disponível e respondendo")
        else:
            st.warning("⚠️ API respondeu mas com status diferente de 200")
    except:
        st.error(f"❌ API não está disponível em {API_BASE_URL}")
        st.info("💡 Certifique-se de que a API está rodando. Execute: `python api_server.py` ou `python start_all.py`")
    
    st.divider()
    
    # Exemplo com Python
    st.subheader("🐍 Exemplo com Python")
    st.markdown("""
    Use a biblioteca `requests` para fazer upload do arquivo:
    """)
    
    python_example = f'''import requests

# URL do endpoint
url = "{api_url}"

# Fazer upload do arquivo
with open("arquivo.xlsx", "rb") as f:
    files = {{"file": ("arquivo.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}}
    response = requests.post(url, files=files, timeout=300)

if response.status_code == 200:
    result = response.json()
    print("✅ Upload realizado com sucesso!")
    print(f"  Registros salvos: {{result['total_saved']}}")
    print(f"  Controles criados: {{result['control_created']}}")
    print(f"  Sequências: {{', '.join(result['sequencias'])}}")
else:
    print(f"❌ Erro: {{response.status_code}}")
    print(f"  {{response.text}}")'''
    
    st.code(python_example, language="python")
    
    # Botão para copiar código Python
    if st.button("📋 Copiar código Python", key="copy_python"):
        pyperclip.copy(python_example)
        st.success("✅ Código copiado para a área de transferência!")
    
    st.divider()
    
    # Exemplo com curl
    st.subheader("💻 Exemplo com curl")
    st.markdown("""
    Use `curl` na linha de comando:
    """)
    
    curl_example = f'''curl -X POST "{api_url}" \\
  -F "file=@caminho/para/arquivo.xlsx" \\
  -H "accept: application/json"'''
    
    st.code(curl_example, language="bash")
    
    # Botão para copiar código curl
    if st.button("📋 Copiar comando curl", key="copy_curl"):
        pyperclip.copy(curl_example)
        st.success("✅ Comando copiado para a área de transferência!")
    
    st.divider()
    
    # Exemplo com PowerShell
    st.subheader("🔷 Exemplo com PowerShell")
    st.markdown("""
    Use `Invoke-RestMethod` no PowerShell:
    """)
    
    powershell_example = f'''$uri = "{api_url}"
$filePath = "caminho\\para\\arquivo.xlsx"

$form = @{{
    file = Get-Item -Path $filePath
}}

$response = Invoke-RestMethod -Uri $uri -Method Post -Form $form

Write-Host "✅ Upload realizado com sucesso!"
Write-Host "  Registros salvos: $($response.total_saved)"
Write-Host "  Controles criados: $($response.control_created)"
Write-Host "  Sequências: $($response.sequencias -join ', ')"'''
    
    st.code(powershell_example, language="powershell")
    
    # Botão para copiar código PowerShell
    if st.button("📋 Copiar código PowerShell", key="copy_powershell"):
        pyperclip.copy(powershell_example)
        st.success("✅ Código copiado para a área de transferência!")
    
    st.divider()
    
    # Resposta esperada
    st.subheader("📥 Resposta Esperada")
    st.markdown("""
    O endpoint retorna um JSON com as seguintes informações:
    """)
    
    response_example = {
        "success": True,
        "message": "Arquivo processado com sucesso",
        "filename": "arquivo.xlsx",
        "total_rows": 153,
        "total_saved": 153,
        "control_created": 50,
        "sequencias": ["REDE", "OPENSHIFT", "NFS", "SI"],
        "sequencias_count": 4
    }
    
    st.json(response_example)
    
    st.divider()
    
    # Teste rápido
    st.subheader("🧪 Teste Rápido")
    st.markdown("""
    Faça upload de um arquivo Excel diretamente aqui para testar o endpoint:
    """)
    
    test_file = st.file_uploader(
        "Selecione um arquivo Excel para testar",
        type=["xlsx", "xls"],
        key="api_test_uploader"
    )
    
    if test_file is not None:
        if st.button("🚀 Testar Upload via API", type="primary"):
            try:
                with st.spinner("Enviando arquivo para a API..."):
                    files = {
                        'file': (test_file.name, test_file.getvalue(), 
                                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    }
                    response = requests.post(api_url, files=files, timeout=300)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Upload realizado com sucesso!")
                        st.json(result)
                        
                        # Recarregar dados do banco
                        saved_excel_data = st.session_state.db_manager.load_excel_data()
                        if saved_excel_data:
                            control_data = st.session_state.db_manager.get_all_activities_control()
                            st.session_state.data_dict = merge_control_data(saved_excel_data, control_data)
                            st.session_state.current_file = test_file.name
                            st.info("💡 Dados recarregados do banco. A página será atualizada.")
                            st.rerun()
                    else:
                        st.error(f"❌ Erro: HTTP {response.status_code}")
                        try:
                            error_json = response.json()
                            st.json(error_json)
                        except:
                            st.text(response.text)
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Não foi possível conectar à API em {API_BASE_URL}")
                st.info("💡 Certifique-se de que a API está rodando.")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

elif page == "Configurações":
    st.header("⚙️ Configurações")
    
    st.subheader("📋 Informações da Aplicação")
    st.markdown("""
    **Janela de Mudança TI** é uma aplicação web interativa para gerenciamento de janelas de mudança de TI.
    
    ### Funcionalidades:
    - ✅ Importação de dados de arquivo Excel
    - ✅ Edição interativa de dados em tempo real
    - ✅ Dashboard executivo com gráficos e indicadores
    - ✅ Geração automática de mensagem consolidada para WhatsApp
    - ✅ Persistência de dados em banco SQLite local
    
    ### Formato de Data/Hora:
    - Formato esperado: `DD/MM/AAAA HH:MM:SS`
    - Exemplo: `25/12/2024 14:30:00`
    
    ### Status Disponíveis:
    - **Planejado**: Atividade ainda não iniciada
    - **Em Execução**: Atividade em andamento
    - **Concluído**: Atividade finalizada
    - **Atrasado**: Atividade concluída com atraso
    - **Adiantado**: Atividade concluída antes do prazo
    
    ### Estrutura do Arquivo Excel:
    O arquivo Excel deve conter 4 abas com os seguintes nomes (ou contendo):
    - **REDE** (72 atividades)
    - **OPENSHIFT** (39 atividades)
    - **NFS** (17 atividades)
    - **SI** (25 atividades)
    
    Cada aba deve ter as seguintes colunas:
    - Seq, Atividade, Grupo, Localidade, Executor, Telefone, Inicio, Fim, Tempo
    (Nota: As colunas Localidade, Executor e Telefone são importadas mas não são exibidas por questões de segurança)
    """)
    
    st.divider()
    
    st.subheader("🔧 Informações Técnicas")
    st.markdown(f"""
    - **Banco de Dados**: SQLite local (`db/activity_control.db`)
    - **Formato de Data**: `{DATE_FORMAT}`
    - **Total de Atividades**: 153
    """)
    
    if st.session_state.data_dict:
        st.divider()
        st.subheader("📊 Status Atual")
        stats = calculate_statistics(st.session_state.data_dict)
        geral = stats["geral"]
        
        st.json({
            "Total": geral["total"],
            "Concluídas": geral["concluidas"],
            "Em Execução": geral["em_execucao"],
            "Planejadas": geral["planejadas"],
            "Atrasadas": geral["atrasadas"]
        })
