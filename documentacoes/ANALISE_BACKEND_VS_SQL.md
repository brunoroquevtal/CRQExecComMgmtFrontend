# Análise: Backend vs. Queries SQL

Este documento compara a lógica implementada no backend com as queries SQL fornecidas.

## 📋 Resumo da Análise

Após análise do código do backend (`CRQExecComMgmtBackend`), foi identificado que:

1. ✅ **O backend NÃO faz queries SQL diretas** - Ele usa o cliente Supabase que busca todos os dados e processa em memória
2. ✅ **A lógica de cálculo de status é dinâmica** - Baseada em datas e campos do banco
3. ⚠️ **O endpoint `/api/statistics` NÃO aplica filtro de rollback** - Apenas os endpoints de mensagem aplicam
4. ✅ **A lógica de filtros corresponde às queries SQL** - Com algumas diferenças importantes

## 🔍 Detalhamento da Lógica do Backend

### 1. Endpoint `/api/statistics` (server.js, linha 1691)

**Arquivo:** `CRQExecComMgmtBackend/server.js`

**Fluxo:**
1. Busca todos os dados: `loadExcelData()` e `getAllActivitiesControl()`
2. Itera sobre todas as atividades
3. Filtra atividades visíveis (`is_visible = 1`)
4. Calcula status usando `calculateActivityStatus()`
5. Ignora milestones (`is_milestone = true` ou status = 'N/A')
6. Conta por status

**Código relevante:**
```javascript
// Linha 1751-1777
for (const row of data.dataframe) {
  // Filtrar apenas atividades visíveis
  if (row.is_visible !== 1 && row.is_visible !== true) {
    continue;
  }
  
  // Calcular status
  const calculatedStatus = calculateActivityStatus(
    { seq: seqNum, sequencia, inicio: row.inicio, fim: row.fim },
    control
  );
  
  // Ignorar milestones
  if (calculatedStatus === 'N/A' || control.is_milestone) {
    continue;
  }
  
  // Contar por status...
}
```

**⚠️ IMPORTANTE:** Este endpoint **NÃO aplica filtro de rollback**! Ele processa todas as atividades.

### 2. Cálculo de Status (status_calculator.js)

**Arquivo:** `CRQExecComMgmtBackend/status_calculator.js`

**Lógica:**
1. Se é milestone → retorna 'N/A'
2. Se status salvo contém "concluído" → retorna 'Concluído'
3. Se `horario_fim_real` está preenchido → retorna 'Concluído'
4. Se `horario_inicio_real` está preenchido e `horario_fim_real` está vazio:
   - Se `atraso_minutos > 0` → 'Em execução fora do prazo'
   - Senão → 'Em execução no prazo'
5. Se `horario_inicio_real` está vazio:
   - Se `atraso_minutos > 0` → 'A Iniciar fora do prazo'
   - Senão → 'A Iniciar no prazo'

**Código relevante:**
```javascript
// Linha 13-67
function calculateActivityStatus(activity, control) {
  // Se é milestone
  if (control.is_milestone) {
    return 'N/A';
  }
  
  // Priorizar status salvo
  if (control.status) {
    const statusLower = String(control.status).toLowerCase().trim();
    if (statusLower.includes('concluído') || statusLower.includes('concluido')) {
      return 'Concluído';
    }
    // ... outros status salvos
  }
  
  // Se está concluída (tem horario_fim_real)
  if (control.horario_fim_real) {
    return 'Concluído';
  }
  
  // Verificar se está em execução
  const isInExecution = control.horario_inicio_real && !control.horario_fim_real;
  const isDelayed = (control.atraso_minutos || 0) > 0;
  
  if (isInExecution) {
    return isDelayed ? 'Em execução fora do prazo' : 'Em execução no prazo';
  } else {
    return isDelayed ? 'A Iniciar fora do prazo' : 'A Iniciar no prazo';
  }
}
```

### 3. Filtro de Rollback (message_builder.js)

**Arquivo:** `CRQExecComMgmtBackend/message_builder.js`

**Aplicado apenas em:**
- `/api/message` (linha 2183)
- `/api/message-detailed` (linha 2204)

**Lógica:**
```javascript
// Linha 52-62
if (rollbackFilter === 'rollback') {
  // Mostrar apenas rollback
  if (!row.is_rollback && !control.is_rollback) {
    continue;
  }
} else if (rollbackFilter === 'principal') {
  // Mostrar apenas principais (não rollback)
  if (row.is_rollback || control.is_rollback) {
    continue;
  }
}
```

**⚠️ IMPORTANTE:** O endpoint `/api/statistics` **NÃO aplica este filtro**!

### 4. Busca de Dados (database-supabase.js)

**Arquivo:** `CRQExecComMgmtBackend/database-supabase.js`

**Método `loadExcelData()` (linha 200-264):**
- Busca todas as atividades da tabela `activities`
- Filtra por `is_visible = 1` (por padrão)
- Agrupa por `sequencia`
- **NÃO aplica filtro de rollback ou milestones na query**

