-- ============================================
-- Script para criar tabela user_profiles no Supabase
-- Execute este script no SQL Editor do Supabase Dashboard
-- ============================================

-- 1. Criar a tabela user_profiles
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  full_name TEXT,
  role TEXT DEFAULT 'visualizador' CHECK (role IN ('visualizador', 'lider_mudanca', 'administrador')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON user_profiles(role);
CREATE INDEX IF NOT EXISTS idx_user_profiles_created_at ON user_profiles(created_at);

-- 3. Criar função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 4. Criar trigger para atualizar updated_at
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 5. Habilitar Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- 6. Remover políticas antigas se existirem
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Admins can update all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Public can insert own profile" ON user_profiles;

-- 7. Política: Usuários podem ver seu próprio perfil
CREATE POLICY "Users can view own profile"
ON user_profiles
FOR SELECT
USING (auth.uid() = id);

-- 8. Política: Usuários podem atualizar seu próprio perfil
-- Nota: A restrição de não mudar role será feita via trigger ou aplicação
CREATE POLICY "Users can update own profile"
ON user_profiles
FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- 9. Política: Usuários podem inserir seu próprio perfil
CREATE POLICY "Public can insert own profile"
ON user_profiles
FOR INSERT
WITH CHECK (auth.uid() = id);

-- 10. Política: Administradores podem ver todos os perfis
CREATE POLICY "Admins can view all profiles"
ON user_profiles
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM user_profiles
    WHERE id = auth.uid() AND role = 'administrador'
  )
);

-- 11. Política: Administradores podem atualizar todos os perfis
CREATE POLICY "Admins can update all profiles"
ON user_profiles
FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM user_profiles
    WHERE id = auth.uid() AND role = 'administrador'
  )
);

-- 12. Criar perfis para todos os usuários existentes no auth.users
-- (Apenas se ainda não tiverem perfil)
INSERT INTO user_profiles (id, email, role, full_name)
SELECT 
  id,
  email,
  'visualizador' as role,
  raw_user_meta_data->>'full_name' as full_name
FROM auth.users
WHERE id NOT IN (SELECT id FROM user_profiles)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- FIM DO SCRIPT
-- ============================================
-- 
-- Após executar este script:
-- 1. Verifique se a tabela foi criada: Table Editor > user_profiles
-- 2. Verifique se os usuários existentes receberam perfis
-- 3. Para tornar um usuário administrador, execute:
--    UPDATE user_profiles SET role = 'administrador' WHERE email = 'seu-email@exemplo.com';
-- ============================================
