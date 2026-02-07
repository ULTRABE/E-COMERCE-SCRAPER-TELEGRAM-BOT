import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from deal_processor import DealProcessor
from database import Database
from scrapers import ALL_SCRAPERS


def scrape_live_deals(limit: int = 30):
    db = Database()
    processor = DealProcessor(db)
    all_deals = []
    for scraper_class in ALL_SCRAPERS:
        scraper = scraper_class()
        all_deals.extend(scraper.scrape())
    return processor.process_deals(all_deals)[:limit]


class DealsApiHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json({"ok": True})
            return

        if parsed.path == "/api/deals/live":
            query = parse_qs(parsed.query)
            try:
                limit = int(query.get("limit", ["30"])[0])
            except ValueError:
                limit = 30
            deals = scrape_live_deals(limit=max(1, min(limit, 100)))
            self._send_json({"count": len(deals), "deals": deals})
            return

        self._send_json({"error": "Not Found"}, status=404)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), DealsApiHandler)
    print("Deals API server running on :8080")
    server.serve_forever()
