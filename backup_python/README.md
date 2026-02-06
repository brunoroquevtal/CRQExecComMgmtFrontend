# 🚀 Janela de Mudança TI - Aplicação Streamlit

Aplicação web interativa para gerenciamento de janelas de mudança de TI, com dashboard executivo e geração automática de mensagens de comunicação.

## 📋 Funcionalidades

- ✅ Importação de dados de arquivo Excel (4 abas: REDE, OPENSHIFT, NFS, SI)
- ✅ Edição interativa de dados em tempo real
- ✅ Dashboard executivo com gráficos e indicadores
- ✅ Geração automática de mensagem consolidada para comunicação
- ✅ Persistência de dados em banco SQLite local
- ✅ Cálculo automático de atrasos/adiantamentos

## 🚀 Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app.py
```

## 📁 Estrutura do Projeto

```
janela-mudanca-ti-app/
├── app.py                      # Arquivo principal
├── requirements.txt            # Dependências
├── config.py                   # Configurações
├── modules/
│   ├── __init__.py
│   ├── data_loader.py         # Carregamento de Excel
│   ├── database.py            # Gerenciamento de SQLite
│   ├── calculations.py        # Cálculos e lógica
│   ├── dashboard.py           # Componentes do dashboard
│   ├── message_builder.py     # Gerador de mensagem de comunicação
│   ├── data_editor.py         # Editor de dados
│   └── ui.py                  # Componentes de UI
├── data/                       # Arquivos Excel
└── db/                         # Banco de dados SQLite
```

## 📊 Uso

1. Faça upload do arquivo Excel `CRQVIRADAREDE(3).xlsx`
2. Navegue pelo dashboard para visualizar indicadores
3. Edite os dados na aba "Dados"
4. Gere e copie a mensagem de comunicação na aba "Comunicação"

## 🔧 Tecnologias

- Streamlit
- Pandas
- Plotly
- SQLite
- OpenPyXL
