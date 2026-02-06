"""
Configurações da aplicação
"""
import os

# Configurações de diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "activity_control.db")

# Configurações de CRQs
SEQUENCIAS = {
    "REDE": {"nome": "REDE", "total": 72, "emoji": "🟢"},
    "OPENSHIFT": {"nome": "OPENSHIFT", "total": 39, "emoji": "🔵"},
    "NFS": {"nome": "NFS", "total": 17, "emoji": "🟠"},
    "SI": {"nome": "SI", "total": 25, "emoji": "🟡"}
}

TOTAL_GERAL = 153

# Status permitidos
STATUS_OPCOES = [
    "Planejado",
    "Em Execução",
    "Concluído",
    "Atrasado",
    "Adiantado"
]

# Mapeamento de colunas do Excel
EXCEL_COLUMNS = {
    "Seq": "A",
    "Atividade": "B",
    "Grupo": "C",
    "Localidade": "D",
    "Executor": "E",
    "Telefone": "F",
    "Inicio": "G",
    "Fim": "H",
    "Tempo": "I"
}

# Formato de data
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
DATE_FORMAT_DISPLAY = "DD/MM/AAAA HH:MM:SS"

# Cores para status
STATUS_COLORS = {
    "Concluído": "#28a745",  # Verde
    "Em Execução": "#007bff",  # Azul
    "Planejado": "#ffc107",  # Amarelo
    "Atrasado": "#dc3545",  # Vermelho
    "Adiantado": "#17a2b8"  # Ciano
}

# Criar diretórios se não existirem
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)
