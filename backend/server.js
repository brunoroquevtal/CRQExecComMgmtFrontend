/**
 * Servidor Express para API REST
 */
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const DatabaseManager = require('./database');
const { SEQUENCIAS, DATE_FORMAT } = require('./config');

const app = express();
const PORT = process.env.PORT || 3000;

// Criar diretório de uploads se não existir
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rotas de autenticação
const authRoutes = require('./routes/auth');
app.use('/api/auth', authRoutes);

// Middleware de autenticação
const { requireAuth, requireRole, optionalAuth } = require('./middleware/auth');

// Configurar multer para upload de arquivos
const upload = multer({ 
  dest: uploadsDir,
  limits: { fileSize: 50 * 1024 * 1024 } // 50MB
});

// Inicializar banco de dados
const dbManager = new DatabaseManager();

// Middleware de logging (debug mode)
const DEBUG_MODE = process.env.API_DEBUG === 'true';
if (DEBUG_MODE) {
  app.use((req, res, next) => {
    console.log('='.repeat(60));
    console.log(`[REQUISICAO] ${req.method} ${req.path}`);
    console.log(`Query:`, req.query);
    console.log(`Body:`, req.body);
    const start = Date.now();
    res.on('finish', () => {
      const duration = Date.now() - start;
      console.log(`[RESPOSTA] Status: ${res.statusCode}, Tempo: ${duration}ms`);
      console.log('='.repeat(60));
    });
    next();
  });
}

// ==================== ROTAS ====================

// Health check
app.get('/health', (req, res) => {
  try {
    // Testar conexão com banco
    dbManager.getConnection();
    res.json({
      status: 'healthy',
      database: 'connected',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      database: 'disconnected',
      error: error.message
    });
  }
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'API de Gerenciamento de Janela de Mudança TI',
    version: '2.0.0',
    endpoints: {
      health: '/health',
      upload: '/api/upload-excel',
      activities: '/api/activities',
      activity: '/api/activity/:sequencia/:seq',
      statistics: '/api/statistics',
      message: '/api/message'
    }
  });
});

