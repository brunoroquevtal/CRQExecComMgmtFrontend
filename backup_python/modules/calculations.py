"""
Módulo para cálculos e lógica de negócio
"""
import pandas as pd
from datetime import datetime, timedelta
from config import DATE_FORMAT, STATUS_OPCOES, SEQUENCIAS, TOTAL_GERAL


def convert_time_to_minutes(time_str):
    """
    Converte tempo no formato hh:mm:ss ou hh:mm para minutos
    
    Args:
        time_str: String no formato "hh:mm:ss" ou "hh:mm" ou número (já em minutos)
        
    Returns:
        float: Tempo em minutos
    """
    if pd.isna(time_str) or time_str is None:
        return 0
    
    # Se já é um número, assumir que já está em minutos
    if isinstance(time_str, (int, float)):
        return float(time_str)
    
    # Converter para string
    time_str = str(time_str).strip()
    
    if not time_str or time_str == "" or time_str.lower() == "nan":
        return 0
    
    try:
        # Tentar converter diretamente para número (caso já esteja em minutos)
        return float(time_str)
    except ValueError:
        pass
    
    # Tentar parsear formato hh:mm:ss ou hh:mm
    try:
        parts = time_str.split(":")
        if len(parts) == 3:  # hh:mm:ss
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return hours * 60 + minutes + seconds / 60
        elif len(parts) == 2:  # hh:mm
            hours = int(parts[0])
            minutes = int(parts[1])
            return hours * 60 + minutes
        else:
            return 0
    except (ValueError, IndexError):
        return 0


def calculate_delay(fim_planejado, fim_real):
    """
    Calcula atraso/adiantamento em minutos
    
    Args:
        fim_planejado: Data/hora planejada (datetime ou string)
        fim_real: Data/hora real (datetime ou string)
        
    Returns:
        int: Atraso em minutos (negativo se adiantado)
    """
    if not fim_planejado or not fim_real:
        return 0
    
    try:
        # Converter strings para datetime se necessário
        if isinstance(fim_planejado, str):
            fim_planejado = datetime.strptime(fim_planejado, DATE_FORMAT)
        if isinstance(fim_real, str):
            fim_real = datetime.strptime(fim_real, DATE_FORMAT)
        
        if not isinstance(fim_planejado, datetime) or not isinstance(fim_real, datetime):
            return 0
        
        # Calcular diferença em minutos
        diff = fim_real - fim_planejado
        return int(diff.total_seconds() / 60)
    
    except Exception:
        return 0


def format_delay(minutes):
    """
    Formata atraso/adiantamento para formato legível
    
    Args:
        minutes: Atraso em minutos (negativo se adiantado)
        
    Returns:
        str: Formato legível (ex: "+1h 15min", "-30min")
    """
    if minutes == 0:
        return "0 min"
    
    sign = "+" if minutes > 0 else "-"
    abs_minutes = abs(minutes)
    
    if abs_minutes < 60:
        return f"{sign}{abs_minutes} min"
    else:
        hours = abs_minutes // 60
        mins = abs_minutes % 60
        if mins == 0:
            return f"{sign}{hours}h"
        else:
            return f"{sign}{hours}h {mins}min"


def update_status_by_delay(status, delay_minutes):
    """
    Atualiza status baseado no atraso calculado
    
    Args:
        status: Status atual
        delay_minutes: Atraso em minutos
        
    Returns:
        str: Novo status
    """
    if status == "Concluído":
        if delay_minutes > 0:
            return "Atrasado"
        elif delay_minutes < 0:
            return "Adiantado"
        else:
            return "Concluído"
    
    return status


