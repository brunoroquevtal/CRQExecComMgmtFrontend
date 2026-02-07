# 📊 Lógica de Importação do Excel - Documentação Completa

## 🔄 Fluxo Geral de Processamento

### 1. **Upload e Validação Inicial**
- ✅ Aceita apenas arquivos `.xlsx` ou `.xls`
- ✅ Requer autenticação e role `lider_mudanca` ou `administrador`
- ✅ Lê todas as abas do arquivo Excel

### 2. **Identificação de Sequências (CRQs)**
O sistema identifica as sequências pelo **nome da aba**:
- Procura por: `REDE`, `OPENSHIFT`, `NFS`, `SI` (case-insensitive)
- **Abas não reconhecidas são IGNORADAS** (não processadas)

### 3. **Processamento de Cada Linha**

#### 3.1. **Normalização de Colunas**
O sistema é **tolerante a variações** nos nomes das colunas:
- Procura por nomes alternativos (case-insensitive, ignora espaços)
- Exemplos aceitos:
  - `Seq`, `seq`, `SEQ`, `Sequência`, `sequencia`
  - `Atividade`, `atividade`, `ATIVIDADE`
  - `Grupo`, `grupo`, `GRUPO`
  - `Inicio`, `inicio`, `INICIO`, `Início`, `início`, `INÍCIO`
  - `Fim`, `fim`, `FIM`
  - `Tempo`, `tempo`, `TEMPO`

#### 3.2. **Validação de Dados**

**Critérios para uma linha ser considerada VÁLIDA (`is_visible = 1`):**
1. ✅ **Seq válido**: Deve ser um número válido
2. ✅ **Atividade não vazia**: Campo `Atividade` deve ter conteúdo
3. ✅ **Pelo menos uma data**: Deve ter `Inicio` OU `Fim` válidos

**Linhas que NÃO atendem esses critérios são marcadas como `is_visible = 0`** (ocultas)

#### 3.3. **Validação de Datas**
- Tenta converter `Inicio` e `Fim` para objetos Date
- **Rejeita valores que parecem ser status** em vez de datas:
  - Palavras-chave rejeitadas (ver seção abaixo)
- Se não conseguir converter ou parecer status → `null`

#### 3.4. **Conversão de Tempo**
- Aceita formato `hh:mm` ou `hh:mm:ss`
- Converte para **minutos** (número decimal)
- Se já for número, assume que já está em minutos
- Se inválido → `0`

### 4. **Marcação como Milestone**

**Uma atividade é marcada como `is_milestone = true` quando:**
- ✅ Campo `Grupo` está **vazio** ou **nulo**
- Verificações feitas:
  - `Grupo` é `null` ou `undefined`
  - `Grupo` é string vazia `""`
  - `Grupo` contém apenas espaços em branco
  - `Grupo` é `"nan"` (string)

**Milestones:**
- ❌ **NÃO são contados** nas estatísticas
- ❌ **NÃO aparecem** no Dashboard (exceto se explicitamente incluídos)
- ❌ **NÃO são considerados** no cálculo de status
- ✅ **Aparecem** no Gantt Chart (mas com status "N/A")
- ✅ **Podem ser editados** manualmente

### 5. **Salvamento no Banco**

#### 5.1. **Tabela `excel_data`**
- ✅ **TODAS as linhas são salvas** (visíveis e ocultas)
- Campo `is_visible` indica se deve ser exibida:
  - `is_visible = 1`: Linha válida (será exibida)
  - `is_visible = 0`: Linha inválida (oculta, mas salva)

#### 5.2. **Tabela `activity_control`**
- ✅ **Apenas linhas VISÍVEIS** recebem registro de controle
- Criado apenas se não existir registro para `(seq, sequencia)`
- Campos iniciais:
  - `status`: `'Planejado'`
  - `is_milestone`: baseado no campo `Grupo` (vazio = milestone)
  - `horario_inicio_real`: `null`
  - `horario_fim_real`: `null`
  - `atraso_minutos`: `0`
  - `observacoes`: `''`

## 📋 Resumo: O que é Descartado vs. O que é Salvo

### ❌ **Linhas DESCARTADAS (não salvas)**
- Abas que não contêm `REDE`, `OPENSHIFT`, `NFS` ou `SI` no nome
- Abas completamente vazias

### ✅ **Linhas SALVAS mas OCULTAS (`is_visible = 0`)**
- Linhas sem `Seq` válido
- Linhas sem `Atividade` preenchida
- Linhas sem `Inicio` E sem `Fim` válidos
- Linhas onde `Inicio` ou `Fim` parecem ser status em vez de datas