// Upload de arquivo Excel (apenas líderes e administradores)
app.post('/api/upload-excel', requireAuth, requireRole('lider_mudanca', 'administrador'), upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Nenhum arquivo enviado' });
    }

    if (!req.file.originalname.match(/\.(xlsx|xls)$/i)) {
      fs.unlinkSync(req.file.path); // Remover arquivo
      return res.status(400).json({ error: 'Arquivo deve ser Excel (.xlsx ou .xls)' });
    }

    const XLSX = require('xlsx');
    const workbook = XLSX.readFile(req.file.path);
    const dataDict = {};

    // Processar cada aba
    for (const sheetName of workbook.SheetNames) {
      let sequencia = null;

      // Identificar sequência
      for (const [key, info] of Object.entries(SEQUENCIAS)) {
        if (sheetName.toUpperCase().includes(key)) {
          sequencia = key;
          break;
        }
      }

      if (!sequencia) {
        continue; // Pular abas não reconhecidas
      }

      // Ler dados da aba
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json(worksheet);

      // Log das colunas identificadas para debug (primeira linha)
      if (jsonData.length > 0) {
        const firstRow = jsonData[0];
        const columns = Object.keys(firstRow);
        console.log(`[DEBUG] Colunas identificadas na aba ${sheetName}:`, columns);
      }

      // Processar e normalizar dados (sem dados sensíveis: Executor, Telefone, Localidade)
      // Filtrar apenas linhas com Seq válido E Atividade não vazia E (Inicio OU Fim)
      const processedData = jsonData
        .filter(row => {
          const hasSeq = row.Seq && !isNaN(parseInt(row.Seq));
          const hasAtividade = row.Atividade && String(row.Atividade).trim() !== '';
          const hasInicio = row.Inicio && row.Inicio !== '';
          const hasFim = row.Fim && row.Fim !== '';
          // Exigir: Seq válido, Atividade não vazia, e pelo menos Inicio ou Fim
          return hasSeq && hasAtividade && (hasInicio || hasFim);
        })
        .map(row => {
          // Normalizar nomes de colunas (case-insensitive e tolerante a espaços)
          const getValue = (possibleNames) => {
            for (const name of possibleNames) {
              const keys = Object.keys(row);
              const found = keys.find(k => k.toLowerCase().trim() === name.toLowerCase().trim());
              if (found !== undefined) {
                return row[found];
              }
            }
            return undefined;
          };

          // Extrair valores com nomes alternativos
          const seq = getValue(['Seq', 'seq', 'SEQ', 'Sequência', 'sequencia']);
          const atividade = getValue(['Atividade', 'atividade', 'ATIVIDADE']);
          const grupo = getValue(['Grupo', 'grupo', 'GRUPO']);
          const inicio = getValue(['Inicio', 'inicio', 'INICIO', 'Início', 'início', 'INÍCIO']);
          const fim = getValue(['Fim', 'fim', 'FIM']);
          let tempo = getValue(['Tempo', 'tempo', 'TEMPO']);
          
          // Converter tempo de hh:mm para minutos se necessário
          if (tempo !== undefined && tempo !== null && tempo !== '') {
            try {
              // Se já é um número, assumir que já está em minutos
              if (typeof tempo === 'number') {
                tempo = tempo;
              } else {
                const tempoStr = String(tempo).trim();
                // Tentar converter diretamente para número
                if (!isNaN(tempoStr) && tempoStr !== '') {
                  tempo = parseFloat(tempoStr);
                } else if (tempoStr.includes(':')) {
                  // Formato hh:mm ou hh:mm:ss
                  const parts = tempoStr.split(':');
                  if (parts.length === 3) {
                    // hh:mm:ss
                    const hours = parseInt(parts[0]) || 0;
                    const minutes = parseInt(parts[1]) || 0;
                    const seconds = parseInt(parts[2]) || 0;
                    tempo = hours * 60 + minutes + seconds / 60;
                  } else if (parts.length === 2) {
                    // hh:mm
                    const hours = parseInt(parts[0]) || 0;
                    const minutes = parseInt(parts[1]) || 0;
                    tempo = hours * 60 + minutes;
                  } else {
                    tempo = 0;
                  }
                } else {
                  tempo = 0;
                }
              }
            } catch (e) {
              console.warn('Erro ao converter tempo:', tempo, e);
              tempo = 0;
            }
          } else {
            tempo = 0;
          }

          // Validar que Inicio e Fim não são strings de status
          let inicioDate = null;
          let fimDate = null;

          if (inicio) {
            try {
              // Tentar converter para data
              const date = new Date(inicio);
              // Verificar se é uma data válida e não é um status comum
              const inicioStr = String(inicio).toLowerCase().trim();
              const statusKeywords = ['concluído', 'concluido', 'em execução', 'em execucao', 'planejado', 'atrasado', 'adiantado'];
              if (!isNaN(date.getTime()) && !statusKeywords.some(kw => inicioStr.includes(kw))) {
                inicioDate = date;
              } else {
                console.warn(`[DEBUG] Valor de Inicio parece ser status em vez de data: ${inicio}`);
              }
            } catch (e) {
              console.warn(`[DEBUG] Erro ao converter Inicio para data: ${inicio}`, e);
            }
          }

          if (fim) {
            try {
              const date = new Date(fim);
              const fimStr = String(fim).toLowerCase().trim();
              const statusKeywords = ['concluído', 'concluido', 'em execução', 'em execucao', 'planejado', 'atrasado', 'adiantado'];
              if (!isNaN(date.getTime()) && !statusKeywords.some(kw => fimStr.includes(kw))) {
                fimDate = date;
              } else {
                console.warn(`[DEBUG] Valor de Fim parece ser status em vez de data: ${fim}`);
              }
            } catch (e) {
              console.warn(`[DEBUG] Erro ao converter Fim para data: ${fim}`, e);
            }
          }

          return {
            Seq: seq ? parseInt(seq) : null,
            Atividade: atividade ? String(atividade).trim() : '',
            Grupo: grupo ? String(grupo).trim() : '',
            Inicio: inicioDate,
            Fim: fimDate,
            Tempo: tempo ? parseFloat(tempo) : 0
          };
        })
        .filter(row => row.Atividade !== ''); // Garantir que atividade não está vazia após trim

      if (processedData.length > 0) {
        dataDict[sequencia] = {
          dataframe: processedData,
          sheet_name: sheetName
        };
      }
    }

    // Remover arquivo temporário
    fs.unlinkSync(req.file.path);

    if (Object.keys(dataDict).length === 0) {
      return res.status(400).json({ error: 'Nenhum dado válido encontrado no arquivo Excel' });
    }

    // Salvar no banco
    const totalSaved = await dbManager.saveExcelData(dataDict, req.file.originalname);

    // Criar registros de controle
    let controlCreated = 0;
    for (const [sequencia, data] of Object.entries(dataDict)) {
      for (const row of data.dataframe) {
        if (!row.Seq) continue;

        const existing = await dbManager.getActivityControl(row.Seq, sequencia);
        if (!existing) {
          const isMilestone = !row.Grupo || row.Grupo.trim() === '';
          try {
            await dbManager.saveActivityControl({
              seq: row.Seq,
              sequencia: sequencia,
              status: 'Planejado',
              is_milestone: isMilestone
            });
            controlCreated++;
          } catch (error) {
            console.error(`Erro ao criar controle para Seq ${row.Seq}, CRQ ${sequencia}:`, error);
          }
        }
      }
    }

    res.json({
      success: true,
      message: 'Arquivo processado com sucesso',
      filename: req.file.originalname,
      total_rows: Object.values(dataDict).reduce((sum, data) => sum + data.dataframe.length, 0),
      total_saved: totalSaved,
      control_created: controlCreated,
      sequencias: Object.keys(dataDict),
      sequencias_count: Object.keys(dataDict).length
    });

  } catch (error) {
    console.error('Erro ao processar upload:', error);
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    res.status(500).json({ error: `Erro ao processar arquivo: ${error.message}` });
  }
});

