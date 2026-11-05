import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import json
import time
from typing import List, Dict, Optional

class SearchEngineV2:
    """Motor de busca melhorado com múltiplas fontes"""
    
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.timeout = 8
        
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Busca com fallback automático entre fontes
        """
        print(f"  [SEARCH] Pesquisando: '{query}'")
        
        # Tenta métodos em ordem de confiabilidade
        methods = [
            self._search_brave,
            self._search_ddg_api,
            self._search_wikipedia,
            self._search_ddg_lite
        ]
        
        for method in methods:
            try:
                results = method(query, max_results)
                if results and len(results) > 0:
                    print(f"  [SEARCH] ✓ Encontrado {len(results)} resultados via {method.__name__}")
                    return results
            except Exception as e:
                print(f"  [SEARCH] ⚠ {method.__name__} falhou: {e}")
                continue
        
        print(f"  [SEARCH] ✗ Nenhuma fonte funcionou")
        return []
    
    def _search_brave(self, query: str, max_results: int) -> List[Dict]:
        """
        Brave Search API (sem necessidade de chave para uso básico)
        """
        url = "https://search.brave.com/search"
        params = {
            'q': query,
            'source': 'web'
        }
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # Brave usa divs com classe específica
        for item in soup.select('div.snippet')[:max_results]:
            try:
                title_elem = item.select_one('a')
                snippet_elem = item.select_one('p.snippet-description')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'source': 'brave'
                    })
            except:
                continue
        
        return results
    
    def _search_ddg_api(self, query: str, max_results: int) -> List[Dict]:
        """
        DuckDuckGo Instant Answer API
        """
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        # Abstract (resposta direta)
        if data.get('Abstract'):
            results.append({
                'title': data.get('Heading', query),
                'url': data.get('AbstractURL', ''),
                'snippet': data.get('Abstract', ''),
                'source': 'duckduckgo_instant'
            })
        
        # Related topics
        for topic in data.get('RelatedTopics', [])[:max_results-len(results)]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append({
                    'title': topic.get('Text', '')[:100],
                    'url': topic.get('FirstURL', ''),
                    'snippet': topic.get('Text', ''),
                    'source': 'duckduckgo_related'
                })
        
        return results
    
    def _search_wikipedia(self, query: str, max_results: int) -> List[Dict]:
        """
        Wikipedia API - excelente para conhecimento factual
        """
        url = "https://pt.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srlimit': max_results,
            'srprop': 'snippet'
        }
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        for item in data.get('query', {}).get('search', []):
            # Remove HTML tags do snippet
            snippet = BeautifulSoup(item.get('snippet', ''), 'html.parser').get_text()
            
            results.append({
                'title': item.get('title', ''),
                'url': f"https://pt.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                'snippet': snippet,
                'source': 'wikipedia'
            })
        
        return results
    
    def _search_ddg_lite(self, query: str, max_results: int) -> List[Dict]:
        """
        DuckDuckGo Lite (versão HTML simplificada)
        """
        url = "https://lite.duckduckgo.com/lite/"
        params = {'q': query}
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # DDG Lite usa uma estrutura mais simples
        for row in soup.select('tr')[:max_results * 2]:  # Pega mais pois alguns são ads
            try:
                link = row.select_one('a.result-link')
                snippet = row.select_one('td.result-snippet')
                
                if link and snippet:
                    results.append({
                        'title': link.get_text(strip=True),
                        'url': link.get('href', ''),
                        'snippet': snippet.get_text(strip=True),
                        'source': 'duckduckgo_lite'
                    })
                    
                    if len(results) >= max_results:
                        break
            except:
                continue
        
        return results
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Busca notícias recentes
        """
        # Google News RSS (público)
        url = "https://news.google.com/rss/search"
        params = {
            'q': query,
            'hl': 'pt-BR',
            'gl': 'BR',
            'ceid': 'BR:pt-419'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'xml')
            results = []
            
            for item in soup.find_all('item')[:max_results]:
                results.append({
                    'title': item.title.text if item.title else '',
                    'url': item.link.text if item.link else '',
                    'snippet': item.description.text if item.description else '',
                    'date': item.pubDate.text if item.pubDate else '',
                    'source': 'google_news'
                })
            
            return results
        except:
            return []
    
    def get_page_content(self, url: str, max_length: int = 1000) -> Optional[str]:
        """
        Extrai conteúdo principal de uma página
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts e styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Pega texto dos principais elementos
            main_content = soup.find(['article', 'main', 'div'])
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
            
            # Limpa espaços excessivos
            text = ' '.join(text.split())
            
            return text[:max_length]
        except:
            return None


# TESTES
if __name__ == "__main__":
    print("="*60)
    print("TESTE DO MOTOR DE BUSCA V2")
    print("="*60)
    
    engine = SearchEngineV2()
    
    queries = [
        "Python programming",
        "Minecraft dicas",
        "Inteligência artificial"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        results = engine.search(query, max_results=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   Snippet: {result['snippet'][:150]}...")
                print(f"   Fonte: {result['source']}")
        else:
            print("Nenhum resultado encontrado")
        
        time.sleep(1)  # Rate limiting