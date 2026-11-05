import threading
import time
from datetime import datetime

class BackgroundSearch:
    """Gerencia pesquisas em segundo plano"""
    
    def __init__(self):
        self.active_searches = []
        self.completed_searches = []
        self.max_concurrent = 3  # Máximo de pesquisas simultâneas
    
    def start_search(self, query, search_engine):
        """Inicia pesquisa em segundo plano"""
        # Verifica se já não está pesquisando isso
        for search in self.active_searches:
            if search['query'].lower() == query.lower():
                return False
        
        # Cria entrada de pesquisa
        search_data = {
            'query': query,
            'started_at': datetime.now(),
            'completed': False,
            'results': [],
            'error': None
        }
        
        self.active_searches.append(search_data)
        
        # Inicia thread de pesquisa
        thread = threading.Thread(
            target=self._search_thread,
            args=(search_data, search_engine),
            daemon=True
        )
        thread.start()
        
        return True
    
    def _search_thread(self, search_data, search_engine):
        """Thread que executa a pesquisa"""
        try:
            print(f"  [BACKGROUND] Pesquisando '{search_data['query']}'...")
            
            # Executa pesquisa
            results = search_engine.search(search_data['query'], max_results=10)
            
            # Atualiza resultados
            search_data['results'] = results
            search_data['completed'] = True
            search_data['completed_at'] = datetime.now()
            
            # Move para concluídas
            if search_data in self.active_searches:
                self.active_searches.remove(search_data)
            self.completed_searches.append(search_data)
            
            # Mantém apenas últimas 10 pesquisas
            if len(self.completed_searches) > 10:
                self.completed_searches.pop(0)
            
            print(f"  [BACKGROUND] ✓ Pesquisa '{search_data['query']}' concluída!")
            
        except Exception as e:
            search_data['error'] = str(e)
            search_data['completed'] = True
            print(f"  [BACKGROUND] ✗ Erro na pesquisa '{search_data['query']}': {e}")
    
    def get_results(self):
        """Retorna todas as pesquisas (ativas e completas)"""
        all_searches = self.active_searches + self.completed_searches
        return sorted(all_searches, key=lambda x: x['started_at'], reverse=True)
    
    def get_completed(self):
        """Retorna apenas pesquisas completas"""
        return self.completed_searches
    
    def get_active(self):
        """Retorna pesquisas em andamento"""
        return self.active_searches
    
    def get_search(self, query):
        """Busca pesquisa específica"""
        query_lower = query.lower()
        
        for search in self.get_results():
            if search['query'].lower() == query_lower:
                return search
        
        return None
    
    def stop_all(self):
        """Para todas as pesquisas (na verdade, só marca como paradas)"""
        # Threads daemon são automaticamente paradas
        self.active_searches.clear()
    
    def clear_completed(self):
        """Limpa pesquisas completas"""
        self.completed_searches.clear()