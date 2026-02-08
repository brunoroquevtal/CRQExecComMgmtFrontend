# Análise da Lógica de `is_visible`

Este documento analisa a lógica de `is_visible` e identifica problemas encontrados.

## ✅ O Que Está Funcionando

### 1. Cálculo de `is_visible`

**Arquivo:** `activity-validation-helper.js`

A função `validateActivity()` calcula `is_visible` corretamente baseado nas regras de configuração:
- ✅ Usa `validationConfig.visibility.useValidationRules` para determinar se usa as mesmas regras de validação
- ✅ Calcula baseado em: Seq válido, Atividade não vazia, (Inicio OU Fim), (grupo OU status não vazios)
- ✅ Retorna `isVisible: 0` ou `isVisible: 1`

### 2. Filtro em `loadExcelData()`

**Arquivo:** `database-supabase.js`

O método `loadExcelData(includeHidden = false)` filtra corretamente:
- ✅ Por padrão, filtra `is_visible = 1` (apenas visíveis)
- ✅ Se `includeHidden = true`, carrega todas as atividades

### 3. Filtro em `calculateStatisticsSQL()`

**Arquivo:** `database-supabase.js`

O método `calculateStatisticsSQL()` filtra corretamente:
- ✅ Sempre filtra `is_visible = 1`
- ✅ Usado no endpoint `/api/statistics`

### 4. Filtro no endpoint `/api/activities`

**Arquivo:** `server.js`

O endpoint filtra corretamente:
- ✅ Usa `loadExcelData(false)` - apenas visíveis
- ✅ Verifica novamente `is_visible` no loop (dupla verificação)

## ⚠️ Problemas Encontrados

### 1. `getAllActivitiesControl()` NÃO filtra por `is_visible`

**Arquivo:** `database-supabase.js`, linha 336

**Problema:**
```javascript
async getAllActivitiesControl() {
  const { data: rows, error } = await this.supabase
    .from('activities')
    .select('*');  // ❌ NÃO filtra por is_visible!
  // ...
}
```

**Impacto:**
- Atividades ocultas (`is_visible = 0`) aparecem nos dados de controle
- Pode causar inconsistências quando usado junto com `loadExcelData(false)`
- Endpoints que usam ambos podem ter dados desencontrados

**Endpoints Afetados:**
- `/api/message` - usa `loadExcelData()` (filtra) e `getAllActivitiesControl()` (não filtra)
- `/api/message-detailed` - usa `loadExcelData()` (filtra) e `getAllActivitiesControl()` (não filtra)
- `/api/statistics` (versão antiga) - usa ambos

**Solução:**
Adicionar parâmetro `includeHidden` ao método `getAllActivitiesControl()` e filtrar por padrão.

### 2. Endpoints de mensagem não passam parâmetro `includeHidden`

**Arquivo:** `server.js`, linhas 2168 e 2189

**Problema:**
```javascript
const excelData = await dbManager.loadExcelData(); // ❌ Sem parâmetro - usa padrão false
const controlData = await dbManager.getAllActivitiesControl(); // ❌ Não filtra
```

**Impacto:**
- `excelData` filtra por `is_visible = 1` (padrão)
- `controlData` não filtra
- Pode haver atividades em `controlData` que não estão em `excelData`

**Solução:**
Garantir que ambos usem o mesmo filtro ou que `getAllActivitiesControl()` filtre por padrão.

## 🔧 Correções Necessárias

### Correção 1: Adicionar filtro em `getAllActivitiesControl()`

```javascript
async getAllActivitiesControl(includeHidden = false) {
  console.log('[DATABASE] 🔍 Carregando dados da tabela activities (unificada)...', {
    includeHidden: includeHidden
  });
  
  let query = this.supabase
    .from('activities')
    .select('*');
  
  // Filtrar por is_visible se não incluir ocultas
  if (!includeHidden) {
    query = query.eq('is_visible', 1);
    console.log('[DATABASE] 🔍 Filtrando apenas atividades visíveis (is_visible = 1)');
  } else {
    console.log('[DATABASE] 🔍 Carregando TODAS as atividades (incluindo ocultas)');
  }
  
  const { data: rows, error } = await query;
  // ... resto do código
}
```

### Correção 2: Atualizar chamadas a `getAllActivitiesControl()`

Garantir que todas as chamadas passem o parâmetro correto:
- Endpoints que usam `loadExcelData(false)` → `getAllActivitiesControl(false)`
- Endpoints que usam `loadExcelData(true)` → `getAllActivitiesControl(true)`

## 📊 Resumo

| Método/Endpoint | Filtra `is_visible`? | Status |
|----------------|---------------------|--------|
| `loadExcelData(false)` | ✅ Sim | ✅ OK |
| `loadExcelData(true)` | ❌ Não (intencional) | ✅ OK |
| `getAllActivitiesControl()` | ❌ Não | ⚠️ **PROBLEMA** |
| `calculateStatisticsSQL()` | ✅ Sim | ✅ OK |
| `/api/activities` | ✅ Sim | ✅ OK |
| `/api/statistics` | ✅ Sim | ✅ OK |
| `/api/message` | ⚠️ Parcial | ⚠️ **PROBLEMA** |
| `/api/message-detailed` | ⚠️ Parcial | ⚠️ **PROBLEMA** |

## ✅ Próximos Passos

1. Corrigir `getAllActivitiesControl()` para aceitar parâmetro `includeHidden`
2. Atualizar todas as chamadas para passar o parâmetro correto
3. Testar endpoints de mensagem para garantir consistência
4. Verificar se há outros lugares que usam `getAllActivitiesControl()` sem filtro
