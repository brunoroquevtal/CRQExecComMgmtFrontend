import React, { useMemo, useState, useEffect } from 'react';
import { format, parseISO, addHours, addMinutes, startOfDay, differenceInHours, differenceInMinutes } from 'date-fns';
import api from '../utils/api';

const GanttChart = ({ activities, activeTab = 'all' }) => {
  const [rollbackStates, setRollbackStates] = useState({});
  const [currentTime, setCurrentTime] = useState(new Date());
  const [tooltip, setTooltip] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [leftColumnVisible, setLeftColumnVisible] = useState(true);
  
  // Atualizar horário atual a cada minuto
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // Atualizar a cada minuto
    
    return () => clearInterval(interval);
  }, []);
  
  // Buscar estados de rollback
  useEffect(() => {
    const fetchRollbackStates = async () => {
      try {
        const response = await api.get('/rollback-states');
        const states = {};
        if (response.data && Array.isArray(response.data)) {
          response.data.forEach(state => {
            states[state.sequencia] = state;
          });
        }
        setRollbackStates(states);
      } catch (error) {
        console.error('Erro ao buscar estados de rollback:', error);
      }
    };
    fetchRollbackStates();
  }, []);
  // Função auxiliar para parsear data de diferentes formatos
  const parseDate = (dateValue) => {
    if (!dateValue) return null;
    
    // Se já é um objeto Date válido
    if (dateValue instanceof Date && !isNaN(dateValue.getTime())) {
      return dateValue;
    }
    
    // Se é string, tentar parseISO primeiro
    if (typeof dateValue === 'string') {
      try {
        // Tentar parseISO (formato ISO: 2024-01-01T10:00:00Z)
        const isoDate = parseISO(dateValue);
        if (!isNaN(isoDate.getTime())) {
          return isoDate;
        }
        
        // Tentar outros formatos comuns
        const date = new Date(dateValue);
        if (!isNaN(date.getTime())) {
          return date;
        }
      } catch (e) {
        console.warn('Erro ao parsear data:', dateValue, e);
      }
    }
    
    return null;
  };

  // Filtrar atividades baseado na aba selecionada e lógica de rollback
  const filteredActivities = useMemo(() => {
    if (!activities || activities.length === 0) return [];
    
    let filtered = activities;
    if (activeTab !== 'all') {
      filtered = filtered.filter(a => a.sequencia === activeTab);
    }
    
    // Aplicar filtro de rollback usando os estados do backend
    const filteredByRollback = filtered.filter(activity => {
      const sequencia = activity.sequencia;
      const rollbackState = rollbackStates[sequencia] || { rollback_active: false };
      const isRollbackActive = rollbackState.rollback_active;
      
      const isEncerramento = activity.is_encerramento;
      const isRollback = activity.is_rollback;
      
      // Aplicar mesma lógica do backend:
      // - Encerramento sempre aparece
      // - Se rollback ativo: mostrar apenas rollback + encerramento
      // - Se rollback inativo: mostrar apenas principais + encerramento
      if (isEncerramento) {
        // Sempre mostrar encerramento
        return true;
      } else if (isRollbackActive && !isRollback) {
        // Rollback ativo: suprimir principais
        return false;
      } else if (!isRollbackActive && isRollback) {
        // Rollback inativo: suprimir rollback
        return false;
      } else {
        // Adicionar atividade (principal quando rollback inativo, ou rollback quando ativo)
        return true;
      }
    });
    
    // Filtrar apenas atividades com início e fim válidos e parseáveis
    return filteredByRollback.filter(a => {
      if (!a.inicio || !a.fim) return false;
      
      const inicioParsed = parseDate(a.inicio);
      const fimParsed = parseDate(a.fim);
      
      return inicioParsed && fimParsed && !isNaN(inicioParsed.getTime()) && !isNaN(fimParsed.getTime());
    });
  }, [activities, activeTab, rollbackStates]);

  // Agrupar atividades por sequência (CRQ)
  const activitiesBySequencia = useMemo(() => {
    const grouped = {};
    filteredActivities.forEach(activity => {
      if (!grouped[activity.sequencia]) {
        grouped[activity.sequencia] = [];
      }
      grouped[activity.sequencia].push(activity);
    });
    return grouped;
  }, [filteredActivities]);

  // Calcular range de tempo global
  const timeRange = useMemo(() => {
    if (filteredActivities.length === 0) return null;

    let minTime = null;
    let maxTime = null;

    filteredActivities.forEach(activity => {
      try {
        const inicio = parseDate(activity.inicio);
        const fim = parseDate(activity.fim);
        
        if (!inicio || !fim || isNaN(inicio.getTime()) || isNaN(fim.getTime())) {
          console.warn('Data inválida na atividade:', activity.seq, activity.sequencia, {
            inicio: activity.inicio,
            fim: activity.fim,
            inicioParsed: inicio,
            fimParsed: fim
          });
          return;
        }
        
        if (!minTime || inicio < minTime) minTime = inicio;
        if (!maxTime || fim > maxTime) maxTime = fim;
      } catch (e) {
        console.warn('Erro ao parsear data da atividade:', activity, e);
      }
    });

    if (!minTime || !maxTime) return null;

    // Arredondar para o início da hora (para baixo no início)
    const minHour = minTime.getHours();
    const minMinute = minTime.getMinutes();
    minTime = startOfDay(minTime);
    minTime = addHours(minTime, minHour);
    minTime = addMinutes(minTime, Math.floor(minMinute / 15) * 15); // Arredondar para múltiplo de 15 minutos
    
    // Arredondar para o próximo intervalo de 15 minutos (para cima no fim)
    const maxHour = maxTime.getHours();
    const maxMinute = maxTime.getMinutes();
    maxTime = startOfDay(maxTime);
    maxTime = addHours(maxTime, maxHour);
    maxTime = addMinutes(maxTime, Math.ceil(maxMinute / 15) * 15); // Arredondar para próximo múltiplo de 15 minutos
    if (maxTime.getMinutes() === 0 && maxMinute > 0) {
      maxTime = addHours(maxTime, 1); // Se arredondou para hora cheia mas tinha minutos, adicionar 1 hora
    }

    return { minTime, maxTime };
  }, [filteredActivities]);

  if (!timeRange || filteredActivities.length === 0) {
    // Debug: mostrar informações sobre por que não há atividades
    const debugInfo = activities && activities.length > 0 ? {
      total: activities.length,
      filtered: filteredActivities.length,
      withDates: activities.filter(a => a.inicio && a.fim).length,
      sampleActivity: activities.find(a => a.inicio && a.fim) || null
    } : { total: 0 };
    
    return (
      <div className="bg-white rounded-xl shadow-md p-6 text-center text-vtal-gray-500">
        <p>Nenhuma atividade com horários definidos para exibir no gráfico de Gantt</p>
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 text-xs text-left bg-gray-100 p-4 rounded">
            <p><strong>Debug:</strong></p>
            <p>Total de atividades: {debugInfo.total}</p>
            <p>Atividades filtradas: {debugInfo.filtered}</p>
            <p>Atividades com datas: {debugInfo.withDates}</p>
            {debugInfo.sampleActivity && (
              <div className="mt-2">
                <p><strong>Exemplo de atividade:</strong></p>
                <p>Seq: {debugInfo.sampleActivity.seq}, Sequencia: {debugInfo.sampleActivity.sequencia}</p>
                <p>Inicio: {String(debugInfo.sampleActivity.inicio)} (tipo: {typeof debugInfo.sampleActivity.inicio})</p>
                <p>Fim: {String(debugInfo.sampleActivity.fim)} (tipo: {typeof debugInfo.sampleActivity.fim})</p>
                <p>Parse inicio: {parseDate(debugInfo.sampleActivity.inicio) ? 'OK' : 'FALHOU'}</p>
                <p>Parse fim: {parseDate(debugInfo.sampleActivity.fim) ? 'OK' : 'FALHOU'}</p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  const { minTime, maxTime } = timeRange;
  
  // Garantir que minTime e maxTime são válidos
  if (!minTime || !maxTime || isNaN(minTime.getTime()) || isNaN(maxTime.getTime())) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6 text-center text-vtal-gray-500">
        <p>Erro ao calcular intervalo de tempo do gráfico de Gantt</p>
      </div>
    );
  }
  
  const totalMinutes = differenceInMinutes(maxTime, minTime);
  const intervalMinutes = 15; // Intervalo de 15 minutos
  const intervals = [];
  
  // Gerar array de intervalos de 15 minutos para o eixo X
  for (let i = 0; i <= totalMinutes; i += intervalMinutes) {
    const interval = addMinutes(minTime, i);
    intervals.push(interval);
  }
  
  const totalIntervals = intervals.length;
  
  // Garantir que totalIntervals é válido
  if (!totalIntervals || totalIntervals === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6 text-center text-vtal-gray-500">
        <p>Nenhum intervalo de tempo válido para exibir no gráfico de Gantt</p>
      </div>
    );
  }

  // Calcular posição e largura de uma barra
  const getBarPosition = (activity) => {
    try {
      const inicio = parseDate(activity.inicio);
      const fim = parseDate(activity.fim);
      
      if (!inicio || !fim || isNaN(inicio.getTime()) || isNaN(fim.getTime())) {
        console.warn('Data inválida ao calcular posição:', activity.seq, activity.sequencia);
        return { leftPercent: 0, widthPercent: 0 };
      }
      
      const startOffsetMinutes = differenceInMinutes(inicio, minTime);
      const durationMinutes = Math.max(15, differenceInMinutes(fim, inicio)); // Mínimo 15 minutos
      
      const leftPercent = Math.max(0, (startOffsetMinutes / totalMinutes) * 100);
      const widthPercent = Math.max(0.5, (durationMinutes / totalMinutes) * 100); // Mínimo 0.5% para visibilidade
      
      return { leftPercent, widthPercent };
    } catch (e) {
      console.warn('Erro ao calcular posição da barra:', activity, e);
      return { leftPercent: 0, widthPercent: 0 };
    }
  };

  // Calcular tamanho máximo para abreviação de nomes de atividades
  const maxActivityNameLength = useMemo(() => {
    let maxLength = 0;
    filteredActivities.forEach(activity => {
      const activityName = activity.atividade || '';
      if (activityName.length > maxLength) {
        maxLength = activityName.length;
      }
    });
    // Retornar 2/3 do maior nome
    return Math.max(15, Math.floor(maxLength * (2/3))); // Mínimo de 15 caracteres
  }, [filteredActivities]);

  // Abreviar nome da atividade se necessário
  const abbreviateActivityName = (activityName) => {
    if (!activityName) return '';
    if (activityName.length <= maxActivityNameLength) {
      return activityName;
    }
    return activityName.substring(0, maxActivityNameLength) + '...';
  };

  // Calcular posição do horário atual
  const getCurrentTimePosition = () => {
    if (!timeRange || !currentTime) return null;
    const { minTime, maxTime } = timeRange;
    
    // Verificar se o horário atual está dentro do range
    if (currentTime < minTime || currentTime > maxTime) return null;
    
    const currentOffsetMinutes = differenceInMinutes(currentTime, minTime);
    const totalMinutes = differenceInMinutes(maxTime, minTime);
    
    if (totalMinutes <= 0) return null;
    
    return (currentOffsetMinutes / totalMinutes) * 100;
  };

  const currentTimePosition = getCurrentTimePosition();

  // Calcular a hora atual (arredondada para baixo) para destacar atividades
  const getCurrentHour = () => {
    if (!currentTime) return null;
    const currentHour = currentTime.getHours();
    const currentMinute = currentTime.getMinutes();
    // Se estamos em 14:30, queremos destacar atividades da coluna 14:00
    // Então retornamos a hora cheia atual
    return currentHour;
  };

  const currentHour = getCurrentHour();

  // Verificar se uma atividade está na coluna do horário atual
  const isActivityInCurrentHour = (activity) => {
    if (!currentHour || !activity.inicio) return false;
    
    try {
      const inicio = parseDate(activity.inicio);
      if (!inicio || isNaN(inicio.getTime())) return false;
      
      const activityHour = inicio.getHours();
      // Verificar se a atividade começa na hora atual (coluna atual)
      // Ou se está em execução durante a hora atual
      const activityStartHour = inicio.getHours();
      const fim = parseDate(activity.fim);
      const activityEndHour = fim ? fim.getHours() : activityStartHour;
      
      // Atividade está na coluna atual se:
      // 1. Começa na hora atual, OU
      // 2. Está em execução durante a hora atual (começa antes e termina depois ou durante)
      return activityStartHour === currentHour || 
             (activityStartHour < currentHour && (activityEndHour >= currentHour || !fim));
    } catch (e) {
      return false;
    }
  };

  // Renderizar uma atividade como barra
  const renderActivityBar = (activity, rowIndex) => {
    const { leftPercent, widthPercent } = getBarPosition(activity);
    // Verificar se é rollback pela flag ou pelo texto da atividade
    const atividadeLower = activity.atividade ? activity.atividade.toLowerCase() : '';
    const isRollback = activity.is_rollback || 
                       atividadeLower.includes('rollback') || 
                       atividadeLower.includes('atividade rollback');
    const isEncerramento = activity.is_encerramento;
    
    // Verificar se a atividade está na coluna do horário atual
    const isInCurrentHour = isActivityInCurrentHour(activity);
    
    // Cores: rollback = vermelho escuro (sempre), principal = verde escuro, encerramento principal = azul
    // Prioridade: rollback > encerramento > principal
    let bgColor;
    if (isRollback) {
      // Qualquer atividade com flag de rollback ou texto "rollback" fica vermelho escuro
      bgColor = '#991B1B';
    } else if (isEncerramento) {
      // Encerramento sem rollback fica azul
      bgColor = '#0066CC';
    } else {
      // Atividade principal fica verde escuro
      bgColor = '#065F46';
    }
    
    // Se está na hora atual, clarear a cor para destacar
    if (isInCurrentHour) {
      if (isRollback) {
        bgColor = '#DC2626'; // Vermelho mais claro
      } else if (isEncerramento) {
        bgColor = '#2563EB'; // Azul mais claro
      } else {
        bgColor = '#10B981'; // Verde mais claro
      }
    }
    
    const borderColor = isRollback ? '#7F1D1D' : (isEncerramento ? '#0052A3' : '#064E3B');
    // Borda mais destacada se está na hora atual
    const finalBorderColor = isInCurrentHour 
      ? (isRollback ? '#B91C1C' : (isEncerramento ? '#1D4ED8' : '#059669'))
      : borderColor;
    const textColor = '#FFFFFF'; // texto branco para ambas para melhor legibilidade
    
    try {
      const inicio = parseDate(activity.inicio);
      const fim = parseDate(activity.fim);
      
      if (!inicio || !fim || isNaN(inicio.getTime()) || isNaN(fim.getTime())) {
        console.warn('Data inválida ao renderizar barra:', activity.seq, activity.sequencia);
        return null;
      }
      
      const grupo = activity.grupo || 'Sem Grupo';
      const status = activity.status || 'N/A';
      const tempo = activity.tempo || 0;
      const tempoFormatado = `${Math.floor(tempo / 60)}h${tempo % 60 > 0 ? (tempo % 60).toString().padStart(2, '0') + 'm' : ''}`;
      
      const handleMouseEnter = (e) => {
        setTooltip({
          atividade: activity.atividade,
          grupo: grupo,
          status: status,
          inicio: format(inicio, "dd/MM/yyyy HH'h'mm"),
          fim: format(fim, "dd/MM/yyyy HH'h'mm"),
          tempo: tempoFormatado,
          isRollback: isRollback,
          isEncerramento: isEncerramento,
          sequencia: activity.sequencia,
          seq: activity.seq
        });
        setTooltipPosition({
          x: e.clientX,
          y: e.clientY
        });
      };

      const handleMouseMove = (e) => {
        setTooltipPosition({
          x: e.clientX,
          y: e.clientY
        });
      };

      const handleMouseLeave = () => {
        setTooltip(null);
      };
      
      return (
        <div
          key={`${activity.seq}-${activity.sequencia}-${activity.excel_data_id || rowIndex}`}
          className="absolute"
          style={{
            left: `${leftPercent}%`,
            width: `${widthPercent}%`,
            minWidth: '20px',
            top: '2px',
            height: `${rowHeight - 4}px`
          }}
        >
          <div
            className={`h-full rounded px-1 flex items-center cursor-pointer transition-all hover:opacity-80 hover:z-10 ${
              isInCurrentHour ? 'animate-pulse' : ''
            }`}
            style={{
              backgroundColor: bgColor,
              border: `2px solid ${finalBorderColor}`,
              boxShadow: isInCurrentHour 
                ? '0 0 12px rgba(59, 130, 246, 0.6), 0 4px 8px rgba(0,0,0,0.2)' 
                : '0 1px 2px rgba(0,0,0,0.1)',
              color: textColor,
              transform: isInCurrentHour ? 'scale(1.02)' : 'scale(1)',
              zIndex: isInCurrentHour ? 15 : 1
            }}
            onMouseEnter={handleMouseEnter}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
          >
            <span className="truncate text-[8px] font-medium">{abbreviateActivityName(activity.atividade)}</span>
          </div>
        </div>
      );
    } catch (e) {
      console.warn('Erro ao renderizar barra:', activity, e);
      return null;
    }
  };

  const rowHeight = 30; // Altura de cada linha (reduzida para atividades em uma linha)
  const headerHeight = 60; // Altura do cabeçalho (reduzida)
  // Largura da coluna esquerda responsiva
  const leftColumnWidth = typeof window !== 'undefined' && window.innerWidth < 768 ? 120 : 200;
  const actualLeftColumnWidth = leftColumnVisible ? leftColumnWidth : 0;

  return (
    <div className="bg-white rounded-xl shadow-md p-3 md:p-6">
      <div className="flex items-center justify-between mb-3 md:mb-4">
        <h3 className="text-lg md:text-xl font-display font-semibold text-vtal-gray-800">
          Gráfico de Gantt {activeTab !== 'all' ? `- ${activeTab}` : ''}
        </h3>
        <button
          onClick={() => setLeftColumnVisible(!leftColumnVisible)}
          className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-vtal-gray-700 bg-vtal-light hover:bg-vtal-gray-200 rounded-lg transition-colors"
          title={leftColumnVisible ? 'Ocultar coluna de atividades' : 'Mostrar coluna de atividades'}
        >
          {leftColumnVisible ? (
            <>
              <span>◀</span>
              <span className="hidden sm:inline">Ocultar</span>
            </>
          ) : (
            <>
              <span>▶</span>
              <span className="hidden sm:inline">Mostrar</span>
            </>
          )}
        </button>
      </div>
      
      <div 
        className="relative overflow-y-auto overflow-x-auto"
        style={{ 
          minWidth: `${actualLeftColumnWidth + totalIntervals * 20}px`,
          scrollbarWidth: 'thin'
        }}
      >
        {/* Cabeçalho com intervalos de tempo */}
        <div className="sticky top-0 bg-white z-10 mb-2" style={{ height: `${headerHeight}px`, marginLeft: `${actualLeftColumnWidth}px` }}>
          <div className="relative border-b-2 border-vtal-gray-300">
            {intervals.map((interval, index) => {
              // Mostrar apenas horas cheias ou intervalos de 30 minutos para não ficar muito poluído
              const minutes = interval.getMinutes();
              const shouldShow = minutes === 0 || minutes === 30;
              
              if (!shouldShow) return null;
              
              const intervalHour = interval.getHours();
              const isCurrentHourColumn = minutes === 0 && intervalHour === currentHour;
              
              return (
                <div
                  key={index}
                  className={`absolute border-l ${
                    isCurrentHourColumn 
                      ? 'border-blue-500 border-2 text-blue-700 font-bold' 
                      : 'border-vtal-gray-200 text-vtal-gray-600'
                  }`}
                  style={{
                    left: `${totalIntervals > 1 ? (index / (totalIntervals - 1)) * 100 : 0}%`,
                    paddingLeft: '2px',
                    paddingTop: '2px',
                    fontSize: isCurrentHourColumn ? '10px' : '8.4px', // Maior se for a hora atual
                    backgroundColor: isCurrentHourColumn ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    zIndex: isCurrentHourColumn ? 10 : 1
                  }}
                >
                  {format(interval, "HH'h'")}
                  {isCurrentHourColumn && <span className="ml-1">⭐</span>}
                </div>
              );
            })}
          </div>
          <div className="relative border-b border-vtal-gray-200" style={{ height: '30px' }}>
            {intervals.map((interval, index) => {
              if (index === 0 || index === intervals.length - 1) return null;
              const minutes = interval.getMinutes();
              // Linha mais grossa para horas cheias, mais fina para intervalos de 15 minutos
              const isHour = minutes === 0;
              const intervalHour = interval.getHours();
              const isCurrentHourColumn = isHour && intervalHour === currentHour;
              
              return (
                <div
                  key={`line-${index}`}
                  className={`absolute border-l ${
                    isCurrentHourColumn 
                      ? 'border-blue-500 border-2 bg-blue-50 bg-opacity-20' 
                      : isHour 
                        ? 'border-vtal-gray-300' 
                        : 'border-vtal-gray-100'
                  }`}
                  style={{
                    left: `${totalIntervals > 1 ? (index / (totalIntervals - 1)) * 100 : 0}%`,
                    height: '100%',
                    zIndex: isCurrentHourColumn ? 5 : 0
                  }}
                />
              );
            })}
            {/* Linha vertical do horário atual */}
            {currentTimePosition !== null && (
              <div
                className="absolute border-l-2 border-red-500 z-20 pointer-events-none"
                style={{
                  left: `${currentTimePosition}%`,
                  height: '100%',
                  boxShadow: '0 0 4px rgba(239, 68, 68, 0.5)'
                }}
                title={`Horário atual: ${format(currentTime, "dd/MM/yyyy HH'h'mm")}`}
              />
            )}
          </div>
        </div>

        {/* Linhas de atividades agrupadas por CRQ */}
        <div className="space-y-4">
          {Object.entries(activitiesBySequencia)
            .sort(([seqA], [seqB]) => {
              // Ordenar: REDE primeiro, depois as outras em ordem alfabética
              if (seqA === 'REDE') return -1;
              if (seqB === 'REDE') return 1;
              return seqA.localeCompare(seqB);
            })
            .map(([sequencia, seqActivities]) => {
            // Ordenar atividades por início
            const sortedActivities = [...seqActivities].sort((a, b) => {
              try {
                const aInicio = parseDate(a.inicio);
                const bInicio = parseDate(b.inicio);
                if (!aInicio || !bInicio) return 0;
                return aInicio - bInicio;
              } catch {
                return 0;
              }
            });

            return (
              <div key={sequencia} className="mb-3">
                {/* Cabeçalho da sequência */}
                <div className="font-bold text-sm text-vtal-gray-800 mb-1 px-2 py-0.5 bg-vtal-light rounded">
                  {sequencia}
                </div>

                {/* Lista de atividades individuais */}
                {sortedActivities.map((activity, rowIndex) => {
                  const activityName = activity.atividade || `Atividade ${activity.seq}`;
                  const abbreviatedName = abbreviateActivityName(activityName);
                  const needsAbbreviation = activityName.length > maxActivityNameLength;
                  
                  return (
                    <div key={`${activity.seq}-${activity.sequencia}-${activity.excel_data_id || rowIndex}`} className="mb-1">
                      {/* Nome da atividade */}
                      <div className="flex items-center">
                        <div
                          className={`font-medium text-[10px] text-vtal-gray-700 pr-4 cursor-help transition-all duration-300 overflow-hidden ${
                            leftColumnVisible ? 'opacity-100' : 'opacity-0 w-0'
                          }`}
                          style={{ 
                            width: leftColumnVisible ? `${leftColumnWidth}px` : '0px',
                            flexShrink: 0
                          }}
                          title={needsAbbreviation ? activityName : `${activityName}${activity.grupo ? ` (Grupo: ${activity.grupo})` : ''}`}
                        >
                          {abbreviatedName}
                        </div>
                        <div 
                          className="flex-1 relative border border-vtal-gray-200 rounded" 
                          style={{ 
                            height: `${rowHeight}px`,
                            padding: '2px'
                          }}
                        >
                          {/* Linhas de grade */}
                          {intervals.map((interval, index) => {
                            if (index === 0) return null;
                            const minutes = interval.getMinutes();
                            const isHour = minutes === 0;
                            const intervalHour = interval.getHours();
                            // Destacar a coluna da hora atual
                            const isCurrentHourColumn = isHour && intervalHour === currentHour;
                            
                            return (
                              <div
                                key={`grid-${index}`}
                                className={`absolute border-l ${
                                  isCurrentHourColumn 
                                    ? 'border-blue-500 border-2 bg-blue-50 bg-opacity-30' 
                                    : isHour 
                                      ? 'border-vtal-gray-200' 
                                      : 'border-vtal-gray-100'
                                }`}
                                style={{
                                  left: `${totalIntervals > 1 ? (index / (totalIntervals - 1)) * 100 : 0}%`,
                                  height: '100%',
                                  top: 0,
                                  zIndex: isCurrentHourColumn ? 5 : 0
                                }}
                              />
                            );
                          })}
                          
                          {/* Linha vertical do horário atual */}
                          {currentTimePosition !== null && (
                            <div
                              className="absolute border-l-2 border-red-500 z-20 pointer-events-none"
                              style={{
                                left: `${currentTimePosition}%`,
                                height: '100%',
                                top: 0,
                                boxShadow: '0 0 4px rgba(239, 68, 68, 0.5)'
                              }}
                            />
                          )}
                          
                          {/* Barra da atividade */}
                          {renderActivityBar(activity, rowIndex)}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>

      {/* Tooltip customizado */}
      {tooltip && (
        <div
          className="fixed z-50 bg-white border-2 border-vtal-secondary rounded-lg shadow-xl p-4 pointer-events-none"
          style={{
            left: `${tooltipPosition.x + 15}px`,
            top: `${tooltipPosition.y - 15}px`,
            transform: 'translateY(-100%)',
            minWidth: '280px',
            maxWidth: '400px',
            fontSize: '16px'
          }}
        >
          <div className="space-y-2">
            <div className="font-bold text-lg text-vtal-gray-800 border-b border-vtal-gray-200 pb-2">
              {tooltip.atividade}
            </div>
            <div className="space-y-1 text-base">
              <div><strong className="text-vtal-gray-700">CRQ:</strong> {tooltip.sequencia}</div>
              <div><strong className="text-vtal-gray-700">Seq:</strong> {tooltip.seq}</div>
              <div><strong className="text-vtal-gray-700">Grupo:</strong> {tooltip.grupo}</div>
              <div><strong className="text-vtal-gray-700">Status:</strong> 
                <span className={`ml-2 font-semibold ${
                  tooltip.status === 'Concluído' ? 'text-green-600' :
                  tooltip.status?.includes('fora do prazo') ? 'text-red-600' :
                  tooltip.status?.includes('no prazo') ? 'text-blue-600' :
                  'text-vtal-gray-600'
                }`}>
                  {tooltip.status}
                </span>
              </div>
              <div><strong className="text-vtal-gray-700">Início Planejado:</strong> {tooltip.inicio}</div>
              <div><strong className="text-vtal-gray-700">Fim Planejado:</strong> {tooltip.fim}</div>
              <div><strong className="text-vtal-gray-700">Tempo:</strong> {tooltip.tempo}</div>
              <div className="flex items-center gap-2 mt-2 pt-2 border-t border-vtal-gray-200">
                {tooltip.isRollback && (
                  <span className="px-2 py-1 bg-red-100 text-red-800 text-sm font-semibold rounded">ROLLBACK</span>
                )}
                {tooltip.isEncerramento && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-sm font-semibold rounded">ENCERRAMENTO</span>
                )}
                {!tooltip.isRollback && !tooltip.isEncerramento && (
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded">PRINCIPAL</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Legenda */}
      <div className="mt-6 flex items-center space-x-6 text-sm">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-4 rounded" style={{ backgroundColor: '#065F46' }}></div>
          <span className="text-vtal-gray-700">Atividade Principal</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-6 h-4 rounded" style={{ backgroundColor: '#991B1B' }}></div>
          <span className="text-vtal-gray-700">Atividade Rollback</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-6 h-4 rounded" style={{ backgroundColor: '#0066CC' }}></div>
          <span className="text-vtal-gray-700">Encerramento</span>
        </div>
      </div>
    </div>
  );
};

export default GanttChart;
