-- ============================================================================
-- QUERIES SQL PARA VERIFICAR TOTALIZADORES DO DASHBOARD
-- ============================================================================
-- Este arquivo contém as queries SQL equivalentes às consultas feitas pelo
-- backend para calcular os totalizadores do dashboard.
--
-- IMPORTANTE: 
-- 1. O backend usa Supabase (PostgreSQL) e pode calcular o status
--    dinamicamente baseado em datas, não apenas no campo 'status' salvo.
-- 2. O backend sempre filtra atividades visíveis (is_visible = 1)
-- 3. O endpoint /api/statistics NÃO aplica filtro de rollback
--    (apenas os endpoints de mensagem aplicam)
-- ============================================================================

-- ============================================================================
-- 1. TOTAL DE ATIVIDADES (excluindo milestones)
-- ============================================================================
-- Este total é calculado no frontend, mas aqui está a query equivalente:

-- Para TODAS as atividades (sem filtro de rollback):
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as total
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1;

-- Para ATIVIDADES PRINCIPAIS (sem rollback):
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as total
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND (is_rollback = 0 OR is_rollback IS NULL);

-- Para ATIVIDADES DE ROLLBACK:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as total
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND is_rollback = 1;

-- ============================================================================
-- 2. ATIVIDADES CONCLUÍDAS
-- ============================================================================
-- Critérios: status contém "concluído" OU horario_fim_real está preenchido

-- Todas as concluídas:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as concluidas
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND (
    -- Status contém "concluído" (múltiplas variações)
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
    OR LOWER(status) = 'concluído'
    OR LOWER(status) = 'concluido'
    OR LOWER(status) = 'concluida'
    -- OU tem horário de fim real
    OR horario_fim_real IS NOT NULL
  );

-- Concluídas - Principais:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as concluidas
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND (is_rollback = 0 OR is_rollback IS NULL)
  AND (
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
    OR LOWER(status) = 'concluído'
    OR LOWER(status) = 'concluido'
    OR LOWER(status) = 'concluida'
    OR horario_fim_real IS NOT NULL
  );

-- Concluídas - Rollback:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as concluidas
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND is_rollback = 1
  AND (
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
    OR LOWER(status) = 'concluído'
    OR LOWER(status) = 'concluido'
    OR LOWER(status) = 'concluida'
    OR horario_fim_real IS NOT NULL
  );

-- ============================================================================
-- 3. EM EXECUÇÃO NO PRAZO
-- ============================================================================
-- Critérios: status contém "em execução no prazo" E não está concluída

-- Todas:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as em_execucao_no_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND (
    LOWER(status) LIKE '%em execução no prazo%'
    OR LOWER(status) LIKE '%em execucao no prazo%'
  )
  AND horario_fim_real IS NULL  -- Não está concluída
  AND NOT (
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
  );

-- Principais:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as em_execucao_no_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND (is_rollback = 0 OR is_rollback IS NULL)
  AND (
    LOWER(status) LIKE '%em execução no prazo%'
    OR LOWER(status) LIKE '%em execucao no prazo%'
  )
  AND horario_fim_real IS NULL
  AND NOT (
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
  );

-- Rollback:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as em_execucao_no_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND is_rollback = 1
  AND (
    LOWER(status) LIKE '%em execução no prazo%'
    OR LOWER(status) LIKE '%em execucao no prazo%'
  )
  AND horario_fim_real IS NULL
  AND NOT (
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
  );

-- ============================================================================
-- 4. EM EXECUÇÃO FORA DO PRAZO
-- ============================================================================
-- Critérios: status contém "em execução fora do prazo" E não está concluída

-- Todas:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as em_execucao_fora_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND (
    LOWER(status) LIKE '%em execução fora do prazo%'
    OR LOWER(status) LIKE '%em execucao fora do prazo%'
  )
  AND horario_fim_real IS NULL
  AND NOT (
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
  );

