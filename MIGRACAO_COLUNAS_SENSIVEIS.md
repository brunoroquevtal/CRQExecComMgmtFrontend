# 🔒 Migração: Remoção de Colunas Sensíveis

## 📋 Resumo

Esta migração remove colunas sensíveis do banco de dados para proteger dados pessoais:
- ❌ **executor** (nome da pessoa)
- ❌ **telefone** (telefone de contato)
- ❌ **localidade** (localização específica)

## ✅ Colunas Mantidas

- ✅ **seq** - Número sequencial
- ✅ **sequencia** - CRQ/Sequência (REDE, OPENSHIFT, NFS, SI)
- ✅ **atividade** - Descrição da atividade
- ✅ **grupo** - Grupo de trabalho (não pessoal)
- ✅ **inicio** - Data/hora de início planejada
- ✅ **fim** - Data/hora de fim planejada
- ✅ **tempo** - Duração estimada
- ✅ **file_name** - Nome do arquivo Excel
- ✅ **data_importacao** - Data de importação

## 🚀 Como Executar a Migração

### 1. Fazer Backup (Recomendado)

O script de migração cria um backup automaticamente, mas é recomendado fazer um backup manual também:

```bash
# Windows PowerShell
Copy-Item "db\activity_control.db" "db\activity_control.db.backup"

# Linux/Mac
cp db/activity_control.db db/activity_control.db.backup
```

### 2. Executar Migração

```bash
cd backend
node migrate_remove_sensitive_columns.js
```

### 3. Verificar Resultado

O script irá:
- ✅ Criar backup automático
- ✅ Verificar estrutura atual
- ✅ Criar nova tabela sem colunas sensíveis
- ✅ Copiar dados existentes
- ✅ Remover tabela antiga
- ✅ Recriar índices

## ⚠️ Importante

- **Backup automático**: O script cria um backup antes de migrar
- **Dados preservados**: Todos os dados não-sensíveis são preservados
- **Irreversível**: As colunas sensíveis serão permanentemente removidas
- **Sem downtime**: A migração é rápida e não requer parar a aplicação

## 🔄 Mudanças no Código

### Backend

1. **database.js**: Tabela `excel_data` atualizada sem colunas sensíveis
2. **server.js**: Processamento de Excel atualizado para não ler colunas sensíveis
3. **API endpoints**: Respostas não incluem mais dados sensíveis

### Frontend

- Componentes atualizados para não exibir dados sensíveis
- Formulários não solicitam mais informações sensíveis

## 📊 Estrutura Antes vs Depois

### Antes
```sql
CREATE TABLE excel_data (
  id INTEGER PRIMARY KEY,
  seq INTEGER,
  sequencia TEXT,
  atividade TEXT,
  grupo TEXT,
  localidade TEXT,      -- ❌ REMOVIDO
  executor TEXT,        -- ❌ REMOVIDO
  telefone TEXT,        -- ❌ REMOVIDO
  inicio TEXT,
  fim TEXT,
  tempo REAL,
  file_name TEXT,
  data_importacao TIMESTAMP
)
```

### Depois
```sql
CREATE TABLE excel_data (
  id INTEGER PRIMARY KEY,
  seq INTEGER,
  sequencia TEXT,
  atividade TEXT,
  grupo TEXT,
  inicio TEXT,
  fim TEXT,
  tempo REAL,
  file_name TEXT,
  data_importacao TIMESTAMP
)
```

## 🛡️ Segurança

Esta migração melhora a segurança da aplicação ao:
- ✅ Remover dados pessoais identificáveis (PII)
- ✅ Reduzir risco de exposição de informações sensíveis
- ✅ Cumprir boas práticas de privacidade de dados
- ✅ Facilitar conformidade com LGPD/GDPR

## 📝 Notas

- Se você precisar dos dados sensíveis no futuro, eles estarão no backup
- O backup pode ser restaurado se necessário (mas não é recomendado)
- Novos uploads de Excel não processarão mais essas colunas
