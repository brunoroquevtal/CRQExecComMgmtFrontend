# 🔧 Solução: Role não atualiza após mudança no banco

## 🐛 Problema

Você alterou o role no banco de dados Supabase para `administrador`, mas o sistema ainda mostra `visualizador`.

## ✅ Solução Aplicada

O código foi atualizado para buscar o perfil diretamente do Supabase quando o backend não está disponível.

### O que foi corrigido:

1. **Busca em cascata**: 
   - Primeiro tenta buscar do backend (`/api/auth/profile`)
   - Se não existir (404), busca diretamente do Supabase
   - Só usa perfil padrão se não encontrar em nenhum lugar

2. **Função de recarregamento**: 
   - Adicionada função `reloadProfile()` para forçar atualização

## 🔄 Como Forçar Atualização

### Método 1: Logout e Login (Recomendado)

1. Faça **logout** do sistema
2. Faça **login** novamente
3. O perfil será recarregado do Supabase

### Método 2: Recarregar a Página

1. Pressione `Ctrl+F5` (ou `Cmd+Shift+R` no Mac) para recarregar sem cache
2. O perfil será recarregado automaticamente

### Método 3: Limpar Cache do Navegador

1. Abra o DevTools (F12)
2. Clique com botão direito no botão de recarregar
3. Selecione "Limpar cache e atualizar forçadamente"

## 🔍 Verificar se Está Funcionando

### 1. Verificar no Supabase

Execute este SQL no Supabase para confirmar:

```sql
SELECT id, email, role 
FROM user_profiles 
WHERE email = 'seu-email@exemplo.com';
```

O `role` deve estar como `administrador`.

### 2. Verificar no Console do Navegador

1. Abra o DevTools (F12)
2. Vá na aba **Console**
3. Faça login novamente
4. Você deve ver o perfil sendo carregado

### 3. Verificar no Sistema

Após login, você deve ver:
- ✅ Menu "Usuários" aparecendo no menu lateral
- ✅ Badge "Administrador" no perfil
- ✅ Acesso a todas as funcionalidades administrativas

## 🐛 Se Ainda Não Funcionar

### Verificar se a tabela existe

Execute no Supabase:

```sql
SELECT * FROM user_profiles LIMIT 1;
```

Se der erro, a tabela não existe. Execute o script `CRIAR_TABELA_USER_PROFILES_CORRIGIDO.sql`.

### Verificar se o perfil existe para seu usuário

Execute no Supabase:

```sql
SELECT * FROM user_profiles WHERE id = auth.uid();
```

Se não retornar nada, você precisa criar o perfil:

```sql
INSERT INTO user_profiles (id, email, role)
VALUES (auth.uid(), auth.email(), 'administrador')
ON CONFLICT (id) DO UPDATE SET role = 'administrador';
```

### Verificar RLS (Row Level Security)

Se você não consegue ver seu próprio perfil, pode ser problema de RLS. Execute:

```sql
-- Verificar políticas
SELECT * FROM pg_policies WHERE tablename = 'user_profiles';

-- Se necessário, desabilitar RLS temporariamente para teste
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
```

**⚠️ Atenção**: Desabilitar RLS remove a segurança. Reabilite depois:

```sql
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
```

## 📝 Código Atualizado

O código agora faz:

1. Tenta buscar do backend → Se 404, busca do Supabase
2. Busca diretamente da tabela `user_profiles` no Supabase
3. Usa o role que está no banco de dados
4. Só usa perfil padrão se não encontrar nada

## ✅ Checklist

- [ ] Tabela `user_profiles` existe no Supabase
- [ ] Seu usuário tem um registro na tabela
- [ ] O campo `role` está como `administrador`
- [ ] Fez logout e login novamente
- [ ] Limpou o cache do navegador (se necessário)

## 🆘 Ainda com Problemas?

Se após seguir todos os passos ainda não funcionar:

1. Verifique os logs do console do navegador (F12)
2. Verifique se há erros de CORS ou permissão
3. Verifique se o Supabase está configurado corretamente no frontend (variáveis de ambiente)
4. Tente criar o perfil manualmente via SQL (veja acima)
