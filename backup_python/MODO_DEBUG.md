# Modo Debug da API

O servidor API possui um modo debug que permite ver todas as requisições recebidas e erros em detalhes.

## Como Ativar

### Opção 1: Variável de Ambiente (Recomendado)

**PowerShell:**
```powershell
$env:API_DEBUG='true'
python api_server.py
```

**CMD:**
```cmd
set API_DEBUG=true
python api_server.py
```

### Opção 2: Via start_all.py

```powershell
python start_all.py --debug
```

### Opção 3: Diretamente no código

O modo debug é ativado automaticamente se a variável de ambiente `API_DEBUG` estiver definida como `'true'`, `'1'` ou `'yes'`.

## O que o Modo Debug Mostra

Quando ativado, o modo debug registra:

### 1. Todas as Requisições Recebidas
- Método HTTP (GET, POST, PUT, etc.)
- URL e path
- Query parameters
- Headers
- Body completo (JSON formatado)

### 2. Tempo de Processamento
- Tempo total de cada requisição
- Tempo de cada etapa (salvar no banco, etc.)
- Alertas para requisições lentas (> 5 segundos)

### 3. Erros Detalhados
- Tipo de erro
- Mensagem completa
- Stack trace completo
- Tempo até o erro ocorrer

### 4. Logs de Operações
- Criação de atividades
- Atualizações em lote
- Arquivamento
- Ativação de rollback

## Exemplo de Logs

Com debug ativado, você verá logs como:

```
2026-02-05 14:30:00 - DEBUG - ============================================================
2026-02-05 14:30:00 - DEBUG - [REQUISICAO RECEBIDA] POST /activity
2026-02-05 14:30:00 - DEBUG - Query params: {}
2026-02-05 14:30:00 - DEBUG - Headers: {'content-type': 'application/json', ...}
2026-02-05 14:30:00 - DEBUG - Body (JSON): {
  "seq": 1,
  "sequencia": "REDE",
  "atividade": "Teste",
  ...
}
2026-02-05 14:30:00 - DEBUG - [CREATE] Iniciando criacao: Seq 1, CRQ REDE, Rollback: False
2026-02-05 14:30:01 - DEBUG - [CREATE] Excel_data processado: ID 123, Tempo: 0.234s
2026-02-05 14:30:01 - DEBUG - [CREATE] Concluido com sucesso em 0.456s
2026-02-05 14:30:01 - DEBUG - [RESPOSTA] Status: 200, Tempo: 0.456s
2026-02-05 14:30:01 - DEBUG - ============================================================
```

## Arquivo de Log

Todos os logs são salvos em `api_server.log` com encoding UTF-8.

Para ver os logs em tempo real:

**PowerShell:**
```powershell
Get-Content api_server.log -Wait -Tail 50
```

**Linux/Mac:**
```bash
tail -f api_server.log
```

## Desativar Debug

Para desativar, simplesmente não defina a variável de ambiente ou defina como `'false'`:

```powershell
$env:API_DEBUG='false'
python api_server.py
```

Ou simplesmente:
```powershell
python api_server.py
```

## Dicas

1. **Use debug apenas quando necessário** - gera muitos logs e pode afetar performance
2. **Monitore o arquivo de log** - pode crescer rapidamente em modo debug
3. **Procure por "ERRO" ou "ERROR"** - facilita encontrar problemas
4. **Verifique tempos de processamento** - ajuda a identificar gargalos

## Troubleshooting

### Timeout nas requisições

Com debug ativado, você verá exatamente onde a requisição está demorando:

```
[CREATE] Excel_data processado: ID 123, Tempo: 0.234s
[CREATE] Concluido com sucesso em 45.678s  <-- Aqui está o problema!
```

### Erros no servidor

Todos os erros são logados com stack trace completo:

```
[ERRO NA REQUISICAO] POST /activity
Tempo ate erro: 2.345s
Erro: ValueError: Invalid date format
Traceback (most recent call last):
  ...
```
