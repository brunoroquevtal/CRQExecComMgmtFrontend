# Guia de Uso da API de Atualização de Atividades

Este documento descreve como usar a API REST para atualizar tarefas do sistema de gerenciamento de CRQs.

## Índice

1. [Instalação](#instalação)
2. [Iniciando o Servidor API](#iniciando-o-servidor-api)
3. [Endpoints Disponíveis](#endpoints-disponíveis)
4. [Exemplos de Uso](#exemplos-de-uso)
5. [Script de Sincronização](#script-de-sincronização)
6. [Troubleshooting](#troubleshooting)

## Instalação

### Dependências

Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

As novas dependências incluem:
- `fastapi`: Framework para criar a API REST
- `uvicorn`: Servidor ASGI para rodar a API
- `requests`: Cliente HTTP para fazer requisições

## Iniciando o Servidor API

### Modo Desenvolvimento

#### Opção 1: Iniciar tudo de uma vez (Recomendado)

Use o script `start_all.py` para iniciar tanto o Streamlit quanto a API:

```bash
python start_all.py
```

Isso iniciará:
- API REST em `http://localhost:8000`
- Streamlit em `http://localhost:8501`

#### Opção 2: Iniciar apenas a API

Para iniciar apenas o servidor API na porta 8000:

```bash
python api_server.py
```

Ou usando uvicorn diretamente:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

#### Opção 3: Processos separados

**Terminal 1 - API:**
```bash
python api_server.py
```

**Terminal 2 - Streamlit:**
```bash
streamlit run app.py
```

### Modo Produção

Para produção, use um servidor WSGI como gunicorn ou configure um proxy reverso (nginx) apontando para uvicorn.

O servidor estará disponível em: `http://localhost:8000`

## Endpoints Disponíveis

### 1. GET `/`

Informações sobre a API e endpoints disponíveis.

**Resposta:**
```json
{
  "message": "API de Atualização de Atividades",
  "version": "1.0.0",
  "endpoints": { ... }
}
```

### 2. GET `/health`

Verifica a saúde da API e conexão com o banco de dados.

**Resposta:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-12-25T14:30:00"
}
```

### 3. GET `/activity/{sequencia}/{seq}`

Busca uma atividade específica.

**Parâmetros:**
- `sequencia`: CRQ/Sequência (REDE, OPENSHIFT, NFS, SI)
- `seq`: Número sequencial da atividade
- `excel_data_id` (query param, opcional): ID da linha no excel_data

**Exemplo:**
```bash
curl http://localhost:8000/activity/REDE/999093
```

**Resposta:**
```json
{
  "success": true,
  "activity": {
    "status": "Em Execução",
    "horario_inicio_real": "25/12/2024 14:30:00",
    "horario_fim_real": null,
    "atraso_minutos": 0,
    "observacoes": null,
    "is_milestone": false,
    "predecessoras": ""
  }
}
```

### 4. PUT `/activity`

Atualiza uma atividade.

**Body (JSON):**
```json
{
  "seq": 999093,
  "sequencia": "REDE",
  "status": "Em Execução",
  "horario_inicio_real": "25/12/2024 14:30:00",
  "horario_fim_real": "25/12/2024 15:30:00",
  "observacoes": "Atividade iniciada conforme planejado",
  "excel_data_id": 123
}
```

**Campos:**
- `seq` (obrigatório): Número sequencial da atividade
- `sequencia` (obrigatório): CRQ/Sequência (REDE, OPENSHIFT, NFS, SI)
- `status` (opcional): Status da atividade (Planejado, Em Execução, Concluído, Atrasado, Adiantado)
- `horario_inicio_real` (opcional): Horário de início real no formato `DD/MM/YYYY HH:MM:SS`
- `horario_fim_real` (opcional): Horário de fim real no formato `DD/MM/YYYY HH:MM:SS`
- `observacoes` (opcional): Observações sobre a atividade
- `excel_data_id` (opcional): ID da linha no excel_data (para identificar unicamente)

**Exemplo:**
```bash
curl -X PUT http://localhost:8000/activity \
  -H "Content-Type: application/json" \
  -d '{
    "seq": 999093,
    "sequencia": "REDE",
    "status": "Em Execução",
    "horario_inicio_real": "25/12/2024 14:30:00"
  }'
```

**Resposta:**
```json
{
  "success": true,
  "message": "Atividade atualizada com sucesso",
  "seq": 999093,
  "sequencia": "REDE",
  "updated_fields": ["status", "horario_inicio_real"]
}
```

### 5. PUT `/activities/bulk`

Atualiza múltiplas atividades em lote.

**Body (JSON):**
```json
{
  "activities": [
    {
      "seq": 999093,
      "sequencia": "REDE",
      "status": "Em Execução",
      "horario_inicio_real": "25/12/2024 14:30:00"
    },
    {
      "seq": 999094,
      "sequencia": "REDE",
      "status": "Concluído",
      "horario_fim_real": "25/12/2024 16:00:00"
    }
  ]
}
```

**Exemplo:**
```bash
curl -X PUT http://localhost:8000/activities/bulk \
  -H "Content-Type: application/json" \
  -d @activities.json
```

**Resposta:**
```json
{
  "total": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "success": true,
      "message": "Atividade atualizada com sucesso",
      "seq": 999093,
      "sequencia": "REDE",
      "updated_fields": ["status", "horario_inicio_real"]
    },
    {
      "success": true,
      "message": "Atividade atualizada com sucesso",
      "seq": 999094,
      "sequencia": "REDE",
      "updated_fields": ["status", "horario_fim_real"]
    }
  ]
}
```

## Exemplos de Uso

### Python

```python
import requests

# Atualizar uma atividade
activity = {
    "seq": 999093,
    "sequencia": "REDE",
    "status": "Em Execução",
    "horario_inicio_real": "25/12/2024 14:30:00"
}

response = requests.put("http://localhost:8000/activity", json=activity)
print(response.json())

# Atualizar múltiplas atividades
activities = {
    "activities": [
        {
            "seq": 999093,
            "sequencia": "REDE",
            "status": "Concluído",
            "horario_fim_real": "25/12/2024 15:30:00"
        },
        {
            "seq": 999094,
            "sequencia": "REDE",
            "status": "Em Execução"
        }
    ]
}

response = requests.put("http://localhost:8000/activities/bulk", json=activities)
print(response.json())
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

// Atualizar uma atividade
const activity = {
  seq: 999093,
  sequencia: "REDE",
  status: "Em Execução",
  horario_inicio_real: "25/12/2024 14:30:00"
};

axios.put('http://localhost:8000/activity', activity)
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```

## Script de Sincronização

O script `sync_excel.py` lê o Excel do SharePoint e atualiza as atividades automaticamente via API.

### Uso Básico

```bash
python sync_excel.py
```

O script tentará baixar o arquivo Excel do SharePoint automaticamente.

### Fornecendo Arquivo Local

Se o download automático não funcionar (requer autenticação), você pode baixar o arquivo manualmente e fornecer o caminho:

```bash
python sync_excel.py "C:\caminho\para\arquivo.xlsx"
```

### Configuração

Você pode configurar a URL da API através de variável de ambiente:

```bash
# Windows PowerShell
$env:API_BASE_URL="http://localhost:8000"
python sync_excel.py

# Linux/Mac
export API_BASE_URL="http://localhost:8000"
python sync_excel.py
```

### Como Funciona

1. **Identificação de Abas**: O script procura por abas que começam com "CRQ" e terminam com "2" (segunda tentativa de execução)

2. **Identificação de Sequência**: Tenta identificar a sequência (REDE, OPENSHIFT, NFS, SI) baseado no nome da aba

3. **Extração de Dados**: Extrai os seguintes dados de cada linha:
   - `seq`: Número sequencial
   - `status`: Status da atividade (se disponível)
   - `horario_inicio_real`: Horário de início real (se disponível)
   - `horario_fim_real`: Horário de fim real (se disponível)

4. **Atualização via API**: Envia todas as atividades para a API em lote

### Logs

O script gera logs em:
- Console: Saída em tempo real
- Arquivo: `sync_excel.log`

## Troubleshooting

### API não está respondendo

1. Verifique se o servidor está rodando:
   ```bash
   curl http://localhost:8000/health
   ```

2. Verifique os logs do servidor em `api_server.log`

### Erro ao baixar Excel do SharePoint

O download automático pode falhar por vários motivos:

#### Erro de Certificado SSL

Se você receber erro `CERTIFICATE_VERIFY_FAILED` ou `self-signed certificate`:

**Causa**: Ambientes corporativos frequentemente usam certificados autoassinados que o navegador aceita, mas o Python não confia automaticamente.

**Soluções**:

1. **Baixar manualmente** (Recomendado):
   - Baixe o arquivo do SharePoint manualmente
   - Execute: `python sync_excel.py "C:\caminho\para\arquivo.xlsx"`

2. **Desabilitar verificação SSL** (Apenas em ambiente controlado):
   ```powershell
   # PowerShell
   $env:DISABLE_SSL_VERIFY='true'
   python sync_excel.py
   ```
   
   ```bash
   # Linux/Mac
   export DISABLE_SSL_VERIFY=true
   python sync_excel.py
   ```

3. **Usar URL de download direto**:
   - No SharePoint, clique com botão direito no arquivo
   - Selecione "Download" ou "Copiar link de download"
   - Use essa URL no script

4. **Configurar autenticação OAuth**:
   - Use bibliotecas como `Office365-REST-Python-Client` para autenticação adequada
   - Isso resolve problemas de certificado e autenticação

#### Outros Erros

- **403 Forbidden**: Arquivo requer autenticação. Use solução 1 ou 4.
- **404 Not Found**: URL incorreta ou arquivo movido. Verifique a URL.
- **Timeout**: Conexão lenta. Tente baixar manualmente (solução 1).

### Erro de formato de data

Certifique-se de que as datas no Excel estão no formato `DD/MM/YYYY HH:MM:SS` ou formatos compatíveis.

### Atividades não encontradas

Verifique:
1. Se o `seq` está correto
2. Se a `sequencia` está correta (REDE, OPENSHIFT, NFS, SI)
3. Se a atividade existe no banco de dados

### Logs

Todos os logs são salvos em arquivos:
- `api_server.log`: Logs do servidor API
- `sync_excel.log`: Logs do script de sincronização

## Segurança

**Nota**: A API atual não possui autenticação. Para uso em produção, recomenda-se:

1. Adicionar autenticação (JWT, API Key, etc.)
2. Usar HTTPS
3. Implementar rate limiting
4. Validar e sanitizar todas as entradas

## Suporte

Para problemas ou dúvidas, verifique os logs ou entre em contato com a equipe de desenvolvimento.
