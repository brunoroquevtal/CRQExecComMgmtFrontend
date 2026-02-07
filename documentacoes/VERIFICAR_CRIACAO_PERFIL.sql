-- Script para verificar e corrigir criação de perfis em user_profiles
-- Execute este script no SQL Editor do Supabase

-- 1. Verificar usuários no auth.users que não têm perfil em user_profiles
SELECT 
  au.id,
  au.email,
  au.created_at as auth_created_at,
  CASE 
    WHEN up.id IS NULL THEN 'SEM PERFIL'
    ELSE 'COM PERFIL'
  END as status_perfil,
  up.role,
  up.full_name,
  up.created_at as profile_created_at
FROM auth.users au
LEFT JOIN public.user_profiles up ON au.id = up.id
WHERE up.id IS NULL
ORDER BY au.created_at DESC;

-- 2. Criar perfis para usuários que não têm (ajuste o role conforme necessário)
INSERT INTO public.user_profiles (id, email, role, full_name, created_at, updated_at)
SELECT 
  au.id,
  au.email,
  'visualizador' as role, -- Role padrão
  COALESCE(au.raw_user_meta_data->>'full_name', SPLIT_PART(au.email, '@', 1)) as full_name,
  au.created_at,
  NOW() as updated_at
FROM auth.users au
LEFT JOIN public.user_profiles up ON au.id = up.id
WHERE up.id IS NULL
ON CONFLICT (id) DO NOTHING;

-- 3. Verificar se RLS está bloqueando inserções
-- Verificar se RLS está habilitado
SELECT 
  schemaname,
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public' 
  AND tablename = 'user_profiles';

-- Verificar políticas RLS existentes
SELECT 
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'public' 
  AND tablename = 'user_profiles';

-- 4. Se necessário, desabilitar RLS temporariamente (apenas se usar Service Role Key)
-- ⚠️ ATENÇÃO: Desabilitar RLS remove a segurança. Use apenas se o backend usar Service Role Key!
-- ALTER TABLE public.user_profiles DISABLE ROW LEVEL SECURITY;

-- 5. Verificar se a Service Role Key está sendo usada corretamente
-- (Isso deve ser verificado nas variáveis de ambiente do backend, não no SQL)

-- 6. Criar função RPC para criar perfil (alternativa se RLS estiver bloqueando)
CREATE OR REPLACE FUNCTION create_user_profile(
  p_user_id UUID,
  p_email TEXT,
  p_role TEXT DEFAULT 'visualizador',
  p_full_name TEXT DEFAULT NULL
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER -- Executa com privilégios do criador da função
AS $$
DECLARE
  v_profile JSON;
BEGIN
  INSERT INTO public.user_profiles (id, email, role, full_name, created_at, updated_at)
  VALUES (
    p_user_id,
    p_email,
    p_role,
    COALESCE(p_full_name, SPLIT_PART(p_email, '@', 1)),
    NOW(),
    NOW()
  )
  ON CONFLICT (id) DO UPDATE
  SET 
    email = EXCLUDED.email,
    updated_at = NOW()
  RETURNING json_build_object(
    'id', id,
    'email', email,
    'role', role,
    'full_name', full_name
  ) INTO v_profile;
  
  RETURN v_profile;
EXCEPTION
  WHEN OTHERS THEN
    RETURN json_build_object(
      'error', TRUE,
      'message', SQLERRM,
      'code', SQLSTATE
    );
END;
$$;

-- 7. Testar a função RPC (substitua os valores pelos dados reais)
-- SELECT create_user_profile(
--   'uuid-do-usuario'::UUID,
--   'email@exemplo.com',
--   'visualizador',
--   'Nome Completo'
-- );

-- 8. Verificar todos os perfis criados
SELECT 
  id,
  email,
  role,
  full_name,
  created_at,
  updated_at
FROM public.user_profiles
ORDER BY created_at DESC
LIMIT 20;
