# 🔧 Solução: Erro `getActivityBySeqSequenciaAtividade is not a function`

## 🔴 Problema Identificado

O erro HTTP 500 ocorre quando a API tenta sincronizar uma atividade:

```
TypeError: dbManager.getActivityBySeqSequenciaAtividade is not a function
    at /var/task/server.js:1055:43
```

## 📋 Análise

1. **O método existe**: O método `getActivityBySeqSequenciaAtividade` existe no arquivo `database-supabase.js` (linha 692)
2. **O método não está disponível**: O `dbManager` usado no `server.js` não tem esse método
3. **Localização do erro**: `server.js` linha 1055

## ✅ Solução

O problema está no backend Node.js (repositório `CRQExecComMgmtBackend`). Verifique:

### 1. Verificar Exportação do Método

No arquivo `database-supabase.js`, verifique se o método está sendo exportado:

```javascript
// database-supabase.js
class DatabaseManager {
  // ... outros métodos ...
  
  async getActivityBySeqSequenciaAtividade(seq, sequencia, atividade) {
    // implementação do método
  }
}

module.exports = DatabaseManager; // ou export default DatabaseManager
```

### 2. Verificar Importação no server.js

No arquivo `server.js` (linha ~1055), verifique se o `dbManager` está sendo instanciado corretamente:

```javascript
// server.js
const DatabaseManager = require('./database-supabase'); // ou o caminho correto
const dbManager = new DatabaseManager();

// Verificar se o método existe antes de usar
if (typeof dbManager.getActivityBySeqSequenciaAtividade !== 'function') {
  console.error('Método getActivityBySeqSequenciaAtividade não encontrado!');
  // Usar método alternativo ou criar fallback
}
```

### 3. Solução Alternativa: Usar Método Existente

Se o método não existir ou não estiver disponível, você pode usar o método `getActivityBySeqSequencia` existente e filtrar por atividade:

```javascript
// No server.js, linha ~1055
// ANTES (causa erro):
const existingActivity = await dbManager.getActivityBySeqSequenciaAtividade(seq, sequencia, atividade);

// DEPOIS (solução alternativa):
// Opção 1: Usar método existente e filtrar
const activities = await dbManager.getActivitiesBySeqSequencia(seq, sequencia);
const existingActivity = activities?.find(a => a.atividade === atividade);

// Opção 2: Criar método wrapper se necessário
if (!dbManager.getActivityBySeqSequenciaAtividade) {
  dbManager.getActivityBySeqSequenciaAtividade = async function(seq, sequencia, atividade) {
    const activities = await this.getActivitiesBySeqSequencia(seq, sequencia);
    return activities?.find(a => a.atividade === atividade) || null;
  };
}
```

### 4. Verificar Instanciação do dbManager

Certifique-se de que o `dbManager` está sendo instanciado corretamente:

```javascript
// server.js
let dbManager;

// Verificar se está usando Supabase
if (process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY) {
  const DatabaseManager = require('./database-supabase');
  dbManager = new DatabaseManager({
    supabaseUrl: process.env.SUPABASE_URL,
    supabaseKey: process.env.SUPABASE_SERVICE_ROLE_KEY
  });
} else {
  throw new Error('SUPABASE_URL é obrigatório');
}

// Verificar se dbManager foi criado corretamente
if (!dbManager) {
  throw new Error('dbManager não foi inicializado');
}

// Verificar se o método existe
if (typeof dbManager.getActivityBySeqSequenciaAtividade !== 'function') {
  console.warn('Método getActivityBySeqSequenciaAtividade não encontrado, usando alternativa');
  // Implementar fallback
}
```

## 🔍 Verificação Rápida

Execute no backend para verificar se o método existe:

```javascript
// Adicionar temporariamente no server.js para debug
console.log('Métodos disponíveis no dbManager:', Object.getOwnPropertyNames(Object.getPrototypeOf(dbManager)));
console.log('getActivityBySeqSequenciaAtividade existe?', typeof dbManager.getActivityBySeqSequenciaAtividade);
```

## 🛠️ Solução Rápida: Implementar Método Alternativo

Se você não conseguir acessar o arquivo `database-supabase.js` ou o método não existir, você pode criar um método wrapper no `server.js` antes de usar:

