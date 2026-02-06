/**
 * Módulo para construção de mensagem consolidada para WhatsApp
 */
const { SEQUENCIAS } = require('./config');
const { calculateActivityStatus } = require('./status_calculator');

/**
 * Calcula estatísticas dos dados usando os novos status
 * Exclui milestones das contagens
 */
function calculateStatistics(excelData, controlData) {
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
      
      // Excluir milestones das contagens
      if (control.is_milestone) {
        continue;
      }
      
      // Calcular status usando a função de cálculo
      const calculatedStatus = calculateActivityStatus(
        { seq: row.seq, sequencia, inicio: row.inicio, fim: row.fim },
        control
      );

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

    // Calcular percentuais
    if (seqStats.total > 0) {
      seqStats.pct_concluidas = (seqStats.concluidas / seqStats.total) * 100;
      seqStats.pct_em_execucao_no_prazo = (seqStats.em_execucao_no_prazo / seqStats.total) * 100;
      seqStats.pct_em_execucao_fora_prazo = (seqStats.em_execucao_fora_prazo / seqStats.total) * 100;
      seqStats.pct_a_iniciar_no_prazo = (seqStats.a_iniciar_no_prazo / seqStats.total) * 100;
      seqStats.pct_a_iniciar_fora_prazo = (seqStats.a_iniciar_fora_prazo / seqStats.total) * 100;
    }

    stats.por_sequencia[sequencia] = seqStats;
  }

  // Calcular percentuais gerais
  if (stats.geral.total > 0) {
    stats.geral.pct_concluidas = (stats.geral.concluidas / stats.geral.total) * 100;
    stats.geral.pct_em_execucao_no_prazo = (stats.geral.em_execucao_no_prazo / stats.geral.total) * 100;
    stats.geral.pct_em_execucao_fora_prazo = (stats.geral.em_execucao_fora_prazo / stats.geral.total) * 100;
    stats.geral.pct_a_iniciar_no_prazo = (stats.geral.a_iniciar_no_prazo / stats.geral.total) * 100;
    stats.geral.pct_a_iniciar_fora_prazo = (stats.geral.a_iniciar_fora_prazo / stats.geral.total) * 100;
  }

  return stats;
}

/**
 * Verifica se uma sequência está concluída
 * Uma sequência está concluída se todas as atividades estão com status "Concluído"
 * (exclui milestones da verificação)
 */
function isSequenceCompleted(excelData, controlData, sequencia) {
  if (!excelData[sequencia]) {
    return false;
  }

  const data = excelData[sequencia];

  if (data.dataframe.length === 0) {
    return false;
  }

  let total = 0;
  let concluidas = 0;

  for (const row of data.dataframe) {
    const key = `${row.seq}_${sequencia}`;
    const control = controlData[key] || {};
    
    // Excluir milestones
    if (control.is_milestone) {
      continue;
    }

    total++;
    
    // Calcular status usando a função de cálculo
    const calculatedStatus = calculateActivityStatus(
      { seq: row.seq, sequencia, inicio: row.inicio, fim: row.fim },
      control
    );
    
    const statusLower = calculatedStatus.toLowerCase();
    // Apenas "Concluído" conta como concluída
    if (statusLower.includes('concluído') || statusLower.includes('concluido')) {
      concluidas++;
    }
  }

  return total > 0 && concluidas === total;
}

/**
 * Obtém atividades atrasadas
 * Inclui atividades com status "fora do prazo" ou com atraso_minutos > 0
 * Exclui milestones
 */