-- Principais:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as em_execucao_fora_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND (is_rollback = 0 OR is_rollback IS NULL)
  AND (
    LOWER(status) LIKE '%em execução fora do prazo%'
    OR LOWER(status) LIKE '%em execucao fora do prazo%'
  )
  AND horario_fim_real IS NULL
  AND NOT (
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
  );

-- Rollback:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as em_execucao_fora_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND is_rollback = 1
  AND (
    LOWER(status) LIKE '%em execução fora do prazo%'
    OR LOWER(status) LIKE '%em execucao fora do prazo%'
  )
  AND horario_fim_real IS NULL
  AND NOT (
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
  );

-- ============================================================================
-- 5. A INICIAR NO PRAZO
-- ============================================================================
-- Critérios: status contém "a iniciar no prazo" E horario_inicio_real está vazio

-- Todas:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as a_iniciar_no_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND LOWER(status) LIKE '%a iniciar no prazo%'
  AND (horario_inicio_real IS NULL OR horario_inicio_real = '');

-- Principais:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as a_iniciar_no_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND (is_rollback = 0 OR is_rollback IS NULL)
  AND LOWER(status) LIKE '%a iniciar no prazo%'
  AND (horario_inicio_real IS NULL OR horario_inicio_real = '');

-- Rollback:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as a_iniciar_no_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND is_rollback = 1
  AND LOWER(status) LIKE '%a iniciar no prazo%'
  AND (horario_inicio_real IS NULL OR horario_inicio_real = '');

-- ============================================================================
-- 6. A INICIAR FORA DO PRAZO
-- ============================================================================
-- Critérios: status contém "a iniciar fora do prazo" E horario_inicio_real está vazio

-- Todas:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as a_iniciar_fora_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND LOWER(status) LIKE '%a iniciar fora do prazo%'
  AND (horario_inicio_real IS NULL OR horario_inicio_real = '');

-- Principais:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as a_iniciar_fora_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND (is_rollback = 0 OR is_rollback IS NULL)
  AND LOWER(status) LIKE '%a iniciar fora do prazo%'
  AND (horario_inicio_real IS NULL OR horario_inicio_real = '');

-- Rollback:
-- IMPORTANTE: Backend sempre filtra is_visible = 1
SELECT COUNT(*) as a_iniciar_fora_prazo
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND is_rollback = 1
  AND LOWER(status) LIKE '%a iniciar fora do prazo%'
  AND (horario_inicio_real IS NULL OR horario_inicio_real = '');

-- ============================================================================
-- QUERY COMPLETA PARA TODOS OS TOTALIZADORES (TODAS AS ATIVIDADES)
-- ============================================================================
-- Esta query retorna todos os totalizadores de uma vez:

