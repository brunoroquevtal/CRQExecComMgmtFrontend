# 🚀 Início Rápido - Aplicação Completa

## Instalação

```powershell
python -m pip install -r requirements.txt
```

## Iniciar Aplicação

### Opção 1: Tudo de uma vez (Recomendado) ⭐

```powershell
python start_all.py
```

Isso iniciará automaticamente:
- ✅ API REST em `http://localhost:8000`
- ✅ Streamlit em `http://localhost:8501`

**Para parar:** Pressione `Ctrl+C` no terminal

### Opção 2: Processos Separados

**Terminal 1 - API:**
```powershell
python api_server.py
```

**Terminal 2 - Streamlit:**
```powershell
streamlit run app.py
```

## Acessar

- **Streamlit (Interface Web):** http://localhost:8501
- **API REST:** http://localhost:8000
- **Documentação da API:** http://localhost:8000/docs

## Sincronizar Excel do SharePoint

```powershell
# Tentar baixar automaticamente
python sync_excel.py

# Ou fornecer arquivo local
python sync_excel.py "CRQ VIRADA REDE.xlsx"
```

## Solução de Problemas

### Porta já em uso
Se a porta 8000 ou 8501 estiver em uso:
1. Feche outros processos usando essas portas
2. Ou altere as portas nos arquivos de configuração

### Erro ao iniciar
- Verifique se todas as dependências estão instaladas: `python -m pip install -r requirements.txt`
- Verifique se os arquivos `app.py` e `api_server.py` existem

## Próximos Passos

- Consulte `GUIA_API.md` para documentação completa da API
- Consulte `README_API.md` para exemplos de uso
- Consulte `GUIA_INSTALACAO.md` para instalação detalhada
