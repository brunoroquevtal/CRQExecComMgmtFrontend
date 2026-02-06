"""
Módulo para carregamento de dados do arquivo Excel
"""
import pandas as pd
import streamlit as st
from datetime import datetime
from config import EXCEL_COLUMNS, SEQUENCIAS


@st.cache_data(show_spinner="Carregando arquivo Excel...")
def load_excel_file(uploaded_file):
    """
    Carrega arquivo Excel e retorna dados de todas as abas
    
    Args:
        uploaded_file: Arquivo Excel carregado via Streamlit
        
    Returns:
        dict: Dicionário com dados de cada sequência
    """
    try:
        # Ler todas as abas do Excel
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        dados = {}
        
        for sheet_name in sheet_names:
            # Identificar sequência pelo nome da aba
            sequencia = None
            for seq_key, seq_info in SEQUENCIAS.items():
                if seq_key in sheet_name.upper():
                    sequencia = seq_key
                    break
            
            if not sequencia:
                # Tentar identificar por padrão
                if "REDE" in sheet_name.upper():
                    sequencia = "REDE"
                elif "OPENSHIFT" in sheet_name.upper():
                    sequencia = "OPENSHIFT"
                elif "NFS" in sheet_name.upper():
                    sequencia = "NFS"
                elif "SI" in sheet_name.upper():
                    sequencia = "SI"
                else:
                    # Pular abas não reconhecidas
                    continue
            
            # Ler aba
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            # Verificar se o dataframe está vazio
            if df.empty or len(df.columns) == 0:
                continue
            
            # Normalizar nomes das colunas (remover espaços, normalizar maiúsculas/minúsculas)
            df.columns = [str(col).strip() for col in df.columns]
            
            # Mapear nomes de colunas para os esperados (case-insensitive e tolerante a espaços)
            expected_cols = ["Seq", "Atividade", "Grupo", "Localidade", 
                            "Executor", "Telefone", "Inicio", "Fim", "Tempo"]
            
            # Criar mapeamento flexível
            col_mapping = {}
            for i, expected in enumerate(expected_cols):
                # Procurar coluna correspondente (case-insensitive, ignorando espaços)
                found = False
                for j, actual_col in enumerate(df.columns):
                    if actual_col.strip().lower() == expected.lower():
                        col_mapping[expected] = j
                        found = True
                        break
                
                # Se não encontrou, usar posição por índice (assumindo ordem)
                if not found and i < len(df.columns):
                    col_mapping[expected] = i
            
            # Verificar se temos pelo menos as colunas essenciais
            if len(col_mapping) < 5:  # Mínimo: Seq, Atividade, Inicio, Fim, Tempo
                st.warning(f"Estrutura da aba {sheet_name} pode estar incorreta. Colunas encontradas: {list(df.columns[:9])}")
                continue
            
            # Selecionar e renomear colunas
            selected_cols = []
            for expected in expected_cols:
                if expected in col_mapping:
                    idx = col_mapping[expected]
                    if idx < len(df.columns):
                        selected_cols.append(df.columns[idx])
                    else:
                        selected_cols.append(None)
                else:
                    selected_cols.append(None)
            
            # Criar novo dataframe com colunas corretas
            new_df = pd.DataFrame()
            for i, expected in enumerate(expected_cols):
                if selected_cols[i] is not None and selected_cols[i] in df.columns:
                    new_df[expected] = df[selected_cols[i]]
                else:
                    new_df[expected] = None
            
            df = new_df
            
            # Limpar dados - ser mais tolerante
            # Remover apenas linhas onde AMBOS Seq E Atividade estão completamente vazios
            # Se tiver pelo menos um preenchido, manter a linha
            
            # Converter Seq para string primeiro para verificar vazios
            df["Seq"] = df["Seq"].astype(str)
            df["Atividade"] = df["Atividade"].astype(str)
            
            # Criar máscara: manter se Seq não está vazio OU Atividade não está vazia
            mask_valid = (
                (df["Seq"].notna() & (df["Seq"].str.strip() != "") & (df["Seq"].str.strip() != "nan")) |
                (df["Atividade"].notna() & (df["Atividade"].str.strip() != "") & (df["Atividade"].str.strip() != "nan"))
            )
            df = df[mask_valid].copy()
            
            # Converter tipos
            try:
                # Tentar converter Seq para numérico, mas manter linhas mesmo se falhar
                # Usar errors='coerce' para converter inválidos para NaN, mas manter a linha
                df["Seq"] = pd.to_numeric(df["Seq"], errors='coerce').astype('Int64')
                
                # Não remover linhas baseado apenas em Seq - manter todas que têm Atividade
                # O salvamento no banco vai tratar linhas sem Seq válido
            except Exception as e:
                st.warning(f"Erro ao converter Seq na aba {sheet_name}: {str(e)}")
                # Continuar mesmo com erro, tentar salvar o que conseguir
                # Manter Seq como string se não conseguir converter
            
            # Converter datas
            for col in ["Inicio", "Fim"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Converter colunas de texto para string (evitar tipos mistos)
            # Função robusta para converter qualquer tipo para string
            def safe_str_convert(val):
                if pd.isna(val) or val is None:
                    return ""
                try:
                    if isinstance(val, (int, float)):
                        return str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
                    return str(val)
                except:
                    return ""
            
            for col in ["Telefone", "Grupo", "Localidade", "Executor", "Atividade"]:
                if col in df.columns:
                    df[col] = df[col].apply(safe_str_convert)
            
            # Converter coluna Tempo de hh:mm:ss para minutos
            if "Tempo" in df.columns:
                from modules.calculations import convert_time_to_minutes
                df["Tempo"] = df["Tempo"].apply(convert_time_to_minutes)
                # Converter para float (minutos)
                df["Tempo"] = pd.to_numeric(df["Tempo"], errors='coerce').fillna(0)
            
            # Adicionar CRQ ao dataframe
            df["CRQ"] = sequencia
            
            dados[sequencia] = {
                "dataframe": df,
                "sheet_name": sheet_name
            }
        
        return dados
    
    except Exception as e:
        st.error(f"Erro ao carregar arquivo Excel: {str(e)}")
        return None


def merge_control_data(excel_data, control_data):
    """
    Mescla dados do Excel com dados de controle do banco
    
    Args:
        excel_data: Dados carregados do Excel
        control_data: Dados de controle do banco de dados
        
    Returns:
        dict: Dados mesclados
    """
    merged_data = {}
    
    for sequencia, data in excel_data.items():
        df = data["dataframe"].copy()
        
        # Adicionar colunas de controle
        df["Status"] = "Planejado"
        df["Horario_Inicio_Real"] = None
        df["Horario_Fim_Real"] = None
        df["Atraso_Minutos"] = 0
        df["Observacoes"] = ""
        df["Is_Milestone"] = False
        df["Predecessoras"] = ""
        
        # Marcar como milestone linhas com Grupo vazio
        if "Grupo" in df.columns:
            for idx, row in df.iterrows():
                grupo_value = row.get("Grupo")
                # Verificar se Grupo está vazio (NaN), string vazia, ou contém apenas espaços
                is_empty = (
                    pd.isna(grupo_value) or 
                    grupo_value == "" or 
                    (isinstance(grupo_value, str) and grupo_value.strip() == "") or
                    str(grupo_value).strip() == "nan"
                )
                if is_empty:
                    df.at[idx, "Is_Milestone"] = True
        
        # Converter colunas sensíveis para string ANTES do merge (evitar tipos mistos do PyArrow)
        def safe_str_convert(val):
            if pd.isna(val) or val is None:
                return ""
            try:
                if isinstance(val, (int, float)):
                    return str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
                return str(val)
            except:
                return ""
        
        for col in ["Telefone", "Grupo", "Localidade", "Executor", "Atividade"]:
            if col in df.columns:
                df[col] = df[col].apply(safe_str_convert)
        
        # Converter coluna Tempo de hh:mm:ss para minutos (se ainda não foi convertido)
        if "Tempo" in df.columns:
            from modules.calculations import convert_time_to_minutes
            # Verificar se já está em formato numérico
            if not pd.api.types.is_numeric_dtype(df["Tempo"]):
                df["Tempo"] = df["Tempo"].apply(convert_time_to_minutes)
                df["Tempo"] = pd.to_numeric(df["Tempo"], errors='coerce').fillna(0)
        
        # Preencher com dados de controle existentes
        for idx, row in df.iterrows():
            seq = int(row["Seq"])
            excel_data_id = row.get("Excel_Data_ID", 0) if "Excel_Data_ID" in row else 0
            
            # Tentar buscar usando excel_data_id primeiro (mais preciso)
            if excel_data_id and excel_data_id != 0:
                key = f"{seq}_{sequencia}_{excel_data_id}"
            else:
                key = f"{seq}_{sequencia}"
            
            # Se não encontrou com excel_data_id, tentar sem ele (compatibilidade)
            if key not in control_data:
                key = f"{seq}_{sequencia}"
            
            if key in control_data:
                control = control_data[key]
                df.at[idx, "Status"] = control.get("status", "Planejado")
                df.at[idx, "Horario_Inicio_Real"] = control.get("horario_inicio_real")
                df.at[idx, "Horario_Fim_Real"] = control.get("horario_fim_real")
                df.at[idx, "Atraso_Minutos"] = control.get("atraso_minutos", 0)
                df.at[idx, "Observacoes"] = control.get("observacoes", "")
                # Se já existe milestone no banco, manter o valor do banco
                # Caso contrário, usar o valor detectado do Excel
                if control.get("is_milestone", False):
                    df.at[idx, "Is_Milestone"] = True
                # Se não está no banco mas foi detectado como milestone, manter True
                # (já foi definido acima)
                df.at[idx, "Predecessoras"] = control.get("predecessoras", "")
        
        # Garantir que todas as colunas sensíveis sejam string ANTES de retornar
        # Isso evita erros do PyArrow mesmo que as colunas não sejam exibidas
        for col in ["Telefone", "Grupo", "Localidade", "Executor", "Atividade"]:
            if col in df.columns:
                df[col] = df[col].apply(safe_str_convert)
        
        # Garantir que Tempo está em minutos (numérico)
        if "Tempo" in df.columns:
            from modules.calculations import convert_time_to_minutes
            if not pd.api.types.is_numeric_dtype(df["Tempo"]):
                df["Tempo"] = df["Tempo"].apply(convert_time_to_minutes)
                df["Tempo"] = pd.to_numeric(df["Tempo"], errors='coerce').fillna(0)
        
        merged_data[sequencia] = {
            "dataframe": df,
            "sheet_name": data["sheet_name"]
        }
    
    return merged_data


def validate_excel_structure(uploaded_file):
    """
    Valida se o arquivo Excel tem a estrutura esperada
    
    Args:
        uploaded_file: Arquivo Excel carregado
        
    Returns:
        bool: True se válido, False caso contrário
    """
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        
        if len(excel_file.sheet_names) == 0:
            return False
        
        # Verificar se pelo menos uma aba reconhecida tem estrutura válida
        expected_cols_lower = ["seq", "atividade", "grupo", "localidade", 
                              "executor", "telefone", "inicio", "fim", "tempo"]
        
        for sheet_name in excel_file.sheet_names:
            # Verificar se a aba é uma das sequências esperadas
            is_recognized = False
            for seq_key in SEQUENCIAS.keys():
                if seq_key in sheet_name.upper():
                    is_recognized = True
                    break
            
            if not is_recognized:
                continue
            
            # Ler aba
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name, nrows=5)
            
            # Verificar se está vazia
            if df.empty or len(df.columns) == 0:
                continue
            
            # Normalizar nomes das colunas
            df.columns = [str(col).strip().lower() for col in df.columns]
            
            # Verificar se tem pelo menos algumas colunas esperadas
            found_cols = sum(1 for col in expected_cols_lower[:5] if col in df.columns)
            if found_cols >= 3:  # Pelo menos Seq, Atividade e mais uma
                return True
        
        return False
    
    except Exception as e:
        return False
