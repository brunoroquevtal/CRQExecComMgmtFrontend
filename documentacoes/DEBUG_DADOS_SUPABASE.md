# 🔍 Debug: Dados do Supabase Não Estão Retornando

## ⚠️ Problema

Os dados do Supabase não estão retornando, mesmo existindo usuários e vários registros no banco.

## 🔍 Possíveis Causas

### 1. **Problema com RLS (Row Level Security)**

As tabelas `excel_data` e `activity_control` podem ter RLS habilitado sem políticas adequadas, bloqueando as consultas.

**Solução:**
- Verificar se RLS está habilitado nas tabelas
- Criar políticas adequadas ou desabilitar RLS
- Usar Service Role Key (que ignora RLS)

### 2. **Usando Anon Key ao invés de Service Role Key**

O backend pode estar usando `SUPABASE_ANON_KEY` que está sujeita a RLS.

**Solução:**
- Configurar `SUPABASE_SERVICE_ROLE_KEY` nas variáveis de ambiente
- Service Role Key ignora RLS completamente

### 3. **Tabelas Não Existem ou Têm Nomes Diferentes**

As tabelas podem não ter sido criadas ou ter nomes diferentes.

**Solução:**
- Verificar no Supabase Dashboard → Table Editor
- Executar o schema SQL se necessário

### 4. **Erros Silenciosos nas Consultas**

Os erros podem estar sendo ignorados ou não logados.

**Solução:**
- Verificar logs do backend (agora com logs detalhados)
- Procurar por erros de RLS, permissão ou conexão

## 📋 Checklist de Verificação

### 1. Verificar Variáveis de Ambiente

No Netlify/Railway onde o backend está deployado:

- [ ] `SUPABASE_URL` está configurada
- [ ] `SUPABASE_SERVICE_ROLE_KEY` está configurada (NÃO `SUPABASE_ANON_KEY`)
- [ ] Valores estão corretos

### 2. Verificar Tabelas no Supabase

No Supabase Dashboard:

- [ ] Tabela `excel_data` existe
- [ ] Tabela `activity_control` existe
- [ ] Tabela `crq_rollback_state` existe
- [ ] Tabela `user_profiles` existe
- [ ] Há registros nas tabelas

### 3. Verificar RLS (Row Level Security)

No Supabase Dashboard → Table Editor → cada tabela:

- [ ] RLS está desabilitado OU
- [ ] Políticas RLS estão configuradas corretamente

**Para desabilitar RLS (se usar Service Role Key):**
```sql
ALTER TABLE excel_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE activity_control DISABLE ROW LEVEL SECURITY;
ALTER TABLE crq_rollback_state DISABLE ROW LEVEL SECURITY;
```

### 4. Verificar Logs do Backend

Após fazer uma requisição, verifique os logs:

```
[DATABASE] 🔧 Inicializando DatabaseManager
[DATABASE] 🔍 Carregando dados do excel_data...
[DATABASE] 📦 Resultado da consulta excel_data
[API] 🔍 Endpoint /api/activities chamado
```

**Procurar por:**
- Erros de RLS (`permission denied`, `policy`)
- Erros de conexão
- Contagem de registros (deve ser > 0)
- Avisos sobre uso de Anon Key

## 🔧 Soluções

### Solução 1: Configurar Service Role Key (RECOMENDADO)

1. Acesse: https://app.supabase.com
2. Selecione seu projeto
3. Vá em **Settings** → **API**
4. Copie a **`service_role` key**
5. No Netlify/Railway, adicione:
   - Key: `SUPABASE_SERVICE_ROLE_KEY`
   - Value: (cole a service_role key)
6. Faça novo deploy

### Solução 2: Desabilitar RLS

Se preferir manter Anon Key, desabilite RLS:

```sql
-- Execute no SQL Editor do Supabase
ALTER TABLE excel_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE activity_control DISABLE ROW LEVEL SECURITY;
ALTER TABLE crq_rollback_state DISABLE ROW LEVEL SECURITY;
```

### Solução 3: Criar Políticas RLS (Se quiser manter RLS)

```sql
-- Permitir todas as operações (se usar Service Role Key, não precisa)
CREATE POLICY "Allow all operations on excel_data"
ON excel_data FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on activity_control"
ON activity_control FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on crq_rollback_state"
ON crq_rollback_state FOR ALL USING (true) WITH CHECK (true);
```

## 📊 Logs Esperados

Após configurar corretamente, os logs devem mostrar:

```
[DATABASE] 🔧 Inicializando DatabaseManager: {
  usingServiceKey: true
}
[DATABASE] 🔍 Carregando dados do excel_data...
[DATABASE] 📦 Resultado da consulta excel_data: {
  hasData: true,
  rowCount: 150,  // Deve ser > 0
  hasError: false
}
[DATABASE] ✅ Dados carregados: {
  totalRows: 150,
  sequencias: ['REDE', 'OPENSHIFT', ...]
}
```

## 🚨 Se Ainda Não Funcionar

1. **Verifique os logs completos** do backend após fazer uma requisição
2. **Teste diretamente no Supabase:**
   - Vá em Table Editor
   - Verifique se consegue ver os dados
   - Tente fazer uma query manual no SQL Editor
3. **Verifique a URL do Supabase:**
   - Deve ser: `https://[projeto].supabase.co`
   - Não deve ter `/rest/v1` no final
4. **Verifique se as tabelas têm os campos corretos:**
   - Compare com o schema esperado em `supabase/schema.sql`

## 🔗 Referências

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Service Role Key](https://supabase.com/docs/guides/api/api-keys)
- Schema SQL: `supabase/schema.sql`
