# 🔐 Guia de Controle de Acesso com Supabase

Este guia explica como configurar e usar o sistema de controle de acesso com 3 perfis: **Administrador**, **Líder da Mudança** e **Visualizador**.

## 📋 Perfis de Usuário

### 1. **Administrador**
- ✅ Acesso total ao sistema
- ✅ Pode gerenciar usuários e roles
- ✅ Pode gerenciar domínios permitidos
- ✅ Pode fazer upload de Excel
- ✅ Pode editar atividades
- ✅ Pode limpar base de dados

### 2. **Líder da Mudança**
- ✅ Pode visualizar todas as atividades
- ✅ Pode fazer upload de Excel
- ✅ Pode editar atividades
- ❌ Não pode gerenciar usuários
- ❌ Não pode limpar base de dados

### 3. **Visualizador**
- ✅ Pode visualizar todas as atividades
- ✅ Pode ver estatísticas e relatórios
- ❌ Não pode fazer upload de Excel
- ❌ Não pode editar atividades
- ❌ Não pode gerenciar usuários

## 🚀 Configuração Inicial

### 1. Configurar Supabase

#### 1.1 Criar Projeto no Supabase
1. Acesse https://supabase.com
2. Crie um novo projeto
3. Anote a **URL** e a **Anon Key** do projeto

#### 1.2 Executar Schema SQL
1. No Supabase Dashboard, vá em **SQL Editor**
2. Execute o arquivo `backend/supabase/auth-schema.sql`
3. Isso criará:
   - Tabela `user_profiles`
   - Tabela `allowed_domains`
   - Políticas RLS (Row Level Security)
   - Trigger para criar perfil automaticamente

### 2. Configurar Variáveis de Ambiente

#### Backend (`.env`)
```env
# Supabase Configuration
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-chave-anon-key
SUPABASE_SERVICE_ROLE_KEY=sua-chave-service-role-key

# Domínios permitidos (separados por vírgula)
ALLOWED_EMAIL_DOMAINS=vtal.com,exemplo.com
```

#### Frontend (`.env`)
```env
VITE_SUPABASE_URL=https://seu-projeto.supabase.co
VITE_SUPABASE_ANON_KEY=sua-chave-anon-key
VITE_API_URL=http://localhost:3000/api
```

#### Netlify (Environment Variables)
No dashboard do Netlify, configure:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ALLOWED_EMAIL_DOMAINS`
- `VITE_SUPABASE_URL` (para o frontend)
- `VITE_SUPABASE_ANON_KEY` (para o frontend)
- `VITE_API_URL` (para o frontend)

### 3. Instalar Dependências

#### Backend
```bash
cd backend
npm install
```

#### Frontend
```bash
cd frontend
npm install
```

## 👤 Cadastro de Usuários

### Auto Cadastro
1. Acesse a página de cadastro (`/signup`)
2. Preencha:
   - Nome completo
   - Email (deve ser de um domínio permitido)
   - Senha (mínimo 6 caracteres)
   - Confirmação de senha
3. Clique em "Cadastrar"
4. Verifique seu email para confirmar a conta
5. Após confirmação, você será criado como **Visualizador** por padrão

### Promover Usuário a Administrador
Apenas administradores podem promover outros usuários:

1. Faça login como administrador
2. Acesse a página de configurações
3. Vá em "Gerenciar Usuários"
4. Selecione o usuário e altere o role

**OU** via SQL no Supabase:
```sql
UPDATE user_profiles 
SET role = 'administrador' 
WHERE email = 'usuario@vtal.com';
```

## 🔧 Gerenciar Domínios Permitidos

### Via Interface (Administradores)
1. Faça login como administrador
2. Acesse Configurações > Domínios Permitidos
3. Adicione ou remova domínios

### Via API
```bash
# Listar domínios
GET /api/auth/domains

# Adicionar domínio
POST /api/auth/domains
{
  "domain": "exemplo.com",
  "description": "Domínio da empresa exemplo"
}

# Remover domínio
DELETE /api/auth/domains/:id
```

### Via SQL
```sql
-- Adicionar domínio
INSERT INTO allowed_domains (domain, description)
VALUES ('exemplo.com', 'Domínio da empresa exemplo');

-- Desativar domínio
UPDATE allowed_domains 
SET active = false 
WHERE domain = 'exemplo.com';
```

## 🛡️ Proteção de Rotas

### Backend
As rotas estão protegidas com middleware:

```javascript
// Requer autenticação
app.get('/api/activities', requireAuth, ...);