SELECT 
  -- Total (excluindo milestones e ocultas)
  COUNT(*) FILTER (WHERE is_milestone = 0 AND is_visible = 1) as total,
  
  -- Concluídas
  COUNT(*) FILTER (
    WHERE is_milestone = 0
    AND is_visible = 1
    AND (
      LOWER(status) LIKE '%concluído%'
      OR LOWER(status) LIKE '%concluido%'
      OR LOWER(status) LIKE '%concluida%'
      OR horario_fim_real IS NOT NULL
    )
  ) as concluidas,
  
  -- Em Execução no Prazo
  COUNT(*) FILTER (
    WHERE is_milestone = 0
    AND (
      LOWER(status) LIKE '%em execução no prazo%'
      OR LOWER(status) LIKE '%em execucao no prazo%'
    )
    AND horario_fim_real IS NULL
    AND NOT (
      LOWER(status) LIKE '%concluído%'
      OR LOWER(status) LIKE '%concluido%'
      OR LOWER(status) LIKE '%concluida%'
    )
  ) as em_execucao_no_prazo,
  
  -- Em Execução Fora do Prazo
  COUNT(*) FILTER (
    WHERE is_milestone = 0
    AND (
      LOWER(status) LIKE '%em execução fora do prazo%'
      OR LOWER(status) LIKE '%em execucao fora do prazo%'
    )
    AND horario_fim_real IS NULL
    AND NOT (
      LOWER(status) LIKE '%concluído%'
      OR LOWER(status) LIKE '%concluido%'
      OR LOWER(status) LIKE '%concluida%'
    )
  ) as em_execucao_fora_prazo,
  
  -- A Iniciar no Prazo
  COUNT(*) FILTER (
    WHERE is_milestone = 0
    AND LOWER(status) LIKE '%a iniciar no prazo%'
    AND (horario_inicio_real IS NULL OR horario_inicio_real = '')
  ) as a_iniciar_no_prazo,
  
  -- A Iniciar Fora do Prazo
  COUNT(*) FILTER (
    WHERE is_milestone = 0
    AND LOWER(status) LIKE '%a iniciar fora do prazo%'
    AND (horario_inicio_real IS NULL OR horario_inicio_real = '')
  ) as a_iniciar_fora_prazo,
  
  -- Milestones (para referência)
  COUNT(*) FILTER (WHERE is_milestone = 1) as milestones
  
FROM activities
WHERE is_visible = 1;  -- IMPORTANTE: Backend sempre filtra is_visible = 1

-- ============================================================================
-- QUERY COM FILTRO DE ROLLBACK (PRINCIPAIS)
-- ============================================================================

SELECT 
  COUNT(*) FILTER (WHERE is_milestone = 0) as total,
  COUNT(*) FILTER (
    WHERE is_milestone = 0
    AND (
      LOWER(status) LIKE '%concluído%'
      OR LOWER(status) LIKE '%concluido%'
      OR LOWER(status) LIKE '%concluida%'
      OR horario_fim_real IS NOT NULL
    )
  ) as concluidas,
  COUNT(*) FILTER (
    WHERE is_milestone = false
    AND (
      LOWER(status) LIKE '%em execução no prazo%'
      OR LOWER(status) LIKE '%em execucao no prazo%'
    )
    AND horario_fim_real IS NULL
  ) as em_execucao_no_prazo,
  COUNT(*) FILTER (
    WHERE is_milestone = false
    AND (
      LOWER(status) LIKE '%em execução fora do prazo%'
      OR LOWER(status) LIKE '%em execucao fora do prazo%'
    )
    AND horario_fim_real IS NULL
  ) as em_execucao_fora_prazo,
  COUNT(*) FILTER (
    WHERE is_milestone = false
    AND LOWER(status) LIKE '%a iniciar no prazo%'
    AND (horario_inicio_real IS NULL OR horario_inicio_real = '')
  ) as a_iniciar_no_prazo,
  COUNT(*) FILTER (
    WHERE is_milestone = false
    AND LOWER(status) LIKE '%a iniciar fora do prazo%'
    AND (horario_inicio_real IS NULL OR horario_inicio_real = '')
  ) as a_iniciar_fora_prazo
FROM activities
WHERE is_visible = 1
  AND (is_rollback = 0 OR is_rollback IS NULL);

-- ============================================================================
-- QUERY COM FILTRO DE ROLLBACK (ROLLBACK)
-- ============================================================================

