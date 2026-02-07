# 🔧 Solução: Erro 500 ao Buscar user_profiles no Supabase

## 🐛 Problema

Você está vendo erros 500 ao tentar buscar `user_profiles` do Supabase:
```
Failed to load resource: the server responded with a status of 500 (Internal Server Error)
```

## ✅ Causa

A tabela `user_profiles` **não existe** no seu projeto Supabase.

## 🔧 Solução

### Passo 1: Criar a Tabela

1. Acesse o **Supabase Dashboard**: https://app.supabase.com
2. Selecione seu projeto
3. Vá em **SQL Editor** → **New Query**
4. Abra o arquivo `CRIAR_TABELA_USER_PROFILES_CORRIGIDO.sql` neste projeto
5. **Copie TODO o conteúdo** e cole no SQL Editor
6. Clique em **Run** (ou `Ctrl+Enter`)

### Passo 2: Verificar se Funcionou

1. Vá em **Table Editor** no Supabase
2. Procure pela tabela `user_profiles`
3. Você deve ver a tabela criada

### Passo 3: Criar Perfil para Seu Usuário

Execute este SQL (substitua o email):

```sql
-- Criar perfil para seu usuário
INSERT INTO user_profiles (id, email, role, full_name)
SELECT 
  id,
  email,
  'administrador' as role,
  COALESCE(
    raw_user_meta_data->>'full_name',
    split_part(email, '@', 1)
  ) as full_name
FROM auth.users
WHERE email = 'seu-email@exemplo.com'
ON CONFLICT (id) DO UPDATE SET role = 'administrador';
```

### Passo 4: Testar

1. Faça **logout** do sistema
2. Faça **login** novamente
3. O erro 500 deve desaparecer
4. Seu perfil deve ser carregado corretamente

## 🔍 Verificar se a Tabela Existe

Execute este SQL no Supabase:

```sql
SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name = 'user_profiles'
);
```

Se retornar `false`, a tabela não existe. Execute o script de criação.

## ⚠️ Se Ainda Der Erro 500

### Verificar RLS (Row Level Security)

Se a tabela existe mas ainda dá erro 500, pode ser problema de RLS:

```sql
-- Verificar se RLS está habilitado
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'user_profiles';

-- Se necessário, verificar políticas
SELECT * FROM pg_policies WHERE tablename = 'user_profiles';
```

### Criar Política Básica

Se não houver políticas, crie uma básica:

```sql
-- Permitir que usuários vejam seu próprio perfil
CREATE POLICY "Users can view own profile"
ON user_profiles FOR SELECT
USING (auth.uid() = id);
```

## 📝 Nota

O código do frontend foi atualizado para:
- ✅ Não mostrar erros 500 no console (apenas em modo dev)
- ✅ Usar perfil padrão quando a tabela não existe
- ✅ Funcionar mesmo sem a tabela `user_profiles`

Mas para ter roles funcionando corretamente, você precisa criar a tabela.
