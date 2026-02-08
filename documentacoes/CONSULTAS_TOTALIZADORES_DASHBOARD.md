# Consultas e Cálculos dos Totalizadores do Dashboard

Este documento explica como os totalizadores do dashboard são calculados e quais consultas são feitas.

## 📊 Fonte de Dados

O dashboard obtém dados de **duas APIs**:

1. **`GET /api/statistics?rollback={filtro}`** - Retorna estatísticas calculadas pelo backend
2. **`GET /api/activities`** - Retorna todas as atividades para filtragem no frontend

## 🔍 Totalizadores Exibidos

### 1. **Total** (📋)
- **Fonte**: Calculado no **frontend** baseado nas atividades filtradas
- **Cálculo**: 
  ```javascript
  atividadesFiltradasPorRollback = filterByRollback(activities.filter(a => !a.is_milestone))
  totalFiltrado = atividadesFiltradasPorRollback.length
  ```
- **Filtros aplicados**:
  - ✅ Exclui milestones (`is_milestone = false`)
  - ✅ Aplica filtro de rollback (`rollbackFilter`: 'all', 'principal', 'rollback')
  - ✅ Respeita a aba de CRQ selecionada (se houver)

### 2. **Concluídas** (✅)
- **Fonte**: Vem do backend via `statistics.geral.concluidas`
- **Cálculo no Backend**: 
  - Conta atividades onde:
    - `status` contém "Concluído", "Concluido" ou "Concluida" **OU**
    - `horario_fim_real` está preenchido
  - Exclui milestones
  - Aplica filtro de rollback (se fornecido)

### 3. **Em Execução no Prazo** (⏳)
- **Fonte**: Vem do backend via `statistics.geral.em_execucao_no_prazo`
- **Cálculo no Backend**:
  - Conta atividades onde:
    - `status` contém "em execução no prazo" **E**
    - Não está concluída (`horario_fim_real` está vazio)
  - Exclui milestones
  - Aplica filtro de rollback (se fornecido)

### 4. **Em Execução Fora do Prazo** (🔴)
- **Fonte**: Vem do backend via `statistics.geral.em_execucao_fora_prazo`
- **Cálculo no Backend**:
  - Conta atividades onde:
    - `status` contém "em execução fora do prazo" **E**
    - Não está concluída
  - Exclui milestones
  - Aplica filtro de rollback (se fornecido)

### 5. **A Iniciar no Prazo** (🟦)
- **Fonte**: Vem do backend via `statistics.geral.a_iniciar_no_prazo`
- **Cálculo no Backend**:
  - Conta atividades onde:
    - `status` contém "a iniciar no prazo" **E**
    - `horario_inicio_real` está vazio (não foi iniciada)
  - Exclui milestones
  - Aplica filtro de rollback (se fornecido)

### 6. **A Iniciar Fora do Prazo** (🟠)
- **Fonte**: Vem do backend via `statistics.geral.a_iniciar_fora_prazo`
- **Cálculo no Backend**:
  - Conta atividades onde:
    - `status` contém "a iniciar fora do prazo" **E**
    - `horario_inicio_real` está vazio
  - Exclui milestones
  - Aplica filtro de rollback (se fornecido)

## 🔄 Filtro de Rollback

O filtro de rollback é aplicado **no backend** quando o parâmetro `rollback` é enviado:

- **`rollback=all`**: Todas as atividades (padrão)
- **`rollback=principal`**: Apenas atividades principais (`is_rollback = false` ou `is_rollback = 0`)
- **`rollback=rollback`**: Apenas atividades de rollback (`is_rollback = true` ou `is_rollback = 1`)

## 📝 Consultas SQL (Backend)

As queries SQL exatas estão disponíveis no arquivo **`QUERIES_SQL_TOTALIZADORES.sql`**.

Este arquivo contém:
- ✅ Queries individuais para cada totalizador
- ✅ Queries com filtro de rollback (todas, principais, rollback)
- ✅ Query completa que retorna todos os totalizadores de uma vez
- ✅ Queries de verificação e diagnóstico

**📄 Ver arquivo completo:** `documentacoes/QUERIES_SQL_TOTALIZADORES.sql`

## ⚠️ Diferenças Possíveis

Se você está vendo quantidades diferentes no banco de dados, verifique:

1. **Milestones**: Os totalizadores **excluem milestones** (`is_milestone = true`)
2. **Status calculado vs. salvo**: O backend pode calcular o status dinamicamente baseado em datas, não apenas no campo `status` salvo
3. **Filtro de rollback**: Certifique-se de que está comparando com o mesmo filtro aplicado
4. **Aba de CRQ**: Se uma aba específica está selecionada, apenas atividades daquele CRQ são contadas
5. **Status com variações**: O sistema aceita múltiplas variações de "concluído" (com/sem acento, singular/plural)

## 🔧 Como Verificar

Para verificar se as consultas estão corretas:

1. **No Frontend**: Abra o console do navegador e veja os logs:
   ```
   [Dashboard] Carregando dados com filtro de rollback: all
   [Dashboard] Estatísticas recebidas: {geral: {...}, por_sequencia: {...}}
   ```

2. **No Backend**: Verifique os logs do servidor para ver as queries SQL executadas

3. **No Banco de Dados**: Execute queries similares às descritas acima, lembrando de:
   - Excluir milestones
   - Aplicar filtro de rollback (se necessário)
   - Verificar múltiplas variações de status

## 📌 Notas Importantes

- O **Total** é calculado no frontend e pode diferir do backend se houver filtros adicionais
- Os outros totalizadores vêm do backend e são calculados usando a lógica do `status_calculator.js`
- O status pode ser calculado dinamicamente baseado em datas, não apenas no campo `status` salvo no banco