// Obter todas as atividades (todos os usuários autenticados podem ver)
app.get('/api/activities', requireAuth, async (req, res) => {
  try {
    const excelData = await dbManager.loadExcelData();
    const controlData = await dbManager.getAllActivitiesControl();
    const rollbackStates = await dbManager.getAllRollbackStates();
    const { calculateActivityStatus } = require('./status_calculator');

    if (!excelData) {
      return res.json({ activities: [] });
    }

    // Mesclar dados
    const activities = [];
    for (const [sequencia, data] of Object.entries(excelData)) {
      const rollbackState = rollbackStates[sequencia] || { rollback_active: false };
      const isRollbackActive = rollbackState.rollback_active;

      // Encontrar a última atividade (encerramento) - maior seq
      let maxSeq = 0;
      for (const row of data.dataframe) {
        if (row.seq && row.seq > maxSeq) {
          maxSeq = row.seq;
        }
      }

      for (const row of data.dataframe) {
        const isEncerramento = row.seq === maxSeq;
        const isRollback = row.is_rollback === 1;

        // Filtrar atividades baseado no estado de rollback
        // Se rollback está ativo: mostrar apenas rollback + encerramento
        // Se rollback não está ativo: mostrar apenas principais + encerramento
        if (isEncerramento) {
          // Sempre mostrar encerramento
        } else if (isRollbackActive && !isRollback) {
          // Rollback ativo: suprimir principais
          continue;
        } else if (!isRollbackActive && isRollback) {
          // Rollback inativo: suprimir rollback
          continue;
        }

        const key = `${row.seq}_${sequencia}`;
        const control = controlData[key] || {};

        // Calcular status usando a nova função
        const calculatedStatus = calculateActivityStatus(
          { seq: row.seq, sequencia, inicio: row.inicio, fim: row.fim },
          control
        );

        // Garantir que inicio e fim estão em formato ISO string para o frontend
        let inicioISO = null;
        let fimISO = null;
        
        if (row.inicio) {
          try {
            // Se já é string ISO, usar diretamente
            if (typeof row.inicio === 'string' && row.inicio.includes('T')) {
              inicioISO = row.inicio;
            } else {
              // Tentar converter para Date e depois para ISO
              const date = new Date(row.inicio);
              if (!isNaN(date.getTime())) {
                inicioISO = date.toISOString();
              }
            }
          } catch (e) {
            console.warn('Erro ao converter inicio para ISO:', row.inicio, e);
          }
        }
        
        if (row.fim) {
          try {
            // Se já é string ISO, usar diretamente
            if (typeof row.fim === 'string' && row.fim.includes('T')) {
              fimISO = row.fim;
            } else {
              // Tentar converter para Date e depois para ISO
              const date = new Date(row.fim);
              if (!isNaN(date.getTime())) {
                fimISO = date.toISOString();
              }
            }
          } catch (e) {
            console.warn('Erro ao converter fim para ISO:', row.fim, e);
          }
        }

        activities.push({
          seq: row.seq,
          sequencia: sequencia,
          atividade: row.atividade,
          grupo: row.grupo,
          status: calculatedStatus, // Usar status calculado
          inicio: inicioISO,
          fim: fimISO,
          tempo: row.tempo || 0,
          horario_inicio_real: control.horario_inicio_real,
          horario_fim_real: control.horario_fim_real,
          atraso_minutos: control.atraso_minutos || 0,
          observacoes: control.observacoes || '',
          is_milestone: control.is_milestone || false,
          is_rollback: isRollback,
          is_encerramento: isEncerramento,
          excel_data_id: row.id || null
        });
      }
    }

    res.json({ activities });
  } catch (error) {
    console.error('Erro ao buscar atividades:', error);
    res.status(500).json({ error: error.message });
  }
});

// Obter uma atividade específica (todos os usuários autenticados podem ver)
app.get('/api/activity/:sequencia/:seq', requireAuth, async (req, res) => {
  try {
    const { sequencia, seq } = req.params;
    const activity = await dbManager.getActivityControl(parseInt(seq), sequencia);

    if (!activity) {
      return res.status(404).json({ error: 'Atividade não encontrada' });
    }

    res.json({ activity });
  } catch (error) {
    console.error('Erro ao buscar atividade:', error);
    res.status(500).json({ error: error.message });
  }
});

