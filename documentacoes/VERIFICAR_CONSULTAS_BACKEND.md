# Como Verificar se as Consultas SQL Correspondem ao Backend

Este documento explica como verificar se as queries SQL fornecidas correspondem à lógica implementada no backend.

## 📍 Localização do Backend

O backend está no repositório: **`CRQExecComMgmtBackend`**

## 🔍 Arquivos do Backend a Verificar

### 1. **`server.js`** - Endpoint `/api/statistics`
- Localização: Provavelmente em `CRQExecComMgmtBackend/server.js`
- Procure por: `app.get('/api/statistics'` ou `router.get('/statistics'`
- Verifique: Como o parâmetro `rollback` é processado e passado para a função de cálculo

### 2. **`status_calculator.js`** - Cálculo de Status
- Localização: Provavelmente em `CRQExecComMgmtBackend/status_calculator.js`
- Função principal: `calculateActivityStatus()`
- Verifique: Como o status é calculado baseado em:
  - Campo `status` salvo no banco
  - `horario_fim_real` (indica conclusão)
  - `horario_inicio_real` (indica início)
  - Comparação de datas (inicio, fim vs. data atual)

### 3. **`database-supabase.js`** - Consultas ao Banco
- Localização: Provavelmente em `CRQExecComMgmtBackend/database-supabase.js`
- Métodos importantes:
  - `getAllActivitiesControl()` - Busca todas as atividades
  - Verifique: Se há filtros SQL aplicados diretamente nas queries

### 4. **Função de Cálculo de Estatísticas**
- Procure por: `calculateStatistics()` ou função similar
- Verifique: Como as estatísticas são calculadas após buscar os dados

## 🔎 O Que Verificar

### 1. **Filtro de Milestones**
```javascript
// Backend deve ter algo como:
WHERE is_milestone = false
// ou
WHERE is_milestone = 0
```

### 2. **Filtro de Rollback**
```javascript
// Quando rollback = 'principal':
WHERE (is_rollback = false OR is_rollback = 0 OR is_rollback IS NULL)

// Quando rollback = 'rollback':
WHERE (is_rollback = true OR is_rollback = 1)
```

### 3. **Cálculo de Status "Concluído"**
```javascript
// Backend deve verificar:
- status contém "concluído" OU
- horario_fim_real IS NOT NULL
```

### 4. **Cálculo de Status "Em Execução no Prazo"**
```javascript
// Backend deve verificar:
- status contém "em execução no prazo" E
- horario_fim_real IS NULL (não concluída)
```

### 5. **Cálculo de Status "A Iniciar"**
```javascript
// Backend deve verificar:
- status contém "a iniciar" E
- horario_inicio_real IS NULL (não iniciada)
```

## 📝 Checklist de Verificação

Execute este checklist no código do backend:

- [ ] **Endpoint `/api/statistics`** aceita parâmetro `rollback`?
- [ ] **Filtro de milestones** é aplicado (`is_milestone = false`)?
- [ ] **Filtro de rollback** é aplicado quando fornecido?
- [ ] **Status "Concluído"** verifica `horario_fim_real`?
- [ ] **Status "Em Execução"** verifica que não está concluída?
- [ ] **Status "A Iniciar"** verifica que `horario_inicio_real` está vazio?
- [ ] **Múltiplas variações** de "concluído" são consideradas?

## 🔧 Como Verificar

### Opção 1: Verificar Código do Backend

1. Abra o repositório `CRQExecComMgmtBackend`
2. Procure pelo arquivo `server.js` ou similar
3. Encontre o endpoint `/api/statistics`
4. Verifique a função que calcula as estatísticas
5. Compare com as queries SQL fornecidas

### Opção 2: Verificar Logs do Backend

1. Acesse os logs do backend no Netlify
2. Procure por queries SQL executadas
3. Compare com as queries fornecidas

### Opção 3: Testar Diretamente

1. Execute as queries SQL fornecidas no Supabase
2. Compare os resultados com o dashboard
3. Se houver diferenças, o backend pode estar calculando o status dinamicamente

## ⚠️ Diferenças Esperadas

### 1. **Status Calculado Dinamicamente**

O backend pode calcular o status baseado em datas, não apenas no campo `status` salvo:

```javascript
// Exemplo de lógica dinâmica:
if (horario_fim_real) {
  status = 'Concluído';
} else if (horario_inicio_real && agora < fim) {
  status = 'Em Execução no Prazo';
} else if (horario_inicio_real && agora > fim) {
  status = 'Em Execução Fora do Prazo';
} else if (agora < inicio) {
  status = 'A Iniciar no Prazo';
} else {
  status = 'A Iniciar Fora do Prazo';
}
```

### 2. **Uso de Supabase Client**

O backend pode usar o cliente Supabase que faz queries diferentes:

```javascript
// Exemplo:
const { data, error } = await supabase
  .from('activities')
  .select('*')
  .eq('is_milestone', false);
```

### 3. **Processamento em Memória**

O backend pode buscar todos os dados e processar em memória:

```javascript
// Busca todos os dados
const activities = await getAllActivities();

// Processa em memória
const concluidas = activities.filter(a => 
  a.status.includes('concluído') || a.horario_fim_real
);
```

## 📋 Queries SQL Equivalentes

Se o backend processa em memória, as queries SQL fornecidas são equivalentes à lógica aplicada após buscar os dados.

Se o backend faz queries SQL diretas, as queries devem ser muito similares às fornecidas.

## 🔍 Próximos Passos

1. **Acesse o repositório do backend**: `CRQExecComMgmtBackend`
2. **Verifique o arquivo `server.js`**: Procure pelo endpoint `/api/statistics`
3. **Verifique o arquivo `status_calculator.js`**: Veja como o status é calculado
4. **Compare com as queries SQL**: Verifique se a lógica corresponde
5. **Execute as queries SQL**: Teste diretamente no Supabase e compare com o dashboard

## 📌 Nota Importante

As queries SQL fornecidas são baseadas na **lógica esperada** do sistema. Se houver diferenças, pode ser porque:

1. O backend calcula o status dinamicamente baseado em datas
2. O backend usa uma lógica diferente para determinar o status
3. O backend aplica filtros adicionais não documentados

Para verificar exatamente, é necessário acessar o código do backend.
