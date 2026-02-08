# Comparação: Queries SQL vs. Backend

Este documento ajuda a verificar se as queries SQL fornecidas correspondem à lógica implementada no backend.

## 📋 Checklist de Verificação

Para verificar se o backend usa consultas semelhantes, verifique os seguintes pontos no código do backend:

### 1. **Endpoint `/api/statistics`**

**Arquivo:** `CRQExecComMgmtBackend/server.js` (ou similar)

**O que verificar:**
```javascript
// Deve aceitar parâmetro rollback
app.get('/api/statistics', async (req, res) => {
  const rollbackFilter = req.query.rollback || 'all';
  // ...
});
```

### 2. **Filtro de Milestones**

**O que verificar:**
- ✅ Backend deve excluir milestones: `is_milestone = 0` ou `is_milestone = false`
- ✅ Em JavaScript: `activity.is_milestone === false` ou `activity.is_milestone === 0`

**Query SQL equivalente:**
```sql
WHERE is_milestone = 0
```

### 3. **Filtro de Rollback**

**O que verificar:**
- ✅ Quando `rollback = 'principal'`: `is_rollback = 0` ou `is_rollback IS NULL`
- ✅ Quando `rollback = 'rollback'`: `is_rollback = 1`

**Query SQL equivalente:**
```sql
-- Principais
WHERE (is_rollback = 0 OR is_rollback IS NULL)

-- Rollback
WHERE is_rollback = 1
```

### 4. **Cálculo de "Concluídas"**

**O que verificar no backend:**
```javascript
// Deve verificar:
- status.toLowerCase().includes('concluído') OU
- status.toLowerCase().includes('concluido') OU
- status.toLowerCase().includes('concluida') OU
- horario_fim_real !== null
```

**Query SQL equivalente:**
```sql
WHERE (
  LOWER(status) LIKE '%concluído%'
  OR LOWER(status) LIKE '%concluido%'
  OR LOWER(status) LIKE '%concluida%'
  OR horario_fim_real IS NOT NULL
)
```

### 5. **Cálculo de "Em Execução no Prazo"**

**O que verificar no backend:**
```javascript
// Deve verificar:
- status.toLowerCase().includes('em execução no prazo') OU
- status.toLowerCase().includes('em execucao no prazo')
- E horario_fim_real === null (não concluída)
```

**Query SQL equivalente:**
```sql
WHERE (
  LOWER(status) LIKE '%em execução no prazo%'
  OR LOWER(status) LIKE '%em execucao no prazo%'
)
AND horario_fim_real IS NULL
```

### 6. **Cálculo de "A Iniciar"**

**O que verificar no backend:**
```javascript
// Deve verificar:
- status.toLowerCase().includes('a iniciar no prazo') OU
- status.toLowerCase().includes('a iniciar fora do prazo')
- E horario_inicio_real === null (não iniciada)
```

**Query SQL equivalente:**
```sql
WHERE LOWER(status) LIKE '%a iniciar no prazo%'
AND (horario_inicio_real IS NULL OR horario_inicio_real = '')
```

## 🔍 Onde Verificar no Backend

### Arquivo 1: `server.js` ou `routes/statistics.js`
```javascript
// Procure por:
app.get('/api/statistics', ...)
// ou
router.get('/statistics', ...)
```

### Arquivo 2: `status_calculator.js`
```javascript
// Procure por:
function calculateActivityStatus(activity, control) {
  // Lógica de cálculo de status
}
```

### Arquivo 3: `database-supabase.js` ou similar
```javascript
// Procure por:
async getAllActivitiesControl() {
  // Query SQL ou uso do Supabase client
}
```

### Arquivo 4: Função de cálculo de estatísticas
```javascript
// Procure por:
function calculateStatistics(excelData, controlData, rollbackFilter) {
  // Lógica de contagem por status
}
```

## ⚠️ Diferenças Possíveis

### 1. **Status Calculado Dinamicamente**

O backend pode calcular o status baseado em datas, não apenas no campo `status` salvo:

```javascript
// Exemplo de lógica dinâmica:
const now = new Date();
if (activity.horario_fim_real) {
  status = 'Concluído';
} else if (activity.horario_inicio_real) {
  if (now <= activity.fim) {
    status = 'Em Execução no Prazo';
  } else {
    status = 'Em Execução Fora do Prazo';
  }
} else {
  if (now <= activity.inicio) {
    status = 'A Iniciar no Prazo';
  } else {
    status = 'A Iniciar Fora do Prazo';
  }
}
```

**Se isso acontecer:** As queries SQL precisarão incluir lógica de comparação de datas.

### 2. **Processamento em Memória vs. SQL**

O backend pode:
- **Opção A:** Fazer queries SQL diretas (similar às queries fornecidas)
- **Opção B:** Buscar todos os dados e processar em memória (queries SQL serão diferentes)

### 3. **Uso do Supabase Client**

O backend pode usar o cliente Supabase que abstrai as queries:

```javascript
const { data } = await supabase
  .from('activities')
  .select('*')
  .eq('is_milestone', false)
  .eq('is_rollback', rollbackFilter === 'rollback' ? 1 : 0);
```

## 📝 Como Verificar

### Passo 1: Acesse o Repositório do Backend
```bash
cd ../CRQExecComMgmtBackend
```

### Passo 2: Procure pelo Endpoint de Estatísticas
```bash
# Procure por "statistics" nos arquivos
grep -r "statistics" --include="*.js"
```

### Passo 3: Verifique a Lógica de Cálculo
- Abra o arquivo que contém o endpoint `/api/statistics`
- Verifique como os filtros são aplicados
- Compare com as queries SQL fornecidas

### Passo 4: Execute as Queries SQL
- Execute as queries SQL no Supabase
- Compare os resultados com o dashboard
- Se houver diferenças, verifique se o backend calcula o status dinamicamente

## ✅ Resultado Esperado

Se as queries SQL corresponderem ao backend, você deve ver:

1. ✅ Mesmo filtro de milestones (`is_milestone = 0`)
2. ✅ Mesmo filtro de rollback (`is_rollback = 0` ou `1`)
3. ✅ Mesma lógica para "Concluídas" (status OU horario_fim_real)
4. ✅ Mesma lógica para "Em Execução" (status E não concluída)
5. ✅ Mesma lógica para "A Iniciar" (status E não iniciada)

## 🔧 Se Houver Diferenças

Se as queries SQL não corresponderem exatamente:

1. **Verifique se o backend calcula o status dinamicamente**
   - Se sim, adicione lógica de comparação de datas nas queries SQL

2. **Verifique se há filtros adicionais**
   - Pode haver filtros por CRQ, data, ou outros critérios

3. **Verifique a estrutura da tabela**
   - Os nomes das colunas podem ser diferentes
   - Os tipos de dados podem ser diferentes (boolean vs. integer)

## 📌 Arquivos de Referência

- **Queries SQL:** `documentacoes/QUERIES_SQL_TOTALIZADORES.sql`
- **Documentação de Consultas:** `documentacoes/CONSULTAS_TOTALIZADORES_DASHBOARD.md`
- **Este arquivo:** `documentacoes/COMPARACAO_QUERIES_BACKEND.md`