def calculate_statistics(data_dict):
    """
    Calcula estatísticas gerais e por CRQ
    EXCLUI milestones das contagens de atividades
    
    Args:
        data_dict: Dicionário com dataframes por CRQ
        
    Returns:
        dict: Estatísticas calculadas
    """
    stats = {
        "geral": {
            "total": 0,
            "concluidas": 0,
            "em_execucao": 0,
            "planejadas": 0,
            "atrasadas": 0,
            "adiantadas": 0,
            "milestones": 0
        },
        "por_sequencia": {}
    }
    
    for sequencia, data in data_dict.items():
        df = data["dataframe"]
        
        # Filtrar milestones (excluir das contagens de atividades)
        if "Is_Milestone" in df.columns:
            # Verificação mais robusta usando fillna para tratar NaN/None
            df_activities = df[df["Is_Milestone"].fillna(False) != True].copy()
            df_milestones = df[df["Is_Milestone"].fillna(False) == True].copy()
            milestones_count = len(df_milestones)
        else:
            df_activities = df.copy()
            milestones_count = 0
        
        seq_stats = {
            "total": len(df_activities),  # Apenas atividades, sem milestones
            "concluidas": 0,
            "em_execucao": 0,
            "planejadas": 0,
            "atrasadas": 0,
            "adiantadas": 0,
            "milestones": milestones_count
        }
        
        # Contar por status (apenas atividades, não milestones)
        if len(df_activities) > 0:
            status_counts = df_activities["Status"].value_counts()
            
            seq_stats["concluidas"] = int(status_counts.get("Concluído", 0))
            # Adiantado é tratado como Em Execução para estatísticas
            em_execucao_count = int(status_counts.get("Em Execução", 0))
            adiantado_count = int(status_counts.get("Adiantado", 0))
            seq_stats["em_execucao"] = em_execucao_count + adiantado_count
            seq_stats["planejadas"] = int(status_counts.get("Planejado", 0))
            seq_stats["atrasadas"] = int(status_counts.get("Atrasado", 0))
            seq_stats["adiantadas"] = adiantado_count  # Manter contagem separada para referência
            
            # Adicionar atividades com atraso > 0 mesmo que status não seja "Atrasado"
            atrasadas_por_tempo = len(df_activities[(df_activities["Atraso_Minutos"] > 0) & (df_activities["Status"] != "Atrasado")])
            seq_stats["atrasadas"] += atrasadas_por_tempo
        
        stats["por_sequencia"][sequencia] = seq_stats
        
        # Acumular no geral
        stats["geral"]["total"] += seq_stats["total"]
        stats["geral"]["concluidas"] += seq_stats["concluidas"]
        stats["geral"]["em_execucao"] += seq_stats["em_execucao"]
        stats["geral"]["planejadas"] += seq_stats["planejadas"]
        stats["geral"]["atrasadas"] += seq_stats["atrasadas"]
        stats["geral"]["adiantadas"] += seq_stats["adiantadas"]
        stats["geral"]["milestones"] += milestones_count
    
    # Calcular percentuais
    for key in ["geral"] + list(stats["por_sequencia"].keys()):
        if key == "geral":
            total = stats["geral"]["total"]
        else:
            total = stats["por_sequencia"][key]["total"]
        
        if total > 0:
            if key == "geral":
                stats["geral"]["pct_concluidas"] = (stats["geral"]["concluidas"] / total) * 100
                stats["geral"]["pct_em_execucao"] = (stats["geral"]["em_execucao"] / total) * 100
                stats["geral"]["pct_planejadas"] = (stats["geral"]["planejadas"] / total) * 100
                stats["geral"]["pct_atrasadas"] = (stats["geral"]["atrasadas"] / total) * 100
            else:
                seq_stats = stats["por_sequencia"][key]
                seq_stats["pct_concluidas"] = (seq_stats["concluidas"] / total) * 100
                seq_stats["pct_em_execucao"] = (seq_stats["em_execucao"] / total) * 100
                seq_stats["pct_planejadas"] = (seq_stats["planejadas"] / total) * 100
                seq_stats["pct_atrasadas"] = (seq_stats["atrasadas"] / total) * 100
    
    return stats