function getDelayedActivities(excelData, controlData) {
  const delayed = [];

  for (const [sequencia, data] of Object.entries(excelData)) {
    for (const row of data.dataframe) {
      const key = `${row.seq}_${sequencia}`;
      const control = controlData[key] || {};
      
      // Excluir milestones
      if (control.is_milestone) {
        continue;
      }
      
      // Calcular status usando a função de cálculo
      const calculatedStatus = calculateActivityStatus(
        { seq: row.seq, sequencia, inicio: row.inicio, fim: row.fim },
        control
      );
      
      const statusLower = calculatedStatus.toLowerCase();
      const atrasoMinutos = control.atraso_minutos || 0;
      
      // Incluir se status contém "fora do prazo" ou se tem atraso_minutos > 0
      if (statusLower.includes('fora do prazo') || atrasoMinutos > 0) {
        delayed.push({
          sequencia: sequencia,
          atividade: row.atividade || `Atividade ${row.seq}`,
          atraso_minutos: atrasoMinutos,
          observacoes: control.observacoes || ''
        });
      }
    }
  }

  return delayed;
}

/**
 * Formata atraso/adiantamento para formato legível
 * Formato: "+1h 15min" ou "-30min" ou "0 min"
 */
function formatDelay(minutes) {
  if (minutes === 0) {
    return '0 min';
  }

  const sign = minutes > 0 ? '+' : '-';
  const absMinutes = Math.abs(minutes);

  if (absMinutes < 60) {
    return `${sign}${absMinutes} min`;
  }

  const hours = Math.floor(absMinutes / 60);
  const mins = absMinutes % 60;

  if (mins === 0) {
    return `${sign}${hours}h`;
  }

  return `${sign}${hours}h ${mins}min`;
}

/**
 * Constrói mensagem consolidada para WhatsApp
 */
