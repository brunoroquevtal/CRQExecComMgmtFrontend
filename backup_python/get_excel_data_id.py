"""
Script auxiliar para buscar excel_data_id de atividades no banco
Útil para debug e verificação
"""
import sqlite3
import sys
from config import DB_PATH

def get_excel_data_id(seq: int, sequencia: str) -> list:
    """
    Busca excel_data_id(s) de uma atividade no banco
    
    Returns:
        list: Lista de excel_data_id encontrados
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar no excel_data
    cursor.execute("""
        SELECT id, seq, sequencia, atividade 
        FROM excel_data 
        WHERE seq = ? AND sequencia = ?
    """, (seq, sequencia))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python get_excel_data_id.py <seq> <sequencia>")
        print("Exemplo: python get_excel_data_id.py 999093 REDE")
        sys.exit(1)
    
    seq = int(sys.argv[1])
    sequencia = sys.argv[2]
    
    results = get_excel_data_id(seq, sequencia)
    
    if results:
        print(f"Encontrados {len(results)} registro(s) para Seq {seq}, CRQ {sequencia}:")
        for row in results:
            print(f"  Excel_Data_ID: {row[0]}, Seq: {row[1]}, CRQ: {row[2]}, Atividade: {row[3][:50]}...")
    else:
        print(f"Nenhum registro encontrado para Seq {seq}, CRQ {sequencia}")
        print("A atividade precisa estar no banco (excel_data) antes de poder ser atualizada.")
