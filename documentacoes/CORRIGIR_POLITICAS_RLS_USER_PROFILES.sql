-- ============================================
-- Script para corrigir políticas RLS com recursão infinita
-- Execute este script no SQL Editor do Supabase Dashboard
-- ============================================

-- PROBLEMA: As políticas de administrador estão causando recursão infinita
-- porque tentam consultar user_profiles dentro de user_profiles

-- SOLUÇÃO: Remover as políticas problemáticas e criar novas sem recursão

-- 1. Remover políticas antigas que causam recursão
DROP POLICY IF EXISTS "Admins can view all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Admins can update all profiles" ON user_profiles;

-- 2. Criar função auxiliar para verificar se usuário é administrador
-- Esta função usa auth.jwt() para evitar recursão
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM user_profiles
    WHERE id = user_id AND role = 'administrador'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Política SIMPLIFICADA: Administradores podem ver todos os perfis
-- Usa a função auxiliar que evita recursão
CREATE POLICY "Admins can view all profiles"
ON user_profiles
FOR SELECT
USING (
  -- Permitir se for o próprio perfil
  auth.uid() = id
  OR
  -- Ou se for administrador (usando função que evita recursão)
  is_admin(auth.uid())
);

-- 4. Política SIMPLIFICADA: Administradores podem atualizar todos os perfis
CREATE POLICY "Admins can update all profiles"
ON user_profiles
FOR UPDATE
USING (
  -- Permitir se for o próprio perfil
  auth.uid() = id
  OR
  -- Ou se for administrador
  is_admin(auth.uid())
)
WITH CHECK (
  -- Permitir se for o próprio perfil
  auth.uid() = id
  OR
  -- Ou se for administrador
  is_admin(auth.uid())
);

-- ============================================
-- ALTERNATIVA MAIS SIMPLES (RECOMENDADA):
-- Desabilitar RLS para operações do backend
-- O backend deve usar Service Role Key que ignora RLS
-- ============================================

-- Se preferir, você pode simplesmente desabilitar RLS:
-- ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- Mas isso só funciona se o backend usar Service Role Key
-- (que já deve estar configurado)

-- ============================================
-- FIM DO SCRIPT
-- ============================================
-- 
-- IMPORTANTE: O backend DEVE usar SUPABASE_SERVICE_ROLE_KEY
-- A Service Role Key ignora RLS completamente
-- ============================================