function buildWhatsAppMessage(excelData, controlData) {
  if (!excelData || Object.keys(excelData).length === 0) {
    return 'Nenhum dado disponível';
  }

  const stats = calculateStatistics(excelData, controlData);
  const totalGeral = stats.geral.total;

  // Cabeçalho - usar GMT-3 (Brasil)
  const now = new Date();
  const gmtMinus3 = new Date(now.getTime() - (3 * 60 * 60 * 1000));
  const dataStr = gmtMinus3.toLocaleDateString('pt-BR');
  const horaStr = gmtMinus3.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  // Construir mensagem
  let message = '🚀 *JANELA DE MUDANÇA - REDE*\n\n';
  message += `📅 Data: ${dataStr} | 🕐 Horário: ${horaStr}\n\n`;
  message += '━━━━━━━━━━━━━━━━━━\n\n';
  message += '📈 *STATUS CRQ GERAL*\n';
  message += `  ✅ Concluídas: ${stats.geral.concluidas}/${totalGeral} (${stats.geral.pct_concluidas.toFixed(1)}%)\n`;
  message += `  ⏳ Em Execução no Prazo: ${stats.geral.em_execucao_no_prazo}/${totalGeral} (${stats.geral.pct_em_execucao_no_prazo.toFixed(1)}%)\n`;
  message += `  🔴 Em Execução Fora do Prazo: ${stats.geral.em_execucao_fora_prazo}/${totalGeral} (${stats.geral.pct_em_execucao_fora_prazo.toFixed(1)}%)\n`;
  message += `  🟦 A Iniciar no Prazo: ${stats.geral.a_iniciar_no_prazo}/${totalGeral} (${stats.geral.pct_a_iniciar_no_prazo.toFixed(1)}%)\n`;
  message += `  🟠 A Iniciar Fora do Prazo: ${stats.geral.a_iniciar_fora_prazo}/${totalGeral} (${stats.geral.pct_a_iniciar_fora_prazo.toFixed(1)}%)\n\n`;
  message += '━━━━━━━━━━━━━━━━━━\n';

  // Separar CRQs iniciadas das não iniciadas
  const crqsIniciadas = [];
  const crqsNaoIniciadas = [];

  for (const [sequenciaKey, sequenciaInfo] of Object.entries(SEQUENCIAS)) {
    if (stats.por_sequencia[sequenciaKey]) {
      const seqStats = stats.por_sequencia[sequenciaKey];

      if (seqStats.total > 0) {
        // CRQ está iniciada se tiver atividades em execução ou concluídas
        if (seqStats.em_execucao_no_prazo > 0 ||
            seqStats.em_execucao_fora_prazo > 0 ||
            seqStats.concluidas > 0) {
          crqsIniciadas.push([sequenciaKey, sequenciaInfo, seqStats]);
        } else {
          crqsNaoIniciadas.push([sequenciaKey, sequenciaInfo, seqStats]);
        }
      }
    }
  }

  // Mostrar primeiro CRQs iniciadas (com detalhamento)
  if (crqsIniciadas.length > 0) {
    message += '\n📊 *CRQs INICIADAS*\n';
    for (const [sequenciaKey, sequenciaInfo, seqStats] of crqsIniciadas) {
      const emoji = sequenciaInfo.emoji;
      const nome = sequenciaInfo.nome;
      const total = seqStats.total;

      message += `\n${emoji} *STATUS CRQ ${nome}*\n`;
      message += `  ✅ Concluídas: ${seqStats.concluidas}/${total} (${seqStats.pct_concluidas.toFixed(1)}%)\n`;
      message += `  ⏳ Em Execução no Prazo: ${seqStats.em_execucao_no_prazo}/${total} (${seqStats.pct_em_execucao_no_prazo.toFixed(1)}%)\n`;
      message += `  🔴 Em Execução Fora do Prazo: ${seqStats.em_execucao_fora_prazo}/${total} (${seqStats.pct_em_execucao_fora_prazo.toFixed(1)}%)\n`;
      message += `  🟦 A Iniciar no Prazo: ${seqStats.a_iniciar_no_prazo}/${total} (${seqStats.pct_a_iniciar_no_prazo.toFixed(1)}%)\n`;
      message += `  🟠 A Iniciar Fora do Prazo: ${seqStats.a_iniciar_fora_prazo}/${total} (${seqStats.pct_a_iniciar_fora_prazo.toFixed(1)}%)\n`;
    }
  }

  // Mostrar depois CRQs não iniciadas (apenas indicador)
  if (crqsNaoIniciadas.length > 0) {
    message += '\n\n⏸️ *CRQs NÃO INICIADAS*\n';
    const nomesNaoIniciadas = [];
    for (const [sequenciaKey, sequenciaInfo, seqStats] of crqsNaoIniciadas) {
      const emoji = sequenciaInfo.emoji;
      const nome = sequenciaInfo.nome;
      nomesNaoIniciadas.push(`${emoji} ${nome}`);
    }

    message += `  ${nomesNaoIniciadas.join(', ')}\n`;
  }

  message += '\n━━━━━━━━━━━━━━━━━━\n\n';

  // CRQs concluídos
  const concluidas = [];
  for (const [sequenciaKey, sequenciaInfo] of Object.entries(SEQUENCIAS)) {
    if (isSequenceCompleted(excelData, controlData, sequenciaKey)) {
      concluidas.push(sequenciaInfo.nome);
    }
  }

  if (concluidas.length > 0) {
    message += '📋 *CONCLUÍDAS*\n';
    message += `  ${concluidas.join(', ')}\n\n`;
    message += '━━━━━━━━━━━━━━━━━━\n\n';
  }

  // Atividades atrasadas
  const delayed = getDelayedActivities(excelData, controlData);

  if (delayed.length > 0) {
    message += '🚨 *ATIVIDADES ATRASADAS*\n';

    // Agrupar por CRQ
    for (const [sequenciaKey, sequenciaInfo] of Object.entries(SEQUENCIAS)) {
      const seqDelayed = delayed.filter(d => d.sequencia === sequenciaKey);

      if (seqDelayed.length > 0) {
        const emoji = sequenciaInfo.emoji;
        const nome = sequenciaInfo.nome;

        for (const item of seqDelayed) {
          const atrasoStr = formatDelay(item.atraso_minutos);

          message += `\n  ${emoji} [${nome}] ${item.atividade}: ${atrasoStr}\n`;
          if (item.observacoes && item.observacoes.trim()) {
            message += `     Observação: ${item.observacoes}\n`;
          }
        }
      }
    }

    message += '\n━━━━━━━━━━━━━━━━━━\n\n';
  }

  // Rodapé - usar o mesmo horário GMT-3
  const atualizadoStr = gmtMinus3.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
  message += `✅ Atualizado em: ${atualizadoStr}\n`;

  return message;
}

