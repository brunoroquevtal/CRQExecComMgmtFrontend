/**
 * Rotas de autenticação usando Supabase
 */
const express = require('express');
const router = express.Router();
const { createClient } = require('@supabase/supabase-js');
const { requireAuth, requireRole } = require('../middleware/auth');

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

// Cliente Supabase para operações administrativas
let supabaseAdmin = null;
if (supabaseUrl && supabaseServiceKey) {
  supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey);
}

// Cliente Supabase público (para frontend)
let supabasePublic = null;
if (supabaseUrl && supabaseAnonKey) {
  supabasePublic = createClient(supabaseUrl, supabaseAnonKey);
}

/**
 * Obter domínios permitidos (público, para validação no frontend)
 */
router.get('/allowed-domains', async (req, res) => {
  try {
    if (!supabasePublic) {
      // Se não usar Supabase, retornar domínios do .env
      const domains = (process.env.ALLOWED_EMAIL_DOMAINS || 'vtal.com').split(',').map(d => d.trim());
      return res.json({ domains });
    }

    const { data, error } = await supabasePublic
      .from('allowed_domains')
      .select('domain, description')
      .eq('active', true);

    if (error) {
      console.error('Erro ao buscar domínios:', error);
      // Fallback para .env
      const domains = (process.env.ALLOWED_EMAIL_DOMAINS || 'vtal.com').split(',').map(d => d.trim());
      return res.json({ domains });
    }

    res.json({ 
      domains: data.map(d => d.domain),
      descriptions: data.reduce((acc, d) => {
        acc[d.domain] = d.description;
        return acc;
      }, {})
    });
  } catch (error) {
    console.error('Erro ao obter domínios permitidos:', error);
    const domains = (process.env.ALLOWED_EMAIL_DOMAINS || 'vtal.com').split(',').map(d => d.trim());
    res.json({ domains });
  }
});

/**
 * Cadastro de novo usuário
 * O cadastro real é feito pelo Supabase Auth no frontend
 * Esta rota apenas valida o domínio
 */
router.post('/signup', async (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({ error: 'Email é obrigatório' });
    }

    // Validar domínio do email
    const emailDomain = email.toLowerCase().split('@')[1];
    if (!emailDomain) {
      return res.status(400).json({ error: 'Email inválido' });
    }

    // Verificar domínios permitidos
    let allowedDomains = [];
    if (supabasePublic) {
      const { data } = await supabasePublic
        .from('allowed_domains')
        .select('domain')
        .eq('active', true);
      
      if (data) {
        allowedDomains = data.map(d => d.domain);
      }
    }

    // Fallback para .env se não houver dados do Supabase
    if (allowedDomains.length === 0) {
      allowedDomains = (process.env.ALLOWED_EMAIL_DOMAINS || 'vtal.com')
        .split(',')
        .map(d => d.trim());
    }

    if (!allowedDomains.includes(emailDomain)) {
      return res.status(403).json({ 
        error: 'Domínio de email não permitido',
        allowedDomains: allowedDomains
      });
    }

    // Retornar sucesso (o cadastro real será feito pelo frontend via Supabase Auth)
    res.json({ 
      success: true,
      message: 'Domínio permitido. Você pode prosseguir com o cadastro.',
      allowedDomains
    });
  } catch (error) {
    console.error('Erro ao validar cadastro:', error);
    res.status(500).json({ error: 'Erro ao validar cadastro' });
  }
});

/**
 * Obter perfil do usuário autenticado
 */