def get_activities_by_status(data_dict, status, sequencia=None, exclude_milestones=True):
    """
    Retorna atividades filtradas por status
    EXCLUI milestones por padrão
    NOTA: Quando status é "Em Execução", também inclui atividades "Adiantado"
    
    Args:
        data_dict: Dicionário com dataframes
        status: Status para filtrar
        sequencia: Sequência específica (None para todas)
        exclude_milestones: Se True, exclui milestones das atividades
        
    Returns:
        pd.DataFrame: Dataframe filtrado
    """
    # Se buscar "Em Execução", incluir também "Adiantado"
    if status == "Em Execução":
        statuses_to_filter = ["Em Execução", "Adiantado"]
    else:
        statuses_to_filter = [status]
    
    if sequencia:
        if sequencia in data_dict:
            df = data_dict[sequencia]["dataframe"]
            filtered = df[df["Status"].isin(statuses_to_filter)].copy()
            # Excluir milestones se solicitado
            if exclude_milestones and "Is_Milestone" in filtered.columns:
                # Verificação mais robusta: excluir se Is_Milestone é True (não importa se é NaN, None, etc)
                filtered = filtered[filtered["Is_Milestone"].fillna(False) != True]
            return filtered
        return pd.DataFrame()
    else:
        all_dfs = []
        for seq, data in data_dict.items():
            df = data["dataframe"]
            filtered = df[df["Status"].isin(statuses_to_filter)].copy()
            # Excluir milestones se solicitado
            if exclude_milestones and "Is_Milestone" in filtered.columns:
                # Verificação mais robusta: excluir se Is_Milestone é True (não importa se é NaN, None, etc)
                filtered = filtered[filtered["Is_Milestone"].fillna(False) != True]
            all_dfs.append(filtered)
        
        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        return pd.DataFrame()


def get_delayed_activities(data_dict, sequencia=None):
    """
    Retorna atividades atrasadas
    EXCLUI milestones
    
    Args:
        data_dict: Dicionário com dataframes
        sequencia: Sequência específica (None para todas)
        
    Returns:
        pd.DataFrame: Dataframe com atividades atrasadas
    """
    if sequencia:
        if sequencia in data_dict:
            df = data_dict[sequencia]["dataframe"]
            filtered = df[(df["Status"] == "Atrasado") | (df["Atraso_Minutos"] > 0)].copy()
            # Excluir milestones
            if "Is_Milestone" in filtered.columns:
                filtered = filtered[filtered["Is_Milestone"].fillna(False) != True]
            return filtered
        return pd.DataFrame()
    else:
        all_dfs = []
        for seq, data in data_dict.items():
            df = data["dataframe"]
            filtered = df[(df["Status"] == "Atrasado") | (df["Atraso_Minutos"] > 0)].copy()
            # Excluir milestones
            if "Is_Milestone" in filtered.columns:
                filtered = filtered[filtered["Is_Milestone"].fillna(False) != True]
            all_dfs.append(filtered)
        
        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        return pd.DataFrame()


def get_next_activities(data_dict, sequencia=None, limit=10):
    """
    Retorna próximas atividades a executar (planejadas, ordenadas por horário)
    EXCLUI milestones
    
    Args:
        data_dict: Dicionário com dataframes
        sequencia: Sequência específica (None para todas)
        limit: Limite de resultados
        
    Returns:
        pd.DataFrame: Dataframe com próximas atividades
    """
    df = get_activities_by_status(data_dict, "Planejado", sequencia, exclude_milestones=True)
    
    # Garantir que milestones sejam excluídos (verificação adicional)
    if len(df) > 0 and "Is_Milestone" in df.columns:
        df = df[df["Is_Milestone"].fillna(False) != True]
    
    if len(df) > 0 and "Inicio" in df.columns:
        # Ordenar por horário planejado
        df = df.sort_values("Inicio")
        return df.head(limit)
    
    return df.head(limit)


def is_sequence_completed(data_dict, sequencia):
    """
    Verifica se uma sequência está 100% concluída
    Considera apenas atividades (exclui milestones)
    
    Args:
        data_dict: Dicionário com dataframes
        sequencia: Sequência para verificar
        
    Returns:
        bool: True se concluída, False caso contrário
    """
    if sequencia not in data_dict:
        return False
    
    df = data_dict[sequencia]["dataframe"]
    
    # Excluir milestones
    if "Is_Milestone" in df.columns:
        df = df[df["Is_Milestone"].fillna(False) != True]
    
    total = len(df)
    concluidas = len(df[df["Status"] == "Concluído"])
    
    return total > 0 and concluidas == total


def validate_datetime_string(dt_string):
    """
    Valida formato de data/hora
    
    Args:
        dt_string: String de data/hora
        
    Returns:
        bool: True se válido, False caso contrário
    """
    if not dt_string or pd.isna(dt_string):
        return True  # Vazio é válido
    
    try:
        datetime.strptime(dt_string, DATE_FORMAT)
        return True
    except:
        return False