// Atualizar uma atividade (apenas líderes e administradores)
app.put('/api/activity', requireAuth, requireRole('lider_mudanca', 'administrador'), async (req, res) => {
  try {
    const { seq, sequencia, excel_data_id, tempo, grupo, atividade, inicio, fim, is_rollback, is_encerramento, ultima_sincronizacao, ...updates } = req.body;

    if (!seq || !sequencia) {
      return res.status(400).json({ error: 'seq e sequencia são obrigatórios' });
    }

    // Validar campos obrigatórios se estiver criando nova atividade
    // Se atividade está sendo atualizada, verificar se os campos obrigatórios existem no banco
    if (atividade !== undefined && (!atividade || atividade.trim() === '')) {
      return res.status(400).json({ error: 'atividade (descrição) é obrigatória e não pode estar vazia' });
    }

    // Se está criando nova atividade em excel_data, validar início ou fim
    if (!excel_data_id && (inicio === undefined && fim === undefined)) {
      // Verificar se já existe no banco
      const existingExcelData = await dbManager.getExcelDataBySeq(parseInt(seq), sequencia);
      if (!existingExcelData) {
        // Nova atividade: deve ter início ou fim
        if (!inicio && !fim) {
          return res.status(400).json({ error: 'Nova atividade deve ter início ou fim planejado' });
        }
      }
    }

    // Buscar excel_data_id se não foi fornecido
    let finalExcelDataId = excel_data_id;
    if (!finalExcelDataId) {
      const excelData = await dbManager.getExcelDataBySeq(parseInt(seq), sequencia);
      if (excelData) {
        finalExcelDataId = excelData.id;
      }
    }

    // Verificar se houve mudanças nos dados do excel_data
    let hasChanges = false;
    if (finalExcelDataId) {
      const existing = await dbManager.getExcelDataById(finalExcelDataId);
      if (existing) {
        // Comparar valores para detectar mudanças
        if ((tempo !== undefined && existing.tempo !== tempo) ||
            (grupo !== undefined && existing.grupo !== grupo) ||
            (atividade !== undefined && existing.atividade !== atividade) ||
            (inicio !== undefined && existing.inicio !== inicio) ||
            (fim !== undefined && existing.fim !== fim) ||
            (is_rollback !== undefined && existing.is_rollback !== (is_rollback ? 1 : 0)) ||
            (is_encerramento !== undefined && existing.is_encerramento !== (is_encerramento ? 1 : 0))) {
          hasChanges = true;
        }
      }
    }

    // Atualizar excel_data se tempo, grupo, atividade, inicio, fim, is_rollback ou is_encerramento foram fornecidos
    if (finalExcelDataId && (tempo !== undefined || grupo !== undefined || atividade !== undefined || inicio !== undefined || fim !== undefined || is_rollback !== undefined || is_encerramento !== undefined || ultima_sincronizacao !== undefined)) {
      const excelUpdates = {};
      if (tempo !== undefined) excelUpdates.tempo = tempo;
      if (grupo !== undefined) excelUpdates.grupo = grupo;
      if (atividade !== undefined) excelUpdates.atividade = atividade;
      if (inicio !== undefined) excelUpdates.inicio = inicio;
      if (fim !== undefined) excelUpdates.fim = fim;
      if (is_rollback !== undefined) excelUpdates.is_rollback = is_rollback ? 1 : 0;
      if (is_encerramento !== undefined) excelUpdates.is_encerramento = is_encerramento ? 1 : 0;
      if (ultima_sincronizacao !== undefined) excelUpdates.ultima_sincronizacao = ultima_sincronizacao;
      
      if (Object.keys(excelUpdates).length > 0) {
        await dbManager.updateExcelData(finalExcelDataId, excelUpdates);
      }
    } else if (!finalExcelDataId && (tempo !== undefined || grupo !== undefined || atividade !== undefined || inicio !== undefined || fim !== undefined || is_rollback !== undefined || is_encerramento !== undefined)) {
      // Criar excel_data se não existe mas tem dados para salvar
      finalExcelDataId = await dbManager.createExcelData({
        seq: parseInt(seq),
        sequencia: sequencia,
        atividade: atividade || '',
        grupo: grupo || '',
        tempo: tempo || 0,
        inicio: inicio || null,
        fim: fim || null,
        is_rollback: is_rollback || false,
        is_encerramento: is_encerramento || false,
        file_name: 'sync',
        ultima_sincronizacao: ultima_sincronizacao || null
      });
      hasChanges = true; // Nova atividade sempre é considerada mudança
    }

    // Remover campos que não pertencem a activity_control do objeto updates
    const { atividade: _, grupo: __, tempo: ___, inicio: ____, fim: _____, is_rollback: ______, is_encerramento: _______, ...activityControlUpdates } = updates;

    // Verificar se a atividade existe
    const existing = await dbManager.getActivityControl(
      parseInt(seq),
      sequencia,
      finalExcelDataId || null
    );

    // Se não existe, criar
    if (!existing) {
      await dbManager.saveActivityControl({
        seq: parseInt(seq),
        sequencia: sequencia,
        excel_data_id: finalExcelDataId || null,
        status: activityControlUpdates.status || 'Planejado',
        horario_inicio_real: activityControlUpdates.horario_inicio_real || null,
        horario_fim_real: activityControlUpdates.horario_fim_real || null,
        observacoes: activityControlUpdates.observacoes || '',
        is_milestone: activityControlUpdates.is_milestone || false,
        ...activityControlUpdates
      });
      
      return res.json({
        success: true,
        message: 'Atividade criada e atualizada com sucesso',
        created: true,
        updated_fields: Object.keys(activityControlUpdates),
        excel_data_id: finalExcelDataId
      });
    }

    // Detectar mudança de status e atualizar tempos reais automaticamente
    const { calculateActivityStatus } = require('./status_calculator');
    
    // Buscar dados completos da atividade para calcular status anterior
    const excelData = finalExcelDataId ? await dbManager.getExcelDataById(finalExcelDataId) : await dbManager.getExcelDataBySeq(parseInt(seq), sequencia);
    const activityForStatus = {
      seq: parseInt(seq),
      sequencia: sequencia,
      inicio: excelData?.inicio || inicio,
      fim: excelData?.fim || fim
    };
    
    // Calcular status anterior (antes da atualização)
    const previousStatus = calculateActivityStatus(activityForStatus, existing);
    
    // Preparar dados para calcular novo status
    // Se status foi fornecido no update, pode indicar mudança (mas vamos calcular baseado nos tempos reais)
    const newControlData = {
      ...existing,
      ...activityControlUpdates,
      // Se horario_inicio_real ou horario_fim_real foram fornecidos, usar os novos valores
      horario_inicio_real: activityControlUpdates.horario_inicio_real !== undefined 
        ? activityControlUpdates.horario_inicio_real 
        : existing.horario_inicio_real,
      horario_fim_real: activityControlUpdates.horario_fim_real !== undefined 
        ? activityControlUpdates.horario_fim_real 
        : existing.horario_fim_real,
      is_milestone: activityControlUpdates.is_milestone !== undefined 
        ? (typeof activityControlUpdates.is_milestone === 'boolean' 
            ? activityControlUpdates.is_milestone 
            : activityControlUpdates.is_milestone === 'true' || activityControlUpdates.is_milestone === true || activityControlUpdates.is_milestone === 1)
        : existing.is_milestone
    };
    
    // Calcular novo status baseado nos tempos reais
    const newStatus = calculateActivityStatus(activityForStatus, newControlData);
    
    // Verificar mudança de status e atualizar tempos reais
    const now = new Date().toISOString();
    const statusChanged = previousStatus !== newStatus;
    
    // Verificar também se o status foi fornecido no update (pode vir do Excel)
    const statusFromUpdate = activityControlUpdates.status;
    const statusFromUpdateLower = statusFromUpdate ? String(statusFromUpdate).toLowerCase() : '';
    
    // Detectar mudança de status (por cálculo ou por status fornecido)
    let detectedStatusChange = statusChanged;
    let detectedNewStatus = newStatus;
    
    // Se status foi fornecido e indica mudança, usar ele
    if (statusFromUpdate) {
      // Normalizar status do Excel para comparar
      const normalizedStatus = statusFromUpdateLower.includes('concluído') || statusFromUpdateLower.includes('concluido') 
        ? 'Concluído'
        : statusFromUpdateLower.includes('em execução') || statusFromUpdateLower.includes('em execucao')
        ? (statusFromUpdateLower.includes('fora') ? 'Em execução fora do prazo' : 'Em execução no prazo')
        : statusFromUpdateLower.includes('a iniciar')
        ? (statusFromUpdateLower.includes('fora') ? 'A Iniciar fora do prazo' : 'A Iniciar no prazo')
        : null;
      
      if (normalizedStatus && normalizedStatus !== previousStatus) {
        detectedStatusChange = true;
        detectedNewStatus = normalizedStatus;
      }
    }
    
    if (detectedStatusChange) {
      // Se mudou de "A iniciar" para "Em execução"
      const wasAIniciar = previousStatus === 'A Iniciar no prazo' || previousStatus === 'A Iniciar fora do prazo';
      const isEmExecucao = detectedNewStatus === 'Em execução no prazo' || detectedNewStatus === 'Em execução fora do prazo' ||
                          statusFromUpdateLower.includes('em execução') || statusFromUpdateLower.includes('em execucao');
      
      if (wasAIniciar && isEmExecucao) {
        // Atualizar horario_inicio_real se ainda não foi definido
        if (!newControlData.horario_inicio_real) {
          activityControlUpdates.horario_inicio_real = now;
          // Atualizar newControlData para refletir a mudança
          newControlData.horario_inicio_real = now;
          console.log(`[AUTO] Atividade Seq ${seq}, CRQ ${sequencia}: Início real atualizado automaticamente (mudança de status: ${previousStatus} -> ${detectedNewStatus})`);
        }
      }
      
      // Se mudou para "Concluído"
      const isConcluido = detectedNewStatus === 'Concluído' || 
                         statusFromUpdateLower.includes('concluído') || 
                         statusFromUpdateLower.includes('concluido');
      
      if (isConcluido && previousStatus !== 'Concluído') {
        // Atualizar horario_fim_real se ainda não foi definido
        if (!newControlData.horario_fim_real) {
          activityControlUpdates.horario_fim_real = now;
          // Atualizar newControlData para refletir a mudança
          newControlData.horario_fim_real = now;
          console.log(`[AUTO] Atividade Seq ${seq}, CRQ ${sequencia}: Fim real atualizado automaticamente (mudança de status: ${previousStatus} -> ${detectedNewStatus})`);
          
          // Calcular atraso quando fim real é atualizado
          if (excelData?.fim) {
            try {
              const fimPlanejado = new Date(excelData.fim);
              const fimReal = new Date(now);
              if (!isNaN(fimPlanejado.getTime()) && !isNaN(fimReal.getTime())) {
                const atrasoMs = fimReal.getTime() - fimPlanejado.getTime();
                const atrasoMinutos = Math.round(atrasoMs / (1000 * 60));
                activityControlUpdates.atraso_minutos = atrasoMinutos;
                console.log(`[AUTO] Atividade Seq ${seq}, CRQ ${sequencia}: Atraso calculado: ${atrasoMinutos} minutos`);
              }
            } catch (e) {
              console.warn(`[AUTO] Erro ao calcular atraso para Seq ${seq}, CRQ ${sequencia}:`, e);
            }
          }
        }
      }
    }
    
    // Recalcular atraso se horario_fim_real foi atualizado (manual ou automático)
    if (activityControlUpdates.horario_fim_real && excelData?.fim && activityControlUpdates.atraso_minutos === undefined) {
      try {
        const fimPlanejado = new Date(excelData.fim);
        const fimReal = new Date(activityControlUpdates.horario_fim_real);
        if (!isNaN(fimPlanejado.getTime()) && !isNaN(fimReal.getTime())) {
          const atrasoMs = fimReal.getTime() - fimPlanejado.getTime();
          const atrasoMinutos = Math.round(atrasoMs / (1000 * 60));
          activityControlUpdates.atraso_minutos = atrasoMinutos;
        }
      } catch (e) {
        console.warn(`[AUTO] Erro ao recalcular atraso para Seq ${seq}, CRQ ${sequencia}:`, e);
      }
    }
    
    // Se existe, atualizar
    const updated = await dbManager.updateActivityControl(
      parseInt(seq),
      sequencia,
      finalExcelDataId || null,
      activityControlUpdates
    );

    if (updated || hasChanges) {
      res.json({
        success: true,
        message: hasChanges ? 'Atividade atualizada com sucesso' : 'Atividade atualizada com sucesso',
        updated: updated || hasChanges,
        updated_fields: Object.keys(activityControlUpdates)
      });
    } else {
      // Se não atualizou mas existe, pode ser que não houve mudanças
      res.json({
        success: true,
        message: 'Atividade já está atualizada',
        updated: false,
        updated_fields: []
      });
    }
  } catch (error) {
    console.error('Erro ao atualizar atividade:', error);
    res.status(500).json({ error: error.message });
  }
});

