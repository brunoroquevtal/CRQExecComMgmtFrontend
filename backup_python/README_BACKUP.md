# 📦 Backup - Versão Python/Streamlit

Esta pasta contém todos os arquivos da versão original da aplicação em Python/Streamlit.

## 📁 Conteúdo

- **Arquivos Python principais:**
  - `app.py` - Aplicação Streamlit principal
  - `api_server.py` - Servidor FastAPI
  - `sync_excel.py` - Script de sincronização com Excel
  - `config.py` - Configurações
  - `start_all.py` - Script para iniciar tudo

- **Módulos Python (`modules/`):**
  - `api_client.py` - Cliente HTTP para API
  - `auth.py` - Autenticação
  - `calculations.py` - Cálculos e estatísticas
  - `crud_activities.py` - CRUD de atividades
  - `dashboard.py` - Componentes do dashboard
  - `data_editor.py` - Editor de dados
  - `data_loader.py` - Carregamento de Excel
  - `database.py` - Gerenciamento SQLite
  - `message_builder.py` - Geração de mensagens
  - `ui.py` - Componentes de UI

- **Documentação:**
  - `README.md` - Documentação principal
  - `README_API.md` - Documentação da API
  - `GUIA_*.md` - Vários guias
  - `INSTRUCOES.md` - Instruções de uso
  - `SISTEMA_LOGIN.md` - Sistema de login

- **Outros:**
  - `requirements.txt` - Dependências Python
  - `*.log` - Arquivos de log
  - `__pycache__/` - Cache Python

## 🔄 Como restaurar

Se precisar restaurar a versão Python:

1. Mova os arquivos de volta para a raiz do projeto
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute: `streamlit run app.py` ou `python start_all.py`

## 📝 Nota

A aplicação foi migrada para Node.js/React.js. Os arquivos Python foram movidos para backup para manter histórico e permitir referência futura.
