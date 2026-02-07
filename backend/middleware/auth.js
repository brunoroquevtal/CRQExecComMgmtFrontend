/**
 * Middleware de autenticação usando Supabase
 */
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;

// Criar cliente Supabase para verificação de tokens
let supabaseClient = null;
if (supabaseUrl && supabaseServiceKey) {
  supabaseClient = createClient(supabaseUrl, supabaseServiceKey);
}

/**
 * Middleware para verificar autenticação
 */
async function requireAuth(req, res, next) {
  // Se Supabase não está configurado, permitir acesso (modo desenvolvimento)
  if (!supabaseClient) {
    console.warn('[AUTH] Supabase não configurado - permitindo acesso sem autenticação');
    req.user = { id: 'dev-user', role: 'administrador' }; // Modo dev
    return next();
  }

  try {
    // Obter token do header Authorization
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token de autenticação não fornecido' });
    }

    const token = authHeader.substring(7); // Remover "Bearer "

    // Verificar token com Supabase
    const { data: { user }, error } = await supabaseClient.auth.getUser(token);

    if (error || !user) {
      return res.status(401).json({ error: 'Token inválido ou expirado' });
    }

    // Buscar perfil do usuário
    let profile = null;
    let profileError = null;
    
    try {
      const result = await supabaseClient
        .from('user_profiles')
        .select('*')
        .eq('id', user.id)
        .single();
      
      profile = result.data;
      profileError = result.error;
    } catch (err) {
      console.warn('[AUTH] Erro ao buscar perfil do Supabase:', err.message);
      profileError = err;
    }

    // Se perfil não existe ou houve erro, criar um padrão ou usar dados básicos
    if (profileError || !profile) {
      // Criar perfil padrão se não existir
      try {
        const defaultProfile = {
          id: user.id,
          email: user.email,
          role: 'visualizador',
          full_name: user.user_metadata?.full_name || user.email?.split('@')[0] || 'Usuário'
        };

        const { data: newProfile, error: insertError } = await supabaseClient
          .from('user_profiles')
          .insert(defaultProfile)
          .select()
          .single();

        if (!insertError && newProfile) {
          req.user = {
            id: user.id,
            email: user.email,
            role: newProfile.role,
            full_name: newProfile.full_name,
            created_at: newProfile.created_at,
            updated_at: newProfile.updated_at
          };
        } else {
          // Se não conseguir criar, usar perfil básico
          console.warn('[AUTH] Não foi possível criar perfil no Supabase, usando perfil básico');
          req.user = {
            id: user.id,
            email: user.email,
            role: 'visualizador',
            full_name: user.user_metadata?.full_name || user.email?.split('@')[0] || 'Usuário'
          };
        }
      } catch (createError) {
        console.warn('[AUTH] Erro ao criar perfil padrão:', createError.message);
        // Usar perfil básico em caso de erro
        req.user = {
          id: user.id,
          email: user.email,
          role: 'visualizador',
          full_name: user.user_metadata?.full_name || user.email?.split('@')[0] || 'Usuário'
        };
      }
    } else {
      // Adicionar informações do usuário à requisição
      req.user = {
        id: user.id,
        email: user.email,
        role: profile.role,
        full_name: profile.full_name,
        created_at: profile.created_at,
        updated_at: profile.updated_at
      };
    }

    next();
  } catch (error) {
    console.error('[AUTH] Erro ao verificar autenticação:', error);
    return res.status(500).json({ error: 'Erro ao verificar autenticação' });
  }
}

/**
 * Middleware para verificar se usuário tem role específica
 */
function requireRole(...allowedRoles) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Usuário não autenticado' });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ 
        error: 'Acesso negado',
        required: allowedRoles,
        current: req.user.role
      });
    }

    next();
  };
}

/**
 * Middleware opcional - adiciona user se autenticado, mas não bloqueia
 */
async function optionalAuth(req, res, next) {
  if (!supabaseClient) {
    return next();
  }

  try {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const { data: { user }, error } = await supabaseClient.auth.getUser(token);

      if (!error && user) {
        const { data: profile } = await supabaseClient
          .from('user_profiles')
          .select('*')
          .eq('id', user.id)
          .single();

        if (profile) {
          req.user = {
            id: user.id,
            email: user.email,
            role: profile.role,
            full_name: profile.full_name
          };
        }
      }
    }
  } catch (error) {
    // Ignorar erros em auth opcional
  }

  next();
}

module.exports = {
  requireAuth,
  requireRole,
  optionalAuth,
  supabaseClient
};
