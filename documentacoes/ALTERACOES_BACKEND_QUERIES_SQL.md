# Alterações no Backend: Implementação de Queries SQL Equivalentes

Este documento descreve as alterações realizadas no backend para usar lógica equivalente às queries SQL fornecidas.

## 📋 Resumo das Alterações

### 1. Novo Método no DatabaseManager

**Arquivo:** `CRQExecComMgmtBackend/database-supabase.js`

**Método adicionado:** `calculateStatisticsSQL(rollbackFilter = 'all')`

Este método:
- ✅ Usa a API REST do Supabase com filtros equivalentes às queries SQL
- ✅ Filtra `is_milestone = 0` e `is_visible = 1` (sempre)
- ✅ Aplica filtro de rollback quando fornecido (`'all'`, `'principal'`, `'rollback'`)
- ✅ Calcula estatísticas baseado no campo `status` salvo e `horario_fim_real`
- ✅ Retorna estatísticas no mesmo formato do endpoint anterior

**Lógica implementada:**
1. Busca todas as atividades que atendem aos critérios base
2. Para cada atividade, verifica o status:
   - **Concluídas:** status contém "concluído" OU `horario_fim_real IS NOT NULL`
   - **Em Execução no Prazo:** status contém "em execução no prazo" E `horario_fim_real IS NULL`
   - **Em Execução Fora do Prazo:** status contém "em execução fora do prazo" E `horario_fim_real IS NULL`
   - **A Iniciar no Prazo:** status contém "a iniciar no prazo" E `horario_inicio_real IS NULL`
   - **A Iniciar Fora do Prazo:** status contém "a iniciar fora do prazo" E `horario_inicio_real IS NULL`

### 2. Atualização do Endpoint `/api/statistics`

**Arquivo:** `CRQExecComMgmtBackend/server.js`

**Alterações:**
- ✅ Substituído processamento em memória por chamada ao novo método `calculateStatisticsSQL()`
- ✅ Adicionado suporte ao parâmetro `rollback` na query string
- ✅ Simplificado código (de ~120 linhas para ~30 linhas)
- ✅ Melhor performance (uma query ao invés de buscar todos os dados)

**Antes:**
```javascript
// Buscava todos os dados e processava em memória
const excelData = await dbManager.loadExcelData();
const controlData = await dbManager.getAllActivitiesControl();
// ... processamento em memória ...
```

**Depois:**
```javascript
// Usa queries SQL equivalentes
const rollbackFilter = req.query.rollback || 'all';
const stats = await dbManager.calculateStatisticsSQL(rollbackFilter);
```

## 🔄 Compatibilidade

### Parâmetros Aceitos

O endpoint `/api/statistics` agora aceita:
- `?rollback=all` - Todas as atividades (padrão)
- `?rollback=principal` - Apenas atividades principais (não rollback)
- `?rollback=rollback` - Apenas atividades de rollback

### Formato de Resposta

O formato de resposta permanece o mesmo:

```json
{
  "geral": {
    "total": 100,
    "concluidas": 50,
    "em_execucao_no_prazo": 20,
    "em_execucao_fora_prazo": 10,
    "a_iniciar_no_prazo": 15,
    "a_iniciar_fora_prazo": 5
  },
  "por_sequencia": {
    "REDE": {
      "total": 50,
      "concluidas": 25,
      ...
    }
  }
}
```

## ✅ Benefícios

1. **Performance:** Uma query ao invés de buscar todos os dados
2. **Consistência:** Lógica equivalente às queries SQL fornecidas
3. **Filtro de Rollback:** Agora suportado no endpoint `/api/statistics`
4. **Manutenibilidade:** Código mais simples e direto
5. **Rastreabilidade:** Logs detalhados do processo

## ⚠️ Diferenças Importantes

### 1. Cálculo Dinâmico de Status

O método `calculateStatisticsSQL()` usa o campo `status` salvo no banco. Se o status não estiver salvo, pode não corresponder exatamente ao cálculo dinâmico do `status_calculator.js`.

**Solução:** Garantir que o status seja sempre salvo quando uma atividade é atualizada.

### 2. Filtro de Atividades Visíveis

O novo método sempre filtra `is_visible = 1`, correspondendo ao comportamento anterior.

### 3. Filtro de Milestones

O novo método sempre filtra `is_milestone = 0`, correspondendo ao comportamento anterior.

## 📝 Próximos Passos (Opcional)

1. **Garantir que o status seja sempre salvo:**
   - Quando uma atividade é atualizada, calcular e salvar o status
   - Usar `status_calculator.js` para calcular o status antes de salvar

2. **Adicionar cache (opcional):**
   - Cachear estatísticas por alguns segundos para melhorar performance
   - Invalidar cache quando atividades são atualizadas

3. **Adicionar testes:**
   - Testes unitários para `calculateStatisticsSQL()`
   - Testes de integração para o endpoint `/api/statistics`

## 🔍 Verificação

Para verificar se as alterações estão funcionando:

1. **Testar endpoint sem filtro:**
   ```bash
   GET /api/statistics
   ```

2. **Testar endpoint com filtro de rollback:**
   ```bash
   GET /api/statistics?rollback=principal
   GET /api/statistics?rollback=rollback
   ```

3. **Comparar com queries SQL:**
   - Execute as queries SQL fornecidas no Supabase
   - Compare os resultados com o endpoint
   - Devem corresponder (se o status estiver salvo)

## 📌 Arquivos Modificados

1. `CRQExecComMgmtBackend/database-supabase.js`
   - Adicionado método `calculateStatisticsSQL()`

2. `CRQExecComMgmtBackend/server.js`
   - Atualizado endpoint `/api/statistics`

## ✅ Status

- ✅ Método `calculateStatisticsSQL()` implementado
- ✅ Endpoint `/api/statistics` atualizado
- ✅ Filtro de rollback adicionado
- ✅ Lógica equivalente às queries SQL
- ✅ Compatibilidade mantida com formato de resposta anterior