def parse_datetime_string(dt_string):
    """
    Converte string de data/hora para datetime
    
    Args:
        dt_string: String de data/hora
        
    Returns:
        datetime: Objeto datetime ou None
    """
    if not dt_string or pd.isna(dt_string):
        return None
    
    try:
        if isinstance(dt_string, datetime):
            return dt_string
        return datetime.strptime(dt_string, DATE_FORMAT)
    except:
        return None


def get_milestones(data_dict, sequencia=None):
    """
    Retorna milestones (marcos do projeto)
    
    Args:
        data_dict: Dicionário com dataframes
        sequencia: Sequência específica (None para todas)
        
    Returns:
        pd.DataFrame: Dataframe com milestones
    """
    if sequencia:
        if sequencia in data_dict:
            df = data_dict[sequencia]["dataframe"]
            if "Is_Milestone" in df.columns:
                return df[df["Is_Milestone"] == True].copy()
        return pd.DataFrame()
    else:
        all_dfs = []
        for seq, data in data_dict.items():
            df = data["dataframe"]
            if "Is_Milestone" in df.columns:
                filtered = df[df["Is_Milestone"] == True].copy()
                all_dfs.append(filtered)
        
        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        return pd.DataFrame()


def get_predecessoras_list(predecessoras_str):
    """
    Converte string de predecessoras para lista de inteiros
    
    Args:
        predecessoras_str: String com predecessoras (ex: "1,5,10")
        
    Returns:
        list: Lista de números de sequência
    """
    if not predecessoras_str or pd.isna(predecessoras_str):
        return []
    
    try:
        return [int(p.strip()) for p in str(predecessoras_str).split(",") if p.strip()]
    except:
        return []


def check_dependencies_ready(data_dict, seq, sequencia, predecessoras_str):
    """
    Verifica se todas as predecessoras estão concluídas
    
    Args:
        data_dict: Dicionário com dataframes
        seq: Número da sequência da atividade
        sequencia: Nome da sequência
        predecessoras_str: String com predecessoras
        
    Returns:
        tuple: (todas_prontas: bool, predecessoras_pendentes: list)
    """
    if not predecessoras_str:
        return True, []
    
    pred_list = get_predecessoras_list(predecessoras_str)
    if not pred_list:
        return True, []
    
    if sequencia not in data_dict:
        return False, pred_list
    
    df = data_dict[sequencia]["dataframe"]
    pendentes = []
    
    for pred_seq in pred_list:
        pred_row = df[df["Seq"] == pred_seq]
        if len(pred_row) == 0:
            pendentes.append(pred_seq)
        else:
            status = pred_row.iloc[0]["Status"]
            if status != "Concluído":
                pendentes.append(pred_seq)
    
    return len(pendentes) == 0, pendentes


def get_activities_blocked_by_dependencies(data_dict):
    """
    Retorna atividades bloqueadas por dependências não concluídas
    EXCLUI milestones
    
    Args:
        data_dict: Dicionário com dataframes
        
    Returns:
        pd.DataFrame: Dataframe com atividades bloqueadas
    """
    blocked = []
    
    for sequencia, data in data_dict.items():
        df = data["dataframe"]
        
        # Excluir milestones
        if "Is_Milestone" in df.columns:
            df = df[df["Is_Milestone"].fillna(False) != True]
        
        if "Predecessoras" not in df.columns:
            continue
        
        for _, row in df.iterrows():
            seq = int(row["Seq"])
            predecessoras = row.get("Predecessoras", "")
            status = row["Status"]
            
            # Só verificar se não está concluída
            if status in ["Concluído", "Atrasado", "Adiantado"]:
                continue
            
            todas_prontas, pendentes = check_dependencies_ready(
                data_dict, seq, sequencia, predecessoras
            )
            
            if not todas_prontas and pendentes:
                row_copy = row.copy()
                row_copy["Predecessoras_Pendentes"] = ", ".join(map(str, pendentes))
                blocked.append(row_copy)
    
    if blocked:
        return pd.DataFrame(blocked)
    return pd.DataFrame()
