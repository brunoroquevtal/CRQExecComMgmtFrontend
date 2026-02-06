"""
Exemplo de uso da API de atualização de atividades
Demonstra como usar a API para atualizar tarefas programaticamente
"""
import requests
import json
from datetime import datetime

# Configuração
API_BASE_URL = "http://localhost:8000"

def exemplo_atualizar_uma_atividade():
    """Exemplo: Atualizar uma única atividade"""
    print("=" * 60)
    print("Exemplo 1: Atualizar uma atividade")
    print("=" * 60)
    
    activity = {
        "seq": 999093,
        "sequencia": "REDE",
        "status": "Em Execução",
        "horario_inicio_real": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "observacoes": "Atividade iniciada via API"
    }
    
    try:
        response = requests.put(f"{API_BASE_URL}/activity", json=activity)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Sucesso: {result['message']}")
        print(f"  Seq: {result['seq']}")
        print(f"  CRQ: {result['sequencia']}")
        print(f"  Campos atualizados: {', '.join(result['updated_fields'])}")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Resposta: {e.response.text}")


def exemplo_atualizar_multiplas_atividades():
    """Exemplo: Atualizar múltiplas atividades em lote"""
    print("\n" + "=" * 60)
    print("Exemplo 2: Atualizar múltiplas atividades")
    print("=" * 60)
    
    activities = {
        "activities": [
            {
                "seq": 999093,
                "sequencia": "REDE",
                "status": "Concluído",
                "horario_fim_real": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "observacoes": "Concluída via API"
            },
            {
                "seq": 999094,
                "sequencia": "REDE",
                "status": "Em Execução",
                "horario_inicio_real": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            },
            {
                "seq": 999095,
                "sequencia": "OPENSHIFT",
                "status": "Planejado"
            }
        ]
    }
    
    try:
        response = requests.put(f"{API_BASE_URL}/activities/bulk", json=activities)
        response.raise_for_status()
        result = response.json()
        
        print(f"Total: {result['total']}")
        print(f"Sucesso: {result['successful']}")
        print(f"Falhas: {result['failed']}")
        
        print("\nDetalhes:")
        for i, res in enumerate(result['results'], 1):
            status = "✓" if res['success'] else "✗"
            print(f"  {status} Atividade {i}: Seq {res['seq']}, CRQ {res['sequencia']}")
            if not res['success']:
                print(f"    Erro: {res['message']}")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Resposta: {e.response.text}")


def exemplo_buscar_atividade():
    """Exemplo: Buscar uma atividade"""
    print("\n" + "=" * 60)
    print("Exemplo 3: Buscar uma atividade")
    print("=" * 60)
    
    sequencia = "REDE"
    seq = 999093
    
    try:
        response = requests.get(f"{API_BASE_URL}/activity/{sequencia}/{seq}")
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            activity = result['activity']
            print(f"✓ Atividade encontrada:")
            print(f"  Seq: {seq}")
            print(f"  CRQ: {sequencia}")
            print(f"  Status: {activity.get('status', 'N/A')}")
            print(f"  Início Real: {activity.get('horario_inicio_real', 'N/A')}")
            print(f"  Fim Real: {activity.get('horario_fim_real', 'N/A')}")
            print(f"  Atraso: {activity.get('atraso_minutos', 0)} minutos")
            print(f"  Observações: {activity.get('observacoes', 'N/A')}")
        else:
            print(f"✗ {result.get('message', 'Erro desconhecido')}")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro: {e}")
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 404:
                print(f"  Atividade não encontrada")
            else:
                print(f"  Resposta: {e.response.text}")


def exemplo_verificar_saude():
    """Exemplo: Verificar saúde da API"""
    print("\n" + "=" * 60)
    print("Exemplo 4: Verificar saúde da API")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Status: {result['status']}")
        print(f"  Banco de dados: {result['database']}")
        print(f"  Timestamp: {result['timestamp']}")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro: {e}")
        print("  A API não está disponível. Verifique se o servidor está rodando.")


def main():
    """Executa todos os exemplos"""
    print("\n" + "=" * 60)
    print("EXEMPLOS DE USO DA API")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print("\nCertifique-se de que o servidor API está rodando:")
    print("  python api_server.py")
    print("\n" + "=" * 60 + "\n")
    
    # Verificar saúde primeiro
    exemplo_verificar_saude()
    
    # Executar exemplos
    exemplo_buscar_atividade()
    exemplo_atualizar_uma_atividade()
    exemplo_atualizar_multiplas_atividades()
    
    print("\n" + "=" * 60)
    print("Exemplos concluídos!")
    print("=" * 60)


if __name__ == "__main__":
    main()
