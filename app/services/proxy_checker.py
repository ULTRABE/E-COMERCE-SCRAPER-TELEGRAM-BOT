import asyncio
import aiohttp

class ProxyChecker:
    def __init__(self, api_key: str, concurrency: int, connect_timeout: int, total_timeout: int):
        self.api_key = api_key
        self.sem = asyncio.Semaphore(concurrency)
        self.timeout = aiohttp.ClientTimeout(total=total_timeout, connect=connect_timeout)

    async def _fraud_ok(self, session: aiohttp.ClientSession, ip: str):
        url = f"https://proxycheck.io/v2/{ip}?key={self.api_key}&risk=1&vpn=1&asn=1"
        try:
            async with session.get(url, timeout=self.timeout) as r:
                data = await r.json(content_type=None)
                row = data.get(ip, {})
                risk = int(str(row.get("risk", "100")).split('.')[0])
                return risk < 20 and row.get("proxy") == "no" or risk < 20
        except Exception:
            return False

    async def _check_one(self, session, proto: str, proxy: str):
        async with self.sem:
            proxy_url = f"{proto}://{proxy}"
            test_url = "https://api.ipify.org?format=json"
            try:
                async with session.get(test_url, proxy=proxy_url, timeout=self.timeout) as r:
                    if r.status != 200:
                        return None
                    ip = (await r.json()).get("ip")
                    if not ip:
                        return None
                    if not await self._fraud_ok(session, ip):
                        return None
                    cat = "HTTP/HTTPS" if proto in {"http", "https"} else proto.upper()
                    return cat, proxy
            except Exception:
                return None

    async def check_batch(self, proxies, progress_cb=None):
        out = {"HTTP/HTTPS": [], "SOCKS4": [], "SOCKS5": [], "Residential": []}
        done = alive = filtered = 0
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = [self._check_one(session, proto, proxy) for proto, proxy in proxies]
            for fut in asyncio.as_completed(tasks):
                done += 1
                result = await fut
                if result:
                    alive += 1
                    cat, p = result
                    out[cat].append(p)
                    filtered += 1
                if progress_cb and done % 50 == 0:
                    await progress_cb(done, len(tasks), alive, filtered)
        return {k: v for k, v in out.items() if v}
