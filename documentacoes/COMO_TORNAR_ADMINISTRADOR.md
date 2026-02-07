# 🔧 Como Tornar um Usuário Administrador

## ⚠️ Problema

O perfil de administrador não está carregando porque o role no Supabase não está configurado como `administrador`.

## ✅ Solução 1: Atualizar via SQL no Supabase (Recomendado)

### Passo 1: Acessar o SQL Editor do Supabase

1. Acesse o painel do Supabase: https://app.supabase.com
2. Selecione seu projeto
3. Vá em **SQL Editor** no menu lateral
4. Clique em **New Query**

### Passo 2: Executar o SQL

Execute o seguinte SQL, substituindo `SEU_EMAIL@vtal.com` pelo seu email:

```sql
-- Verificar se a tabela user_profiles existe e ver usuários
SELECT id, email, role, full_name 
FROM user_profiles 
ORDER BY created_at DESC;

-- Atualizar seu usuário para administrador
UPDATE user_profiles 
SET role = 'administrador' 
WHERE email = 'SEU_EMAIL@vtal.com';

-- Verificar se foi atualizado
SELECT id, email, role, full_name 
FROM user_profiles 
WHERE email = 'SEU_EMAIL@vtal.com';
```

### Passo 3: Criar perfil se não existir

Se o perfil não existir, você precisa criar primeiro. Para isso, você precisa do `id` do usuário no Supabase Auth:

```sql
-- Primeiro, encontre o ID do usuário na tabela auth.users
-- (Isso requer acesso ao Supabase Dashboard > Authentication > Users)
-- Ou use o ID que você vê no frontend após fazer login

-- Depois, crie o perfil:
INSERT INTO user_profiles (id, email, role, full_name)
VALUES (
  'ID_DO_USUARIO_AQUI',  -- Substitua pelo ID real
  'SEU_EMAIL@vtal.com',  -- Substitua pelo seu email
  'administrador',
  'Seu Nome'  -- Opcional
)
ON CONFLICT (id) DO UPDATE 
SET role = 'administrador';
```

## ✅ Solução 2: Usar a Interface de Gerenciamento de Usuários

Se você já tem acesso a outro administrador ou consegue acessar a página de gerenciamento de usuários:

1. Faça login no sistema
2. Vá em **Usuários** no menu lateral (se disponível)
3. Encontre seu usuário na lista
4. Altere o role para **Administrador**
5. Salve

**Nota:** Isso só funciona se você já tiver acesso de administrador ou se houver outro administrador que possa fazer isso por você.

## ✅ Solução 3: Criar Script de Atualização

Se você tem acesso ao backend, pode criar um script temporário para atualizar o role:

### Script Node.js (temporário)

Crie um arquivo `update-admin.js` no backend:

```javascript
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Variáveis de ambiente do Supabase não configuradas');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function updateUserToAdmin(email) {
  try {
    // Buscar usuário pelo email
    const { data: users, error: userError } = await supabase.auth.admin.listUsers();
    
    if (userError) {
      console.error('Erro ao buscar usuários:', userError);
      return;
    }

    const user = users.users.find(u => u.email === email);
    
    if (!user) {
      console.error('Usuário não encontrado:', email);
      return;
    }

    // Atualizar ou criar perfil
    const { data: profile, error: profileError } = await supabase
      .from('user_profiles')
      .upsert({
        id: user.id,
        email: user.email,
        role: 'administrador',
        full_name: user.user_metadata?.full_name || user.email.split('@')[0]
      }, {
        onConflict: 'id'
      })
      .select()
      .single();

    if (profileError) {
      console.error('Erro ao atualizar perfil:', profileError);
      return;
    }

    console.log('✅ Usuário atualizado para administrador:', profile);
  } catch (error) {
    console.error('Erro:', error);
  }
}

// Substitua pelo seu email
const email = process.argv[2] || 'SEU_EMAIL@vtal.com';
updateUserToAdmin(email);
```

Execute:
```bash
node update-admin.js seu-email@vtal.com
```

## 🔍 Verificar se Funcionou

Após atualizar:

1. **Faça logout** do sistema
2. **Faça login novamente**
3. Verifique se:
   - O menu "Usuários" aparece no menu lateral
   - O perfil mostra "Administrador" no topo
   - Você tem acesso a todas as funcionalidades

## 📝 Notas Importantes

- O role deve ser exatamente `administrador` (minúsculas)
- Após atualizar, você precisa fazer logout e login novamente
- Se ainda não funcionar, verifique o console do navegador (F12) para ver erros
- Verifique se o endpoint `/api/auth/profile` está retornando o role correto

## 🆘 Se Nada Funcionar

1. Verifique os logs do backend para ver se há erros
2. Verifique se a tabela `user_profiles` existe no Supabase
3. Verifique se o middleware de autenticação está carregando o perfil corretamente
4. Tente limpar o cache do navegador e fazer login novamente