**Método `getAllActivitiesControl()` (linha 314-360):**
- Busca todas as atividades da tabela `activities`
- Converte para formato de dicionário (chave: `seq_sequencia`)
- **NÃO aplica filtros na query**

## 🔄 Comparação: Backend vs. Queries SQL

### ✅ Correspondências

1. **Filtro de Milestones:**
   - **Backend:** `if (calculatedStatus === 'N/A' || control.is_milestone) continue;`
   - **SQL:** `WHERE is_milestone = 0`
   - ✅ **Corresponde**

2. **Filtro de Atividades Visíveis:**
   - **Backend:** `if (row.is_visible !== 1 && row.is_visible !== true) continue;`
   - **SQL:** `WHERE is_visible = 1` (não incluído nas queries, mas deveria ser)
   - ⚠️ **Queries SQL não incluem este filtro**

3. **Cálculo de "Concluídas":**
   - **Backend:** `statusLower.includes('concluído') || control.horario_fim_real`
   - **SQL:** `LOWER(status) LIKE '%concluído%' OR horario_fim_real IS NOT NULL`
   - ✅ **Corresponde**

4. **Cálculo de "Em Execução no Prazo":**
   - **Backend:** `statusLower.includes('em execução no prazo')` (após calcular status)
   - **SQL:** `LOWER(status) LIKE '%em execução no prazo%' AND horario_fim_real IS NULL`
   - ✅ **Corresponde** (com ressalva: backend calcula dinamicamente)

5. **Cálculo de "A Iniciar":**
   - **Backend:** `statusLower.includes('a iniciar')` (após calcular status)
   - **SQL:** `LOWER(status) LIKE '%a iniciar%' AND horario_inicio_real IS NULL`
   - ✅ **Corresponde** (com ressalva: backend calcula dinamicamente)

### ⚠️ Diferenças Importantes

1. **Filtro de Rollback:**
   - **Backend:** NÃO aplicado no endpoint `/api/statistics`
   - **SQL:** Incluído nas queries
   - ⚠️ **Diferença crítica**: O backend não filtra por rollback nas estatísticas!

2. **Cálculo Dinâmico de Status:**
   - **Backend:** Calcula status baseado em datas (`atraso_minutos`, `horario_inicio_real`, `horario_fim_real`)
   - **SQL:** Usa apenas o campo `status` salvo
   - ⚠️ **Diferença importante**: Se o status não estiver salvo no banco, as queries SQL podem não corresponder

3. **Filtro de Atividades Visíveis:**
   - **Backend:** Sempre filtra `is_visible = 1`
   - **SQL:** Não incluído nas queries
   - ⚠️ **Diferença**: Queries SQL devem incluir `WHERE is_visible = 1`

4. **Processamento:**
   - **Backend:** Busca todos os dados e processa em memória
   - **SQL:** Queries diretas no banco
   - ✅ **Ambos válidos**, mas resultados podem diferir se o status não estiver salvo

## 📝 Recomendações

### 1. Adicionar Filtro de Rollback no Endpoint `/api/statistics`

O endpoint `/api/statistics` deveria aceitar o parâmetro `rollback` e aplicar o filtro:

```javascript
// Adicionar no início do endpoint (linha 1691)
const rollbackFilter = req.query.rollback || 'all';

// Adicionar no loop (após linha 1756)
if (rollbackFilter === 'rollback') {
  if (!row.is_rollback && !control.is_rollback) {
    continue;
  }
} else if (rollbackFilter === 'principal') {
  if (row.is_rollback || control.is_rollback) {
    continue;
  }
}
```

### 2. Atualizar Queries SQL

As queries SQL devem incluir:

1. **Filtro de atividades visíveis:**
   ```sql
   WHERE is_milestone = 0
     AND is_visible = 1
   ```

2. **Considerar cálculo dinâmico de status:**
   - Se o status não estiver salvo, usar lógica baseada em datas
   - Verificar `atraso_minutos` para determinar se está atrasado

### 3. Sincronizar Status no Banco

Para que as queries SQL correspondam exatamente ao backend, o status deve estar sempre salvo no banco:

- Quando uma atividade é atualizada, salvar o status calculado
- Garantir que `status` sempre reflita o estado atual

## ✅ Conclusão

As queries SQL fornecidas são **parcialmente equivalentes** à lógica do backend, mas há diferenças importantes:

1. ✅ Filtro de milestones: **Corresponde**
2. ✅ Cálculo de status: **Corresponde** (se status estiver salvo)
3. ⚠️ Filtro de rollback: **NÃO aplicado no endpoint `/api/statistics`**
4. ⚠️ Filtro de atividades visíveis: **Não incluído nas queries SQL**
5. ⚠️ Cálculo dinâmico: **Backend calcula, SQL usa campo salvo**

**Para correspondência exata:**
- Adicionar filtro de rollback no endpoint `/api/statistics`
- Incluir `is_visible = 1` nas queries SQL
- Garantir que o status esteja sempre salvo no banco
