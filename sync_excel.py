"""
Script para sincronizar atividades do Excel com a API Node.js
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
from datetime import datetime, timedelta
import os
import io
import time
import argparse
import signal
import requests

# Variáveis globais para controle de interrupção
interrupted = False
processed_count = 0
created_count = 0
updated_count = 0
failed_count = 0
deleted_count = 0

# Configurar stdout para UTF-8 no Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Handler para arquivo (sempre UTF-8)
file_handler = logging.FileHandler('sync_excel.log', encoding='utf-8')

# Handler para console (tentar UTF-8, fallback para ASCII)
try:
    console_handler = logging.StreamHandler(sys.stdout)
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
# URL padrão: Backend no Netlify (produção)
# Para desenvolvimento local, defina: export API_BASE_URL=http://localhost:3000
API_BASE_URL = os.getenv("API_BASE_URL", "https://crqcommunidationbackend.netlify.app/.netlify/functions/api")

# Verificação SSL (pode ser desabilitada em ambientes corporativos com proxy)
# Defina SSL_VERIFY=false ou DISABLE_SSL_VERIFY=true para desabilitar
SSL_VERIFY = os.getenv("SSL_VERIFY", "true").lower() not in ("false", "0", "no", "off")
if os.getenv("DISABLE_SSL_VERIFY", "").lower() in ("true", "1", "yes", "on"):
    SSL_VERIFY = False

# Mapeamento de sequências conhecidas
SEQUENCIAS = {
    "REDE": "REDE",
    "OPENSHIFT": "OPENSHIFT",
    "NFS": "NFS",
    "SI": "SI"
}

DATE_FORMAT = "%d/%m/%Y %H:%M:%S"


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


def make_api_request(method: str, endpoint: str, json_data: Optional[Dict] = None, 
                     timeout: int = 60, retry_count: int = 3) -> Optional[requests.Response]:
    """
    Faz requisição HTTP com retry automático
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    # Configuração de SSL
    verify_ssl = SSL_VERIFY
    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logger.warning("AVISO: Verificação SSL desabilitada. Use apenas em ambientes confiáveis!")
    
    for attempt in range(retry_count + 1):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, timeout=timeout, verify=verify_ssl)
            elif method.upper() == 'POST':
                response = requests.post(url, json=json_data, timeout=timeout, verify=verify_ssl)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=json_data, timeout=timeout, verify=verify_ssl)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, json=json_data, timeout=timeout, verify=verify_ssl)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.SSLError as e:
            error_msg = str(e)
            if "CERTIFICATE_VERIFY_FAILED" in error_msg or "self-signed" in error_msg.lower():
                logger.error(f"Erro de certificado SSL em {method} {url}")
                logger.error("Este erro geralmente ocorre em ambientes corporativos com proxy/firewall.")
                logger.error("Solução: Defina a variável de ambiente DISABLE_SSL_VERIFY=true")
                logger.error("Exemplo (PowerShell): $env:DISABLE_SSL_VERIFY='true'")
                logger.error("Exemplo (CMD): set DISABLE_SSL_VERIFY=true")
                logger.error("Exemplo (Linux/Mac): export DISABLE_SSL_VERIFY=true")
            else:
                logger.error(f"Erro SSL em {method} {url}: {e}")
            return None
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout em {method} {url} (tentativa {attempt + 1}/{retry_count + 1})")
            if attempt < retry_count:
                time.sleep(2 * (attempt + 1))
                continue
                
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Erro de conexão em {method} {url} (tentativa {attempt + 1}/{retry_count + 1}): {e}")
            if attempt < retry_count:
                time.sleep(2 * (attempt + 1))
                continue
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {e.response.status_code} em {method} {url}: {e.response.text[:500]}")
            return e.response
            
        except Exception as e:
            logger.error(f"Erro inesperado em {method} {url} (tentativa {attempt + 1}/{retry_count + 1}): {e}")
            if attempt < retry_count:
                time.sleep(2 * (attempt + 1))
                continue
    
    logger.error(f"Falha ao completar {method} {url} após {retry_count + 1} tentativas")
    return None


def check_api_health() -> bool:
    """Verifica se a API está disponível"""
    try:
        response = make_api_request('GET', '/health', timeout=5, retry_count=1)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                logger.info("[OK] API esta disponivel")
                return True
    except Exception:
        pass
    
    logger.warning("[AVISO] Nao foi possivel verificar API automaticamente")
    print("\n[AVISO] Nao foi possivel verificar a API automaticamente.")
    print("Se voce tem certeza que a API esta rodando, pode continuar.")
    resposta = input("Deseja continuar mesmo assim? (s/n): ").lower().strip()
    return resposta in ('s', 'sim', 'y', 'yes')