SELECT 
  COUNT(*) FILTER (WHERE is_milestone = 0) as total,
  COUNT(*) FILTER (
    WHERE is_milestone = 0
    AND (
      LOWER(status) LIKE '%concluído%'
      OR LOWER(status) LIKE '%concluido%'
      OR LOWER(status) LIKE '%concluida%'
      OR horario_fim_real IS NOT NULL
    )
  ) as concluidas,
  COUNT(*) FILTER (
    WHERE is_milestone = false
    AND (
      LOWER(status) LIKE '%em execução no prazo%'
      OR LOWER(status) LIKE '%em execucao no prazo%'
    )
    AND horario_fim_real IS NULL
  ) as em_execucao_no_prazo,
  COUNT(*) FILTER (
    WHERE is_milestone = false
    AND (
      LOWER(status) LIKE '%em execução fora do prazo%'
      OR LOWER(status) LIKE '%em execucao fora do prazo%'
    )
    AND horario_fim_real IS NULL
  ) as em_execucao_fora_prazo,
  COUNT(*) FILTER (
    WHERE is_milestone = false
    AND LOWER(status) LIKE '%a iniciar no prazo%'
    AND (horario_inicio_real IS NULL OR horario_inicio_real = '')
  ) as a_iniciar_no_prazo,
  COUNT(*) FILTER (
    WHERE is_milestone = false
    AND LOWER(status) LIKE '%a iniciar fora do prazo%'
    AND (horario_inicio_real IS NULL OR horario_inicio_real = '')
  ) as a_iniciar_fora_prazo
FROM activities
WHERE is_visible = 1
  AND is_rollback = 1;

-- ============================================================================
-- QUERY PARA VERIFICAR DISTRIBUIÇÃO DE STATUS
-- ============================================================================
-- Use esta query para ver quantas atividades têm cada status:

SELECT 
  status,
  COUNT(*) as quantidade,
  COUNT(*) FILTER (WHERE is_milestone = 0) as atividades,
  COUNT(*) FILTER (WHERE is_milestone = 1) as milestones
FROM activities
GROUP BY status
ORDER BY quantidade DESC;

-- ============================================================================
-- QUERY PARA VERIFICAR ATIVIDADES COM STATUS INCONSISTENTE
-- ============================================================================
-- Atividades que têm horario_fim_real mas status não indica concluído:

SELECT 
  seq,
  sequencia,
  atividade,
  status,
  horario_fim_real,
  is_rollback,
  is_milestone
FROM activities
WHERE is_milestone = 0
  AND is_visible = 1
  AND horario_fim_real IS NOT NULL
  AND NOT (
    LOWER(status) LIKE '%concluído%'
    OR LOWER(status) LIKE '%concluido%'
    OR LOWER(status) LIKE '%concluida%'
  )
ORDER BY sequencia, seq;

-- ============================================================================
-- QUERY PARA VERIFICAR DISTRIBUIÇÃO POR ROLLBACK
-- ============================================================================

SELECT 
  CASE 
    WHEN is_rollback = 1 THEN 'Rollback'
    WHEN is_rollback = 0 OR is_rollback IS NULL THEN 'Principal'
    ELSE 'Indefinido'
  END as tipo,
  COUNT(*) FILTER (WHERE is_milestone = 0) as total_atividades,
  COUNT(*) FILTER (WHERE is_milestone = 1) as total_milestones
FROM activities
GROUP BY 
  CASE 
    WHEN is_rollback = 1 THEN 'Rollback'
    WHEN is_rollback = 0 OR is_rollback IS NULL THEN 'Principal'
    ELSE 'Indefinido'
  END;

-- ============================================================================
-- NOTAS IMPORTANTES
-- ============================================================================
-- 1. O backend pode calcular o status dinamicamente baseado em datas,
--    não apenas no campo 'status' salvo. Essas queries usam apenas o campo
--    'status' salvo no banco.
--
-- 2. Se o backend calcular o status dinamicamente, você precisará adicionar
--    lógica adicional baseada em:
--    - inicio (data/hora planejada de início)
--    - fim (data/hora planejada de fim)
--    - horario_inicio_real (data/hora real de início)
--    - horario_fim_real (data/hora real de fim)
--    - Comparação com a data/hora atual
--
-- 3. Para verificar exatamente como o backend calcula, consulte o arquivo
--    status_calculator.js no repositório do backend.
--
-- 4. O nome da tabela pode ser 'activities' ou outro nome. Verifique no
--    seu banco de dados.
-- ============================================================================
