"""
Servidor API REST para atualização de atividades
Permite atualizar tarefas via requisições HTTP
"""
from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    # Para versões mais recentes do FastAPI, usar Starlette diretamente
    from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging
import os
import time
import json
import pandas as pd
import io

from modules.database import DatabaseManager
from modules.calculations import (
    calculate_delay, parse_datetime_string, 
    validate_datetime_string
)
from config import DATE_FORMAT, STATUS_OPCOES

# Configurar logging com nível baseado em variável de ambiente
DEBUG_MODE = os.getenv('API_DEBUG', 'false').lower() in ('true', '1', 'yes')
LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if DEBUG_MODE:
    logger.info("=" * 60)
    logger.info("MODO DEBUG ATIVADO")
    logger.info("Todas as requisicoes serao logadas em detalhes")
    logger.info("=" * 60)

# Criar aplicação FastAPI
app = FastAPI(
    title="API de Atualização de Atividades",
    description="API REST para atualizar tarefas do sistema de gerenciamento de CRQs",
    version="1.0.0"
)

# Middleware para logar requisições (modo debug)
class DebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log da requisição recebida
        if DEBUG_MODE:
            logger.debug("=" * 60)
            logger.debug(f"[REQUISICAO RECEBIDA] {request.method} {request.url.path}")
            logger.debug(f"Query params: {dict(request.query_params)}")
            logger.debug(f"Headers: {dict(request.headers)}")
            
            # Tentar ler body se houver
            try:
                body = await request.body()
                if body:
                    try:
                        body_json = json.loads(body)
                        logger.debug(f"Body (JSON): {json.dumps(body_json, indent=2, ensure_ascii=False)}")
                    except:
                        logger.debug(f"Body (raw): {body[:500]}")  # Primeiros 500 chars
            except Exception as e:
                logger.debug(f"Erro ao ler body: {e}")
        
        try:
            # Processar requisição
            response = await call_next(request)
            
            # Calcular tempo de processamento
            process_time = time.time() - start_time
            
            if DEBUG_MODE:
                logger.debug(f"[RESPOSTA] Status: {response.status_code}, Tempo: {process_time:.3f}s")
                logger.debug("=" * 60)
            elif process_time > 5.0:  # Logar se demorar mais de 5 segundos mesmo sem debug
                logger.warning(f"Requisicao lenta: {request.method} {request.url.path} levou {process_time:.3f}s")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"[ERRO NA REQUISICAO] {request.method} {request.url.path}")
            logger.error(f"Tempo ate erro: {process_time:.3f}s")
            logger.error(f"Erro: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

# Adicionar middleware de debug
if DEBUG_MODE:
    app.add_middleware(DebugMiddleware)

# Configurar CORS para permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global do DatabaseManager
db_manager = DatabaseManager()


# Modelos Pydantic para validação
class ActivityCreate(BaseModel):
    """Modelo para criação de atividade no excel_data"""
    seq: int = Field(..., description="Número sequencial da atividade")
    sequencia: str = Field(..., description="CRQ/Sequência (REDE, OPENSHIFT, NFS, SI)")
    atividade: Optional[str] = Field(None, description="Nome da atividade")
    grupo: Optional[str] = Field(None, description="Grupo")
    localidade: Optional[str] = Field(None, description="Localidade")
    executor: Optional[str] = Field(None, description="Executor")
    telefone: Optional[str] = Field(None, description="Telefone")
    inicio: Optional[str] = Field(None, description="Data/hora de início planejada (ISO format)")
    fim: Optional[str] = Field(None, description="Data/hora de fim planejada (ISO format)")
    tempo: Optional[str] = Field(None, description="Tempo estimado")
    status: Optional[str] = Field(None, description="Status inicial")
    horario_inicio_real: Optional[str] = Field(None, description="Horário de início real (DD/MM/YYYY HH:MM:SS)")
    horario_fim_real: Optional[str] = Field(None, description="Horário de fim real (DD/MM/YYYY HH:MM:SS)")
    observacoes: Optional[str] = Field(None, description="Observações")
    is_rollback: Optional[bool] = Field(False, description="Se é atividade de rollback")


class ActivityUpdate(BaseModel):
    """Modelo para atualização de atividade"""
    seq: int = Field(..., description="Número sequencial da atividade")
    sequencia: str = Field(..., description="CRQ/Sequência (REDE, OPENSHIFT, NFS, SI)")
    status: Optional[str] = Field(None, description="Status da atividade")
    horario_inicio_real: Optional[str] = Field(None, description="Horário de início real (DD/MM/YYYY HH:MM:SS)")
    horario_fim_real: Optional[str] = Field(None, description="Horário de fim real (DD/MM/YYYY HH:MM:SS)")
    observacoes: Optional[str] = Field(None, description="Observações")
    excel_data_id: Optional[int] = Field(None, description="ID da linha no excel_data (opcional)")

    class Config:
        json_schema_extra = {
            "example": {
                "seq": 999093,
                "sequencia": "REDE",
                "status": "Em Execução",
                "horario_inicio_real": "25/12/2024 14:30:00",
                "horario_fim_real": "25/12/2024 15:30:00",
                "observacoes": "Atividade iniciada conforme planejado"
            }
        }


class BulkActivityUpdate(BaseModel):
    """Modelo para atualização em lote"""
    activities: List[ActivityUpdate] = Field(..., description="Lista de atividades para atualizar")


class BulkActivityCreate(BaseModel):
    """Modelo para criação em lote de atividades"""
    activities: List[ActivityCreate] = Field(..., description="Lista de atividades para criar/atualizar")


class ActivityResponse(BaseModel):
    """Resposta de atualização de atividade"""
    success: bool
    message: str
    seq: int
    sequencia: str
    updated_fields: List[str]


class BulkActivityResponse(BaseModel):
    """Resposta de atualização em lote"""
    total: int
    successful: int
    failed: int
    results: List[ActivityResponse]


# Endpoints
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "API de Atualização de Atividades",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "Informações da API",
            "GET /health": "Status de saúde da API",
            "PUT /activity": "Atualizar uma atividade",
            "PUT /activities/bulk": "Atualizar múltiplas atividades",
            "GET /activity/{sequencia}/{seq}": "Buscar uma atividade"
        }
    }