```javascript
// No server.js, antes da linha 1055 (onde o erro ocorre)
// Adicionar método wrapper se não existir
if (!dbManager.getActivityBySeqSequenciaAtividade) {
  dbManager.getActivityBySeqSequenciaAtividade = async function(seq, sequencia, atividade) {
    try {
      // Buscar atividades por seq e sequencia
      const activities = await this.getActivitiesBySeqSequencia(seq, sequencia);
      
      if (!activities || activities.length === 0) {
        return null;
      }
      
      // Filtrar por atividade (nome)
      const found = activities.find(a => 
        a.atividade && a.atividade.trim().toUpperCase() === atividade.trim().toUpperCase()
      );
      
      return found || null;
    } catch (error) {
      console.error('Erro ao buscar atividade:', error);
      return null;
    }
  };
}
```

**OU** usar método existente diretamente:

```javascript
// No server.js, linha ~1055, substituir:
// ANTES (causa erro):
const existingActivity = await dbManager.getActivityBySeqSequenciaAtividade(seq, sequencia, atividade);

// DEPOIS (solução alternativa):
// Opção 1: Buscar e filtrar manualmente
const activities = await dbManager.getActivitiesBySeqSequencia(seq, sequencia);
const existingActivity = activities?.find(a => 
  a.atividade && a.atividade.trim().toUpperCase() === atividade.trim().toUpperCase()
) || null;

// Opção 2: Usar método que busca por seq e sequencia (ignorar atividade)
const existingActivity = await dbManager.getActivityBySeqSequencia(seq, sequencia);
// Se houver múltiplas, pegar a primeira ou a mais recente
```

## 📝 Checklist de Correção

### Opção 1: Corrigir no database-supabase.js (Recomendado)

- [ ] Verificar se o método `getActivityBySeqSequenciaAtividade` existe em `database-supabase.js`
- [ ] Se não existir, implementar o método conforme necessário
- [ ] Verificar se o método está sendo exportado corretamente
- [ ] Testar localmente antes de fazer deploy

### Opção 2: Corrigir no server.js (Solução Rápida)

- [ ] Localizar a linha ~1055 no `server.js` onde o erro ocorre
- [ ] Verificar se `dbManager` está sendo instanciado corretamente
- [ ] Adicionar método wrapper ou usar método alternativo (ver seção acima)
- [ ] Testar localmente antes de fazer deploy

### Opção 3: Verificação Geral

- [ ] Verificar se `server.js` importa `database-supabase.js` corretamente
- [ ] Verificar se `dbManager` está sendo instanciado antes de usar
- [ ] Adicionar tratamento de erro caso o método não exista
- [ ] Testar a API após correção
- [ ] Verificar logs do Netlify após deploy
- [ ] Testar sincronização via `sync_excel.py` após correção

## 🚨 Se o Problema Persistir

1. **Verificar versão do código**: Certifique-se de que o código mais recente está deployado
2. **Verificar cache**: Limpar cache do Netlify e fazer novo deploy
3. **Verificar variáveis de ambiente**: Certifique-se de que `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` estão configuradas
4. **Verificar logs completos**: Analise os logs do Netlify para mais detalhes

## 🔗 Arquivos Relacionados

- Backend: `CRQExecComMgmtBackend/database-supabase.js` (linha 692 - onde o método deveria estar)
- Backend: `CRQExecComMgmtBackend/server.js` (linha 1055 - onde o erro ocorre)
- Frontend: `sincronizador/sync_excel.py` (linha 943 - faz a chamada PUT)
- Documentação: `documentacoes/REMOCAO_SQLITE.md`
- Documentação: `documentacoes/CONFIGURAR_SUPABASE_NETLIFY.md`

## 📊 Impacto do Erro

Este erro afeta:
- ✅ Sincronização de atividades via `sync_excel.py` (PUT /api/activity)
- ✅ Atualização de atividades no frontend (se usar PUT)
- ❌ Criação de atividades (POST /api/activity) - **não afetado**
- ❌ Leitura de atividades (GET /api/activity) - **não afetado**

## ⚡ Solução Temporária (Workaround)

Se você não puder corrigir o backend imediatamente, pode usar o modo de criação (POST) em vez de atualização (PUT) no `sync_excel.py`:

```python
# No sync_excel.py, linha ~943, mudar de PUT para POST
# ANTES:
response = make_api_request('PUT', '/api/activity', json_data=activity_data, timeout=60)

# DEPOIS (workaround temporário):
response = make_api_request('POST', '/api/activity', json_data=activity_data, timeout=60)
```

**Nota**: Isso criará novas atividades mesmo se já existirem, mas pelo menos funcionará enquanto o backend não é corrigido.
