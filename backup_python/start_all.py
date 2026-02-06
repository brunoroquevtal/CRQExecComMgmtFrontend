"""
Script para iniciar tanto o Streamlit quanto a API simultaneamente
Facilita o desenvolvimento iniciando ambos os serviços de uma vez
"""
import subprocess
import sys
import time
import os
import signal
import requests
from pathlib import Path

# Cores para output (Windows PowerShell suporta)
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
except:
    GREEN = BLUE = YELLOW = RED = RESET = BOLD = ''

# Processos
streamlit_process = None
api_process = None


def check_port_available(port):
    """Verifica se uma porta está disponível"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0


def check_api_health(max_retries=10, delay=1):
    """Verifica se a API está respondendo"""
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                print(f"   Tentativa {i+1}/{max_retries}...", end="\r")
        except Exception as e:
            if i < max_retries - 1:
                print(f"   Erro na verificação: {type(e).__name__}...", end="\r")
        time.sleep(delay)
    print()  # Nova linha após as tentativas
    return False


def start_api(debug=False):
    """Inicia o servidor API"""
    global api_process
    
    print(f"{BLUE}🌐 Iniciando servidor API...{RESET}")
    
    # Verificar se modo debug está ativado
    api_debug = os.getenv('API_DEBUG', 'false').lower() in ('true', '1', 'yes') or debug
    if api_debug:
        print(f"{YELLOW}🔍 Modo DEBUG ativado - todas as requisicoes serao logadas{RESET}")
    
    # Verificar se porta está disponível
    if not check_port_available(8000):
        print(f"{YELLOW}⚠️  Porta 8000 já está em uso. Tentando iniciar mesmo assim...{RESET}")
    
    try:
        # Preparar ambiente
        env = os.environ.copy()
        if api_debug:
            env['API_DEBUG'] = 'true'
        
        # Iniciar API em processo separado
        # Usar subprocess.PIPE para capturar erros, mas também permitir que apareçam no console
        api_process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redirecionar stderr para stdout
            text=True,
            bufsize=1,
            env=env,
            universal_newlines=True
        )
        
        print(f"{GREEN}✓ API iniciada (PID: {api_process.pid}){RESET}")
        print(f"   Aguardando API ficar pronta...")
        
        # Aguardar um pouco para o processo iniciar
        time.sleep(2)
        
        # Verificar se o processo ainda está rodando
        if api_process.poll() is not None:
            # Processo terminou - ler saída para ver o erro
            stdout, _ = api_process.communicate()
            print(f"{RED}✗ API falhou ao iniciar!{RESET}")
            if stdout:
                print(f"{RED}Erro:{RESET}")
                print(stdout[:500])  # Mostrar primeiros 500 caracteres
            return False
        
        # Aguardar API ficar pronta com mais tentativas
        if check_api_health(max_retries=15, delay=2):
            print(f"{GREEN}✓ API está respondendo!{RESET}")
            return True
        else:
            # Verificar se o processo ainda está rodando
            if api_process.poll() is not None:
                stdout, _ = api_process.communicate()
                print(f"{RED}✗ API parou durante a inicialização!{RESET}")
                if stdout:
                    print(f"{RED}Erro:{RESET}")
                    print(stdout[:500])
                return False
            else:
                print(f"{YELLOW}⚠️  API iniciada mas não está respondendo ainda.{RESET}")
                print(f"{YELLOW}   Verifique os logs em api_server.log{RESET}")
                return True  # Continuar mesmo assim
            
    except Exception as e:
        print(f"{RED}✗ Erro ao iniciar API: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False


def start_streamlit():
    """Inicia o Streamlit"""
    global streamlit_process
    
    print(f"{BLUE}🚀 Iniciando Streamlit...{RESET}")
    
    # Verificar se porta está disponível
    if not check_port_available(8501):
        print(f"{YELLOW}⚠️  Porta 8501 já está em uso. Tentando iniciar mesmo assim...{RESET}")
    
    try:
        # Iniciar Streamlit em processo separado
        streamlit_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print(f"{GREEN}✓ Streamlit iniciado (PID: {streamlit_process.pid}){RESET}")
        return True
        
    except Exception as e:
        print(f"{RED}✗ Erro ao iniciar Streamlit: {e}{RESET}")
        return False


def cleanup():
    """Encerra ambos os processos"""
    global streamlit_process, api_process
    
    print(f"\n{YELLOW}🛑 Encerrando serviços...{RESET}")
    
    if streamlit_process:
        try:
            streamlit_process.terminate()
            streamlit_process.wait(timeout=5)
            print(f"{GREEN}✓ Streamlit encerrado{RESET}")
        except:
            try:
                streamlit_process.kill()
            except:
                pass
    
    if api_process:
        try:
            api_process.terminate()
            api_process.wait(timeout=5)
            print(f"{GREEN}✓ API encerrada{RESET}")
        except:
            try:
                api_process.kill()
            except:
                pass
    
    print(f"{GREEN}✅ Todos os serviços foram encerrados.{RESET}")


def signal_handler(sig, frame):
    """Handler para Ctrl+C"""
    cleanup()
    sys.exit(0)


def main():
    """Função principal"""
    # Verificar se modo debug foi solicitado
    import argparse
    parser = argparse.ArgumentParser(description='Inicia Streamlit e API simultaneamente')
    parser.add_argument('--debug', '-d', action='store_true', help='Ativar modo debug na API')
    args = parser.parse_args()
    
    # Registrar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}🚀 Iniciando Aplicação Completa{RESET}")
    if args.debug:
        print(f"{BOLD}{YELLOW}🔍 Modo DEBUG ativado{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}\n")
    
    # Verificar se os arquivos existem
    if not os.path.exists("api_server.py"):
        print(f"{RED}✗ Erro: api_server.py não encontrado!{RESET}")
        sys.exit(1)
    
    if not os.path.exists("app.py"):
        print(f"{RED}✗ Erro: app.py não encontrado!{RESET}")
        sys.exit(1)
    
    # Iniciar API primeiro
    api_ok = start_api(debug=args.debug)
    if not api_ok:
        print(f"{RED}✗ Falha ao iniciar API. Continuando mesmo assim...{RESET}")
    
    # Aguardar um pouco antes de iniciar Streamlit
    time.sleep(2)
    
    # Iniciar Streamlit
    streamlit_ok = start_streamlit()
    if not streamlit_ok:
        print(f"{RED}✗ Falha ao iniciar Streamlit.{RESET}")
        cleanup()
        sys.exit(1)
    
    # Aguardar um pouco para os serviços iniciarem
    time.sleep(3)
    
    # Mostrar informações
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}{GREEN}✅ Aplicação iniciada com sucesso!{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}\n")
    print(f"{BOLD}Serviços disponíveis:{RESET}")
    print(f"  {BLUE}🌐 API REST:{RESET}     http://localhost:8000")
    print(f"  {BLUE}📊 Streamlit:{RESET}    http://localhost:8501")
    print(f"  {BLUE}📖 API Docs:{RESET}     http://localhost:8000/docs")
    if args.debug:
        print(f"  {YELLOW}🔍 Debug:{RESET}        Ativado - veja api_server.log para detalhes")
    print(f"\n{YELLOW}💡 Dica: Pressione Ctrl+C para encerrar ambos os serviços{RESET}")
    print(f"{YELLOW}💡 Para ativar debug: python start_all.py --debug{RESET}\n")
    
    # Monitorar processos
    try:
        while True:
            # Verificar se processos ainda estão rodando
            if streamlit_process and streamlit_process.poll() is not None:
                print(f"{RED}⚠️  Streamlit parou inesperadamente!{RESET}")
                break
            
            if api_process and api_process.poll() is not None:
                print(f"{RED}⚠️  API parou inesperadamente!{RESET}")
                break
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