/**
 * Obtém emoji de status para atividade
 */
function getStatusEmoji(status, atrasoMinutos, fimPlanejado, horarioFimReal) {
  if (!status) return '⬜';
  
  const statusLower = status.toLowerCase();
  
  if (statusLower.includes('concluído') || statusLower.includes('concluido')) {
    return '✅';
  } else if (statusLower.includes('em execução no prazo') || statusLower.includes('em execucao no prazo')) {
    return '⏳';
  } else if (statusLower.includes('em execução fora do prazo') || statusLower.includes('em execucao fora do prazo')) {
    return '🔴';
  } else if (statusLower.includes('a iniciar fora do prazo')) {
    return '⛔';
  } else if (statusLower.includes('a iniciar no prazo')) {
    return '⬜';
  }
  
  // Fallback para status antigos (compatibilidade)
  if (status === 'Em Execução') {
    return '⏳';
  } else if (status === 'Atrasado') {
    return '🔴';
  } else if (status === 'Planejado') {
    // Verificar se está atrasado mesmo sendo "Planejado"
    if (atrasoMinutos > 0 || (fimPlanejado && horarioFimReal && new Date(horarioFimReal) > new Date(fimPlanejado))) {
      return '🔴';
    }
    return '⬜';
  }
  
  return '⬜';
}

/**
 * Formata data/hora para exibição (formato: DD/MM – HH:MM)
 */
function formatDateTime(dateStr) {
  if (!dateStr) return '';
  try {
    const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr;
    if (isNaN(date.getTime())) return '';
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const hour = String(date.getHours()).padStart(2, '0');
    const minute = String(date.getMinutes()).padStart(2, '0');
    return `${day}/${month} – ${hour}:${minute}`;
  } catch {
    return '';
  }
}

/**
 * Formata apenas hora para exibição (formato: HH:MM)
 */
function formatTime(dateStr) {
  if (!dateStr) return '';
  try {
    const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr;
    if (isNaN(date.getTime())) return '';
    const hour = String(date.getHours()).padStart(2, '0');
    const minute = String(date.getMinutes()).padStart(2, '0');
    return `${hour}:${minute}`;
  } catch {
    return '';
  }
}

/**
 * Constrói mensagem detalhada de acompanhamento
 * Formato: Agrupa atividades por CRQ com status individual
 */