@app.get("/health")
async def health_check():
    """Verifica saúde da API e conexão com banco"""
    try:
        conn = db_manager.get_connection()
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


@app.get("/activity/{sequencia}/{seq}")
async def get_activity(sequencia: str, seq: int, excel_data_id: Optional[int] = None):
    """Busca uma atividade específica"""
    try:
        activity = db_manager.get_activity_control(seq, sequencia, excel_data_id)
        if not activity:
            raise HTTPException(
                status_code=404,
                detail=f"Atividade não encontrada: Seq {seq}, CRQ {sequencia}"
            )
        return {
            "success": True,
            "activity": activity
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar atividade: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar atividade: {str(e)}")


@app.post("/activity")
async def create_activity(activity: ActivityCreate):
    """
    Cria uma nova atividade no excel_data e activity_control
    
    Se a atividade já existir, atualiza os dados.
    """
    start_time = time.time()
    if DEBUG_MODE:
        logger.debug(f"[CREATE] Iniciando criacao: Seq {activity.seq}, CRQ {activity.sequencia}, Rollback: {activity.is_rollback}")
    
    try:
        # Validar sequencia
        from config import SEQUENCIAS
        if activity.sequencia not in SEQUENCIAS:
            raise HTTPException(
                status_code=400,
                detail=f"Sequência inválida: {activity.sequencia}. Valores permitidos: {list(SEQUENCIAS.keys())}"
            )
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Verificar se já existe
        cursor.execute("""
            SELECT id FROM excel_data 
            WHERE seq = ? AND sequencia = ?
            LIMIT 1
        """, (activity.seq, activity.sequencia))
        
        existing = cursor.fetchone()
        
        if existing:
            # Atualizar existente
            excel_data_id = existing[0]
            cursor.execute("""
                UPDATE excel_data
                SET atividade = COALESCE(?, atividade),
                    grupo = COALESCE(?, grupo),
                    localidade = COALESCE(?, localidade),
                    executor = COALESCE(?, executor),
                    telefone = COALESCE(?, telefone),
                    inicio = COALESCE(?, inicio),
                    fim = COALESCE(?, fim),
                    tempo = COALESCE(?, tempo)
                WHERE id = ?
            """, (
                activity.atividade,
                activity.grupo,
                activity.localidade,
                activity.executor,
                activity.telefone,
                activity.inicio,
                activity.fim,
                activity.tempo,
                excel_data_id
            ))
            logger.info(f"Atividade atualizada no excel_data: Seq {activity.seq}, CRQ {activity.sequencia}")
        else:
            # Criar nova
            cursor.execute("""
                INSERT INTO excel_data
                (sequencia, seq, atividade, grupo, localidade, executor, 
                 telefone, inicio, fim, tempo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activity.sequencia,
                activity.seq,
                activity.atividade or "",
                activity.grupo or "",
                activity.localidade or "",
                activity.executor or "",
                activity.telefone or "",
                activity.inicio,
                activity.fim,
                activity.tempo or ""
            ))
            excel_data_id = cursor.lastrowid
            logger.info(f"Atividade criada no excel_data: Seq {activity.seq}, CRQ {activity.sequencia}, ID: {excel_data_id}")
        
        conn.commit()
        conn.close()
        
        if DEBUG_MODE:
            logger.debug(f"[CREATE] Excel_data processado: ID {excel_data_id}, Tempo: {time.time() - start_time:.3f}s")
        
        # Criar/atualizar registro de controle
        atraso_minutos = None
        try:
            if activity.horario_fim_real and activity.fim:
                # activity.fim pode estar em formato ISO, tentar parse
                try:
                    from datetime import datetime as dt
                    if isinstance(activity.fim, str) and 'T' in activity.fim:
                        # Formato ISO
                        fim_planejado = dt.fromisoformat(activity.fim.replace('Z', '+00:00'))
                    else:
                        fim_planejado = parse_datetime_string(activity.fim)
                    fim_real = parse_datetime_string(activity.horario_fim_real)
                    if fim_planejado and fim_real:
                        atraso_minutos = calculate_delay(fim_planejado, fim_real)
                except Exception as e:
                    logger.warning(f"Erro ao calcular atraso: {e}")
        
        except Exception as e:
            logger.warning(f"Erro ao processar atraso: {e}")
        
        try:
            # Salvar com flag de rollback usando SQL direto
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            # Verificar se já existe
            cursor.execute("""
                SELECT id FROM activity_control 
                WHERE seq = ? AND sequencia = ? AND excel_data_id = ?
            """, (activity.seq, activity.sequencia, excel_data_id))
            
            existing_control = cursor.fetchone()
            
            if existing_control:
                # Atualizar
                cursor.execute("""
                    UPDATE activity_control
                    SET status = COALESCE(?, status),
                        horario_inicio_real = ?,
                        horario_fim_real = ?,
                        atraso_minutos = ?,
                        observacoes = ?,
                        is_rollback = ?,
                        arquivado = 0,
                        data_atualizacao = ?
                    WHERE seq = ? AND sequencia = ? AND excel_data_id = ?
                """, (
                    activity.status or "Planejado",
                    activity.horario_inicio_real,
                    activity.horario_fim_real,
                    atraso_minutos,
                    activity.observacoes,
                    1 if activity.is_rollback else 0,
                    datetime.now().isoformat(),
                    activity.seq,
                    activity.sequencia,
                    excel_data_id
                ))
            else:
                # Inserir novo
                cursor.execute("""
                    INSERT INTO activity_control
                    (seq, sequencia, excel_data_id, status, horario_inicio_real, 
                     horario_fim_real, atraso_minutos, observacoes, is_rollback, arquivado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    activity.seq,
                    activity.sequencia,
                    excel_data_id,
                    activity.status or "Planejado",
                    activity.horario_inicio_real,
                    activity.horario_fim_real,
                    atraso_minutos,
                    activity.observacoes,
                    1 if activity.is_rollback else 0
                ))
            
            conn.commit()
            conn.close()
            
            total_time = time.time() - start_time
            logger.info(f"Registro de controle salvo: Seq {activity.seq}, CRQ {activity.sequencia}, Excel_ID: {excel_data_id}, Rollback: {activity.is_rollback}, Tempo: {total_time:.3f}s")
            
            if DEBUG_MODE:
                logger.debug(f"[CREATE] Concluido com sucesso em {total_time:.3f}s")
        except Exception as e:
            logger.error(f"Erro ao salvar activity_control: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Erro ao salvar controle: {str(e)}")
        
        return ActivityResponse(
            success=True,
            message="Atividade criada/atualizada com sucesso",
            seq=activity.seq,
            sequencia=activity.sequencia,
            updated_fields=["excel_data", "activity_control"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar atividade: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao criar atividade: {str(e)}")


@app.put("/activity")
async def update_activity(activity: ActivityUpdate):
    """
    Atualiza uma atividade
    
    Atualiza os campos fornecidos de uma atividade específica.
    Campos não fornecidos não são alterados.
    """
    try:
        # Validar sequencia
        from config import SEQUENCIAS
        if activity.sequencia not in SEQUENCIAS:
            raise HTTPException(
                status_code=400,
                detail=f"Sequência inválida: {activity.sequencia}. Valores permitidos: {list(SEQUENCIAS.keys())}"
            )
        
        # Validar status se fornecido
        if activity.status and activity.status not in STATUS_OPCOES:
            raise HTTPException(
                status_code=400,
                detail=f"Status inválido: {activity.status}. Valores permitidos: {STATUS_OPCOES}"
            )
        
        # Validar datas se fornecidas
        if activity.horario_inicio_real and not validate_datetime_string(activity.horario_inicio_real):
            raise HTTPException(
                status_code=400,
                detail=f"Formato de data inválido para horario_inicio_real: {activity.horario_inicio_real}. Use o formato {DATE_FORMAT}"
            )
        
        if activity.horario_fim_real and not validate_datetime_string(activity.horario_fim_real):
            raise HTTPException(
                status_code=400,
                detail=f"Formato de data inválido para horario_fim_real: {activity.horario_fim_real}. Use o formato {DATE_FORMAT}"
            )
        
        # Verificar se a atividade existe no excel_data (deve existir antes de poder atualizar)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        if activity.excel_data_id:
            cursor.execute("""
                SELECT COUNT(*) FROM excel_data 
                WHERE id = ? AND seq = ? AND sequencia = ?
            """, (activity.excel_data_id, activity.seq, activity.sequencia))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM excel_data 
                WHERE seq = ? AND sequencia = ?
            """, (activity.seq, activity.sequencia))
        
        exists_in_excel = cursor.fetchone()[0] > 0
        conn.close()
        
        if not exists_in_excel:
            logger.warning(f"Atividade Seq {activity.seq}, CRQ {activity.sequencia} nao existe no excel_data. "
                         f"Ela precisa ser importada primeiro via Streamlit.")
            # Continuar mesmo assim - pode criar registro de controle sem excel_data
            # Mas avisar no log
        
        # Buscar atividade existente para calcular atraso
        existing = db_manager.get_activity_control(
            activity.seq, 
            activity.sequencia, 
            activity.excel_data_id
        )
        
        # Calcular atraso se houver fim real
        atraso_minutos = None
        if activity.horario_fim_real:
            # Buscar fim planejado do excel_data
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            if activity.excel_data_id:
                cursor.execute("""
                    SELECT fim FROM excel_data 
                    WHERE id = ? AND seq = ? AND sequencia = ?
                """, (activity.excel_data_id, activity.seq, activity.sequencia))
            else:
                cursor.execute("""
                    SELECT fim FROM excel_data 
                    WHERE seq = ? AND sequencia = ?
                    LIMIT 1
                """, (activity.seq, activity.sequencia))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                fim_planejado = parse_datetime_string(result[0])
                fim_real = parse_datetime_string(activity.horario_fim_real)
                if fim_planejado and fim_real:
                    atraso_minutos = calculate_delay(fim_planejado, fim_real)
        
        # Preparar campos atualizados
        updated_fields = []
        if activity.status:
            updated_fields.append("status")
        if activity.horario_inicio_real:
            updated_fields.append("horario_inicio_real")
        if activity.horario_fim_real:
            updated_fields.append("horario_fim_real")
        if activity.observacoes is not None:
            updated_fields.append("observacoes")
        if atraso_minutos is not None:
            updated_fields.append("atraso_minutos")
        
        # Salvar no banco
        try:
            db_manager.save_activity_control(
                seq=activity.seq,
                sequencia=activity.sequencia,
                status=activity.status,
                horario_inicio_real=activity.horario_inicio_real,
                horario_fim_real=activity.horario_fim_real,
                atraso_minutos=atraso_minutos,
                observacoes=activity.observacoes,
                excel_data_id=activity.excel_data_id
            )
            
            # Verificar se foi salvo corretamente
            saved = db_manager.get_activity_control(
                activity.seq, 
                activity.sequencia, 
                activity.excel_data_id
            )
            
            if saved:
                logger.info(f"Atividade atualizada e confirmada no banco: Seq {activity.seq}, CRQ {activity.sequencia}, Campos: {updated_fields}")
            else:
                logger.warning(f"Atividade salva mas nao encontrada na verificacao: Seq {activity.seq}, CRQ {activity.sequencia}")
        except Exception as db_error:
            logger.error(f"Erro ao salvar no banco: {db_error}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {str(db_error)}")
        
        return ActivityResponse(
            success=True,
            message="Atividade atualizada com sucesso",
            seq=activity.seq,
            sequencia=activity.sequencia,
            updated_fields=updated_fields
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar atividade: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar atividade: {str(e)}")


@app.post("/activities/archive-execution")
async def archive_execution_activities(sequencia: str):
    """
    Arquivar todas as atividades de execução de uma sequência (quando rollback é ativado)
    """
    start_time = time.time()
    if DEBUG_MODE:
        logger.debug(f"[ARCHIVE] Iniciando arquivamento de execucao para {sequencia}")
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Arquivar atividades de execução (não rollback) da sequência
        cursor.execute("""
            UPDATE activity_control
            SET arquivado = 1,
                status = 'Arquivado',
                data_atualizacao = ?
            WHERE sequencia = ? AND (is_rollback = 0 OR is_rollback IS NULL) AND arquivado = 0
        """, (datetime.now().isoformat(), sequencia))
        
        archived_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        total_time = time.time() - start_time
        logger.info(f"Arquivadas {archived_count} atividades de execucao para {sequencia} em {total_time:.3f}s")
        
        if DEBUG_MODE:
            logger.debug(f"[ARCHIVE] Concluido: {archived_count} arquivadas em {total_time:.3f}s")
        
        return {
            "success": True,
            "message": f"{archived_count} atividades de execução arquivadas",
            "archived_count": archived_count,
            "sequencia": sequencia,
            "processing_time": round(total_time, 3)
        }
    except Exception as e:
        logger.error(f"Erro ao arquivar atividades: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao arquivar: {str(e)}")


@app.post("/activities/activate-rollback")
async def activate_rollback_activities(sequencia: str):
    """
    Ativar atividades de rollback de uma sequência (desarquivar e tornar ativas)
    """
    start_time = time.time()
    if DEBUG_MODE:
        logger.debug(f"[ACTIVATE ROLLBACK] Iniciando ativacao de rollback para {sequencia}")
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Ativar atividades de rollback (desarquivar e definir status como Planejado)
        cursor.execute("""
            UPDATE activity_control
            SET arquivado = 0,
                status = 'Planejado',
                data_atualizacao = ?
            WHERE sequencia = ? AND is_rollback = 1
        """, (datetime.now().isoformat(), sequencia))
        
        activated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        total_time = time.time() - start_time
        logger.info(f"Ativadas {activated_count} atividades de rollback para {sequencia} em {total_time:.3f}s")
        
        if DEBUG_MODE:
            logger.debug(f"[ACTIVATE ROLLBACK] Concluido: {activated_count} ativadas em {total_time:.3f}s")
        
        return {
            "success": True,
            "message": f"{activated_count} atividades de rollback ativadas",
            "activated_count": activated_count,
            "sequencia": sequencia,
            "processing_time": round(total_time, 3)
        }
    except Exception as e:
        logger.error(f"Erro ao ativar rollback: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao ativar rollback: {str(e)}")


@app.post("/activities/bulk-create")
async def create_activities_bulk(bulk_create: BulkActivityCreate):
    """
    Cria/atualiza múltiplas atividades em lote via POST
    
    Recebe todas as atividades do Excel e faz a carga completa no banco.
    Compara com dados existentes e cria/atualiza conforme necessário.
    """
    start_time = time.time()
    results = []
    created = 0
    updated = 0
    failed = 0
    
    logger.info(f"Recebendo carga em lote: {len(bulk_create.activities)} atividades")
    if DEBUG_MODE:
        logger.debug(f"[BULK] Iniciando processamento de {len(bulk_create.activities)} atividades")
        logger.debug(f"[BULK] Primeiras 3 atividades: {[{'seq': a.seq, 'sequencia': a.sequencia, 'rollback': a.is_rollback} for a in bulk_create.activities[:3]]}")
    
    for activity in bulk_create.activities:
        try:
            # Verificar se já existe
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM excel_data 
                WHERE seq = ? AND sequencia = ?
                LIMIT 1
            """, (activity.seq, activity.sequencia))
            
            existing = cursor.fetchone()
            
            if existing:
                # Atualizar existente
                excel_data_id = existing[0]
                cursor.execute("""
                    UPDATE excel_data
                    SET atividade = COALESCE(?, atividade),
                        grupo = COALESCE(?, grupo),
                        localidade = COALESCE(?, localidade),
                        executor = COALESCE(?, executor),
                        telefone = COALESCE(?, telefone),
                        inicio = COALESCE(?, inicio),
                        fim = COALESCE(?, fim),
                        tempo = COALESCE(?, tempo)
                    WHERE id = ?
                """, (
                    activity.atividade,
                    activity.grupo,
                    activity.localidade,
                    activity.executor,
                    activity.telefone,
                    activity.inicio,
                    activity.fim,
                    activity.tempo,
                    excel_data_id
                ))
                updated += 1
                action = "updated"
            else:
                # Criar nova
                cursor.execute("""
                    INSERT INTO excel_data
                    (sequencia, seq, atividade, grupo, localidade, executor, 
                     telefone, inicio, fim, tempo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    activity.sequencia,
                    activity.seq,
                    activity.atividade or "",
                    activity.grupo or "",
                    activity.localidade or "",
                    activity.executor or "",
                    activity.telefone or "",
                    activity.inicio,
                    activity.fim,
                    activity.tempo or ""
                ))
                excel_data_id = cursor.lastrowid
                created += 1
                action = "created"
            
            conn.commit()
            conn.close()
            
            # Criar/atualizar registro de controle
            atraso_minutos = None
            try:
                if activity.horario_fim_real and activity.fim:
                    try:
                        from datetime import datetime as dt
                        if isinstance(activity.fim, str) and 'T' in activity.fim:
                            fim_planejado = dt.fromisoformat(activity.fim.replace('Z', '+00:00'))
                        else:
                            fim_planejado = parse_datetime_string(activity.fim)
                        fim_real = parse_datetime_string(activity.horario_fim_real)
                        if fim_planejado and fim_real:
                            atraso_minutos = calculate_delay(fim_planejado, fim_real)
                    except:
                        pass
            except:
                pass
            
            # Salvar com flag de rollback usando SQL direto
            conn_control = db_manager.get_connection()
            cursor_control = conn_control.cursor()
            
            # Verificar se já existe
            cursor_control.execute("""
                SELECT id FROM activity_control 
                WHERE seq = ? AND sequencia = ? AND excel_data_id = ?
            """, (activity.seq, activity.sequencia, excel_data_id))
            
            existing_control = cursor_control.fetchone()
            
            if existing_control:
                # Atualizar
                cursor_control.execute("""
                    UPDATE activity_control
                    SET status = COALESCE(?, status),
                        horario_inicio_real = ?,
                        horario_fim_real = ?,
                        atraso_minutos = ?,
                        observacoes = ?,
                        is_rollback = ?,
                        arquivado = 0,
                        data_atualizacao = ?
                    WHERE seq = ? AND sequencia = ? AND excel_data_id = ?
                """, (
                    activity.status or "Planejado",
                    activity.horario_inicio_real,
                    activity.horario_fim_real,
                    atraso_minutos,
                    activity.observacoes,
                    1 if activity.is_rollback else 0,
                    datetime.now().isoformat(),
                    activity.seq,
                    activity.sequencia,
                    excel_data_id
                ))
            else:
                # Inserir novo
                cursor_control.execute("""
                    INSERT INTO activity_control
                    (seq, sequencia, excel_data_id, status, horario_inicio_real, 
                     horario_fim_real, atraso_minutos, observacoes, is_rollback, arquivado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    activity.seq,
                    activity.sequencia,
                    excel_data_id,
                    activity.status or "Planejado",
                    activity.horario_inicio_real,
                    activity.horario_fim_real,
                    atraso_minutos,
                    activity.observacoes,
                    1 if activity.is_rollback else 0
                ))
            
            conn_control.commit()
            conn_control.close()
            
            results.append(ActivityResponse(
                success=True,
                message=f"Atividade {action}",
                seq=activity.seq,
                sequencia=activity.sequencia,
                updated_fields=["excel_data", "activity_control"]
            ))
            
        except Exception as e:
            logger.error(f"Erro ao processar atividade Seq {activity.seq}, CRQ {activity.sequencia}: {e}")
            failed += 1
            results.append(ActivityResponse(
                success=False,
                message=f"Erro: {str(e)}",
                seq=activity.seq,
                sequencia=activity.sequencia,
                updated_fields=[]
            ))
    
    total_time = time.time() - start_time
    logger.info(f"Carga concluida: {created} criadas, {updated} atualizadas, {failed} falhas em {total_time:.3f}s")
    
    if DEBUG_MODE:
        logger.debug(f"[BULK] Tempo total: {total_time:.3f}s ({total_time/len(bulk_create.activities):.3f}s por atividade)")
        if failed > 0:
            logger.debug(f"[BULK] Falhas detalhadas:")
            for r in results:
                if not r.success:
                    logger.debug(f"  - Seq {r.seq}, CRQ {r.sequencia}: {r.message}")
    
    # Retornar resposta customizada com informações de criação/atualização
    return {
        "total": len(bulk_create.activities),
        "created": created,
        "updated": updated,
        "successful": created + updated,
        "failed": failed,
        "processing_time": round(total_time, 3),
        "results": results
    }


@app.put("/activities/bulk")
async def update_activities_bulk(bulk_update: BulkActivityUpdate):
    """
    Atualiza múltiplas atividades em lote
    
    Processa uma lista de atividades e atualiza cada uma.
    Retorna resultado detalhado de cada atualização.
    """
    results = []
    successful = 0
    failed = 0
    
    for activity in bulk_update.activities:
        try:
            # Reutilizar lógica do endpoint individual
            response = await update_activity(activity)
            results.append(response)
            successful += 1
        except HTTPException as e:
            results.append(ActivityResponse(
                success=False,
                message=f"Erro: {e.detail}",
                seq=activity.seq,
                sequencia=activity.sequencia,
                updated_fields=[]
            ))
            failed += 1
        except Exception as e:
            logger.error(f"Erro ao atualizar atividade em lote: {e}")
            results.append(ActivityResponse(
                success=False,
                message=f"Erro inesperado: {str(e)}",
                seq=activity.seq,
                sequencia=activity.sequencia,
                updated_fields=[]
            ))
            failed += 1
    
    return BulkActivityResponse(
        total=len(bulk_update.activities),
        successful=successful,
        failed=failed,
        results=results
    )


def load_excel_file_api(uploaded_file: UploadFile):
    """
    Carrega arquivo Excel e retorna dados de todas as abas (versão para API, sem Streamlit)
    
    Args:
        uploaded_file: Arquivo Excel carregado via FastAPI
        
    Returns:
        dict: Dicionário com dados de cada sequência
    """
    from config import SEQUENCIAS
    
    try:
        # Ler arquivo em memória
        contents = uploaded_file.file.read()
        excel_file = pd.ExcelFile(io.BytesIO(contents))
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
            df = pd.read_excel(io.BytesIO(contents), sheet_name=sheet_name)
            
            # Verificar se o dataframe está vazio
            if df.empty or len(df.columns) == 0:
                continue
            
            # Normalizar nomes das colunas
            df.columns = [str(col).strip() for col in df.columns]
            
            # Mapear nomes de colunas para os esperados
            expected_cols = ["Seq", "Atividade", "Grupo", "Localidade", 
                            "Executor", "Telefone", "Inicio", "Fim", "Tempo"]
            
            # Criar mapeamento flexível
            col_mapping = {}
            for i, expected in enumerate(expected_cols):
                found = False
                for j, actual_col in enumerate(df.columns):
                    if actual_col.strip().lower() == expected.lower():
                        col_mapping[expected] = j
                        found = True
                        break
                
                if not found and i < len(df.columns):
                    col_mapping[expected] = i
            
            # Verificar se temos pelo menos as colunas essenciais
            if len(col_mapping) < 5:
                logger.warning(f"Estrutura da aba {sheet_name} pode estar incorreta. Colunas encontradas: {list(df.columns[:9])}")
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
            
            # Limpar dados
            df["Seq"] = df["Seq"].astype(str)
            df["Atividade"] = df["Atividade"].astype(str)
            
            mask_valid = (
                (df["Seq"].notna() & (df["Seq"].str.strip() != "") & (df["Seq"].str.strip() != "nan")) |
                (df["Atividade"].notna() & (df["Atividade"].str.strip() != "") & (df["Atividade"].str.strip() != "nan"))
            )
            df = df[mask_valid].copy()
            
            # Converter tipos
            try:
                df["Seq"] = pd.to_numeric(df["Seq"], errors='coerce').astype('Int64')
            except Exception as e:
                logger.warning(f"Erro ao converter Seq na aba {sheet_name}: {str(e)}")
            
            # Converter datas
            for col in ["Inicio", "Fim"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Converter colunas de texto para string
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
                df["Tempo"] = pd.to_numeric(df["Tempo"], errors='coerce').fillna(0)
            
            # Adicionar CRQ ao dataframe
            df["CRQ"] = sequencia
            
            dados[sequencia] = {
                "dataframe": df,
                "sheet_name": sheet_name
            }
        
        return dados
    
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo Excel: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivo Excel: {str(e)}")


@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Endpoint para upload de arquivo Excel e processamento automático
    
    Recebe um arquivo Excel, processa usando a mesma lógica do Streamlit,
    salva no banco de dados e cria/atualiza registros de controle.
    
    Returns:
        dict: Estatísticas do processamento
    """
    try:
        # Verificar se é arquivo Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Arquivo deve ser Excel (.xlsx ou .xls)")
        
        logger.info(f"Recebendo upload de arquivo Excel: {file.filename}")
        
        # Carregar dados do Excel
        excel_data = load_excel_file_api(file)
        
        if not excel_data:
            raise HTTPException(status_code=400, detail="Nenhum dado válido encontrado no arquivo Excel")
        
        # Contar total de registros
        total_rows = sum(len(data["dataframe"]) for data in excel_data.values())
        
        # Salvar dados do Excel no banco
        db_manager = DatabaseManager()
        total_saved = db_manager.save_excel_data(excel_data, file.filename)
        
        if total_saved == 0:
            raise HTTPException(status_code=400, detail="Nenhum registro foi salvo no banco. Verifique os dados do Excel.")
        
        # Criar registros de controle para atividades que não existem
        control_data = db_manager.get_all_activities_control()
        control_created = 0
        
        for sequencia, data in excel_data.items():
            df = data["dataframe"]
            for _, row in df.iterrows():
                seq = int(row["Seq"]) if pd.notna(row["Seq"]) else None
                if seq is None:
                    continue
                
                excel_data_id = row.get("Excel_Data_ID", 0) if "Excel_Data_ID" in row else 0
                if pd.isna(excel_data_id):
                    excel_data_id = 0
                else:
                    excel_data_id = int(excel_data_id)
                
                # Buscar usando excel_data_id se disponível
                if excel_data_id and excel_data_id > 0:
                    existing = db_manager.get_activity_control(seq, sequencia, excel_data_id)
                else:
                    existing = db_manager.get_activity_control(seq, sequencia)
                
                if not existing:
                    # Obter valor de Is_Milestone do dataframe
                    is_milestone = row.get("Is_Milestone", False) if "Is_Milestone" in row else False
                    # Se Grupo está vazio, é milestone
                    if "Grupo" in row:
                        grupo_value = row.get("Grupo")
                        is_empty = (
                            pd.isna(grupo_value) or 
                            grupo_value == "" or 
                            (isinstance(grupo_value, str) and grupo_value.strip() == "") or
                            str(grupo_value).strip() == "nan"
                        )
                        if is_empty:
                            is_milestone = True
                    
                    db_manager.save_activity_control(
                        seq=seq,
                        sequencia=sequencia,
                        status="Planejado",
                        is_milestone=is_milestone,
                        excel_data_id=excel_data_id if excel_data_id > 0 else None
                    )
                    control_created += 1
        
        # Estatísticas
        sequencias_processed = list(excel_data.keys())
        
        result = {
            "success": True,
            "message": f"Arquivo processado com sucesso",
            "filename": file.filename,
            "total_rows": total_rows,
            "total_saved": total_saved,
            "control_created": control_created,
            "sequencias": sequencias_processed,
            "sequencias_count": len(sequencias_processed)
        }
        
        logger.info(f"Upload concluído: {total_saved} registros salvos, {control_created} controles criados")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar arquivo: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    if DEBUG_MODE:
        logger.info("=" * 60)
        logger.info("INICIANDO SERVIDOR API EM MODO DEBUG")
        logger.info("Porta: 8000")
        logger.info("Todas as requisicoes serao logadas em detalhes")
        logger.info("=" * 60)
    else:
        logger.info("Iniciando servidor API na porta 8000...")
        logger.info("Para ativar modo debug, defina: $env:API_DEBUG='true'")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug" if DEBUG_MODE else "info")
