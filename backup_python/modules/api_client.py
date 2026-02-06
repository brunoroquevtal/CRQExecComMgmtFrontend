"""
Cliente HTTP centralizado para chamadas à API
Usa a biblioteca requests para todas as comunicações HTTP
"""
import requests
import logging
import time
import os
from typing import Dict, List, Optional, Any
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)

# URL base da API (pode ser configurada via variável de ambiente)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Configurações padrão
DEFAULT_TIMEOUT = 30
DEFAULT_RETRY_COUNT = 2
DEFAULT_RETRY_DELAY = 1.0


class APIClient:
    """
    Cliente HTTP para comunicação com a API REST
    Centraliza todas as chamadas HTTP usando requests
    """
    
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = DEFAULT_TIMEOUT):
        """
        Inicializa o cliente API
        
        Args:
            base_url: URL base da API
            timeout: Timeout padrão para requisições (segundos)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configurar headers padrão
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        timeout: Optional[int] = None,
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY
    ) -> Optional[requests.Response]:
        """
        Faz uma requisição HTTP com retry automático
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint da API (ex: '/activity')
            json_data: Dados JSON para enviar no body
            params: Parâmetros de query string
            timeout: Timeout específico para esta requisição
            retry_count: Número de tentativas em caso de erro
            retry_delay: Delay entre tentativas (segundos)
            
        Returns:
            Response object ou None se falhar após todas as tentativas
        """
        url = f"{self.base_url}{endpoint}"
        timeout = timeout or self.timeout
        
        for attempt in range(retry_count + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    timeout=timeout
                )
                return response
                
            except Timeout as e:
                if attempt < retry_count:
                    wait_time = retry_delay * (attempt + 1)
                    logger.warning(f"Timeout na requisição {method} {endpoint} (tentativa {attempt + 1}/{retry_count + 1}). Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Timeout após {retry_count + 1} tentativas: {method} {endpoint}")
                    raise
                    
            except ConnectionError as e:
                if attempt < retry_count:
                    wait_time = retry_delay * (attempt + 1)
                    logger.warning(f"Erro de conexão em {method} {endpoint} (tentativa {attempt + 1}/{retry_count + 1}). Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Erro de conexão após {retry_count + 1} tentativas: {method} {endpoint}")
                    raise
                    
            except RequestException as e:
                logger.error(f"Erro na requisição {method} {endpoint}: {e}")
                if attempt < retry_count:
                    time.sleep(retry_delay)
                    continue
                raise
        
        return None
    
    def health_check(self) -> bool:
        """
        Verifica se a API está disponível
        
        Returns:
            bool: True se API está respondendo
        """
        try:
            response = self._make_request('GET', '/health', timeout=2, retry_count=0)
            return response is not None and response.status_code == 200
        except Exception:
            return False
    
    def get_activity(self, sequencia: str, seq: int) -> Optional[Dict]:
        """
        Busca uma atividade específica
        
        Args:
            sequencia: Nome da sequência/CRQ
            seq: Número da sequência da atividade
            
        Returns:
            Dict com dados da atividade ou None se não encontrada
        """
        try:
            response = self._make_request('GET', f'/activity/{sequencia}/{seq}')
            if response and response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('activity')
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar atividade {sequencia}/{seq}: {e}")
            return None
    
    def create_activity(self, activity: Dict, timeout: int = 60) -> Dict:
        """
        Cria ou atualiza uma atividade (POST)
        
        Args:
            activity: Dicionário com dados da atividade
            timeout: Timeout específico para esta requisição
            
        Returns:
            Dict com resultado da operação
        """
        try:
            response = self._make_request(
                'POST',
                '/activity',
                json_data=activity,
                timeout=timeout,
                retry_count=1
            )
            
            if response and response.status_code in (200, 201):
                return response.json()
            else:
                error_text = response.text[:300] if response else "Sem resposta"
                return {
                    'success': False,
                    'message': f"HTTP {response.status_code if response else 'N/A'}: {error_text}"
                }
        except Exception as e:
            logger.error(f"Erro ao criar atividade: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def update_activity(self, activity: Dict, timeout: int = 120) -> Dict:
        """
        Atualiza uma atividade existente (PUT)
        
        Args:
            activity: Dicionário com dados da atividade
            timeout: Timeout específico para esta requisição
            
        Returns:
            Dict com resultado da operação
        """
        try:
            response = self._make_request(
                'PUT',
                '/activity',
                json_data=activity,
                timeout=timeout,
                retry_count=2
            )
            
            if response and response.status_code == 200:
                return response.json()
            else:
                error_text = response.text[:200] if response else "Sem resposta"
                return {
                    'success': False,
                    'message': f"HTTP {response.status_code if response else 'N/A'}: {error_text}"
                }
        except Exception as e:
            logger.error(f"Erro ao atualizar atividade: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def create_activities_bulk(self, activities: List[Dict], timeout: int = 300) -> Dict:
        """
        Cria múltiplas atividades em lote (POST)
        
        Args:
            activities: Lista de dicionários com dados das atividades
            timeout: Timeout específico para esta requisição (padrão 5 minutos)
            
        Returns:
            Dict com resultado da operação em lote
        """
        try:
            payload = {"activities": activities}
            response = self._make_request(
                'POST',
                '/activities/bulk-create',
                json_data=payload,
                timeout=timeout,
                retry_count=1
            )
            
            if response and response.status_code in (200, 201):
                return response.json()
            else:
                error_text = response.text[:300] if response else "Sem resposta"
                return {
                    'created': 0,
                    'updated': 0,
                    'failed': len(activities),
                    'message': f"HTTP {response.status_code if response else 'N/A'}: {error_text}"
                }
        except Exception as e:
            logger.error(f"Erro ao criar atividades em lote: {e}")
            return {
                'created': 0,
                'updated': 0,
                'failed': len(activities),
                'message': str(e)
            }
    
    def update_activities_bulk(self, activities: List[Dict], timeout: Optional[int] = None) -> Dict:
        """
        Atualiza múltiplas atividades em lote (PUT)
        
        Args:
            activities: Lista de dicionários com dados das atividades
            timeout: Timeout específico (calculado automaticamente se None)
            
        Returns:
            Dict com resultado da operação em lote
        """
        try:
            # Calcular timeout baseado no número de atividades
            if timeout is None:
                timeout = min(300, max(60, len(activities) * 5))
            
            payload = {"activities": activities}
            response = self._make_request(
                'PUT',
                '/activities/bulk',
                json_data=payload,
                timeout=timeout,
                retry_count=1
            )
            
            if response and response.status_code == 200:
                return response.json()
            else:
                error_text = response.text[:300] if response else "Sem resposta"
                return {
                    'total': len(activities),
                    'successful': 0,
                    'failed': len(activities),
                    'results': [],
                    'message': f"HTTP {response.status_code if response else 'N/A'}: {error_text}"
                }
        except Exception as e:
            logger.error(f"Erro ao atualizar atividades em lote: {e}")
            return {
                'total': len(activities),
                'successful': 0,
                'failed': len(activities),
                'results': [],
                'message': str(e)
            }
    
    def archive_execution_activities(self, sequencia: str) -> Dict:
        """
        Arquivar todas as atividades de execução de uma sequência
        
        Args:
            sequencia: Nome da sequência/CRQ
            
        Returns:
            Dict com resultado da operação
        """
        try:
            response = self._make_request(
                'POST',
                '/activities/archive-execution',
                params={'sequencia': sequencia},
                timeout=30
            )
            
            if response and response.status_code == 200:
                return response.json()
            else:
                return {
                    'archived_count': 0,
                    'message': f"HTTP {response.status_code if response else 'N/A'}"
                }
        except Exception as e:
            logger.error(f"Erro ao arquivar atividades de execução: {e}")
            return {
                'archived_count': 0,
                'message': str(e)
            }
    
    def activate_rollback_activities(self, sequencia: str) -> Dict:
        """
        Ativar todas as atividades de rollback de uma sequência
        
        Args:
            sequencia: Nome da sequência/CRQ
            
        Returns:
            Dict com resultado da operação
        """
        try:
            response = self._make_request(
                'POST',
                '/activities/activate-rollback',
                params={'sequencia': sequencia},
                timeout=30
            )
            
            if response and response.status_code == 200:
                return response.json()
            else:
                return {
                    'activated_count': 0,
                    'message': f"HTTP {response.status_code if response else 'N/A'}"
                }
        except Exception as e:
            logger.error(f"Erro ao ativar atividades de rollback: {e}")
            return {
                'activated_count': 0,
                'message': str(e)
            }


# Instância global do cliente (pode ser reutilizada)
_default_client = None

def get_client(base_url: Optional[str] = None) -> APIClient:
    """
    Obtém uma instância do cliente API (singleton)
    
    Args:
        base_url: URL base da API (opcional, usa padrão se None)
        
    Returns:
        Instância do APIClient
    """
    global _default_client
    if _default_client is None or (base_url and _default_client.base_url != base_url):
        _default_client = APIClient(base_url=base_url or API_BASE_URL)
    return _default_client
