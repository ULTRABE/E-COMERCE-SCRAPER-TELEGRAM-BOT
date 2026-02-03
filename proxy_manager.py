import random
from typing import List, Dict, Optional

class ProxyManager:
    PROXIES = [
        "203033:JmNd95Z3vcX:196.51.106.117:8800",
        "203033:JmNd95Z3vcX:196.51.106.30:8800",
        "203033:JmNd95Z3vcX:196.51.82.198:8800",
        "203033:JmNd95Z3vcX:196.51.106.100:8800",
        "203033:JmNd95Z3vcX:196.51.85.207:8800",
        "203033:JmNd95Z3vcX:196.51.85.156:8800",
        "203033:JmNd95Z3vcX:170.130.62.221:8800",
        "203033:JmNd95Z3vcX:196.51.106.69:8800",
        "203033:JmNd95Z3vcX:196.51.109.8:8800",
        "203033:JmNd95Z3vcX:196.51.221.158:8800",
        "203033:JmNd95Z3vcX:196.51.82.238:8800",
        "203033:JmNd95Z3vcX:196.51.109.31:8800",
        "203033:JmNd95Z3vcX:170.130.62.27:8800",
        "203033:JmNd95Z3vcX:196.51.82.106:8800",
        "203033:JmNd95Z3vcX:196.51.221.46:8800",
        "203033:JmNd95Z3vcX:196.51.221.125:8800",
        "203033:JmNd95Z3vcX:196.51.218.250:8800",
        "203033:JmNd95Z3vcX:196.51.218.169:8800",
        "203033:JmNd95Z3vcX:196.51.221.102:8800",
        "203033:JmNd95Z3vcX:170.130.62.42:8800",
        "203033:JmNd95Z3vcX:77.83.170.30:8800",
        "203033:JmNd95Z3vcX:196.51.82.120:8800",
        "203033:JmNd95Z3vcX:196.51.221.38:8800",
        "203033:JmNd95Z3vcX:196.51.218.236:8800",
        "203033:JmNd95Z3vcX:196.51.85.213:8800",
        "203033:JmNd95Z3vcX:196.51.106.149:8800",
        "203033:JmNd95Z3vcX:196.51.109.151:8800",
        "203033:JmNd95Z3vcX:196.51.82.112:8800",
        "203033:JmNd95Z3vcX:196.51.85.59:8800",
        "203033:JmNd95Z3vcX:196.51.85.7:8800",
        "203033:JmNd95Z3vcX:77.83.170.168:8800",
        "203033:JmNd95Z3vcX:170.130.62.211:8800",
        "203033:JmNd95Z3vcX:196.51.218.179:8800",
        "203033:JmNd95Z3vcX:196.51.82.59:8800",
        "203033:JmNd95Z3vcX:77.83.170.79:8800",
        "203033:JmNd95Z3vcX:170.130.62.223:8800",
        "203033:JmNd95Z3vcX:170.130.62.151:8800",
        "203033:JmNd95Z3vcX:196.51.85.127:8800",
        "203033:JmNd95Z3vcX:196.51.109.138:8800",
        "203033:JmNd95Z3vcX:196.51.106.16:8800",
        "203033:JmNd95Z3vcX:196.51.109.52:8800",
        "203033:JmNd95Z3vcX:170.130.62.251:8800",
        "203033:JmNd95Z3vcX:170.130.62.24:8800",
        "203033:JmNd95Z3vcX:196.51.218.60:8800",
        "203033:JmNd95Z3vcX:196.51.109.6:8800",
        "203033:JmNd95Z3vcX:196.51.221.174:8800",
        "203033:JmNd95Z3vcX:196.51.218.227:8800",
        "203033:JmNd95Z3vcX:77.83.170.124:8800",
        "203033:JmNd95Z3vcX:77.83.170.222:8800",
        "203033:JmNd95Z3vcX:77.83.170.91:8800",
    ]
    
    def __init__(self):
        self.failed_proxies = set()
        self.proxy_pool = self.PROXIES.copy()
        random.shuffle(self.proxy_pool)
    
    def _parse_proxy(self, proxy_str: str) -> Dict[str, str]:
        parts = proxy_str.split(':')
        if len(parts) != 4:
            return {}
        
        username, password, host, port = parts
        proxy_url = f"http://{username}:{password}@{host}:{port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_proxies_for_scraper(self, scraper_name: str, count: int = 5) -> List[Dict[str, str]]:
        available_proxies = [p for p in self.proxy_pool if p not in self.failed_proxies]
        
        if len(available_proxies) < count:
            self.failed_proxies.clear()
            available_proxies = self.proxy_pool.copy()
        
        selected = random.sample(available_proxies, min(count, len(available_proxies)))
        return [self._parse_proxy(p) for p in selected]
    
    def mark_proxy_failed(self, proxy_dict: Dict[str, str]):
        for proxy_str in self.PROXIES:
            if proxy_str in str(proxy_dict):
                self.failed_proxies.add(proxy_str)
                break
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        available_proxies = [p for p in self.proxy_pool if p not in self.failed_proxies]
        
        if not available_proxies:
            self.failed_proxies.clear()
            available_proxies = self.proxy_pool.copy()
        
        if available_proxies:
            return self._parse_proxy(random.choice(available_proxies))
        return None
