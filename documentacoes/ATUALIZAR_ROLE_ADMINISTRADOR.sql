-- ============================================
-- Script para tornar um usuário Administrador
-- Execute este script no SQL Editor do Supabase
-- ============================================

-- IMPORTANTE: Substitua 'SEU_EMAIL@vtal.com' pelo seu email real!

-- 1. Verificar usuários existentes e seus roles
SELECT id, email, role, full_name, created_at 
FROM user_profiles 
ORDER BY created_at DESC;

-- 2. Atualizar seu usuário para administrador
-- SUBSTITUA 'SEU_EMAIL@vtal.com' PELO SEU EMAIL!
UPDATE user_profiles 
SET role = 'administrador',
    updated_at = NOW()
WHERE email = 'SEU_EMAIL@vtal.com';

-- 3. Verificar se foi atualizado corretamente
SELECT id, email, role, full_name 
FROM user_profiles 
WHERE email = 'SEU_EMAIL@vtal.com';

-- ============================================
-- Se o perfil não existir, crie primeiro:
-- ============================================

-- Primeiro, encontre o ID do usuário:
-- Vá em Authentication > Users no Supabase Dashboard
-- Ou use este query (requer permissões especiais):
-- SELECT id, email FROM auth.users WHERE email = 'SEU_EMAIL@vtal.com';

-- Depois, crie o perfil (substitua 'ID_DO_USUARIO' pelo ID real):
/*
INSERT INTO user_profiles (id, email, role, full_name)
VALUES (
  'ID_DO_USUARIO',           -- Substitua pelo ID do usuário do Supabase Auth
  'SEU_EMAIL@vtal.com',      -- Substitua pelo seu email
  'administrador',
  'Seu Nome'                  -- Opcional: seu nome completo
)
ON CONFLICT (id) DO UPDATE 
SET role = 'administrador',
    updated_at = NOW();
*/

-- ============================================
-- FIM DO SCRIPT
-- ============================================
-- 
-- Após executar:
-- 1. Faça logout do sistema
-- 2. Faça login novamente
-- 3. Verifique se o menu "Usuários" aparece
-- 4. Verifique se mostra "Administrador" no perfil
-- ============================================
