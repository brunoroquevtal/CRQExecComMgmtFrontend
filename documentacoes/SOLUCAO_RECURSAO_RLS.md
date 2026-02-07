# 🔧 Solução: Recursão Infinita nas Políticas RLS

## ⚠️ Problema Identificado

O backend está retornando erro:
```
'infinite recursion detected in policy for relation "user_profiles"'
```

E está usando a chave **Anon Key** ao invés da **Service Role Key**:
```
hasServiceKey: false
usingServiceKey: false
```

## 🔍 Causa

1. **Políticas RLS com recursão**: As políticas de administrador tentam verificar se o usuário é administrador consultando `user_profiles`, mas isso cria recursão infinita.

2. **Uso da chave errada**: O backend está usando `SUPABASE_ANON_KEY` como fallback quando não encontra `SUPABASE_SERVICE_ROLE_KEY`, mas a Anon Key está sujeita às políticas RLS.

## ✅ Solução

### Opção 1: Configurar Service Role Key (RECOMENDADO)

A **Service Role Key** ignora completamente as políticas RLS, então não há problema de recursão.

1. **No Netlify/Railway/onde o backend está deployado:**
   - Vá em **Environment Variables**
   - Adicione: `SUPABASE_SERVICE_ROLE_KEY` com o valor da chave service_role do Supabase
   - **NÃO use** `SUPABASE_ANON_KEY` para operações administrativas

2. **Onde encontrar a Service Role Key:**
   - Acesse: https://app.supabase.com
   - Selecione seu projeto
   - Vá em **Settings** → **API**
   - Copie a **`service_role` key** (não a `anon` key!)

### Opção 2: Corrigir Políticas RLS

Se preferir manter RLS ativo, execute o script SQL:

```sql
-- Ver arquivo: documentacoes/CORRIGIR_POLITICAS_RLS_USER_PROFILES.sql
```

Ou simplesmente desabilite RLS para a tabela (se usar Service Role Key):

```sql
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
```

## 📝 Verificação

Após configurar a Service Role Key, os logs devem mostrar:

```
[AUTH] ✅ Cliente Supabase criado com Service Role Key: {
  hasServiceKey: true,
  usingServiceKey: true
}
```

E não deve mais aparecer o erro de recursão infinita.

## 🚨 Importante

- **Service Role Key** = Acesso total, ignora RLS (use no backend)
- **Anon Key** = Sujeita a RLS (use apenas no frontend)
- **Nunca exponha a Service Role Key no frontend!**

## 🔗 Referências

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Service Role Key](https://supabase.com/docs/guides/api/api-keys)