### ✅ **Linhas SALVAS e VISÍVEIS (`is_visible = 1`)**
- Todas as linhas que atendem os critérios de validação
- Recebem registro em `activity_control`

### 🎯 **Linhas Marcadas como MILESTONE**
- Linhas onde `Grupo` está vazio/nulo
- São salvas normalmente, mas:
  - Não contam nas estatísticas
  - Status sempre "N/A"
  - Não aparecem no Dashboard (por padrão)

## 🔍 Exemplos Práticos

### Exemplo 1: Linha Válida Normal
```
Seq: 123
Atividade: "Configurar servidor"
Grupo: "Infraestrutura"
Inicio: "2024-01-01 10:00:00"
Fim: "2024-01-01 12:00:00"
Tempo: "02:00"
```
**Resultado**: ✅ Salva, visível, não é milestone

### Exemplo 2: Linha Milestone
```
Seq: 456
Atividade: "Marco de Início"
Grupo: "" (vazio)
Inicio: "2024-01-01 08:00:00"
Fim: "2024-01-01 08:00:00"
```
**Resultado**: ✅ Salva, visível, **É MILESTONE**

### Exemplo 3: Linha Inválida (sem data)
```
Seq: 789
Atividade: "Atividade sem data"
Grupo: "Desenvolvimento"
Inicio: null
Fim: null
```
**Resultado**: ✅ Salva, **OCULTA** (`is_visible = 0`), não recebe `activity_control`

### Exemplo 4: Linha com Status em vez de Data
```
Seq: 101
Atividade: "Atividade concluída"
Grupo: "Testes"
Inicio: "Concluído" (texto, não data)
Fim: null
```
**Resultado**: ✅ Salva, **OCULTA** (`is_visible = 0`), `Inicio` rejeitado por parecer status

### Exemplo 5: Aba Não Reconhecida
```
Nome da aba: "Dados Gerais"
```
**Resultado**: ❌ **DESCARTADA** (aba não processada)

## 🎨 Comportamento no Frontend

### Dashboard
- Mostra apenas atividades **visíveis** e **não-milestones**
- Milestones são excluídos das contagens

### Gantt Chart
- Mostra todas as atividades **visíveis** (incluindo milestones)
- Milestones aparecem com status "N/A"

### Data Editor
- Mostra todas as atividades **visíveis**
- Milestones podem ser editados
- Status de milestones sempre "N/A"

## ⚙️ Configurações Importantes

### Sequências Reconhecidas
Definidas em `SEQUENCIAS`:
- `REDE`
- `OPENSHIFT`
- `NFS`
- `SI`

### Palavras-chave de Status (rejeitadas como datas)
Os seguintes status são **rejeitados** quando aparecem nos campos `Inicio` ou `Fim`:
- `concluído`, `concluido`
- `em execução no prazo`, `em execucao no prazo`
- `em execução fora do prazo`, `em execucao fora do prazo`
- `a iniciar no prazo`
- `a iniciar fora do prazo`
- `n/a`, `na`

**Nota**: Essas palavras-chave são usadas para identificar quando um campo de data contém um status em vez de uma data válida, evitando que status sejam interpretados incorretamente como datas.

## 📝 Status Possíveis no Sistema

O sistema utiliza os seguintes status para atividades:

1. **Concluído** ✅
   - Atividade finalizada (tem `horario_fim_real`)

2. **Em execução no prazo** ⏳
   - Atividade em andamento sem atraso
   - Tem `horario_inicio_real` mas não tem `horario_fim_real`
   - `atraso_minutos <= 0`

3. **Em execução fora do prazo** 🔴
   - Atividade em andamento com atraso
   - Tem `horario_inicio_real` mas não tem `horario_fim_real`
   - `atraso_minutos > 0`

4. **A Iniciar no prazo** 🟦
   - Atividade ainda não iniciada, sem atraso
   - Não tem `horario_inicio_real`
   - `atraso_minutos <= 0`

5. **A Iniciar fora do prazo** 🟠
   - Atividade ainda não iniciada, com atraso
   - Não tem `horario_inicio_real`
   - `atraso_minutos > 0`

6. **N/A** (Milestones)
   - Apenas para atividades marcadas como milestone
   - Status fixo, não calculado

## 📝 Notas Técnicas

1. **Tolerância a Erros**: O sistema tenta salvar o máximo possível, mesmo com dados parciais
2. **Normalização**: Nomes de colunas são normalizados para facilitar importação de diferentes formatos
3. **Preservação de Dados**: Linhas inválidas são salvas mas marcadas como ocultas (podem ser corrigidas depois)
4. **Milestones**: Identificação automática baseada em `Grupo` vazio
5. **Performance**: Inserções em lotes de 1000 registros (limite do Supabase)
