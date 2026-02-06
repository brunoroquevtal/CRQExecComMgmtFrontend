"""
Script para sincronizar atividades do Excel com a API
Lê abas que começam com "CRQ" e terminam com "2" (segunda tentativa)

Uso:
    python sync_excel.py [--mode individual|bulk] [caminho_do_arquivo.xlsx]
    
Parâmetros:
    --mode, -m: Modo de processamento
        - individual: Envia cada atividade individualmente via POST (padrão)
        - bulk: Envia todas as atividades de uma vez via POST em lote
    
    caminho_do_arquivo.xlsx: Caminho do arquivo Excel (opcional)
        Se não fornecido, o script solicitará interativamente.

Exemplos:
    python sync_excel.py --mode individual
    python sync_excel.py --mode bulk
    python sync_excel.py -m bulk "C:\\caminho\\arquivo.xlsx"
    python sync_excel.py "C:\\caminho\\arquivo.xlsx"  # Usa modo individual (padrão)
"""
import pandas as pd
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os
import io
import time
import argparse
import signal

# Importar cliente API centralizado
from modules.api_client import get_client, APIClient

# Variáveis globais para controle de interrupção
interrupted = False
processed_count = 0
created_count = 0
updated_count = 0
failed_count = 0

# Configurar logging com encoding UTF-8 para suportar emojis

# Configurar stdout para UTF-8 no Windows
if sys.platform == 'win32':
    try:
        # Tentar configurar console para UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Handler para arquivo (sempre UTF-8)
file_handler = logging.FileHandler('sync_excel.log', encoding='utf-8')

# Handler para console (tentar UTF-8, fallback para ASCII)
try:
    console_handler = logging.StreamHandler(sys.stdout)
    # Tentar configurar encoding UTF-8
    if hasattr(console_handler.stream, 'reconfigure'):
        console_handler.stream.reconfigure(encoding='utf-8')
except:
    console_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Configurações
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Obter cliente API
api_client = get_client(API_BASE_URL)

# Mapeamento de sequências conhecidas
SEQUENCIAS = {
    "REDE": "REDE",
    "OPENSHIFT": "OPENSHIFT",
    "NFS": "NFS",
    "SI": "SI"
}

DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

# Variáveis globais para controle de interrupção
interrupted = False
processed_count = 0
created_count = 0
updated_count = 0
failed_count = 0


def signal_handler(sig, frame):
    """Handler para Ctrl+C - permite parar o script graciosamente"""
    global interrupted
    interrupted = True
    print("\n\n" + "=" * 60)
    print("INTERRUPCAO SOLICITADA (Ctrl+C)")
    print("=" * 60)
    print("Aguardando conclusao da requisicao atual...")
    print("Pressione Ctrl+C novamente para forcar encerramento imediato")
    logger.warning("Interrupcao solicitada pelo usuario (Ctrl+C)")