// Obter estatísticas (todos os usuários autenticados podem ver)
app.get('/api/statistics', requireAuth, async (req, res) => {
  try {
    const excelData = await dbManager.loadExcelData();
    const controlData = await dbManager.getAllActivitiesControl();
    const { calculateActivityStatus } = require('./status_calculator');

    if (!excelData) {
      return res.json({
        geral: {
          total: 0,
          concluidas: 0,
          em_execucao_no_prazo: 0,
          em_execucao_fora_prazo: 0,
          a_iniciar_no_prazo: 0,
          a_iniciar_fora_prazo: 0
        },
        por_sequencia: {}
      });
    }

    // Calcular estatísticas usando os novos status
    const stats = {
      geral: {
        total: 0,
        concluidas: 0,
        em_execucao_no_prazo: 0,
        em_execucao_fora_prazo: 0,
        a_iniciar_no_prazo: 0,
        a_iniciar_fora_prazo: 0
      },
      por_sequencia: {}
    };

    for (const [sequencia, data] of Object.entries(excelData)) {
      const seqStats = {
        total: 0,
        concluidas: 0,
        em_execucao_no_prazo: 0,
        em_execucao_fora_prazo: 0,
        a_iniciar_no_prazo: 0,
        a_iniciar_fora_prazo: 0
      };

      for (const row of data.dataframe) {
        const key = `${row.seq}_${sequencia}`;
        const control = controlData[key] || {};
        
        // Calcular status usando a função de cálculo
        const calculatedStatus = calculateActivityStatus(
          { seq: row.seq, sequencia, inicio: row.inicio, fim: row.fim },
          control
        );

        // Ignorar milestones (N/A)
        if (calculatedStatus === 'N/A' || control.is_milestone) {
          continue;
        }

        stats.geral.total++;
        seqStats.total++;

        const statusLower = calculatedStatus.toLowerCase();

        if (statusLower.includes('concluído') || statusLower.includes('concluido')) {
          stats.geral.concluidas++;
          seqStats.concluidas++;
        } else if (statusLower.includes('em execução no prazo') || statusLower.includes('em execucao no prazo')) {
          stats.geral.em_execucao_no_prazo++;
          seqStats.em_execucao_no_prazo++;
        } else if (statusLower.includes('em execução fora do prazo') || statusLower.includes('em execucao fora do prazo')) {
          stats.geral.em_execucao_fora_prazo++;
          seqStats.em_execucao_fora_prazo++;
        } else if (statusLower.includes('a iniciar no prazo')) {
          stats.geral.a_iniciar_no_prazo++;
          seqStats.a_iniciar_no_prazo++;
        } else if (statusLower.includes('a iniciar fora do prazo')) {
          stats.geral.a_iniciar_fora_prazo++;
          seqStats.a_iniciar_fora_prazo++;
        }
      }

      stats.por_sequencia[sequencia] = seqStats;
    }

    res.json(stats);
  } catch (error) {
    console.error('Erro ao calcular estatísticas:', error);
    res.status(500).json({ error: error.message });
  }
});

