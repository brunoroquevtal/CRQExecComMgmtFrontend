# API de Atualização de Atividades - Guia Rápido

## Início Rápido

### 1. Instalar dependências
```bash
python -m pip install -r requirements.txt
```

### 2. Iniciar tudo de uma vez (Recomendado)
```bash
python start_all.py
```

Isso iniciará:
- API REST em `http://localhost:8000`
- Streamlit em `http://localhost:8501`

### 3. Ou iniciar separadamente

**Apenas API:**
```bash
python api_server.py
```

**Apenas Streamlit:**
```bash
streamlit run app.py
```

### 4. Usar o script de sincronização
```bash
# Tentar baixar automaticamente do SharePoint
python sync_excel.py

# Ou fornecer arquivo local
python sync_excel.py "caminho/para/arquivo.xlsx"
```

## Endpoints Principais

- `PUT /activity` - Atualizar uma atividade
- `PUT /activities/bulk` - Atualizar múltiplas atividades
- `GET /activity/{sequencia}/{seq}` - Buscar uma atividade
- `GET /health` - Verificar saúde da API

## Exemplo de Uso

```python
import requests

activity = {
    "seq": 999093,
    "sequencia": "REDE",
    "status": "Em Execução",
    "horario_inicio_real": "25/12/2024 14:30:00"
}

response = requests.put("http://localhost:8000/activity", json=activity)
print(response.json())
```

## Documentação Completa

Consulte `GUIA_API.md` para documentação completa e exemplos detalhados.

## Arquivos Criados

- `api_server.py` - Servidor FastAPI com endpoints REST
- `sync_excel.py` - Script para sincronizar Excel do SharePoint
- `exemplo_uso_api.py` - Exemplos de uso da API
- `GUIA_API.md` - Documentação completa
- `README_API.md` - Este arquivo (guia rápido)
