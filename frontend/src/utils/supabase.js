import { createClient } from '@supabase/supabase-js';

// Inicializar cliente Supabase
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

let supabase = null;

if (supabaseUrl && supabaseAnonKey) {
  supabase = createClient(supabaseUrl, supabaseAnonKey);
} else {
  // Apenas logar em modo desenvolvimento, não em produção
  if (import.meta.env.DEV) {
    console.info('[AUTH] Supabase não configurado. A autenticação não estará disponível. Para habilitar, configure VITE_SUPABASE_URL e VITE_SUPABASE_ANON_KEY');
  }
}

export default supabase;