// Criar nova atividade
app.post('/api/activity', async (req, res) => {
  try {
    const { seq, sequencia, atividade, grupo, inicio, fim, tempo, status, 
            horario_inicio_real, horario_fim_real, observacoes, is_milestone } = req.body;

    if (!seq || !sequencia || !atividade) {
      return res.status(400).json({ 
        error: 'seq, sequencia e atividade são obrigatórios' 
      });
    }

    // Verificar se já existe
    const existing = await dbManager.query(
      'SELECT id FROM excel_data WHERE seq = ? AND sequencia = ?', 
      [parseInt(seq), sequencia]
    );

    if (existing && existing.length > 0) {
      return res.status(400).json({ 
        error: 'Atividade com este seq e sequencia já existe' 
      });
    }

    // Criar em excel_data
    const excelDataId = await dbManager.createExcelData({
      seq: parseInt(seq),
      sequencia,
      atividade: atividade.trim(),
      grupo: grupo ? grupo.trim() : '',
      inicio: inicio || null,
      fim: fim || null,
      tempo: tempo || 0,
      file_name: 'manual'
    });

    // Criar em activity_control
    await dbManager.saveActivityControl({
      seq: parseInt(seq),
      sequencia,
      excel_data_id: excelDataId,
      status: status || 'Planejado',
      horario_inicio_real: horario_inicio_real || null,
      horario_fim_real: horario_fim_real || null,
      observacoes: observacoes || '',
      is_milestone: is_milestone || false
    });

    res.json({
      success: true,
      message: 'Atividade criada com sucesso',
      excel_data_id: excelDataId
    });
  } catch (error) {
    console.error('Erro ao criar atividade:', error);
    res.status(500).json({ error: error.message });
  }
});

