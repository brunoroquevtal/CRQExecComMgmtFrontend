# 📋 Guia de Uso - sync_excel.py

Script adaptado para sincronizar atividades do Excel com a API Node.js.

## 🚀 Instalação

1. Instale as dependências Python necessárias:

```bash
pip install -r requirements_sync.txt
```

Ou manualmente:

```bash
pip install pandas openpyxl requests
```

## ⚙️ Configuração

O script usa a API Node.js no Netlify por padrão (produção).

**URL padrão (produção):**
- `https://crqcommunidationbackend.netlify.app/.netlify/functions/api`

**Para desenvolvimento local**, defina a variável de ambiente:

**Windows PowerShell:**
```powershell
$env:API_BASE_URL="http://localhost:3000"
```

**Windows CMD:**
```cmd
set API_BASE_URL=http://localhost:3000
```

**Linux/Mac:**
```bash
export API_BASE_URL=http://localhost:3000
```

## 📖 Uso

### Modo Individual (padrão)

Envia cada atividade uma por vez:

```bash
python sync_excel.py
```

Ou com caminho do arquivo:

```bash
python sync_excel.py "C:\caminho\arquivo.xlsx"
```

### Modo Bulk (lote)

Envia todas as atividades de uma vez:

```bash
python sync_excel.py --mode bulk
```

Ou:

```bash
python sync_excel.py -m bulk "C:\caminho\arquivo.xlsx"
```

## 📝 Requisitos do Arquivo Excel

O script procura por abas que:
- Começam com **"CRQ"**
- Terminam com **"2"** (segunda tentativa de execução)

Exemplos de nomes de abas válidos:
- `CRQ REDE 2`
- `CRQOPENSHIFT2`
- `CRQ NFS 2`
- `CRQ SI 2`

## 🔍 Colunas Esperadas

O script identifica automaticamente as seguintes colunas:
- **Seq**: Número sequencial da atividade
- **Atividade**: Nome/descrição da atividade
- **Início**: Data/hora de início
- **Fim**: Data/hora de término
- **Status**: Status da atividade (Planejado, Em Execução, Concluído, etc.)

## ⚠️ Importante

1. **API deve estar rodando**: Certifique-se de que o servidor Node.js está rodando:

```bash
cd backend
npm start
```

2. **Formato de data**: O script espera datas no formato `dd/mm/yyyy hh:mm:ss`

3. **Interrupção**: Você pode parar o script com `Ctrl+C` a qualquer momento. O script aguardará a conclusão da requisição atual antes de parar.

## 📊 Exemplo de Saída

```
============================================================
SINCRONIZACAO DE ATIVIDADES DO EXCEL
============================================================

Verificando conexao com API...
[OK] Conexao com API estabelecida!

Lendo arquivo Excel: C:\arquivo.xlsx
Abas encontradas no Excel: ['CRQ REDE 2', 'CRQ OPENSHIFT 2']

Processando aba: CRQ REDE 2
Sequência identificada: REDE
  - 72 atividades extraídas

Total de atividades no Excel: 72

Processando 72 atividades individualmente...
Progresso: 72/72 (OK: 72, Falhas: 0)

============================================================
RESUMO DA SINCRONIZACAO
============================================================
Total de atividades no Excel: 72
Processadas com sucesso: 72
Falhas: 0
============================================================
```

## 🔧 Diferenças da Versão Python

- **Porta padrão**: 3000 (Node.js) ao invés de 8000 (Python)
- **Endpoints**: Usa `/api/activity` (PUT) ao invés de `/activity` (POST)
- **Sem módulos Python**: Não depende de `modules/api_client.py` ou outros módulos do projeto Python
- **Simplificado**: Versão mais simples, focada na sincronização básica

## 🐛 Solução de Problemas

### Erro: "API não está disponível"

1. Verifique se o backend está rodando:
   ```bash
   cd backend
   npm start
   ```

2. Teste a API manualmente:
   ```
   http://localhost:3000/health
   ```

3. Verifique se a porta está correta (padrão: 3000)

### Erro: "Nenhuma aba válida encontrada"

- Certifique-se de que as abas começam com "CRQ" e terminam com "2"
- Exemplo: `CRQ REDE 2` ✅, `REDE` ❌

### Erro de encoding

O script já está configurado para UTF-8. Se ainda houver problemas, verifique se o arquivo Excel está salvo corretamente.