// Requer role específica
app.post('/api/upload-excel', requireAuth, requireRole('lider_mudanca', 'administrador'), ...);

// Apenas administradores
app.delete('/api/clear-database', requireAuth, requireRole('administrador'), ...);
```

### Frontend
As rotas estão protegidas com `ProtectedRoute`:

```jsx
<Route 
  path="dados" 
  element={
    <ProtectedRoute requiredAnyRole={['lider_mudanca', 'administrador']}>
      <DataEditor />
    </ProtectedRoute>
  } 
/>

<Route 
  path="configuracoes" 
  element={
    <ProtectedRoute requiredRole="administrador">
      <Settings />
    </ProtectedRoute>
  } 
/>
```

## 🔍 Verificar Permissões no Código

### Frontend
```jsx
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { hasRole, hasAnyRole, profile } = useAuth();

  if (hasRole('administrador')) {
    // Código apenas para administradores
  }

  if (hasAnyRole(['lider_mudanca', 'administrador'])) {
    // Código para líderes e administradores
  }

  return <div>Role atual: {profile?.role}</div>;
}
```

### Backend
```javascript
// O middleware já verifica automaticamente
// req.user contém informações do usuário
app.get('/api/example', requireAuth, (req, res) => {
  const userRole = req.user.role;
  const userId = req.user.id;
  // ...
});
```

## 📊 Estrutura do Banco de Dados

### Tabela `user_profiles`
```sql
- id (UUID, FK para auth.users)
- email (TEXT)
- full_name (TEXT)
- role (TEXT): 'administrador', 'lider_mudanca', 'visualizador'
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Tabela `allowed_domains`
```sql
- id (BIGINT)
- domain (TEXT, UNIQUE)
- description (TEXT)
- active (BOOLEAN)
- created_at (TIMESTAMP)
```

## 🔐 Row Level Security (RLS)

O Supabase usa RLS para proteger os dados:

- **Visualizadores**: Podem apenas ler dados
- **Líderes**: Podem ler e modificar dados
- **Administradores**: Acesso total

As políticas estão definidas em `backend/supabase/auth-schema.sql`.

## 🐛 Troubleshooting

### "Token inválido ou expirado"
- Verifique se o token está sendo enviado no header `Authorization: Bearer <token>`
- Verifique se o token não expirou (faça login novamente)

### "Domínio não permitido"
- Verifique se o domínio está na tabela `allowed_domains`
- Verifique se o domínio está ativo (`active = true`)
- Verifique a variável `ALLOWED_EMAIL_DOMAINS` no backend

### "Acesso negado"
- Verifique se o usuário tem o role necessário
- Verifique as políticas RLS no Supabase

### Usuário não consegue fazer login
- Verifique se o email foi confirmado no Supabase
- Verifique se o perfil foi criado na tabela `user_profiles`
- Verifique os logs do backend para erros

## 📝 Notas Importantes

1. **Primeiro Administrador**: Crie manualmente via SQL ou promova um usuário existente
2. **Domínios**: Podem ser gerenciados via interface (apenas admins) ou SQL
3. **Roles**: São validados tanto no backend (middleware) quanto no frontend (ProtectedRoute)
4. **RLS**: Protege os dados diretamente no banco, mesmo se alguém contornar o backend
5. **Tokens**: São gerenciados automaticamente pelo Supabase Auth

## 🔄 Migração de Usuários Existentes

Se você já tem usuários no sistema antigo:

1. Crie contas no Supabase Auth para cada usuário
2. Insira perfis na tabela `user_profiles`:
```sql
INSERT INTO user_profiles (id, email, full_name, role)
VALUES (
  'uuid-do-usuario-no-supabase',
  'usuario@vtal.com',
  'Nome do Usuário',
  'visualizador' -- ou 'lider_mudanca' ou 'administrador'
);
```

## ✅ Checklist de Configuração

- [ ] Projeto Supabase criado
- [ ] Schema SQL executado no Supabase
- [ ] Variáveis de ambiente configuradas (backend e frontend)
- [ ] Dependências instaladas
- [ ] Primeiro administrador criado
- [ ] Domínios permitidos configurados
- [ ] Teste de cadastro realizado
- [ ] Teste de login realizado
- [ ] Permissões testadas (visualizador, líder, admin)
