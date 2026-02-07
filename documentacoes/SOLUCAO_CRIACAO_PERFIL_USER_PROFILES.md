# 🔧 Solução: Usuário criado no Auth mas não em user_profiles

## 📋 Problema Identificado

O usuário está sendo criado com sucesso no **Supabase Auth** (`auth.users`), mas **NÃO** está sendo criado na tabela **`public.user_profiles`**.

## 🔍 Causas Possíveis

### 1. **SUPABASE_SERVICE_ROLE_KEY não configurado** ⚠️ (Mais Provável)
- O backend precisa da Service Role Key para criar perfis
- Sem ela, o `supabaseAdmin` é `null` e não consegue inserir na tabela

### 2. **RLS (Row Level Security) bloqueando inserções**
- As políticas RLS podem estar bloqueando inserções mesmo com Service Role Key
- A Service Role Key deveria ignorar RLS, mas pode haver configuração incorreta

### 3. **Erro silencioso na inserção**
- O código estava retornando sucesso mesmo quando o perfil não era criado
- Erros eram apenas logados, não reportados ao frontend

## ✅ Soluções Implementadas

### 1. **Logs Mais Detalhados**
- Verificação explícita se `SUPABASE_SERVICE_ROLE_KEY` está configurado
- Logs detalhados de cada etapa do processo
- Verificação final para confirmar que o perfil foi realmente criado

### 2. **Tratamento de Erros Melhorado**
- Diferentes estratégias para diferentes tipos de erro
- Tentativa alternativa usando RPC se RLS estiver bloqueando
- Verificação final para confirmar criação

### 3. **Script SQL para Verificação e Correção**
- Script `VERIFICAR_CRIACAO_PERFIL.sql` para:
  - Identificar usuários sem perfil
  - Criar perfis faltantes
  - Verificar configuração de RLS
  - Criar função RPC alternativa

## 🚀 Como Resolver

### Passo 1: Verificar Variáveis de Ambiente

No **Netlify** ou **Railway**, verifique se estas variáveis estão configuradas:

```
✅ SUPABASE_URL=https://seu-projeto.supabase.co
✅ SUPABASE_ANON_KEY=eyJhbGc...
✅ SUPABASE_SERVICE_ROLE_KEY=eyJhbGc... ⚠️ CRÍTICO
```

**A Service Role Key é OBRIGATÓRIA** para criar perfis!

### Passo 2: Verificar no Supabase

1. Acesse o **Supabase Dashboard**
2. Vá em **Authentication > Users**
3. Verifique se o usuário do Alysson existe
4. Vá em **Table Editor > user_profiles**
5. Verifique se existe um registro com o ID do usuário

### Passo 3: Executar Script SQL

Execute o script `VERIFICAR_CRIACAO_PERFIL.sql` no **SQL Editor** do Supabase:

1. Abra o arquivo `documentacoes/VERIFICAR_CRIACAO_PERFIL.sql`
2. Copie e cole no SQL Editor do Supabase
3. Execute a query 1 para ver usuários sem perfil
4. Execute a query 2 para criar perfis faltantes

### Passo 4: Verificar Logs do Backend

Após tentar criar um novo usuário, verifique os logs do Netlify/Railway:

Procure por estas mensagens:
- `[AUTH SIGNUP] 🔧 Verificando configuração Supabase Admin`
- `[AUTH SIGNUP] ✅ Perfil criado com sucesso`
- `[AUTH SIGNUP] ❌ Erro ao criar perfil`
- `[AUTH SIGNUP] ✅ Confirmação: Perfil existe na tabela user_profiles`

### Passo 5: Desabilitar RLS (Se Necessário)

Se o problema persistir e você estiver usando Service Role Key, pode desabilitar RLS temporariamente:

```sql
ALTER TABLE public.user_profiles DISABLE ROW LEVEL SECURITY;
```

**⚠️ ATENÇÃO**: Isso remove a segurança. Use apenas se o backend usar Service Role Key!

## 📝 Verificação Rápida

Execute esta query no Supabase para ver usuários sem perfil:

```sql
SELECT 
  au.id,
  au.email,
  au.created_at,
  CASE 
    WHEN up.id IS NULL THEN '❌ SEM PERFIL'
    ELSE '✅ COM PERFIL'
  END as status
FROM auth.users au
LEFT JOIN public.user_profiles up ON au.id = up.id
WHERE up.id IS NULL;
```

## 🔄 Criar Perfis Faltantes

Execute esta query para criar perfis para todos os usuários que não têm:

```sql
INSERT INTO public.user_profiles (id, email, role, full_name, created_at, updated_at)
SELECT 
  au.id,
  au.email,
  'visualizador' as role,
  COALESCE(au.raw_user_meta_data->>'full_name', SPLIT_PART(au.email, '@', 1)) as full_name,
  au.created_at,
  NOW() as updated_at
FROM auth.users au
LEFT JOIN public.user_profiles up ON au.id = up.id
WHERE up.id IS NULL
ON CONFLICT (id) DO NOTHING;
```

## 🎯 Próximos Passos

1. ✅ Verificar se `SUPABASE_SERVICE_ROLE_KEY` está configurado
2. ✅ Executar script SQL para criar perfis faltantes
3. ✅ Verificar logs do backend após novo cadastro
4. ✅ Testar criação de novo usuário
5. ✅ Confirmar que o perfil foi criado na tabela `user_profiles`

## 📚 Arquivos Relacionados

- `routes/auth.js` - Código do endpoint de signup (melhorado)
- `VERIFICAR_CRIACAO_PERFIL.sql` - Script SQL para verificação e correção
- `CORRIGIR_POLITICAS_RLS_USER_PROFILES.sql` - Script para corrigir políticas RLS
