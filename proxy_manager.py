import logging
import random
import time
from typing import Dict, List, Optional

import requests


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

    HEALTH_CHECK_URL = "https://httpbin.org/ip"
    COOLDOWN_SECONDS = 300

    def __init__(self):
        self.failed_proxies: Dict[str, float] = {}
        self.proxy_pool = self.PROXIES.copy()
        self.proxy_stats: Dict[str, Dict[str, int]] = {}
        random.shuffle(self.proxy_pool)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _parse_proxy(self, proxy_str: str) -> Dict[str, str]:
        parts = proxy_str.split(":")
        if len(parts) != 4:
            return {}

        username, password, host, port = parts
        proxy_url = f"http://{username}:{password}@{host}:{port}"

        return {
            "http": proxy_url,
            "https": proxy_url,
        }

    def _proxy_matches(self, proxy_str: str, proxy_dict: Dict[str, str]) -> bool:
        if not proxy_dict:
            return False
        proxy_repr = str(proxy_dict)
        parts = proxy_str.split(":")
        return len(parts) == 4 and parts[2] in proxy_repr and parts[3] in proxy_repr

    def _is_proxy_available(self, proxy_str: str) -> bool:
        failed_at = self.failed_proxies.get(proxy_str)
        if not failed_at:
            return True
        if time.time() - failed_at >= self.COOLDOWN_SECONDS:
            self.failed_proxies.pop(proxy_str, None)
            return True
        return False

    def get_proxies_for_scraper(self, scraper_name: str, count: int = 5) -> List[Dict[str, str]]:
        available_proxies = [p for p in self.proxy_pool if self._is_proxy_available(p)]
        if not available_proxies:
            self.logger.warning("No healthy proxies available for %s. Falling back to direct.", scraper_name)
            return []

        selected = random.sample(available_proxies, min(count, len(available_proxies)))
        self.logger.info("%s proxies selected for %s", len(selected), scraper_name)
        return [self._parse_proxy(p) for p in selected]

    def mark_proxy_failed(self, proxy_dict: Dict[str, str]):
        for proxy_str in self.PROXIES:
            if self._proxy_matches(proxy_str, proxy_dict):
                self.failed_proxies[proxy_str] = time.time()
                stats = self.proxy_stats.setdefault(proxy_str, {"success": 0, "fail": 0})
                stats["fail"] += 1
                self.logger.warning("Marked proxy failed: %s", proxy_str)
                break

    def mark_proxy_success(self, proxy_dict: Dict[str, str]):
        for proxy_str in self.PROXIES:
            if self._proxy_matches(proxy_str, proxy_dict):
                stats = self.proxy_stats.setdefault(proxy_str, {"success": 0, "fail": 0})
                stats["success"] += 1
                if proxy_str in self.failed_proxies:
                    self.failed_proxies.pop(proxy_str, None)
                break

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        available_proxies = [p for p in self.proxy_pool if self._is_proxy_available(p)]
        if not available_proxies:
            self.logger.warning("No healthy proxies available. Returning None.")
            return None
        return self._parse_proxy(random.choice(available_proxies))

    def check_proxy_health(self, proxy_dict: Dict[str, str], timeout: int = 5) -> bool:
        try:
            response = requests.get(self.HEALTH_CHECK_URL, proxies=proxy_dict, timeout=timeout)
            if response.status_code == 200:
                self.mark_proxy_success(proxy_dict)
                return True
        except requests.RequestException:
            self.mark_proxy_failed(proxy_dict)
        return False