// Deletar atividade (apenas líderes e administradores)
app.delete('/api/activity', requireAuth, requireRole('lider_mudanca', 'administrador'), async (req, res) => {
  try {
    const { seq, sequencia, excel_data_id } = req.body;

    if (!seq || !sequencia) {
      return res.status(400).json({ 
        error: 'seq e sequencia são obrigatórios' 
      });
    }

    // Deletar de activity_control
    const controlDeleted = await dbManager.deleteActivityControl(
      parseInt(seq),
      sequencia,
      excel_data_id || null
    );

    // Deletar de excel_data se excel_data_id foi fornecido
    let excelDeleted = false;
    if (excel_data_id) {
      excelDeleted = await dbManager.deleteExcelData(excel_data_id);
    }

    res.json({
      success: true,
      message: 'Atividade excluída com sucesso',
      control_deleted: controlDeleted,
      excel_deleted: excelDeleted
    });
  } catch (error) {
    console.error('Erro ao excluir atividade:', error);
    res.status(500).json({ error: error.message });
  }
});

// Limpar todos os dados do banco (apenas administradores)
app.delete('/api/clear-database', requireAuth, requireRole('administrador'), async (req, res) => {
  try {
    const result = await dbManager.clearAllData();
    res.json({
      success: true,
      message: 'Base de dados limpa com sucesso',
      ...result
    });
  } catch (error) {
    console.error('Erro ao limpar base de dados:', error);
    res.status(500).json({ error: error.message });
  }
});

