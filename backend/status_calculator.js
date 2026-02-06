/**
 * Módulo para cálculo de status de atividades baseado em regras de negócio
 */

/**
 * Calcula o status de uma atividade baseado em:
 * - Se é milestone (retorna "N/A")
 * - Se está concluída (retorna "Concluído")
 * - Se está em execução (tem horario_inicio_real mas não tem horario_fim_real)
 * - Se está atrasada (atraso_minutos > 0)
 * - Se está no prazo ou fora do prazo
 */
function calculateActivityStatus(activity, control) {
  // Se é milestone, retorna "N/A"
  if (control.is_milestone) {
    return 'N/A';
  }

  // Se está concluída (tem horario_fim_real)
  if (control.horario_fim_real) {
    return 'Concluído';
  }

  // Verificar se está em execução (tem horario_inicio_real mas não tem horario_fim_real)
  const isInExecution = control.horario_inicio_real && !control.horario_fim_real;
  
  // Verificar se está atrasada
  const isDelayed = (control.atraso_minutos || 0) > 0;

  if (isInExecution) {
    // Em execução
    if (isDelayed) {
      return 'Em execução fora do prazo';
    } else {
      return 'Em execução no prazo';
    }
  } else {
    // A iniciar (não tem horario_inicio_real)
    if (isDelayed) {
      return 'A Iniciar fora do prazo';
    } else {
      return 'A Iniciar no prazo';
    }
  }
}

/**
 * Obtém a cor do status para exibição no frontend
 */
function getStatusColor(status) {
  if (!status) return { bg: '#F3F4F6', text: '#6B7280' };
  
  const statusLower = status.toLowerCase();
  
  if (statusLower === 'n/a') {
    return { bg: '#F3F4F6', text: '#6B7280' }; // Cinza para N/A
  } else if (statusLower.includes('concluído') || statusLower.includes('concluido')) {
    return { bg: '#D1FAE5', text: '#065F46' }; // Verde claro
  } else if (statusLower.includes('em execução no prazo') || statusLower.includes('em execucao no prazo')) {
    return { bg: '#3B82F6', text: '#FFFFFF' }; // Azul brilhante
  } else if (statusLower.includes('em execução fora do prazo') || statusLower.includes('em execucao fora do prazo')) {
    return { bg: '#EF4444', text: '#FFFFFF' }; // Vermelho
  } else if (statusLower.includes('a iniciar no prazo')) {
    return { bg: '#DBEAFE', text: '#1E40AF' }; // Azul claro
  } else if (statusLower.includes('a iniciar fora do prazo')) {
    return { bg: '#FED7AA', text: '#9A3412' }; // Laranja
  }
  
  // Status desconhecido
  return { bg: '#F3F4F6', text: '#6B7280' };
}

module.exports = {
  calculateActivityStatus,
  getStatusColor
};