def read_excel_sheets(excel_path: str) -> Dict[str, pd.DataFrame]:
    """
    Lê o arquivo Excel e retorna apenas as abas que começam com "CRQ" e terminam com "2"
    
    Args:
        excel_path: Caminho do arquivo Excel
        
    Returns:
        dict: Dicionário com nome da aba e DataFrame
    """
    try:
        # Ler todas as abas
        excel_file = pd.ExcelFile(excel_path)
        sheets = {}
        
        logger.info(f"Abas encontradas no Excel: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            # Verificar se começa com "CRQ" e termina com "2"
            if sheet_name.upper().startswith("CRQ") and sheet_name.upper().endswith("2"):
                logger.info(f"Processando aba: {sheet_name}")
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                sheets[sheet_name] = df
                logger.info(f"  - {len(df)} linhas encontradas na aba {sheet_name}")
        
        if not sheets:
            logger.warning("Nenhuma aba encontrada que comece com 'CRQ' e termine com '2'")
        
        return sheets
    
    except Exception as e:
        logger.error(f"Erro ao ler Excel: {e}")
        raise


def identify_sequencia(sheet_name: str) -> Optional[str]:
    """
    Identifica a sequência (CRQ) baseado no nome da aba
    
    Args:
        sheet_name: Nome da aba
        
    Returns:
        str: Nome da sequência ou None
    """
    sheet_upper = sheet_name.upper()
    
    # Procurar por sequências conhecidas no nome da aba
    for seq_key, seq_value in SEQUENCIAS.items():
        if seq_key in sheet_upper:
            return seq_value
    
    # Se não encontrar, tentar extrair do nome
    # Exemplo: "CRQ REDE 2" -> "REDE"
    if "CRQ" in sheet_upper and "2" in sheet_upper:
        # Remover "CRQ" e "2" e espaços extras
        parts = sheet_upper.replace("CRQ", "").replace("2", "").strip().split()
        if parts:
            # Tentar encontrar correspondência
            for part in parts:
                if part in SEQUENCIAS:
                    return SEQUENCIAS[part]
    
    return None


def parse_datetime_from_excel(value) -> Optional[str]:
    """
    Converte valor do Excel para formato de data esperado
    
    Args:
        value: Valor do Excel (pode ser datetime, string, etc)
        
    Returns:
        str: Data formatada ou None
    """
    if pd.isna(value) or value is None:
        return None
    
    try:
        # Se já é datetime
        if isinstance(value, datetime):
            return value.strftime(DATE_FORMAT)
        
        # Se é string, tentar parsear
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            # Tentar vários formatos
            for fmt in [DATE_FORMAT, "%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(DATE_FORMAT)
                except:
                    continue
        
        # Se é Timestamp do pandas
        if hasattr(value, 'strftime'):
            return value.strftime(DATE_FORMAT)
        
        return None
    
    except Exception as e:
        logger.debug(f"Erro ao parsear data: {e}")
        return None


def detect_rollback_blocks(df: pd.DataFrame) -> Dict:
    """
    Detecta os blocos de janela de execução e janela de rollback no DataFrame
    
    Args:
        df: DataFrame do Excel
        
    Returns:
        dict: {
            "execucao": DataFrame com atividades de execução,
            "rollback": DataFrame com atividades de rollback,
            "rollback_ativado": bool - se rollback deve ser ativado
        }
    """
    # Procurar por indicadores de rollback
    # Geralmente há uma linha separadora ou cabeçalho indicando "ROLLBACK" ou "Janela de Rollback"
    rollback_ativado = False
    execucao_df = df.copy()
    rollback_df = pd.DataFrame()
    
    # Procurar por linhas que indicam início do bloco de rollback
    # Pode ser uma linha com "ROLLBACK", "Janela de Rollback", "ROLLBACK ATIVADO", etc.
    rollback_start_idx = None
    
    for idx, row in df.iterrows():
        # Verificar todas as colunas da linha para encontrar indicadores
        row_str = " ".join([str(val).upper() for val in row.values if pd.notna(val)])
        
        if any(keyword in row_str for keyword in ["ROLLBACK", "JANELA DE ROLLBACK", "ROLLBACK ATIVADO", "OK"]):
            # Verificar se é um "OK" que ativa rollback
            if "OK" in row_str and ("ROLLBACK" in row_str or "ATIVADO" in row_str):
                rollback_ativado = True
                logger.info(f"Rollback detectado como ATIVADO na linha {idx}")
            
            # Se encontrou início do bloco de rollback
            if "ROLLBACK" in row_str and rollback_start_idx is None:
                rollback_start_idx = idx
                logger.info(f"Inicio do bloco de rollback detectado na linha {idx}")
                break
    
    # Se encontrou bloco de rollback, separar os DataFrames
    if rollback_start_idx is not None:
        execucao_df = df.iloc[:rollback_start_idx].copy()
        rollback_df = df.iloc[rollback_start_idx:].copy()
        
        # Remover linha de cabeçalho do rollback se for apenas texto
        if len(rollback_df) > 0:
            first_row_str = " ".join([str(val).upper() for val in rollback_df.iloc[0].values if pd.notna(val)])
            if "ROLLBACK" in first_row_str and not any(pd.notna(val) and str(val).replace(".", "").isdigit() for val in rollback_df.iloc[0].values if str(val) != "ROLLBACK"):
                rollback_df = rollback_df.iloc[1:].copy()
    
    return {
        "execucao": execucao_df,
        "rollback": rollback_df,
        "rollback_ativado": rollback_ativado
    }


def extract_activity_data(df: pd.DataFrame, sequencia: str, is_rollback: bool = False) -> List[Dict]:
    """
    Extrai dados de atividades do DataFrame
    
    Args:
        df: DataFrame do Excel
        sequencia: Nome da sequência/CRQ
        
    Returns:
        list: Lista de dicionários com dados das atividades
    """
    activities = []
    
    # Mapear colunas esperadas (pode variar)
    # Tentar identificar colunas automaticamente
    seq_col = None
    atividade_col = None
    inicio_col = None
    fim_col = None
    inicio_real_col = None
    fim_real_col = None
    status_col = None
    grupo_col = None
    localidade_col = None
    executor_col = None
    telefone_col = None
    tempo_col = None
    
    # Procurar por colunas comuns
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if "seq" in col_lower or "sequencia" in col_lower:
            seq_col = col
        elif "atividade" in col_lower or "tarefa" in col_lower:
            atividade_col = col
        elif ("inicio real" in col_lower or "início real" in col_lower or 
              "horario inicio real" in col_lower or "horário início real" in col_lower or
              "inicio_execucao" in col_lower):
            inicio_real_col = col
        elif ("fim real" in col_lower or "horario fim real" in col_lower or 
              "horário fim real" in col_lower or "fim_execucao" in col_lower):
            fim_real_col = col
        elif ("inicio" in col_lower or "início" in col_lower or "start" in col_lower) and not inicio_real_col:
            # Só usar como início se não encontrou início real
            inicio_col = col
        elif ("fim" in col_lower or "end" in col_lower) and not fim_real_col:
            # Só usar como fim se não encontrou fim real
            fim_col = col
        elif "status" in col_lower or "estado" in col_lower:
            status_col = col
        elif "grupo" in col_lower:
            grupo_col = col
        elif "localidade" in col_lower or "local" in col_lower:
            localidade_col = col
        elif "executor" in col_lower or "responsavel" in col_lower:
            executor_col = col
        elif "telefone" in col_lower or "fone" in col_lower or "tel" in col_lower:
            telefone_col = col
        elif "tempo" in col_lower or "duracao" in col_lower:
            tempo_col = col
    
    # Priorizar colunas de horário real se encontradas
    if inicio_real_col:
        inicio_col = inicio_real_col
    if fim_real_col:
        fim_col = fim_real_col
    
    if not seq_col:
        logger.warning(f"Coluna 'Seq' não encontrada na aba {sequencia}. Colunas disponíveis: {list(df.columns)}")
        return activities
    
    logger.info(f"Colunas identificadas - Seq: {seq_col}, Atividade: {atividade_col}, Início: {inicio_col}, Fim: {fim_col}, Status: {status_col}")
    
    # Processar cada linha
    for idx, row in df.iterrows():
        try:
            seq_value = row[seq_col]
            
            # Pular se Seq estiver vazio
            if pd.isna(seq_value):
                continue
            
            # Converter Seq para int
            try:
                seq = int(float(seq_value))
            except:
                logger.debug(f"Seq inválido na linha {idx}: {seq_value}")
                continue
            
            # Extrair dados
            activity_data = {
                "seq": seq,
                "sequencia": sequencia,
                "is_rollback": is_rollback  # Marcar se é atividade de rollback
            }
            
            # Status (se disponível)
            if status_col and status_col in row:
                status = str(row[status_col]).strip()
                if status and status.lower() not in ["nan", "none", ""]:
                    # Mapear status do Excel para status do sistema
                    status_mapping = {
                        "concluído": "Concluído",
                        "concluido": "Concluído",
                        "em execução": "Em Execução",
                        "em execucao": "Em Execução",
                        "planejado": "Planejado",
                        "atrasado": "Atrasado",
                        "adiantado": "Adiantado"
                    }
                    status_lower = status.lower()
                    if status_lower in status_mapping:
                        activity_data["status"] = status_mapping[status_lower]
                    elif status in ["Concluído", "Em Execução", "Planejado", "Atrasado", "Adiantado"]:
                        activity_data["status"] = status
            
            # Horário início real (se disponível)
            # Priorizar coluna de início real, senão usar início planejado
            if inicio_col and inicio_col in row:
                inicio = parse_datetime_from_excel(row[inicio_col])
                if inicio:
                    activity_data["horario_inicio_real"] = inicio
            
            # Horário fim real (se disponível)
            # Priorizar coluna de fim real, senão usar fim planejado
            if fim_col and fim_col in row:
                fim = parse_datetime_from_excel(row[fim_col])
                if fim:
                    activity_data["horario_fim_real"] = fim
            
            # Dados adicionais para criação
            if atividade_col and atividade_col in row:
                atividade_value = row[atividade_col]
                if not pd.isna(atividade_value):
                    activity_data["atividade"] = str(atividade_value).strip()
            
            if grupo_col and grupo_col in row:
                grupo_value = row[grupo_col]
                if not pd.isna(grupo_value):
                    activity_data["grupo"] = str(grupo_value).strip()
            
            if localidade_col and localidade_col in row:
                localidade_value = row[localidade_col]
                if not pd.isna(localidade_value):
                    activity_data["localidade"] = str(localidade_value).strip()
            
            if executor_col and executor_col in row:
                executor_value = row[executor_col]
                if not pd.isna(executor_value):
                    activity_data["executor"] = str(executor_value).strip()
            
            if telefone_col and telefone_col in row:
                telefone_value = row[telefone_col]
                if not pd.isna(telefone_value):
                    activity_data["telefone"] = str(telefone_value).strip()
            
            if tempo_col and tempo_col in row:
                tempo_value = row[tempo_col]
                if not pd.isna(tempo_value):
                    activity_data["tempo"] = str(tempo_value).strip()
            
            # Datas planejadas (para criação)
            if inicio_col and inicio_col in row and not activity_data.get("horario_inicio_real"):
                inicio_planejado = parse_datetime_from_excel(row[inicio_col])
                if inicio_planejado:
                    try:
                        from modules.calculations import parse_datetime_string
                        activity_data["inicio"] = parse_datetime_string(inicio_planejado).isoformat() if parse_datetime_string(inicio_planejado) else None
                    except:
                        pass
            
            if fim_col and fim_col in row and not activity_data.get("horario_fim_real"):
                fim_planejado = parse_datetime_from_excel(row[fim_col])
                if fim_planejado:
                    try:
                        from modules.calculations import parse_datetime_string
                        activity_data["fim"] = parse_datetime_string(fim_planejado).isoformat() if parse_datetime_string(fim_planejado) else None
                    except:
                        pass
            
            activities.append(activity_data)
        
        except Exception as e:
            logger.debug(f"Erro ao processar linha {idx}: {e}")
            continue
    
    return activities


def get_excel_data_id_from_db(seq: int, sequencia: str) -> Optional[int]:
    """
    Busca o excel_data_id de uma atividade diretamente no banco de dados
    
    Args:
        seq: Número sequencial
        sequencia: CRQ/Sequência
        
    Returns:
        int: excel_data_id ou None se não encontrado
    """
    try:
        from config import DB_PATH
        import sqlite3
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar no excel_data
        cursor.execute("""
            SELECT id FROM excel_data 
            WHERE seq = ? AND sequencia = ?
            LIMIT 1
        """, (seq, sequencia))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            logger.debug(f"Atividade Seq {seq}, CRQ {sequencia} nao encontrada no excel_data")
            return None
    except Exception as e:
        logger.debug(f"Erro ao buscar excel_data_id no banco: {e}")
        return None


def get_activity_from_db(seq: int, sequencia: str) -> Optional[Dict]:
    """
    Busca dados completos de uma atividade no banco
    
    Args:
        seq: Número sequencial
        sequencia: CRQ/Sequência
        
    Returns:
        dict: Dados da atividade ou None se não encontrada
    """
    try:
        from config import DB_PATH
        import sqlite3
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar no excel_data
        cursor.execute("""
            SELECT id, atividade, grupo, localidade, executor, telefone, 
                   inicio, fim, tempo
            FROM excel_data 
            WHERE seq = ? AND sequencia = ?
            LIMIT 1
        """, (seq, sequencia))
        
        excel_row = cursor.fetchone()
        
        if excel_row:
            excel_data_id = excel_row[0]
            # Buscar no activity_control
            cursor.execute("""
                SELECT status, horario_inicio_real, horario_fim_real, 
                       atraso_minutos, observacoes
                FROM activity_control
                WHERE seq = ? AND sequencia = ? AND excel_data_id = ?
            """, (seq, sequencia, excel_data_id))
            
            control_row = cursor.fetchone()
            conn.close()
            
            return {
                "excel_data_id": excel_data_id,
                "atividade": excel_row[1],
                "grupo": excel_row[2],
                "localidade": excel_row[3],
                "executor": excel_row[4],
                "telefone": excel_row[5],
                "inicio": excel_row[6],
                "fim": excel_row[7],
                "tempo": excel_row[8],
                "status": control_row[0] if control_row else None,
                "horario_inicio_real": control_row[1] if control_row else None,
                "horario_fim_real": control_row[2] if control_row else None,
                "atraso_minutos": control_row[3] if control_row else None,
                "observacoes": control_row[4] if control_row else None
            }
        else:
            conn.close()
            return None
    except Exception as e:
        logger.debug(f"Erro ao buscar atividade no banco: {e}")
        return None


def compare_activities(excel_activity: Dict, db_activity: Optional[Dict]) -> Dict:
    """
    Compara atividade do Excel com atividade do banco
    
    Returns:
        dict: {
            "exists": bool,
            "needs_update": bool,
            "changes": list,
            "action": "create" | "update" | "skip"
        }
    """
    if not db_activity:
        return {
            "exists": False,
            "needs_update": True,
            "changes": ["Nova atividade"],
            "action": "create"
        }
    
    changes = []
    
    # Comparar campos principais
    if excel_activity.get("status") and excel_activity["status"] != db_activity.get("status"):
        changes.append(f"Status: {db_activity.get('status')} -> {excel_activity['status']}")
    
    if excel_activity.get("horario_inicio_real") and excel_activity["horario_inicio_real"] != db_activity.get("horario_inicio_real"):
        changes.append(f"Início Real: {db_activity.get('horario_inicio_real')} -> {excel_activity['horario_inicio_real']}")
    
    if excel_activity.get("horario_fim_real") and excel_activity["horario_fim_real"] != db_activity.get("horario_fim_real"):
        changes.append(f"Fim Real: {db_activity.get('horario_fim_real')} -> {excel_activity['horario_fim_real']}")
    
    if excel_activity.get("observacoes") is not None and excel_activity.get("observacoes") != db_activity.get("observacoes"):
        changes.append(f"Observações alteradas")
    
    if changes:
        return {
            "exists": True,
            "needs_update": True,
            "changes": changes,
            "action": "update"
        }
    else:
        return {
            "exists": True,
            "needs_update": False,
            "changes": [],
            "action": "skip"
        }




def create_activities_bulk_via_api(activities: List[Dict], api_url: str = API_BASE_URL) -> Dict:
    """
    Cria múltiplas atividades em lote via POST
    
    Args:
        activities: Lista de dicionários com dados das atividades
        api_url: URL base da API
        
    Returns:
        Dict com resultado da operação
    """
    # Usar cliente API centralizado
    client = get_client(api_url)
    
    # Preparar dados para envio
    activities_data = []
    for activity in activities:
        activities_data.append({
            "seq": activity["seq"],
            "sequencia": activity["sequencia"],
            "atividade": activity.get("atividade", ""),
            "grupo": activity.get("grupo", ""),
            "localidade": activity.get("localidade", ""),
            "executor": activity.get("executor", ""),
            "telefone": activity.get("telefone", ""),
            "inicio": activity.get("inicio"),
            "fim": activity.get("fim"),
            "tempo": activity.get("tempo", ""),
            "status": activity.get("status"),
            "horario_inicio_real": activity.get("horario_inicio_real"),
            "horario_fim_real": activity.get("horario_fim_real"),
            "observacoes": activity.get("observacoes"),
            "is_rollback": activity.get("is_rollback", False)
        })
    
    logger.info(f"Enviando {len(activities_data)} atividades para carga em lote (bulk)...")
    print(f"Enviando {len(activities_data)} atividades para carga em lote (bulk)...")
    
    try:
        result = client.create_activities_bulk(activities_data, timeout=300)
        
        created = result.get('created', 0)
        updated = result.get('updated', 0)
        failed = result.get('failed', 0)
        
        logger.info(f"Carga bulk concluida: {created} criadas, {updated} atualizadas, {failed} falhas")
        print(f"[OK] Carga bulk concluida: {created} criadas, {updated} atualizadas, {failed} falhas")
        
        return {
            "total": result.get('total', len(activities)),
            "created": created,
            "updated": updated,
            "failed": failed,
            "successful": result.get('successful', created + updated)
        }
    except Exception as e:
        logger.error(f"Erro ao criar atividades em lote: {e}")
        print(f"[ERRO] Erro inesperado: {type(e).__name__}")
        return {
            "total": len(activities),
            "created": 0,
            "updated": 0,
            "failed": len(activities),
            "successful": 0
        }


def create_activity_via_api(activity: Dict, api_url: str = API_BASE_URL, retry_count: int = 1) -> bool:
    """
    Cria/atualiza uma atividade individualmente via POST
    
    Args:
        activity: Dicionário com dados da atividade (deve incluir dados do excel_data)
        api_url: URL base da API
        retry_count: Número de tentativas em caso de erro (não usado mais, retry é automático)
        
    Returns:
        bool: True se criado/atualizado com sucesso
    """
    # Usar cliente API centralizado
    client = get_client(api_url)
    
    # Converter para formato de criação (POST)
    create_data = {
        "seq": activity["seq"],
        "sequencia": activity["sequencia"],
        "atividade": activity.get("atividade", ""),
        "grupo": activity.get("grupo", ""),
        "localidade": activity.get("localidade", ""),
        "executor": activity.get("executor", ""),
        "telefone": activity.get("telefone", ""),
        "inicio": activity.get("inicio"),  # ISO format
        "fim": activity.get("fim"),  # ISO format
        "tempo": activity.get("tempo", ""),
        "status": activity.get("status"),
        "horario_inicio_real": activity.get("horario_inicio_real"),
        "horario_fim_real": activity.get("horario_fim_real"),
        "observacoes": activity.get("observacoes"),
        "is_rollback": activity.get("is_rollback", False)
    }
    
    try:
        result = client.create_activity(create_data, timeout=60)
        
        if result.get("success"):
            logger.info(f"[OK] Atividade processada: Seq {activity['seq']}, CRQ {activity['sequencia']}")
            return True
        else:
            error_msg = result.get('message', 'Erro desconhecido')
            logger.warning(f"[ERRO] Falha ao processar Seq {activity['seq']}, CRQ {activity['sequencia']}: {error_msg}")
            return False
    except Exception as e:
        logger.error(f"[ERRO] Erro ao processar atividade: {e}")
        return False


def update_activity_via_api(activity: Dict, api_url: str = API_BASE_URL, retry_count: int = 2, delay: float = 0.5) -> bool:
    """
    Atualiza uma atividade via API com retry e delay
    
    Args:
        activity: Dicionário com dados da atividade
        api_url: URL base da API
        retry_count: Número de tentativas em caso de erro
        delay: Delay em segundos entre tentativas
        
    Returns:
        bool: True se atualizado com sucesso
    """
    # Se não tem excel_data_id, tentar buscar no banco (importante para identificar corretamente)
    if "excel_data_id" not in activity or not activity.get("excel_data_id"):
        excel_data_id = get_excel_data_id_from_db(activity["seq"], activity["sequencia"])
        if excel_data_id:
            activity["excel_data_id"] = excel_data_id
            logger.debug(f"Excel_Data_ID encontrado: {excel_data_id} para Seq {activity['seq']}, CRQ {activity['sequencia']}")
        else:
            logger.warning(f"Excel_Data_ID nao encontrado para Seq {activity['seq']}, CRQ {activity['sequencia']}. "
                         f"A atividade precisa estar no banco (excel_data) antes de poder ser atualizada.")
    
    # Usar cliente API centralizado (retry é automático)
    client = get_client(api_url)
    
    # Log do que está sendo enviado (apenas campos principais)
    logger.debug(f"Enviando: Seq {activity['seq']}, CRQ {activity['sequencia']}, "
               f"Status: {activity.get('status', 'N/A')}, "
               f"Excel_ID: {activity.get('excel_data_id', 'N/A')}")
    
    try:
        result = client.update_activity(activity, timeout=120)
        
        if result.get("success"):
            updated_fields = result.get("updated_fields", [])
            logger.info(f"[OK] Atividade atualizada: Seq {activity['seq']}, CRQ {activity['sequencia']}, "
                      f"Campos: {', '.join(updated_fields) if updated_fields else 'nenhum'}")
            return True
        else:
            error_msg = result.get('message', 'Erro desconhecido')
            logger.warning(f"[ERRO] Falha ao atualizar Seq {activity['seq']}, CRQ {activity['sequencia']}: {error_msg}")
            return False
    except Exception as e:
        logger.error(f"[ERRO] Erro ao atualizar atividade: {e}")
        return False


def update_activities_bulk_via_api(activities: List[Dict], api_url: str = API_BASE_URL, batch_size: int = 10) -> Dict:
    """
    Atualiza múltiplas atividades via API em lotes menores com delays
    
    Args:
        activities: Lista de dicionários com dados das atividades
        api_url: URL base da API
        batch_size: Tamanho do lote (padrão: 10 atividades por vez para evitar sobrecarga)
        
    Returns:
        dict: Estatísticas de atualização
    """
    if not activities:
        return {"total": 0, "successful": 0, "failed": 0}
    
    total = len(activities)
    successful = 0
    failed = 0
    
    # Processar em lotes menores para evitar timeout e sobrecarga
    logger.info(f"Processando {total} atividades em lotes de {batch_size}...")
    print(f"\nProcessando {total} atividades em lotes de {batch_size}...")
    
    for i in range(0, total, batch_size):
        batch = activities[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        logger.info(f"Processando lote {batch_num}/{total_batches} ({len(batch)} atividades)...")
        print(f"Lote {batch_num}/{total_batches}...", end=" ", flush=True)
        
        # Delay antes de processar lote (para não sobrecarregar API)
        if i > 0:
            time.sleep(1)  # 1 segundo entre lotes
        
        try:
            # Usar cliente API centralizado
            client = get_client(api_url)
            # Timeout muito maior: 5 segundos por atividade, mínimo 60 segundos
            timeout = max(60, len(batch) * 5)
            result = client.update_activities_bulk(batch, timeout=timeout)
            
            batch_success = result.get('successful', 0)
            batch_failed = result.get('failed', 0)
            successful += batch_success
            failed += batch_failed
            logger.info(f"Lote {batch_num}: {batch_success} sucesso, {batch_failed} falhas")
            print(f"OK ({batch_success} sucesso, {batch_failed} falhas)")
            
            # Log detalhado de falhas se houver
            if batch_failed > 0 and 'results' in result:
                for res in result['results']:
                    if not res.get('success'):
                        logger.warning(f"  Falha: Seq {res.get('seq')}, CRQ {res.get('sequencia')}: {res.get('message', 'Erro desconhecido')}")
        
        except Exception as e:
            logger.warning(f"Erro no lote {batch_num}: {e}. Tentando uma por uma...")
            print(f"Erro: {type(e).__name__}, tentando uma por uma...")
            # Fallback: atualizar uma por uma neste lote
            for idx, activity in enumerate(batch):
                if idx > 0:
                    time.sleep(0.5)
                if update_activity_via_api(activity, api_url, delay=1.0):
                    successful += 1
                else:
                    failed += 1
        
        # Mostrar progresso
        progress = ((i + len(batch)) / total) * 100
        logger.info(f"Progresso: {i + len(batch)}/{total} ({progress:.1f}%)")
        print(f"[{progress:.1f}%]")
    
    return {"total": total, "successful": successful, "failed": failed}


def check_api_health(api_url: str = API_BASE_URL) -> bool:
    """
    Verifica se a API está disponível
    
    Args:
        api_url: URL base da API
        
    Returns:
        bool: True se API está disponível ou se deve continuar mesmo com erro
    """
    # Verificar se usuário quer pular verificação
    skip_check = os.getenv("SKIP_API_CHECK", "").lower() in ("true", "1", "yes")
    if skip_check:
        logger.info("[AVISO] Verificacao de API pulada (SKIP_API_CHECK=true)")
        return True
    
    # Usar cliente API centralizado
    client = get_client(api_url)
    
    # Tentar verificação rápida
    try:
        if client.health_check():
            logger.info("[OK] API esta disponivel")
            return True
    except Exception:
        pass
    
    # Se não conseguiu verificar, tentar verificação alternativa
    try:
        response = client._make_request('GET', '/', timeout=2, retry_count=0)
        if response and response.status_code == 200:
            logger.info("[OK] API esta disponivel (verificacao alternativa)")
            return True
    except Exception:
        pass
    
    # Timeout pode ser normal se firewall/proxy estiver bloqueando
    logger.warning("[AVISO] Nao foi possivel verificar API automaticamente (pode ser firewall/proxy)")
    logger.info("Se voce consegue acessar http://localhost:8000/docs no navegador,")
    logger.info("a API esta rodando. Continuando mesmo assim...")
    
    # Perguntar se quer continuar mesmo assim
    print("\n[AVISO] Nao foi possivel verificar a API automaticamente.")
    print("Se voce tem certeza que a API esta rodando, pode continuar.")
    resposta = input("Deseja continuar mesmo assim? (s/n): ").lower().strip()
    if resposta in ('s', 'sim', 'y', 'yes'):
        logger.info("Usuario escolheu continuar mesmo sem verificacao")
        return True
    return False


def get_excel_path() -> str:
    """
    Solicita o caminho do arquivo Excel ao usuário
    
    Returns:
        str: Caminho do arquivo Excel
    """
    # Verificar se foi fornecido como argumento
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
        logger.info(f"Usando arquivo fornecido: {excel_path}")
        return excel_path
    
    # Solicitar caminho interativamente
    print("\n" + "=" * 60)
    print("SINCRONIZACAO DE ATIVIDADES DO EXCEL")
    print("=" * 60)
    print("\nPor favor, informe o caminho do arquivo Excel (.xlsx)")
    print("Exemplos:")
    print('  C:\\Users\\SeuUsuario\\Downloads\\CRQ VIRADA REDE.xlsx')
    print('  "C:\\caminho com espacos\\arquivo.xlsx"')
    print(f'  {os.path.join(os.path.expanduser("~"), "Downloads", "CRQ VIRADA REDE.xlsx")}')
    print("\nOu pressione Enter para usar o caminho padrão (Downloads):")
    
    user_input = input("\nCaminho do arquivo: ").strip()
    
    # Se vazio, tentar caminho padrão
    if not user_input:
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", "CRQ VIRADA REDE.xlsx")
        logger.info(f"Nenhum caminho fornecido. Tentando caminho padrao: {default_path}")
        if os.path.exists(default_path):
            return default_path
        else:
            logger.error(f"Arquivo padrao nao encontrado: {default_path}")
            print(f"\n[ERRO] Arquivo padrao nao encontrado: {default_path}")
            print("Por favor, forneca o caminho completo do arquivo.")
            sys.exit(1)
    
    # Remover aspas se o usuário digitou
    excel_path = user_input.strip('"').strip("'")
    
    return excel_path


def main():
    """Função principal"""
    global interrupted, processed_count, created_count, updated_count, failed_count
    
    # Resetar contadores
    interrupted = False
    processed_count = 0
    created_count = 0
    updated_count = 0
    failed_count = 0
    
    # Registrar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Sincroniza atividades do Excel com o banco de dados')
    parser.add_argument('--mode', '-m', 
                       choices=['individual', 'bulk'], 
                       default='individual',
                       help='Modo de processamento: individual (uma por vez) ou bulk (todas de uma vez)')
    parser.add_argument('excel_path', nargs='?', help='Caminho do arquivo Excel (opcional)')
    
    args = parser.parse_args()
    use_bulk_mode = args.mode == 'bulk'
    
    logger.info("=" * 60)
    logger.info("Iniciando sincronização de atividades do Excel")
    logger.info(f"Modo: {'BULK (lote)' if use_bulk_mode else 'INDIVIDUAL (uma por vez)'}")
    logger.info("=" * 60)
    
    # Verificar API
    print("\nVerificando conexao com API...")
    if not check_api_health():
        logger.error("API nao esta disponivel. Verifique se o servidor esta rodando.")
        print("\n[ERRO] API nao esta disponivel.")
        print("\nPossiveis causas:")
        print("  1. O servidor API nao esta rodando")
        print("  2. O servidor esta em outra porta (padrao: 8000)")
        print("  3. Firewall ou antivirus bloqueando a conexao")
        print("  4. O servidor esta muito lento para responder")
        print("\nSolucoes:")
        print("  1. Inicie o servidor API:")
        print("     python api_server.py")
        print("     ou")
        print("     python start_all.py")
        print("\n  2. Verifique se a API esta respondendo:")
        print("     Abra no navegador: http://localhost:8000/health")
        print("\n  3. Se a API esta em outra porta, configure:")
        print("     $env:API_BASE_URL='http://localhost:PORTA'")
        sys.exit(1)
    print("[OK] Conexao com API estabelecida!\n")
    
    # Obter caminho do Excel
    if args.excel_path:
        excel_path = args.excel_path
        logger.info(f"Usando arquivo fornecido: {excel_path}")
    else:
        excel_path = get_excel_path()
    
    # Verificar se arquivo existe
    if not os.path.exists(excel_path):
        logger.error(f"Arquivo nao encontrado: {excel_path}")
        print(f"\n[ERRO] Arquivo nao encontrado: {excel_path}")
        print("\nVerifique se:")
        print("  1. O caminho esta correto")
        print("  2. O arquivo existe no local especificado")
        print("  3. Voce tem permissao para acessar o arquivo")
        sys.exit(1)
    
    # Verificar se é um arquivo Excel
    if not excel_path.lower().endswith(('.xlsx', '.xls')):
        logger.warning(f"O arquivo nao parece ser um Excel (.xlsx ou .xls): {excel_path}")
        resposta = input("Deseja continuar mesmo assim? (s/n): ").lower().strip()
        if resposta not in ('s', 'sim', 'y', 'yes'):
            logger.info("Operacao cancelada pelo usuario.")
            sys.exit(0)
    
    # Ler abas do Excel
    logger.info(f"Lendo arquivo Excel: {excel_path}")
    sheets = read_excel_sheets(excel_path)
    
    if not sheets:
        logger.error("Nenhuma aba válida encontrada (deve começar com 'CRQ' e terminar com '2')")
        sys.exit(1)
    
    # Processar cada aba
    all_activities = []
    rollback_status = {}  # Armazenar status de rollback por sequência
    
    for sheet_name, df in sheets.items():
        logger.info(f"\nProcessando aba: {sheet_name}")
        
        # Identificar sequência
        sequencia = identify_sequencia(sheet_name)
        if not sequencia:
            logger.warning(f"Não foi possível identificar sequência para aba {sheet_name}")
            logger.info(f"Tentando usar nome da aba como sequência...")
            # Tentar usar parte do nome da aba
            sequencia = sheet_name.replace("CRQ", "").replace("2", "").strip().upper()
            if not sequencia:
                logger.warning(f"Pulando aba {sheet_name} - sequência não identificada")
                continue
        
        logger.info(f"Sequência identificada: {sequencia}")
        
        # Detectar blocos de execução e rollback
        blocks = detect_rollback_blocks(df)
        execucao_df = blocks["execucao"]
        rollback_df = blocks["rollback"]
        rollback_ativado = blocks["rollback_ativado"]
        
        # Armazenar status de rollback para esta sequência
        rollback_status[sequencia] = rollback_ativado
        
        logger.info(f"  - Bloco execucao: {len(execucao_df)} linhas")
        logger.info(f"  - Bloco rollback: {len(rollback_df)} linhas")
        logger.info(f"  - Rollback ativado: {rollback_ativado}")
        
        # Processar atividades de execução
        if len(execucao_df) > 0:
            activities_exec = extract_activity_data(execucao_df, sequencia, is_rollback=False)
            logger.info(f"  - {len(activities_exec)} atividades de execucao extraídas")
            all_activities.extend(activities_exec)
        
        # Processar atividades de rollback
        if len(rollback_df) > 0:
            activities_rollback = extract_activity_data(rollback_df, sequencia, is_rollback=True)
            logger.info(f"  - {len(activities_rollback)} atividades de rollback extraídas")
            all_activities.extend(activities_rollback)
        
        # Se rollback está ativado, arquivar atividades de execução
        if rollback_ativado:
            logger.warning(f"ROLLBACK ATIVADO para {sequencia} - atividades de execucao serao arquivadas")
            print(f"\n[AVISO] ROLLBACK ATIVADO para {sequencia}")
            print("  - Atividades de execucao serao arquivadas")
            print("  - Atividades de rollback serao ativadas")
    
    if not all_activities:
        logger.warning("Nenhuma atividade foi extraída do Excel")
        sys.exit(0)
    
    logger.info(f"\nTotal de atividades no Excel: {len(all_activities)}")
    
    # Comparar com banco e preparar ações
    activities_to_create = []
    activities_to_update = []
    activities_unchanged = []
    
    logger.info("\nComparando atividades do Excel com banco de dados...")
    print("\nComparando atividades...")
    
    for activity in all_activities:
        db_activity = get_activity_from_db(activity["seq"], activity["sequencia"])
        comparison = compare_activities(activity, db_activity)
        
        if comparison["action"] == "create":
            # Adicionar dados necessários para criação
            activity["atividade"] = activity.get("atividade", f"Atividade {activity['seq']}")
            activity["grupo"] = activity.get("grupo", "")
            activity["localidade"] = activity.get("localidade", "")
            activity["executor"] = activity.get("executor", "")
            activity["telefone"] = activity.get("telefone", "")
            # Converter datas para ISO se necessário
            if activity.get("horario_inicio_real"):
                try:
                    from modules.calculations import parse_datetime_string
                    dt = parse_datetime_string(activity["horario_inicio_real"])
                    if dt:
                        activity["inicio"] = dt.isoformat()
                except:
                    pass
            if activity.get("horario_fim_real"):
                try:
                    from modules.calculations import parse_datetime_string
                    dt = parse_datetime_string(activity["horario_fim_real"])
                    if dt:
                        activity["fim"] = dt.isoformat()
                except:
                    pass
            activities_to_create.append(activity)
        elif comparison["action"] == "update":
            if db_activity:
                activity["excel_data_id"] = db_activity.get("excel_data_id")
            activities_to_update.append(activity)
        else:
            activities_unchanged.append(activity)
    
    # Resumo da comparação
    logger.info(f"\nResultado da comparacao:")
    logger.info(f"  - Novas atividades (criar): {len(activities_to_create)}")
    logger.info(f"  - Atividades alteradas (atualizar): {len(activities_to_update)}")
    logger.info(f"  - Atividades sem mudancas (pular): {len(activities_unchanged)}")
    
    print(f"\nResultado da comparacao:")
    print(f"  - Novas atividades (criar): {len(activities_to_create)}")
    print(f"  - Atividades alteradas (atualizar): {len(activities_to_update)}")
    print(f"  - Atividades sem mudancas (pular): {len(activities_unchanged)}")
    
    if activities_unchanged:
        print(f"\n{len(activities_unchanged)} atividades nao precisam ser atualizadas (sem mudancas)")
    
    # Processar criações (individual ou bulk conforme parâmetro)
    created_count = 0
    updated_count_from_create = 0
    failed_count = 0
    
    if activities_to_create:
        if use_bulk_mode:
            # Modo BULK: enviar todas de uma vez
            logger.info(f"\nProcessando {len(activities_to_create)} atividades em modo BULK (lote)...")
            print(f"\nProcessando {len(activities_to_create)} atividades em modo BULK (lote)...")
            
            # Preparar dados para envio
            activities_data = []
            for activity in activities_to_create:
                activities_data.append({
                    "seq": activity["seq"],
                    "sequencia": activity["sequencia"],
                    "atividade": activity.get("atividade", ""),
                    "grupo": activity.get("grupo", ""),
                    "localidade": activity.get("localidade", ""),
                    "executor": activity.get("executor", ""),
                    "telefone": activity.get("telefone", ""),
                    "inicio": activity.get("inicio"),  # ISO format
                    "fim": activity.get("fim"),  # ISO format
                    "tempo": activity.get("tempo", ""),
                    "status": activity.get("status"),
                    "horario_inicio_real": activity.get("horario_inicio_real"),
                    "horario_fim_real": activity.get("horario_fim_real"),
                    "observacoes": activity.get("observacoes"),
                    "is_rollback": activity.get("is_rollback", False)
                })
            
            # Enviar tudo de uma vez via POST bulk
            result = create_activities_bulk_via_api(activities_data)
            created_count = result.get("created", 0)
            updated_count_from_create = result.get("updated", 0)
            failed_count = result.get("failed", 0)
        else:
            # Modo INDIVIDUAL: enviar uma por vez
            logger.info(f"\nProcessando {len(activities_to_create)} atividades individualmente via POST...")
            print(f"\nProcessando {len(activities_to_create)} atividades individualmente via POST...")
            print(f"Progresso: 0/{len(activities_to_create)}", end="", flush=True)
            
            for idx, activity in enumerate(activities_to_create, 1):
                # Verificar se foi interrompido
                if interrupted:
                    logger.warning(f"Processamento interrompido pelo usuario na atividade {idx}/{len(activities_to_create)}")
                    print(f"\n[INTERROMPIDO] Processamento parado na atividade {idx}/{len(activities_to_create)}")
                    break
                
                # Preparar dados para envio
                activity_data = {
                    "seq": activity["seq"],
                    "sequencia": activity["sequencia"],
                    "atividade": activity.get("atividade", ""),
                    "grupo": activity.get("grupo", ""),
                    "localidade": activity.get("localidade", ""),
                    "executor": activity.get("executor", ""),
                    "telefone": activity.get("telefone", ""),
                    "inicio": activity.get("inicio"),  # ISO format
                    "fim": activity.get("fim"),  # ISO format
                    "tempo": activity.get("tempo", ""),
                    "status": activity.get("status"),
                    "horario_inicio_real": activity.get("horario_inicio_real"),
                    "horario_fim_real": activity.get("horario_fim_real"),
                    "observacoes": activity.get("observacoes"),
                    "is_rollback": activity.get("is_rollback", False)
                }
                
                # Enviar individualmente via POST
                if create_activity_via_api(activity_data):
                    created_count += 1
                else:
                    failed_count += 1
                
                processed_count += 1
                
                # Pequeno delay entre requisições para não sobrecarregar
                if idx < len(activities_to_create) and not interrupted:
                    time.sleep(0.1)
                
                # Mostrar progresso a cada 10 atividades ou no final
                if idx % 10 == 0 or idx == len(activities_to_create) or interrupted:
                    print(f"\rProgresso: {idx}/{len(activities_to_create)} (OK: {created_count}, Falhas: {failed_count})", end="", flush=True)
            
            print()  # Nova linha após progresso
            logger.info(f"Processamento individual concluido: {created_count} sucesso, {failed_count} falhas")
    
    # Processar atualizações
    updated_count = 0
    if activities_to_update and not interrupted:
        logger.info(f"\nAtualizando {len(activities_to_update)} atividades alteradas...")
        print(f"\nAtualizando {len(activities_to_update)} atividades alteradas...")
        result = update_activities_bulk_via_api(activities_to_update, batch_size=10)
        updated_count = result.get("successful", 0)
    else:
        result = {"total": 0, "successful": 0, "failed": 0}
    
    # Se foi interrompido, mostrar resumo parcial
    if interrupted:
        print("\n\n" + "=" * 60)
        print("PROCESSAMENTO INTERROMPIDO PELO USUARIO")
        print("=" * 60)
        print(f"Atividades processadas ate o momento: {processed_count}")
        print(f"  - Criadas/atualizadas: {created_count}")
        print(f"  - Atualizadas: {updated_count}")
        print(f"  - Falhas: {failed_count}")
        print("\nAs atividades ja processadas foram salvas no banco.")
        print("Execute o script novamente para continuar de onde parou.")
        print("=" * 60)
        
        logger.warning("=" * 60)
        logger.warning("PROCESSAMENTO INTERROMPIDO PELO USUARIO")
        logger.warning(f"Atividades processadas: {processed_count}")
        logger.warning(f"Criadas: {created_count}, Atualizadas: {updated_count}, Falhas: {failed_count}")
        logger.warning("=" * 60)
        
        sys.exit(0)
    
    # Processar rollback se necessário
    for sequencia, rollback_ativado in rollback_status.items():
        if rollback_ativado:
            logger.info(f"\nProcessando rollback para {sequencia}...")
            print(f"\nProcessando rollback para {sequencia}...")
            
            # Arquivar atividades de execução
            try:
                client = get_client(API_BASE_URL)
                result = client.archive_execution_activities(sequencia)
                archived = result.get("archived_count", 0)
                if archived > 0:
                    logger.info(f"Arquivadas {archived} atividades de execucao")
                    print(f"  [OK] Arquivadas {archived} atividades de execucao")
                else:
                    logger.warning(f"Nenhuma atividade arquivada ou erro: {result.get('message', 'N/A')}")
                    print(f"  [AVISO] Nenhuma atividade arquivada")
            except Exception as e:
                logger.error(f"Erro ao arquivar atividades: {e}")
                print(f"  [ERRO] Erro ao arquivar: {type(e).__name__}")
            
            # Ativar atividades de rollback
            try:
                client = get_client(API_BASE_URL)
                result = client.activate_rollback_activities(sequencia)
                activated = result.get("activated_count", 0)
                if activated > 0:
                    logger.info(f"Ativadas {activated} atividades de rollback")
                    print(f"  [OK] Ativadas {activated} atividades de rollback")
                else:
                    logger.warning(f"Nenhuma atividade ativada ou erro: {result.get('message', 'N/A')}")
                    print(f"  [AVISO] Nenhuma atividade de rollback ativada")
            except Exception as e:
                logger.error(f"Erro ao ativar rollback: {e}")
                print(f"  [ERRO] Erro ao ativar rollback: {type(e).__name__}")
    
    # Calcular totais
    total_processed = len(activities_to_create) + len(activities_to_update)
    total_successful = created_count + updated_count_from_create + updated_count
    total_failed = failed_count + (len(activities_to_update) - updated_count)
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DA SINCRONIZACAO")
    print("=" * 60)
    print(f"Total de atividades no Excel: {len(all_activities)}")
    print(f"  - Novas criadas/atualizadas: {created_count}/{len(activities_to_create)}")
    print(f"  - Atualizadas: {updated_count}/{len(activities_to_update)}")
    print(f"  - Sem mudancas (puladas): {len(activities_unchanged)}")
    print(f"\nTotal processado: {total_processed}")
    print(f"Sucesso: {total_successful}")
    print(f"Falhas: {total_failed}")
    print("=" * 60)
    
    logger.info("\n" + "=" * 60)
    logger.info("RESUMO DA SINCRONIZACAO")
    logger.info("=" * 60)
    logger.info(f"Total de atividades no Excel: {len(all_activities)}")
    logger.info(f"  - Novas criadas/atualizadas: {created_count}/{len(activities_to_create)}")
    logger.info(f"  - Atualizadas: {updated_count}/{len(activities_to_update)}")
    logger.info(f"  - Sem mudancas (puladas): {len(activities_unchanged)}")
    logger.info(f"\nTotal processado: {total_processed}")
    logger.info(f"Sucesso: {total_successful}")
    logger.info(f"Falhas: {total_failed}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