function buildDetailedMessage(excelData, controlData, rollbackStates = {}) {
  if (!excelData || Object.keys(excelData).length === 0) {
    return 'Nenhum dado disponível';
  }

  const now = new Date();
  const gmtMinus3 = new Date(now.getTime() - (3 * 60 * 60 * 1000));
  const statusStr = formatDateTime(gmtMinus3);

  let message = '⏳ *ACOMPANHAMENTO – MIGRAÇÃO DE INFRA*\n\n';
  message += `Status: ${statusStr}\n`;
  
  // Calcular próximo status (próxima hora)
  const nextHour = new Date(gmtMinus3);
  nextHour.setHours(nextHour.getHours() + 1);
  const nextStatusStr = formatDateTime(nextHour);
  message += `Próximo Status: ${nextStatusStr}\n\n`;

  // Processar cada CRQ
  for (const [sequenciaKey, sequenciaInfo] of Object.entries(SEQUENCIAS)) {
    if (!excelData[sequenciaKey]) continue;

    const data = excelData[sequenciaKey];
    const emoji = sequenciaInfo.emoji;
    const nome = sequenciaInfo.nome;
    
    // Buscar número do CRQ (pode estar no primeiro registro ou usar padrão)
    // Por enquanto, usar o nome da sequência como identificador
    const crqNumber = sequenciaKey; // Pode ser ajustado se houver campo específico
    
    message += `${emoji} ${crqNumber} – ${nome}`;
    
    // Verificar se há rollback ativo
    const rollbackState = rollbackStates[sequenciaKey] || { rollback_active: false };
    if (rollbackState.rollback_active) {
      message += ' (Rollback Ativo)';
    }
    
    message += '\n';

    // Ordenar atividades por seq e filtrar apenas as concluídas
    const activities = [...data.dataframe]
      .sort((a, b) => (a.seq || 0) - (b.seq || 0))
      .filter(row => {
        const key = `${row.seq}_${sequenciaKey}`;
        const control = controlData[key] || {};
        
        // Pular milestones
        if (control.is_milestone) {
          return false;
        }

        // Usar status calculado se disponível, senão usar status do controle
        const calculatedStatus = calculateActivityStatus(
          { seq: row.seq, sequencia: sequenciaKey, inicio: row.inicio, fim: row.fim },
          control
        );
        const status = calculatedStatus || control.status || 'Planejado';
        
        // Mostrar apenas atividades concluídas
        return status === 'Concluído';
      });

    // Verificar se há atividades concluídas
    if (activities.length === 0) {
      message += 'Nenhuma atividade concluída.\n';
    } else {
      for (const row of activities) {
        const key = `${row.seq}_${sequenciaKey}`;
        const control = controlData[key] || {};

        // Usar status calculado se disponível, senão usar status do controle
        const calculatedStatus = calculateActivityStatus(
          { seq: row.seq, sequencia: sequenciaKey, inicio: row.inicio, fim: row.fim },
          control
        );
        const status = calculatedStatus || control.status || 'Planejado';
        const atividade = row.atividade || '';
        const atrasoMinutos = control.atraso_minutos || 0;
        
        // Determinar emoji de status
        const statusEmoji = getStatusEmoji(status, atrasoMinutos, row.fim, control.horario_fim_real);
        
        message += `${statusEmoji} ${atividade}`;

        // Adicionar horários se disponíveis
        if (control.horario_inicio_real) {
          const inicioReal = formatTime(control.horario_inicio_real);
          
          if (control.horario_fim_real) {
            const fimReal = formatTime(control.horario_fim_real);
            message += ` (${inicioReal} – ${fimReal})`;
          } else {
            message += ` (${inicioReal})`;
          }
        } else if (row.fim) {
          const fimPlan = formatTime(row.fim);
          message += ` (janela até ${fimPlan})`;
        }

        // Adicionar observações se houver
        if (control.observacoes && control.observacoes.trim()) {
          message += `\n   ${control.observacoes}`;
        }

        message += '\n';
      }
    }

    // Status de rollback
    if (rollbackState.rollback_active) {
      // Verificar se há outras CRQs com rollback ativo que podem ser dependências
      const redeRollback = rollbackStates['REDE']?.rollback_active || false;
      
      if (redeRollback && sequenciaKey !== 'REDE') {
        // Se REDE tem rollback ativo e esta não é REDE, está aguardando
        message += `⬜ Rollback: Acionado Aguardando Finalização do Rollback de Redes`;
      } else {
        message += `⏳ Rollback: Acionado o Plano Preparado`;
      }
    } else {
      message += `⬜ Rollback: Não acionado`;
    }
    
    message += '\n\n';
  }

  // Observações Executivas
  message += '📌 *Observação Executiva*\n';
  message += 'Adicione observações executivas aqui...\n\n';

  // Legenda
  message += '📘 *Legenda de Status*\n';
  message += '✅ Concluído\n';
  message += '⏳ Em execução no prazo\n';
  message += '🔴 Em execução fora do prazo\n';
  message += '⬜ A iniciar no prazo\n';
  message += '⛔ A iniciar fora do prazo\n';
  message += '🔁 Rollback disponível\n';

  return message;
}

module.exports = {
  buildWhatsAppMessage,
  buildDetailedMessage,
  calculateStatistics,
  getDelayedActivities,
  formatDelay,
  isSequenceCompleted,
  getStatusEmoji,
  formatDateTime,
  formatTime
};
