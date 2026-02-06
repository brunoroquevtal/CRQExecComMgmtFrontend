"""
Script para remover registros específicos do banco de dados
Remove registros com seq específicos das tabelas activity_control e excel_data
"""
import sqlite3
import os
from config import DB_PATH

def remover_seqs(seqs_para_remover, sequencia="SI"):
    """
    Remove registros com os seq especificados de uma sequência (CRQ) específica
    
    Args:
        seqs_para_remover: Lista de números seq para remover
        sequencia: Nome da sequência/CRQ (padrão: "SI")
    """
    if not os.path.exists(DB_PATH):
        print(f"Banco de dados nao encontrado em {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Converter para lista de inteiros
        seqs = [int(seq) for seq in seqs_para_remover]
        print(f"Removendo registros da CRQ '{sequencia}' com seq: {seqs}")
        
        # Primeiro, verificar quantos registros existem antes de remover
        placeholders = ','.join(['?'] * len(seqs))
        params = seqs + [sequencia]
        
        cursor.execute(f"""
            SELECT COUNT(*) FROM activity_control 
            WHERE seq IN ({placeholders}) AND sequencia = ?
        """, params)
        activity_antes = cursor.fetchone()[0]
        
        cursor.execute(f"""
            SELECT COUNT(*) FROM excel_data 
            WHERE seq IN ({placeholders}) AND sequencia = ?
        """, params)
        excel_antes = cursor.fetchone()[0]
        
        print(f"\nRegistros encontrados antes da remocao:")
        print(f"  - activity_control: {activity_antes}")
        print(f"  - excel_data: {excel_antes}")
        
        if activity_antes == 0 and excel_antes == 0:
            print("\nAVISO: Nenhum registro encontrado para remover!")
            return
        
        # Remover da tabela activity_control (apenas da sequência especificada)
        cursor.execute(f"""
            DELETE FROM activity_control 
            WHERE seq IN ({placeholders}) AND sequencia = ?
        """, params)
        activity_removidos = cursor.rowcount
        
        # Remover da tabela excel_data (apenas da sequência especificada)
        cursor.execute(f"""
            DELETE FROM excel_data 
            WHERE seq IN ({placeholders}) AND sequencia = ?
        """, params)
        excel_removidos = cursor.rowcount
        
        conn.commit()
        
        print(f"\nRegistros removidos:")
        print(f"  - activity_control: {activity_removidos}")
        print(f"  - excel_data: {excel_removidos}")
        print(f"\nTotal de registros removidos: {activity_removidos + excel_removidos}")
        print("OK: Remocao concluida com sucesso!")
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    # Lista de seqs para remover
    seqs_para_remover = [
        999093,
        999094,
        999095,
        999096,
        999097,
        999098,
        999099,
        999100
    ]
    
    # CRQ/Sequência
    sequencia = "SI"
    
    print("=" * 50)
    print("Script de Remocao de Registros")
    print("=" * 50)
    print(f"\nCRQ/Sequencia: {sequencia}")
    print(f"\nATENCAO: Este script vai remover os seguintes seqs da CRQ {sequencia}:")
    for seq in seqs_para_remover:
        print(f"  - {seq}")
    
    resposta = input("\nDeseja continuar? (s/n): ").strip().lower()
    
    if resposta == 's' or resposta == 'sim':
        remover_seqs(seqs_para_remover, sequencia)
    else:
        print("Operacao cancelada.")
