"""
Exemplo de como fazer upload de arquivo Excel para a API
"""
import requests

# URL da API
API_BASE_URL = "http://localhost:8000"

def upload_excel_file(file_path: str):
    """
    Faz upload de um arquivo Excel para a API
    
    Args:
        file_path: Caminho do arquivo Excel (.xlsx ou .xls)
    """
    url = f"{API_BASE_URL}/upload-excel"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print(f"Enviando arquivo: {file_path}")
            response = requests.post(url, files=files, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Upload realizado com sucesso!")
                print(f"  Arquivo: {result['filename']}")
                print(f"  Total de linhas: {result['total_rows']}")
                print(f"  Registros salvos: {result['total_saved']}")
                print(f"  Controles criados: {result['control_created']}")
                print(f"  Sequências processadas: {', '.join(result['sequencias'])}")
                return result
            else:
                print(f"\n❌ Erro: HTTP {response.status_code}")
                print(f"  Resposta: {response.text}")
                return None
                
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Erro ao fazer upload: {e}")
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python exemplo_upload_excel.py <caminho_do_arquivo.xlsx>")
        print("\nExemplo:")
        print("  python exemplo_upload_excel.py \"C:\\caminho\\arquivo.xlsx\"")
        sys.exit(1)
    
    file_path = sys.argv[1]
    upload_excel_file(file_path)
