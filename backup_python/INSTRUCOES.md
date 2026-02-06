# 📖 Instruções de Uso - Janela de Mudança TI

## 🚀 Como Iniciar

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Execute a aplicação:**
```bash
streamlit run app.py
```

3. **Acesse no navegador:**
   - A aplicação abrirá automaticamente em `http://localhost:8501`

## 📁 Estrutura do Arquivo Excel

O arquivo Excel deve ter **4 abas** com os seguintes nomes (ou contendo essas palavras):

- **REDE** (72 atividades esperadas)
- **OPENSHIFT** (39 atividades esperadas)
- **NFS** (17 atividades esperadas)
- **SI** (25 atividades esperadas)

### Colunas Esperadas (em ordem):

1. **Seq** - Número sequencial da atividade
2. **Atividade** - Nome/descrição da atividade
3. **Grupo** - Grupo responsável
4. **Localidade** - Local da execução
5. **Executor** - Pessoa responsável pela execução
6. **Telefone** - Contato do executor
7. **Inicio** - Data/hora planejada de início
8. **Fim** - Data/hora planejada de término
9. **Tempo** - Duração estimada

## 📊 Funcionalidades

### 1. Dashboard
- Visualize indicadores principais (Total, Concluídas, Em Execução, Planejadas, Atrasadas)
- Gráficos interativos:
  - Distribuição de Status (Pizza)
  - Andamento por CRQ (Barras)
  - Top 10 Atividades Atrasadas (Barras Horizontais)
  - Progresso por CRQ (Barras)
- Tabelas de detalhes (segmentadas por CRQ):
  - Atividades em Execução
  - Atividades Atrasadas
  - Próximas Atividades a Executar
- Status por CRQ (cards detalhados)

### 2. Editor de Dados
- Selecione o CRQ (REDE, OPENSHIFT, NFS, SI)
- Filtre por Status, Executor ou busque por Atividade
- Edite diretamente na tabela:
  - **Status**: Dropdown com opções (Planejado, Em Execução, Concluído, Atrasado, Adiantado)
  - **Horário Início Real**: Formato `DD/MM/AAAA HH:MM:SS`
  - **Horário Fim Real**: Formato `DD/MM/AAAA HH:MM:SS`
  - **Observações**: Texto livre
  - **Atraso**: Calculado automaticamente (não editável)

### 3. Comunicação
- Gera automaticamente uma mensagem consolidada
- Inclui:
  - Andamento geral
  - Andamento por CRQ (apenas se houver atividades em execução)
  - CRQs concluídos (100%)
  - Atividades atrasadas com detalhes
- Botão para copiar para clipboard

### 4. Configurações
- Informações sobre a aplicação
- Formato de data/hora esperado
- Status disponíveis
- Estrutura do arquivo Excel

## 💾 Persistência de Dados

- Os dados de controle (Status, Horários Reais, Atraso, Observações) são salvos automaticamente em um banco SQLite local (`db/activity_control.db`)
- Os dados são mantidos entre sessões
- O arquivo Excel original **NÃO é modificado**

## ⚠️ Observações Importantes

1. **Formato de Data/Hora:**
   - Use sempre o formato: `DD/MM/AAAA HH:MM:SS`
   - Exemplo: `25/12/2024 14:30:00`

2. **Validações:**
   - Horário Fim Real deve ser maior ou igual ao Horário Início Real
   - Datas devem estar no formato correto
   - Status deve ser uma das opções disponíveis

3. **Cálculo de Atraso:**
   - Calculado automaticamente quando Horário Fim Real é preenchido
   - Baseado na diferença entre Fim Real e Fim Planejado
   - Valores negativos indicam adiantamento

4. **Cache:**
   - O Streamlit usa cache para melhorar performance
   - Se o arquivo Excel for atualizado, use o botão "🔄 Atualizar" ou "🗑️ Limpar Cache"

## 🔧 Solução de Problemas

### Erro ao carregar arquivo Excel
- Verifique se o arquivo tem as 4 abas esperadas
- Verifique se as colunas estão na ordem correta
- Verifique se não há linhas vazias no início

### Erro ao copiar para clipboard
- Se o pyperclip não funcionar, o código da mensagem será exibido
- Selecione manualmente e pressione Ctrl+C

### Dados não estão sendo salvos
- Verifique se há erros de validação (datas inválidas, etc.)
- Verifique se o banco de dados tem permissões de escrita

### Cache não está atualizando
- Use o botão "🗑️ Limpar Cache" na sidebar
- Ou reinicie a aplicação

## 📞 Suporte

Para problemas ou dúvidas, verifique:
1. Os logs no console
2. As mensagens de erro na interface
3. A estrutura do arquivo Excel
