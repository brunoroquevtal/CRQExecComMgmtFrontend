# 👑 Como Tornar um Usuário Administrador no Supabase

Este guia explica como alterar o role de um usuário para `administrador` no Supabase.

## 📋 Pré-requisitos

- Acesso ao Dashboard do Supabase
- Credenciais de administrador do projeto Supabase
- ID do usuário que você quer tornar administrador

## 🔧 Método 1: Via Dashboard do Supabase (Recomendado)

### Passo 1: Acessar o Supabase Dashboard

1. Acesse: https://app.supabase.com
2. Faça login na sua conta
3. Selecione o projeto do seu sistema

### Passo 2: Acessar a Tabela `user_profiles`

1. No menu lateral, clique em **Table Editor**
2. Procure pela tabela `user_profiles`
3. Se a tabela não existir, você precisará criá-la primeiro (veja Método 3)

### Passo 3: Encontrar o Usuário

1. Na tabela `user_profiles`, encontre o usuário pelo:
   - **Email** (coluna `email`)
   - **ID** (coluna `id` - mesmo ID do Supabase Auth)

### Passo 4: Atualizar o Role

1. Clique na linha do usuário
2. Na coluna `role`, altere o valor para: `administrador`
3. Clique em **Save** ou pressione `Ctrl+S` (Windows) / `Cmd+S` (Mac)

### Passo 5: Verificar

1. Faça logout e login novamente no sistema
2. O usuário agora deve ter acesso de administrador

## 🔧 Método 2: Via SQL Editor (Alternativo)

### Passo 1: Acessar SQL Editor

1. No Dashboard do Supabase, clique em **SQL Editor**
2. Clique em **New Query**

### Passo 2: Executar SQL

Execute o seguinte SQL, substituindo `'seu-email@exemplo.com'` pelo email do usuário:

```sql
-- Atualizar role para administrador pelo email
UPDATE user_profiles
SET role = 'administrador'
WHERE email = 'seu-email@exemplo.com';
```

Ou pelo ID do usuário:

```sql
-- Atualizar role para administrador pelo ID
UPDATE user_profiles
SET role = 'administrador'
WHERE id = 'uuid-do-usuario';
```

### Passo 3: Executar

1. Clique em **Run** ou pressione `Ctrl+Enter`
2. Verifique se a mensagem mostra "Success. No rows returned" ou número de linhas afetadas

## 🔧 Método 3: Criar Tabela `user_profiles` (Se Não Existir)

Se a tabela `user_profiles` não existir, você precisa criá-la primeiro:

### Passo 1: Acessar SQL Editor

1. No Dashboard do Supabase, clique em **SQL Editor**
2. Clique em **New Query**

### Passo 2: Criar Tabela

Execute o seguinte SQL:

```sql
-- Criar tabela user_profiles
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  full_name TEXT,
  role TEXT DEFAULT 'visualizador',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índice para busca rápida
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON user_profiles(role);

-- Habilitar Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Política: Usuários podem ver seu próprio perfil
CREATE POLICY "Users can view own profile"
ON user_profiles
FOR SELECT
USING (auth.uid() = id);

-- Política: Usuários podem atualizar seu próprio perfil (exceto role)
CREATE POLICY "Users can update own profile"
ON user_profiles
FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Política: Administradores podem ver todos os perfis
CREATE POLICY "Admins can view all profiles"
ON user_profiles
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM user_profiles
    WHERE id = auth.uid() AND role = 'administrador'
  )
);

-- Política: Administradores podem atualizar todos os perfis
CREATE POLICY "Admins can update all profiles"
ON user_profiles
FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM user_profiles
    WHERE id = auth.uid() AND role = 'administrador'
  )
);
```

### Passo 3: Criar Perfil para Usuário Existente

Se você já tem usuários no Supabase Auth mas não tem perfis na tabela, crie-os:

```sql
-- Criar perfil para todos os usuários existentes
INSERT INTO user_profiles (id, email, role)
SELECT 
  id,
  email,
  'visualizador' as role
FROM auth.users
WHERE id NOT IN (SELECT id FROM user_profiles)
ON CONFLICT (id) DO NOTHING;
```

### Passo 4: Tornar um Usuário Administrador

Depois de criar a tabela e os perfis, atualize o role:

```sql
-- Tornar um usuário administrador
UPDATE user_profiles
SET role = 'administrador'
WHERE email = 'seu-email@exemplo.com';
```

## 🔧 Método 4: Via API do Backend (Se Estiver Configurado)

Se o backend estiver configurado e você tiver acesso como administrador:

1. Acesse a página **Usuários** no sistema (`/usuarios`)
2. Encontre o usuário na lista
3. No dropdown de **Role**, selecione **Administrador**
4. A alteração será salva automaticamente

## 🔍 Verificar se Funcionou

### Via Dashboard

1. Acesse a tabela `user_profiles`
2. Verifique se a coluna `role` do usuário está como `administrador`

### Via Sistema

1. Faça logout do sistema
2. Faça login novamente
3. Você deve ver:
   - Menu "Usuários" aparecendo no menu lateral
   - Menu "Configurações" acessível
   - Badge "Administrador" no perfil

## ⚠️ Importante

1. **Segurança**: Apenas usuários com acesso ao Dashboard do Supabase podem fazer essa alteração
2. **Backup**: Sempre faça backup antes de alterar dados importantes
3. **Primeiro Administrador**: Se não houver nenhum administrador, você precisará criar um via SQL ou Dashboard
4. **RLS (Row Level Security)**: Se RLS estiver habilitado, certifique-se de que as políticas permitem a atualização

## 🆘 Problemas Comuns

### "Tabela user_profiles não existe"

**Solução**: Use o Método 3 para criar a tabela primeiro.

### "Usuário não aparece na tabela"

**Solução**: O usuário precisa ter feito login pelo menos uma vez, ou você precisa criar o perfil manualmente (veja Método 3, Passo 3).

### "Não consigo editar a tabela"

**Solução**: Verifique se você tem permissões de administrador no projeto Supabase.

### "Mudança não reflete no sistema"

**Solução**: 
1. Faça logout e login novamente
2. Limpe o cache do navegador
3. Verifique se o backend está configurado corretamente

## 📝 Notas

- O role padrão é `visualizador`
- Roles disponíveis: `visualizador`, `lider_mudanca`, `administrador`
- Apenas administradores podem alterar roles de outros usuários (via sistema)
- Alterações via Dashboard/SQL são imediatas
