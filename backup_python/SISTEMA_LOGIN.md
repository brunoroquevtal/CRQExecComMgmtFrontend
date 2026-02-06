# 🔐 Sistema de Login e Controle de Acesso

## 👥 Tipos de Usuários

### 1. **Visualizador** 👁️
- **Usuário:** `visualizador`
- **Senha:** `visual123`
- **Permissões:**
  - ✅ Dashboard Executivo (apenas visualização)
  - ❌ Editor de Dados (sem acesso)
  - ❌ Comunicação (sem acesso)
  - ❌ Configurações (sem acesso)

### 2. **Líder da Mudança** 👔
- **Usuário:** `lider`
- **Senha:** `lider123`
- **Permissões:**
  - ✅ Dashboard Executivo
  - ✅ Editor de Dados (pode editar dados das CRQs)
  - ✅ Comunicação
  - ❌ Configurações (sem acesso)

### 3. **Administrador** 🔧
- **Usuário:** `admin`
- **Senha:** `admin123`
- **Permissões:**
  - ✅ Dashboard Executivo
  - ✅ Editor de Dados
  - ✅ Comunicação
  - ✅ Configurações
  - ✅ Gerenciamento de Arquivo (carregar/atualizar Excel)

---

## 🔑 Funcionalidades por Tipo de Usuário

### Visualizador
- Visualiza o dashboard com todas as informações
- Não pode editar dados
- Não pode carregar arquivos
- Ideal para stakeholders que precisam apenas acompanhar o progresso

### Líder da Mudança
- Visualiza o dashboard
- **Pode editar dados das CRQs:**
  - Status das atividades
  - Horários Reais (Início e Fim)
  - Observações
  - Milestones
  - Predecessoras
- Pode gerar mensagem de comunicação
- Não pode carregar novos arquivos Excel
- Ideal para quem gerencia a execução da mudança

### Administrador
- Acesso completo a todas as funcionalidades
- Pode carregar e atualizar arquivos Excel
- Pode editar todos os dados
- Acesso a configurações
- Ideal para gestores do sistema

---

## ⏰ Ferramentas de Data/Hora

### Botões de Hora Atual

Na página de edição de dados, há ferramentas para facilitar o preenchimento de horários:

1. **🕐 Hora Atual:**
   - Mostra a hora atual no formato `DD/MM/AAAA HH:MM:SS`
   - Botão para copiar para clipboard

2. **📋 Usar Hora Atual para Início Real:**
   - Prepara a hora atual para ser colada na coluna "Horário Início Real"
   - A hora fica disponível para copiar e colar

3. **📋 Usar Hora Atual para Fim Real:**
   - Prepara a hora atual para ser colada na coluna "Horário Fim Real"
   - A hora fica disponível para copiar e colar

### Como Usar:

1. **Opção 1 - Botão de Copiar:**
   - Clique em "📋 Copiar Hora" para copiar a hora atual
   - Cole (Ctrl+V) na célula desejada

2. **Opção 2 - Botão de Usar:**
   - Clique em "📋 Usar Hora Atual" para Início ou Fim
   - A hora será preparada e você pode copiar da mensagem de confirmação
   - Cole na célula correspondente

3. **Opção 3 - Digitação Manual:**
   - Digite manualmente no formato: `DD/MM/AAAA HH:MM:SS`
   - Exemplo: `25/01/2026 14:30:00`

---

## 🔒 Segurança

- As senhas estão definidas no código (para ambiente de desenvolvimento)
- **Recomendação para produção:** Implementar sistema de autenticação mais robusto
- Cada usuário vê apenas as funcionalidades permitidas
- A edição de dados é bloqueada para usuários sem permissão

---

## 📝 Notas Importantes

- O login é necessário ao acessar a aplicação
- Use o botão "🚪 Sair" na sidebar para fazer logout
- As permissões são verificadas em tempo real
- Usuários sem permissão de edição veem os dados em modo somente leitura

---

**Versão:** 1.1.0  
**Data:** Janeiro 2026