def read_excel_sheets(excel_path: str) -> Dict[str, pd.DataFrame]:
    """
    Lê o arquivo Excel e retorna abas que começam com "CRQ" e terminam com "2"
    Identifica abas de rollback (contendo "ROLLBACK" no nome)
    """
    try:
        excel_file = pd.ExcelFile(excel_path)
        sheets = {}
        
        logger.info(f"Abas encontradas no Excel: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            sheet_upper = sheet_name.upper()
            # Aceitar abas que começam com "CRQ" e terminam com "2"
            if sheet_upper.startswith("CRQ") and sheet_upper.endswith("2"):
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
    """Identifica a sequência (CRQ) baseado no nome da aba"""
    sheet_upper = sheet_name.upper()
    
    for seq_key, seq_value in SEQUENCIAS.items():
        if seq_key in sheet_upper:
            return seq_value
    
    if "CRQ" in sheet_upper and "2" in sheet_upper:
        parts = sheet_upper.replace("CRQ", "").replace("2", "").replace("ROLLBACK", "").strip().split()
        if parts:
            for part in parts:
                if part in SEQUENCIAS:
                    return SEQUENCIAS[part]
    
    return None


def is_rollback_sheet(sheet_name: str) -> bool:
    """Identifica se a aba é de rollback baseado no nome"""
    sheet_upper = sheet_name.upper()
    return "ROLLBACK" in sheet_upper or "RB" in sheet_upper


def parse_datetime_from_excel(value) -> Optional[datetime]:
    """Converte valor do Excel para objeto datetime"""
    if pd.isna(value) or value is None:
        return None
    
    try:
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            for fmt in [DATE_FORMAT, "%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt
                except:
                    continue
        
        # Tentar converter usando pandas (para valores numéricos do Excel)
        if isinstance(value, (int, float)):
            try:
                # Excel armazena datas como números (dias desde 1900-01-01)
                dt = pd.to_datetime(value, origin='1899-12-30', unit='D')
                return dt.to_pydatetime()
            except:
                pass
        
        if hasattr(value, 'strftime'):
            # Se já é um objeto datetime-like, retornar como datetime
            return datetime.fromisoformat(str(value)) if hasattr(value, 'isoformat') else value
        
        return None
    
    except Exception as e:
        logger.debug(f"Erro ao parsear data: {e}")
        return None


def extract_activity_data(df: pd.DataFrame, sequencia: str, is_rollback: bool = False) -> List[Dict]:
    """Extrai dados de atividades do DataFrame"""
    activities = []
    
    # Contadores para estatísticas
    total_linhas = len(df)
    ignoradas_seq_vazio = 0
    ignoradas_seq_invalido = 0
    ignoradas_atividade_vazia = 0
    ignoradas_sem_datas = 0
    
    # Identificar colunas
    seq_col = None
    atividade_col = None
    inicio_planejado_col = None  # Coluna de início planejado
    fim_planejado_col = None     # Coluna de fim planejado
    inicio_real_col = None       # Coluna de horário início real
    fim_real_col = None          # Coluna de horário fim real
    status_col = None
    grupo_col = None
    tempo_col = None
    executor_col = None  # Usado apenas para verificar se está vazio (milestone)
    
    # Primeira passagem: identificar colunas mais específicas primeiro
    for col in df.columns:
        col_lower = str(col).lower().strip()
        # Verificar colunas mais específicas primeiro
        if col_lower == "seq" or col_lower.startswith("seq"):
            if not seq_col:
                seq_col = col
        elif col_lower == "atividade" or col_lower.startswith("atividade"):
            if not atividade_col:
                atividade_col = col
        elif col_lower == "status" or col_lower.startswith("status"):
            if not status_col:
                status_col = col
        elif col_lower == "grupo" or col_lower.startswith("grupo"):
            if not grupo_col:
                grupo_col = col
        elif col_lower == "tempo" or col_lower.startswith("tempo"):
            if not tempo_col:
                tempo_col = col
        elif col_lower == "executor" or col_lower.startswith("executor"):
            if not executor_col:
                executor_col = col
    
    # Segunda passagem: identificar colunas de data/hora (mais complexas)
    # Primeiro, identificar todas as colunas que podem ser de data/hora
    possible_inicio_cols = []
    possible_fim_cols = []
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        
        # Ignorar colunas já identificadas
        if col == seq_col or col == atividade_col or col == status_col or col == grupo_col or col == tempo_col or col == executor_col:
            continue
        
        # Coletar todas as colunas que podem ser início ou fim
        if "inicio" in col_lower or "início" in col_lower:
            possible_inicio_cols.append((col, col_lower))
        elif "fim" in col_lower:
            possible_fim_cols.append((col, col_lower))
    
    # Identificar colunas reais primeiro (mais específicas)
    for col, col_lower in possible_inicio_cols:
        # Verificar se é coluna real (deve conter "real", "execução" ou "execucao")
        if "real" in col_lower or "execução" in col_lower or "execucao" in col_lower:
            if not inicio_real_col:
                inicio_real_col = col
                logger.info(f"Coluna identificada como Início Real: {col}")
    
    for col, col_lower in possible_fim_cols:
        # Verificar se é coluna real (deve conter "real", "execução" ou "execucao")
        if "real" in col_lower or "execução" in col_lower or "execucao" in col_lower:
            if not fim_real_col:
                fim_real_col = col
                logger.info(f"Coluna identificada como Fim Real: {col}")
    
    # Depois identificar colunas planejadas (não são reais)
    for col, col_lower in possible_inicio_cols:
        # Se não é real e ainda não foi identificada como real
        if col != inicio_real_col:
            if not inicio_planejado_col:
                inicio_planejado_col = col
                logger.info(f"Coluna identificada como Início Planejado: {col}")
    
    for col, col_lower in possible_fim_cols:
        # Se não é real e ainda não foi identificada como real
        if col != fim_real_col:
            if not fim_planejado_col:
                fim_planejado_col = col
                logger.info(f"Coluna identificada como Fim Planejado: {col}")
    
    # Log das colunas identificadas para debug
    logger.info(f"Colunas identificadas - Seq: {seq_col}, Atividade: {atividade_col}, "
                f"Início Planejado: {inicio_planejado_col}, Fim Planejado: {fim_planejado_col}, "
                f"Início Real: {inicio_real_col}, Fim Real: {fim_real_col}, "
                f"Status: {status_col}, Grupo: {grupo_col}, Tempo: {tempo_col}")
    
    # Validação: garantir que colunas planejadas e reais não sejam a mesma
    if inicio_planejado_col and inicio_real_col and inicio_planejado_col == inicio_real_col:
        logger.error(f"ERRO: Coluna de Início Planejado e Início Real são a mesma: {inicio_planejado_col}")
        inicio_real_col = None  # Priorizar planejado se houver confusão
    
    if fim_planejado_col and fim_real_col and fim_planejado_col == fim_real_col:
        logger.error(f"ERRO: Coluna de Fim Planejado e Fim Real são a mesma: {fim_planejado_col}")
        fim_real_col = None  # Priorizar planejado se houver confusão
    
    # Validação: se não há colunas reais identificadas, garantir que não estamos usando planejadas como reais
    if not inicio_real_col and inicio_planejado_col:
        logger.info(f"Aviso: Nenhuma coluna de Início Real identificada. Usando apenas Início Planejado: {inicio_planejado_col}")
    
    if not fim_real_col and fim_planejado_col:
        logger.info(f"Aviso: Nenhuma coluna de Fim Real identificada. Usando apenas Fim Planejado: {fim_planejado_col}")
    
    # Validação crítica: se não há colunas de início/fim planejado identificadas, logar erro
    if not inicio_planejado_col and not fim_planejado_col:
        logger.error(f"ERRO CRÍTICO: Nenhuma coluna de Início ou Fim Planejado identificada para {sequencia}!")
        logger.error(f"Colunas disponíveis: {list(df.columns)}")
        logger.error(f"Colunas que contêm 'inicio' ou 'início': {[col for col in df.columns if 'inicio' in str(col).lower() or 'início' in str(col).lower()]}")
        logger.error(f"Colunas que contêm 'fim': {[col for col in df.columns if 'fim' in str(col).lower()]}")
        return activities  # Retornar vazio se não há colunas de data
    
    if not seq_col:
        logger.warning(f"Coluna 'Seq' não encontrada. Colunas: {list(df.columns)}")
        return activities
    
    for idx, row in df.iterrows():
        try:
            seq_value = row[seq_col]
            if pd.isna(seq_value):
                ignoradas_seq_vazio += 1
                logger.debug(f"Linha {idx} ignorada: Seq vazio ou NaN")
                continue
            
            try:
                seq = int(float(seq_value))
            except:
                ignoradas_seq_invalido += 1
                logger.warning(f"Linha {idx} ignorada: Seq inválido (valor: {seq_value})")
                continue
            
            # Extrair atividade primeiro para validar
            atividade = None
            if atividade_col and atividade_col in row:
                atividade_value = row[atividade_col]
                if not pd.isna(atividade_value):
                    atividade = str(atividade_value).strip()
            
            # Validar: atividade não pode estar vazia
            if not atividade or atividade == "":
                ignoradas_atividade_vazia += 1
                logger.warning(f"Linha {idx} ignorada: atividade vazia ou não encontrada (Seq: {seq})")
                continue
            
            # Extrair início e fim planejados usando as colunas identificadas
            inicio_planejado = None
            fim_planejado = None
            
            if inicio_planejado_col and inicio_planejado_col in row:
                if pd.notna(row[inicio_planejado_col]):
                    try:
                        inicio_planejado = parse_datetime_from_excel(row[inicio_planejado_col])
                        if inicio_planejado:
                            logger.debug(f"Linha {idx} - Início Planejado extraído de '{inicio_planejado_col}': {inicio_planejado}")
                    except Exception as e:
                        logger.warning(f"Linha {idx} - Erro ao parsear início planejado: {e}")
                        inicio_planejado = None
            
            if fim_planejado_col and fim_planejado_col in row:
                if pd.notna(row[fim_planejado_col]):
                    try:
                        fim_planejado = parse_datetime_from_excel(row[fim_planejado_col])
                        if fim_planejado:
                            logger.debug(f"Linha {idx} - Fim Planejado extraído de '{fim_planejado_col}': {fim_planejado}")
                    except Exception as e:
                        logger.warning(f"Linha {idx} - Erro ao parsear fim planejado: {e}")
                        fim_planejado = None
            
            # Validar: deve ter pelo menos início OU fim planejado
            if not inicio_planejado and not fim_planejado:
                ignoradas_sem_datas += 1
                logger.warning(f"Linha {idx} ignorada: sem início ou fim planejado (Seq: {seq}, Atividade: {atividade})")
                continue
            
            activity_data = {
                "seq": seq,
                "sequencia": sequencia,
                "is_rollback": is_rollback,
                "atividade": atividade
            }
            
            # Adicionar início e fim planejados (NUNCA devem ir para horario_inicio_real ou horario_fim_real)
            if inicio_planejado:
                activity_data["inicio"] = inicio_planejado.isoformat()
                logger.debug(f"Linha {idx} - Adicionado 'inicio' (planejado): {activity_data['inicio']}")
            if fim_planejado:
                activity_data["fim"] = fim_planejado.isoformat()
                logger.debug(f"Linha {idx} - Adicionado 'fim' (planejado): {activity_data['fim']}")
            
            if status_col and status_col in row:
                status_value = row[status_col]
                # Validar que status não é uma data (não deve ser parseável como datetime)
                if pd.notna(status_value):
                    status_str = str(status_value).strip()
                    # Verificar se não é uma data tentando parsear
                    is_date = False
                    try:
                        # Tentar parsear como data
                        test_date = parse_datetime_from_excel(status_value)
                        if test_date:
                            # Se conseguiu parsear como data, provavelmente é uma data, não status
                            is_date = True
                            logger.warning(f"Linha {idx}: Coluna 'Status' contém data em vez de status. Valor: {status_str}")
                    except:
                        pass
                    
                    # Só adicionar como status se não for uma data e não estiver vazio
                    if not is_date and status_str and status_str.lower() not in ["nan", "none", ""]:
                        activity_data["status"] = status_str
            
            # Extrair horários reais (se existirem) - APENAS de colunas identificadas como "real"
            if inicio_real_col and inicio_real_col in row:
                if pd.notna(row[inicio_real_col]):
                    inicio_real = parse_datetime_from_excel(row[inicio_real_col])
                    if inicio_real:
                        activity_data["horario_inicio_real"] = inicio_real.isoformat()
                        logger.debug(f"Linha {idx} - Adicionado 'horario_inicio_real' de '{inicio_real_col}': {activity_data['horario_inicio_real']}")
            
            if fim_real_col and fim_real_col in row:
                if pd.notna(row[fim_real_col]):
                    fim_real = parse_datetime_from_excel(row[fim_real_col])
                    if fim_real:
                        activity_data["horario_fim_real"] = fim_real.isoformat()
                        logger.debug(f"Linha {idx} - Adicionado 'horario_fim_real' de '{fim_real_col}': {activity_data['horario_fim_real']}")
            
            if grupo_col and grupo_col in row:
                grupo_value = row[grupo_col]
                if not pd.isna(grupo_value):
                    activity_data["grupo"] = str(grupo_value).strip()
            
            if tempo_col and tempo_col in row:
                tempo_value = row[tempo_col]
                if not pd.isna(tempo_value):
                    try:
                        # Se já é um número, assumir que já está em minutos
                        if isinstance(tempo_value, (int, float)):
                            tempo = float(tempo_value)
                        else:
                            # Tentar converter string para número primeiro
                            tempo_str = str(tempo_value).strip()
                            try:
                                # Tentar converter diretamente para número (caso já esteja em minutos)
                                tempo = float(tempo_str)
                            except ValueError:
                                # Tentar parsear formato hh:mm:ss ou hh:mm
                                if ':' in tempo_str:
                                    parts = tempo_str.split(':')
                                    if len(parts) == 3:  # hh:mm:ss
                                        hours = int(parts[0])
                                        minutes = int(parts[1])
                                        seconds = int(parts[2])
                                        tempo = hours * 60 + minutes + seconds / 60
                                    elif len(parts) == 2:  # hh:mm
                                        hours = int(parts[0])
                                        minutes = int(parts[1])
                                        tempo = hours * 60 + minutes
                                    else:
                                        tempo = 0
                                        logger.debug(f"Formato de tempo inválido: {tempo_str}")
                                else:
                                    tempo = 0
                                    logger.debug(f"Formato de tempo inválido: {tempo_str}")
                        
                        activity_data["tempo"] = tempo
                        logger.debug(f"Tempo extraído: Seq {seq} = {tempo} minutos (valor original: {tempo_value})")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Erro ao converter tempo para float: {tempo_value} - {e}")
                        activity_data["tempo"] = 0
            
            # Verificar se deve ser milestone: status N/A e executor vazio
            is_milestone = False
            if status_col and status_col in row:
                status_value = str(row[status_col]).strip()
                if status_value.upper() == "N/A":
                    # Verificar se executor está vazio
                    executor_empty = True
                    if executor_col and executor_col in row:
                        executor_value = row[executor_col]
                        if not pd.isna(executor_value):
                            executor_str = str(executor_value).strip()
                            if executor_str and executor_str.lower() not in ["nan", "none", ""]:
                                executor_empty = False
                    else:
                        # Se não há coluna executor, considerar como vazio
                        executor_empty = True
                    
                    if executor_empty:
                        is_milestone = True
                        logger.info(f"Atividade Seq {seq} marcada como milestone (Status: N/A, Executor vazio)")
            
            activity_data["is_milestone"] = is_milestone
            
            activities.append(activity_data)
        
        except Exception as e:
            logger.warning(f"Erro ao processar linha {idx}: {e}")
            continue
    
    # Log de estatísticas
    total_ignoradas = ignoradas_seq_vazio + ignoradas_seq_invalido + ignoradas_atividade_vazia + ignoradas_sem_datas
    if total_ignoradas > 0:
        logger.warning(f"\n[ESTATÍSTICAS] Aba {sequencia} ({'Rollback' if is_rollback else 'Principal'}):")
        logger.warning(f"  - Total de linhas: {total_linhas}")
        logger.warning(f"  - Atividades extraídas: {len(activities)}")
        logger.warning(f"  - Linhas ignoradas: {total_ignoradas}")
        if ignoradas_seq_vazio > 0:
            logger.warning(f"    • Seq vazio: {ignoradas_seq_vazio}")
        if ignoradas_seq_invalido > 0:
            logger.warning(f"    • Seq inválido: {ignoradas_seq_invalido}")
        if ignoradas_atividade_vazia > 0:
            logger.warning(f"    • Atividade vazia: {ignoradas_atividade_vazia}")
        if ignoradas_sem_datas > 0:
            logger.warning(f"    • Sem início/fim planejado: {ignoradas_sem_datas}")
    
    return activities


def create_activity_via_api(activity: Dict, sync_timestamp: Optional[str] = None) -> bool:
    """Cria/atualiza uma atividade individualmente via PUT"""
    try:
        # Validar campos obrigatórios
        if not activity.get('seq') or not activity.get('sequencia'):
            logger.warning(f"[ERRO] Atividade sem seq ou sequencia: {activity}")
            return False
        
        if not activity.get('atividade') or activity.get('atividade').strip() == '':
            logger.warning(f"[ERRO] Atividade sem descrição: Seq {activity.get('seq')}, CRQ {activity.get('sequencia')}")
            return False
        
        if not activity.get('inicio') and not activity.get('fim'):
            logger.warning(f"[ERRO] Atividade sem início ou fim planejado: Seq {activity.get('seq')}, CRQ {activity.get('sequencia')}, Atividade: {activity.get('atividade')}")
            return False
        
        # Preparar dados para envio
        activity_data = {
            "seq": activity.get('seq'),
            "sequencia": activity.get('sequencia'),
            "is_rollback": activity.get('is_rollback', False),
            "atividade": activity.get('atividade'),
            "status": activity.get('status'),
            "horario_inicio_real": activity.get('horario_inicio_real'),
            "horario_fim_real": activity.get('horario_fim_real'),
            "is_milestone": activity.get('is_milestone', False)
        }
        
        # Adicionar timestamp de sincronização se fornecido
        if sync_timestamp:
            activity_data["ultima_sincronizacao"] = sync_timestamp
        
        # Adicionar início e fim planejados (obrigatórios)
        # IMPORTANTE: inicio e fim são sempre planejados, nunca devem ser horários reais
        if activity.get('inicio'):
            activity_data["inicio"] = activity.get('inicio')
            logger.debug(f"Enviando 'inicio' (planejado) para API: {activity_data['inicio']}")
        if activity.get('fim'):
            activity_data["fim"] = activity.get('fim')
            logger.debug(f"Enviando 'fim' (planejado) para API: {activity_data['fim']}")
        
        # Validação: garantir que inicio e fim não estão sendo enviados como horários reais
        if activity.get('inicio') and activity.get('horario_inicio_real') and activity.get('inicio') == activity.get('horario_inicio_real'):
            logger.warning(f"[AVISO] Seq {activity.get('seq')}: 'inicio' e 'horario_inicio_real' têm o mesmo valor. Isso pode indicar erro no mapeamento.")
        
        if activity.get('fim') and activity.get('horario_fim_real') and activity.get('fim') == activity.get('horario_fim_real'):
            logger.warning(f"[AVISO] Seq {activity.get('seq')}: 'fim' e 'horario_fim_real' têm o mesmo valor. Isso pode indicar erro no mapeamento.")
        
        # Adicionar campos opcionais apenas se existirem
        if activity.get('tempo') is not None:
            activity_data["tempo"] = activity.get('tempo')
        if activity.get('grupo'):
            activity_data["grupo"] = activity.get('grupo')
        
        response = make_api_request('PUT', '/api/activity', json_data=activity_data, timeout=60)
        
        if response and response.status_code == 200:
            result = response.json()
            if result.get("success"):
                rollback_info = " (Rollback)" if activity.get('is_rollback') else ""
                encerramento_info = " [ENCERRAMENTO]" if activity.get('is_encerramento') else ""
                logger.info(f"[OK] Atividade processada: Seq {activity['seq']}, CRQ {activity['sequencia']}{rollback_info}{encerramento_info}")
                return True
            else:
                logger.warning(f"[ERRO] Falha ao processar: {result.get('message', 'Erro desconhecido')}")
                return False
        else:
            logger.warning(f"[ERRO] Falha ao processar: HTTP {response.status_code if response else 'N/A'}")
            return False
    except Exception as e:
        logger.error(f"[ERRO] Erro ao processar atividade: {e}")
        return False


def get_existing_activities() -> List[Dict]:
    """Busca todas as atividades existentes no banco de dados"""
    try:
        response = make_api_request('GET', '/api/activities', timeout=60)
        
        if response and response.status_code == 200:
            data = response.json()
            activities = data.get('activities', [])
            logger.info(f"Encontradas {len(activities)} atividades existentes no banco")
            return activities
        else:
            logger.warning(f"Erro ao buscar atividades existentes: HTTP {response.status_code if response else 'N/A'}")
            return []
    except Exception as e:
        logger.error(f"Erro ao buscar atividades existentes: {e}")
        return []


def delete_activity_via_api(activity: Dict) -> bool:
    """Exclui uma atividade via DELETE"""
    try:
        response = make_api_request('DELETE', '/api/activity', json_data=activity, timeout=60)
        
        if response and response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logger.info(f"[EXCLUIDO] Atividade removida: Seq {activity['seq']}, CRQ {activity['sequencia']}")
                return True
            else:
                logger.warning(f"[ERRO] Falha ao excluir: {result.get('message', 'Erro desconhecido')}")
                return False
        else:
            logger.warning(f"[ERRO] Falha ao excluir: HTTP {response.status_code if response else 'N/A'}")
            return False
    except Exception as e:
        logger.error(f"[ERRO] Erro ao excluir atividade: {e}")
        return False


def create_activities_bulk_via_api(activities: List[Dict], sync_timestamp: Optional[str] = None) -> Dict:
    """Cria múltiplas atividades em lote via POST"""
    # A API Node.js não tem endpoint bulk-create, então vamos usar PUT individual
    # Mas podemos otimizar fazendo múltiplas requisições em paralelo ou sequencialmente
    
    logger.info(f"Enviando {len(activities)} atividades...")
    print(f"Enviando {len(activities)} atividades...")
    
    created = 0
    updated = 0
    failed = 0
    
    for activity in activities:
        if create_activity_via_api(activity, sync_timestamp):
            created += 1
        else:
            failed += 1
        time.sleep(0.1)  # Pequeno delay entre requisições
    
    logger.info(f"Carga concluida: {created} sucesso, {failed} falhas")
    print(f"[OK] Carga concluida: {created} sucesso, {failed} falhas")
    
    return {
        "total": len(activities),
        "created": created,
        "updated": updated,
        "failed": failed,
        "successful": created
    }


def get_excel_path() -> str:
    """Solicita o caminho do arquivo Excel ao usuário"""
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        excel_path = sys.argv[1]
        logger.info(f"Usando arquivo fornecido: {excel_path}")
        return excel_path
    
    print("\n" + "=" * 60)
    print("SINCRONIZACAO DE ATIVIDADES DO EXCEL")
    print("=" * 60)
    print("\nPor favor, informe o caminho do arquivo Excel (.xlsx)")
    print("Exemplos:")
    print('  C:\\Users\\SeuUsuario\\Downloads\\CRQ VIRADA REDE.xlsx')
    print('  "C:\\caminho com espacos\\arquivo.xlsx"')
    
    user_input = input("\nCaminho do arquivo: ").strip()
    
    if not user_input:
        logger.error("Nenhum caminho fornecido")
        print("\n[ERRO] Por favor, forneca o caminho completo do arquivo.")
        sys.exit(1)
    
    excel_path = user_input.strip('"').strip("'")
    return excel_path


def get_sync_period() -> Optional[int]:
    """Solicita a periodicidade de execução automática em minutos"""
    print("\n" + "=" * 60)
    print("PERIODICIDADE DE EXECUCAO AUTOMATICA")
    print("=" * 60)
    print("\nDeseja executar a sincronizacao automaticamente?")
    print("Se sim, informe o intervalo em minutos entre cada execucao.")
    print("Se nao, deixe em branco ou digite 0 para executar apenas uma vez.")
    print("\nExemplos:")
    print("  5  - Executa a cada 5 minutos")
    print("  10 - Executa a cada 10 minutos")
    print("  30 - Executa a cada 30 minutos")
    print("  0  - Executa apenas uma vez (padrao)")
    
    user_input = input("\nPeriodicidade (minutos, 0 para uma vez): ").strip()
    
    if not user_input or user_input == '0':
        return None
    
    try:
        period = int(user_input)
        if period < 1:
            print("\n[AVISO] Periodicidade invalida. Executando apenas uma vez.")
            return None
        return period
    except ValueError:
        print("\n[AVISO] Valor invalido. Executando apenas uma vez.")
        return None


def perform_sync(excel_path: str, use_bulk_mode: bool) -> bool:
    """Executa uma sincronização completa"""
    global interrupted, processed_count, created_count, updated_count, failed_count, deleted_count
    
    # Resetar contadores
    processed_count = 0
    created_count = 0
    updated_count = 0
    failed_count = 0
    deleted_count = 0
    
    # Gerar timestamp de sincronização (ISO format)
    sync_timestamp = datetime.now().isoformat()
    logger.info(f"Iniciando sincronização com timestamp: {sync_timestamp}")
    
    if not os.path.exists(excel_path):
        logger.error(f"Arquivo nao encontrado: {excel_path}")
        print(f"\n[ERRO] Arquivo nao encontrado: {excel_path}")
        return False
    
    logger.info(f"Lendo arquivo Excel: {excel_path}")
    sheets = read_excel_sheets(excel_path)
    
    if not sheets:
        logger.error("Nenhuma aba válida encontrada (deve começar com 'CRQ' e terminar com '2')")
        print("\n[ERRO] Nenhuma aba válida encontrada.")
        return False
    
    all_activities = []
    
    for sheet_name, df in sheets.items():
        if interrupted:
            break
            
        logger.info(f"\nProcessando aba: {sheet_name}")
        
        sequencia = identify_sequencia(sheet_name)
        if not sequencia:
            sequencia = sheet_name.replace("CRQ", "").replace("2", "").replace("ROLLBACK", "").replace("RB", "").strip().upper()
            if not sequencia:
                logger.warning(f"Pulando aba {sheet_name} - sequência não identificada")
                continue
        
        is_rollback = is_rollback_sheet(sheet_name)
        logger.info(f"Sequência identificada: {sequencia} (Rollback: {is_rollback})")
        
        activities = extract_activity_data(df, sequencia, is_rollback=is_rollback)
        
        # Identificar última atividade (encerramento) - maior seq
        if activities:
            max_seq = max(a.get('seq', 0) for a in activities if a.get('seq'))
            for activity in activities:
                if activity.get('seq') == max_seq:
                    activity['is_encerramento'] = True
                else:
                    activity['is_encerramento'] = False
        
        logger.info(f"  - {len(activities)} atividades extraídas ({'Rollback' if is_rollback else 'Principal'})")
        all_activities.extend(activities)
    
    if not all_activities:
        logger.warning("Nenhuma atividade foi extraída do Excel")
        print("\n[AVISO] Nenhuma atividade foi extraída do Excel")
        return False
    
    logger.info(f"\nTotal de atividades no Excel: {len(all_activities)}")
    
    # Coletar sequências processadas para verificação de exclusão
    sequencias_processadas = set()
    for activity in all_activities:
        if activity.get('sequencia'):
            sequencias_processadas.add(activity.get('sequencia'))
    
    # Processar atividades do Excel (criar/atualizar)
    if use_bulk_mode:
        # Modificar create_activities_bulk_via_api para aceitar sync_timestamp
        result = create_activities_bulk_via_api(all_activities, sync_timestamp)
        created_count = result.get("created", 0)
        failed_count = result.get("failed", 0)
    else:
        logger.info(f"\nProcessando {len(all_activities)} atividades individualmente...")
        print(f"\nProcessando {len(all_activities)} atividades individualmente...")
        print(f"Progresso: 0/{len(all_activities)}", end="", flush=True)
        
        for idx, activity in enumerate(all_activities, 1):
            if interrupted:
                logger.warning(f"Processamento interrompido na atividade {idx}/{len(all_activities)}")
                print(f"\n[INTERROMPIDO] Processamento parado na atividade {idx}/{len(all_activities)}")
                break
            
            if create_activity_via_api(activity, sync_timestamp):
                created_count += 1
            else:
                failed_count += 1
            
            processed_count += 1
            
            if idx < len(all_activities) and not interrupted:
                time.sleep(0.1)
            
            if idx % 10 == 0 or idx == len(all_activities) or interrupted:
                print(f"\rProgresso: {idx}/{len(all_activities)} (OK: {created_count}, Falhas: {failed_count})", end="", flush=True)
        
        print()
    
    # Buscar atividades não sincronizadas (que não foram atualizadas nesta execução)
    if not interrupted and sequencias_processadas:
        logger.info("\nVerificando atividades não sincronizadas para exclusão...")
        print("\nVerificando atividades não sincronizadas para exclusão...")
        
        try:
            # Buscar atividades não sincronizadas via API
            sequencias_str = ','.join(sequencias_processadas)
            response = make_api_request('GET', f'/api/unsynced-activities?sync_timestamp={sync_timestamp}&sequencias={sequencias_str}', timeout=60)
            
            if response and response.status_code == 200:
                data = response.json()
                unsynced_activities = data.get('activities', [])
                
                if unsynced_activities:
                    logger.info(f"Encontradas {len(unsynced_activities)} atividades não sincronizadas (serão excluídas)")
                    print(f"Encontradas {len(unsynced_activities)} atividades não sincronizadas")
                    
                    for activity_to_delete in unsynced_activities:
                        if interrupted:
                            break
                        
                        if delete_activity_via_api(activity_to_delete):
                            deleted_count += 1
                        else:
                            failed_count += 1
                        
                        time.sleep(0.1)
                    
                    logger.info(f"Exclusão concluída: {deleted_count} atividades excluídas")
                    print(f"Exclusão concluída: {deleted_count} atividades excluídas")
                else:
                    logger.info("Nenhuma atividade não sincronizada encontrada")
                    print("Nenhuma atividade não sincronizada encontrada")
            else:
                logger.warning(f"Erro ao buscar atividades não sincronizadas: HTTP {response.status_code if response else 'N/A'}")
                print(f"[AVISO] Não foi possível verificar atividades para exclusão")
        except Exception as e:
            logger.error(f"Erro ao verificar atividades não sincronizadas: {e}")
            print(f"[ERRO] Erro ao verificar atividades não sincronizadas: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMO DA SINCRONIZACAO")
    print("=" * 60)
    print(f"Total de atividades no Excel: {len(all_activities)}")
    print(f"Processadas com sucesso: {created_count}")
    print(f"Excluidas (nao estao mais no Excel): {deleted_count}")
    print(f"Falhas: {failed_count}")
    print("=" * 60)
    
    logger.info("\n" + "=" * 60)
    logger.info("RESUMO DA SINCRONIZACAO")
    logger.info("=" * 60)
    logger.info(f"Total de atividades no Excel: {len(all_activities)}")
    logger.info(f"Processadas com sucesso: {created_count}")
    logger.info(f"Excluidas (nao estao mais no Excel): {deleted_count}")
    logger.info(f"Falhas: {failed_count}")
    logger.info("=" * 60)
    
    return True


def main():
    """Função principal"""
    global interrupted, processed_count, created_count, updated_count, failed_count, deleted_count
    
    interrupted = False
    processed_count = 0
    created_count = 0
    updated_count = 0
    failed_count = 0
    deleted_count = 0
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
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
    logger.info(f"API: {API_BASE_URL}")
    logger.info(f"Modo: {'BULK (lote)' if use_bulk_mode else 'INDIVIDUAL (uma por vez)'}")
    logger.info("=" * 60)
    
    print("\nVerificando conexao com API...")
    if not check_api_health():
        logger.error("API nao esta disponivel. Verifique se o servidor esta rodando.")
        print("\n[ERRO] API nao esta disponivel.")
        print(f"\nVerifique se o servidor Node.js esta rodando em {API_BASE_URL}")
        print("\nPara iniciar o servidor:")
        print("  cd backend")
        print("  npm start")
        sys.exit(1)
    print("[OK] Conexao com API estabelecida!\n")
    
    if args.excel_path:
        excel_path = args.excel_path
    else:
        excel_path = get_excel_path()
    
    if not os.path.exists(excel_path):
        logger.error(f"Arquivo nao encontrado: {excel_path}")
        print(f"\n[ERRO] Arquivo nao encontrado: {excel_path}")
        sys.exit(1)
    
    if not excel_path.lower().endswith(('.xlsx', '.xls')):
        logger.warning(f"O arquivo nao parece ser um Excel: {excel_path}")
        resposta = input("Deseja continuar mesmo assim? (s/n): ").lower().strip()
        if resposta not in ('s', 'sim', 'y', 'yes'):
            sys.exit(0)
    
    # Solicitar periodicidade
    sync_period = get_sync_period()
    
    # Executar sincronização
    sync_count = 0
    
    while True:
        sync_count += 1
        sync_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        print("\n" + "=" * 60)
        print(f"EXECUCAO #{sync_count} - {sync_time}")
        print("=" * 60)
        logger.info(f"Iniciando execucao #{sync_count} em {sync_time}")
        
        # Executar sincronização
        success = perform_sync(excel_path, use_bulk_mode)
        
        if interrupted:
            print("\n[INTERROMPIDO] Sincronizacao interrompida pelo usuario.")
            logger.warning("Sincronizacao interrompida pelo usuario")
            break
        
        if not success:
            print("\n[ERRO] Falha na sincronizacao. Verifique os logs para mais detalhes.")
            if sync_period is None:
                # Se não há periodicidade, sair após erro
                break
        
        # Se não há periodicidade definida, executar apenas uma vez
        if sync_period is None:
            print("\n[OK] Sincronizacao concluida. Executando apenas uma vez.")
            break
        
        # Calcular próxima execução
        next_execution = datetime.now()
        next_execution = next_execution.replace(second=0, microsecond=0)
        next_execution = next_execution + timedelta(minutes=sync_period)
        
        print("\n" + "=" * 60)
        print(f"PROXIMA EXECUCAO: {next_execution.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Intervalo: {sync_period} minutos")
        print("=" * 60)
        print("\nPressione Ctrl+C para interromper a execucao automatica...")
        logger.info(f"Proxima execucao agendada para {next_execution.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Aguardar até a próxima execução
        wait_seconds = sync_period * 60
        waited = 0
        
        while waited < wait_seconds and not interrupted:
            time.sleep(1)
            waited += 1
            
            # Mostrar contagem regressiva a cada minuto
            remaining_minutes = (wait_seconds - waited) // 60
            remaining_seconds = (wait_seconds - waited) % 60
            if waited % 60 == 0 or waited == 1:
                print(f"\rAguardando proxima execucao... {remaining_minutes:02d}:{remaining_seconds:02d} restantes", end="", flush=True)
        
        print()  # Nova linha após contagem
        
        if interrupted:
            print("\n[INTERROMPIDO] Sincronizacao automatica interrompida pelo usuario.")
            logger.warning("Sincronizacao automatica interrompida pelo usuario")
            break


if __name__ == "__main__":
    main()
