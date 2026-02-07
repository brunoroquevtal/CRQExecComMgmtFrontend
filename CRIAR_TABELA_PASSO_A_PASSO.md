# 📋 Passo a Passo: Criar Tabela user_profiles no Supabase

## 🎯 Objetivo

Criar a tabela `user_profiles` no Supabase para armazenar informações de perfil e roles dos usuários.

## 📝 Passo 1: Acessar o Supabase Dashboard

1. Acesse: https://app.supabase.com
2. Faça login na sua conta
3. Selecione o projeto do seu sistema

## 📝 Passo 2: Abrir o SQL Editor

1. No menu lateral esquerdo, clique em **SQL Editor**
2. Clique no botão **New Query** (ou use o atalho `Ctrl+N`)

## 📝 Passo 3: Copiar e Colar o Script

1. Abra o arquivo `CRIAR_TABELA_USER_PROFILES.sql` neste projeto
2. **Copie TODO o conteúdo** do arquivo
3. **Cole no SQL Editor** do Supabase

## 📝 Passo 4: Executar o Script

1. Clique no botão **Run** (ou pressione `Ctrl+Enter`)
2. Aguarde a execução
3. Você deve ver mensagens de sucesso como:
   - "Success. No rows returned"
   - Ou "Success. X rows affected"

## 📝 Passo 5: Verificar se Funcionou

### Verificar a Tabela

1. No menu lateral, clique em **Table Editor**
2. Procure pela tabela `user_profiles`
3. Você deve ver a tabela com as colunas:
   - `id` (UUID, Primary Key)
   - `email` (Text)
   - `full_name` (Text)
   - `role` (Text)
   - `created_at` (Timestamp)
   - `updated_at` (Timestamp)

### Verificar os Usuários

1. Na tabela `user_profiles`, você deve ver os usuários que já existem no `auth.users`
2. Todos devem ter `role = 'visualizador'` por padrão

## 📝 Passo 6: Tornar um Usuário Administrador

Agora que a tabela existe, você pode tornar um usuário administrador:

### Opção A: Via Table Editor

1. Na tabela `user_profiles`, encontre o usuário pelo email
2. Clique na linha do usuário
3. Na coluna `role`, altere para `administrador`
4. Salve (Ctrl+S ou botão Save)

### Opção B: Via SQL Editor

Execute este SQL (substitua o email):

```sql
UPDATE user_profiles
SET role = 'administrador'
WHERE email = 'seu-email@exemplo.com';
```

## ✅ Verificar no Sistema

1. Faça logout do sistema
2. Faça login novamente com o usuário que você tornou administrador
3. Você deve ver:
   - Menu "Usuários" no menu lateral
   - Badge "Administrador" no perfil
   - Acesso a todas as funcionalidades administrativas

## 🐛 Problemas Comuns

### Erro: "relation user_profiles already exists"

**Solução**: A tabela já existe. Você pode:
- Pular a criação da tabela e ir direto para atualizar roles
- Ou deletar a tabela primeiro (cuidado! isso apaga todos os dados):
  ```sql
  DROP TABLE IF EXISTS user_profiles CASCADE;
  ```
  Depois execute o script novamente.

### Erro: "permission denied"

**Solução**: Verifique se você tem permissões de administrador no projeto Supabase.

### Erro: "foreign key constraint"

**Solução**: Isso significa que há um problema com a referência ao `auth.users`. 
O script usa `ON DELETE CASCADE`, então isso não deveria acontecer. 
Se acontecer, verifique se o ID do usuário existe em `auth.users`.

### Nenhum usuário aparece na tabela

**Solução**: Execute manualmente esta parte do script:

```sql
INSERT INTO user_profiles (id, email, role, full_name)
SELECT 
  id,
  email,
  'visualizador' as role,
  raw_user_meta_data->>'full_name' as full_name
FROM auth.users
WHERE id NOT IN (SELECT id FROM user_profiles)
ON CONFLICT (id) DO NOTHING;
```

## 📚 O que o Script Faz

1. ✅ Cria a tabela `user_profiles` com todas as colunas necessárias
2. ✅ Cria índices para melhor performance
3. ✅ Cria função e trigger para atualizar `updated_at` automaticamente
4. ✅ Habilita Row Level Security (RLS)
5. ✅ Cria políticas de segurança (usuários veem só seu perfil, admins veem todos)
6. ✅ Cria perfis para todos os usuários existentes no `auth.users`

## 🔒 Segurança

O script configura Row Level Security (RLS) que garante:
- Usuários só veem seu próprio perfil
- Usuários não podem mudar seu próprio role
- Apenas administradores podem ver e atualizar todos os perfis
- Novos usuários podem criar seu próprio perfil automaticamente

## 📝 Próximos Passos

Após criar a tabela:
1. ✅ Tornar pelo menos um usuário administrador
2. ✅ Testar o login como administrador
3. ✅ Acessar a página de gerenciamento de usuários (`/usuarios`)
4. ✅ Gerenciar outros usuários através da interface