router.get('/profile', requireAuth, async (req, res) => {
  try {
    // Se o middleware já carregou o perfil, retornar diretamente
    if (req.user && req.user.role) {
      return res.json({
        id: req.user.id,
        email: req.user.email,
        role: req.user.role,
        full_name: req.user.full_name || req.user.email?.split('@')[0] || 'Usuário',
        created_at: req.user.created_at,
        updated_at: req.user.updated_at
      });
    }

    // Se Supabase não está configurado, retornar perfil básico
    if (!supabaseAdmin) {
      return res.json({
        id: req.user.id,
        email: req.user.email,
        role: req.user.role || 'visualizador',
        full_name: req.user.full_name || req.user.email?.split('@')[0] || 'Usuário'
      });
    }

    // Buscar perfil do Supabase
    const { data, error } = await supabaseAdmin
      .from('user_profiles')
      .select('*')
      .eq('id', req.user.id)
      .single();

    if (error || !data) {
      // Se perfil não existe, criar um padrão
      const defaultProfile = {
        id: req.user.id,
        email: req.user.email,
        role: 'visualizador',
        full_name: req.user.email?.split('@')[0] || 'Usuário',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      // Tentar criar o perfil no Supabase
      try {
        const { data: newProfile, error: insertError } = await supabaseAdmin
          .from('user_profiles')
          .insert(defaultProfile)
          .select()
          .single();

        if (!insertError && newProfile) {
          return res.json(newProfile);
        }
      } catch (insertErr) {
        console.warn('Erro ao criar perfil padrão:', insertErr);
      }

      // Retornar perfil padrão mesmo se não conseguir criar no Supabase
      return res.json(defaultProfile);
    }

    res.json(data);
  } catch (error) {
    console.error('Erro ao obter perfil:', error);
    res.status(500).json({ error: 'Erro ao obter perfil' });
  }
});

/**
 * Atualizar perfil do usuário
 */
router.put('/profile', requireAuth, async (req, res) => {
  try {
    const { full_name } = req.body;

    if (!supabaseAdmin) {
      return res.status(503).json({ error: 'Supabase não configurado' });
    }

    const updates = {};
    if (full_name !== undefined) {
      updates.full_name = full_name;
    }

    // Apenas admin pode mudar role
    if (req.body.role && req.user.role !== 'administrador') {
      return res.status(403).json({ error: 'Apenas administradores podem alterar roles' });
    }

    if (req.body.role && req.user.role === 'administrador') {
      updates.role = req.body.role;
    }

    const { data, error } = await supabaseAdmin
      .from('user_profiles')
      .update(updates)
      .eq('id', req.user.id)
      .select()
      .single();

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    res.json(data);
  } catch (error) {
    console.error('Erro ao atualizar perfil:', error);
    res.status(500).json({ error: 'Erro ao atualizar perfil' });
  }
});

/**
 * Listar todos os usuários (apenas administradores)
 */
router.get('/users', requireAuth, requireRole('administrador'), async (req, res) => {
  try {
    if (!supabaseAdmin) {
      return res.status(503).json({ error: 'Supabase não configurado' });
    }

    const { data, error } = await supabaseAdmin
      .from('user_profiles')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    res.json({ users: data });
  } catch (error) {
    console.error('Erro ao listar usuários:', error);
    res.status(500).json({ error: 'Erro ao listar usuários' });
  }
});

/**
 * Atualizar role de um usuário (apenas administradores)
 */
router.put('/users/:userId/role', requireAuth, requireRole('administrador'), async (req, res) => {
  try {
    const { userId } = req.params;
    const { role } = req.body;

    if (!['administrador', 'lider_mudanca', 'visualizador'].includes(role)) {
      return res.status(400).json({ error: 'Role inválido' });
    }

    if (!supabaseAdmin) {
      return res.status(503).json({ error: 'Supabase não configurado' });
    }

    const { data, error } = await supabaseAdmin
      .from('user_profiles')
      .update({ role })
      .eq('id', userId)
      .select()
      .single();

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    res.json(data);
  } catch (error) {
    console.error('Erro ao atualizar role:', error);
    res.status(500).json({ error: 'Erro ao atualizar role' });
  }
});

/**
 * Gerenciar domínios permitidos (apenas administradores)
 */
router.get('/domains', requireAuth, requireRole('administrador'), async (req, res) => {
  try {
    if (!supabaseAdmin) {
      const domains = (process.env.ALLOWED_EMAIL_DOMAINS || 'vtal.com').split(',').map(d => d.trim());
      return res.json({ domains: domains.map(d => ({ domain: d, active: true })) });
    }

    const { data, error } = await supabaseAdmin
      .from('allowed_domains')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    res.json({ domains: data });
  } catch (error) {
    console.error('Erro ao listar domínios:', error);
    res.status(500).json({ error: 'Erro ao listar domínios' });
  }
});

router.post('/domains', requireAuth, requireRole('administrador'), async (req, res) => {
  try {
    const { domain, description } = req.body;

    if (!domain) {
      return res.status(400).json({ error: 'Domínio é obrigatório' });
    }

    if (!supabaseAdmin) {
      return res.status(503).json({ error: 'Supabase não configurado' });
    }

    const { data, error } = await supabaseAdmin
      .from('allowed_domains')
      .insert({ domain: domain.toLowerCase(), description })
      .select()
      .single();

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    res.json(data);
  } catch (error) {
    console.error('Erro ao adicionar domínio:', error);
    res.status(500).json({ error: 'Erro ao adicionar domínio' });
  }
});

router.delete('/domains/:id', requireAuth, requireRole('administrador'), async (req, res) => {
  try {
    const { id } = req.params;

    if (!supabaseAdmin) {
      return res.status(503).json({ error: 'Supabase não configurado' });
    }

    const { error } = await supabaseAdmin
      .from('allowed_domains')
      .delete()
      .eq('id', id);

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    res.json({ success: true });
  } catch (error) {
    console.error('Erro ao remover domínio:', error);
    res.status(500).json({ error: 'Erro ao remover domínio' });
  }
});

module.exports = router;