// Gerar mensagem de comunicação
const { buildWhatsAppMessage, buildDetailedMessage } = require('./message_builder');

app.get('/api/message', requireAuth, async (req, res) => {
  try {
    const excelData = await dbManager.loadExcelData();
    const controlData = await dbManager.getAllActivitiesControl();

    if (!excelData) {
      return res.json({ message: 'Nenhum dado disponível' });
    }

    // Construir mensagem usando o módulo message_builder (igual ao Python)
    const message = buildWhatsAppMessage(excelData, controlData);

    res.json({ message });
  } catch (error) {
    console.error('Erro ao gerar mensagem:', error);
    res.status(500).json({ error: error.message });
  }
});

// Gerar mensagem detalhada de comunicação (todos os usuários autenticados podem ver)
app.get('/api/message-detailed', requireAuth, async (req, res) => {
  try {
    const excelData = await dbManager.loadExcelData();
    const controlData = await dbManager.getAllActivitiesControl();
    const rollbackStatesMap = await dbManager.getAllRollbackStates();

    if (!excelData) {
      return res.json({ message: 'Nenhum dado disponível' });
    }

    // rollbackStatesMap já é um objeto indexado por sequencia, não precisa converter
    const message = buildDetailedMessage(excelData, controlData, rollbackStatesMap);

    res.json({ message });
  } catch (error) {
    console.error('Erro ao gerar mensagem detalhada:', error);
    res.status(500).json({ error: error.message });
  }
});

// Obter estado de rollback de uma CRQ (todos os usuários autenticados podem ver)
app.get('/api/rollback-state/:sequencia', requireAuth, async (req, res) => {
  try {
    const { sequencia } = req.params;
    const state = await dbManager.getRollbackState(sequencia);
    res.json(state);
  } catch (error) {
    console.error('Erro ao buscar estado de rollback:', error);
    res.status(500).json({ error: error.message });
  }
});

// Obter todos os estados de rollback (todos os usuários autenticados podem ver)
app.get('/api/rollback-states', requireAuth, async (req, res) => {
  try {
    const states = await dbManager.getAllRollbackStates();
    res.json({ states });
  } catch (error) {
    console.error('Erro ao buscar estados de rollback:', error);
    res.status(500).json({ error: error.message });
  }
});

// Ativar/desativar rollback para uma CRQ (apenas líderes e administradores)
app.put('/api/rollback-state/:sequencia', requireAuth, requireRole('lider_mudanca', 'administrador'), async (req, res) => {
  try {
    const { sequencia } = req.params;
    const { rollback_active } = req.body;

    if (typeof rollback_active !== 'boolean') {
      return res.status(400).json({ error: 'rollback_active deve ser um booleano' });
    }

    await dbManager.setRollbackState(sequencia, rollback_active);
    res.json({
      success: true,
      message: `Rollback ${rollback_active ? 'ativado' : 'desativado'} para CRQ ${sequencia}`,
      sequencia,
      rollback_active
    });
  } catch (error) {
    console.error('Erro ao atualizar estado de rollback:', error);
    res.status(500).json({ error: error.message });
  }
});

// Obter atividades não sincronizadas (todos os usuários autenticados podem ver)
app.get('/api/unsynced-activities', requireAuth, async (req, res) => {
  try {
    const { sync_timestamp, sequencias } = req.query;
    
    if (!sync_timestamp) {
      return res.status(400).json({ error: 'sync_timestamp é obrigatório' });
    }
    
    const sequenciasArray = sequencias ? sequencias.split(',') : [];
    const unsynced = await dbManager.getUnsyncedActivities(sync_timestamp, sequenciasArray);
    
    res.json({
      count: unsynced.length,
      activities: unsynced.map(row => ({
        id: row.id,
        seq: row.seq,
        sequencia: row.sequencia,
        atividade: row.atividade,
        excel_data_id: row.id
      }))
    });
  } catch (error) {
    console.error('Erro ao buscar atividades não sincronizadas:', error);
    res.status(500).json({ error: error.message });
  }
});

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor rodando na porta ${PORT}`);
  console.log(`📖 Documentação: http://localhost:${PORT}/`);
  if (DEBUG_MODE) {
    console.log('🔍 Modo DEBUG ativado');
  }
});

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Encerrando servidor...');
  await dbManager.close();
  process.exit(0);
});
