from typing import Dict, List

import config

from .base_scraper import BaseScraper


class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Amazon"
        self.deal_urls = [
            "https://www.amazon.in/deals",
            "https://www.amazon.in/gp/goldbox",
            "https://www.amazon.in/s?i=todays-deals",
            "https://www.amazon.in/s?k=discount",
        ]

    def scrape(self) -> List[Dict]:
        deals = []

        for url in self.deal_urls:
            soup = self.get_page(url)
            if not soup:
                continue

            deal_items = soup.select("div[data-asin]")
            for item in deal_items:
                asin = item.get("data-asin", "").strip()
                if not asin:
                    continue

                try:
                    title_elem = (
                        item.select_one("h2 a span")
                        or item.select_one("span.a-size-base-plus")
                        or item.select_one("img[alt]")
                    )
                    product_name = (
                        title_elem.get_text(strip=True)
                        if title_elem and hasattr(title_elem, "get_text")
                        else title_elem.get("alt", "")
                        if title_elem
                        else ""
                    )
                    if len(product_name) < 8:
                        continue

                    link_elem = item.select_one("a.a-link-normal[href]")
                    raw_url = link_elem.get("href", "") if link_elem else f"/dp/{asin}"
                    product_url = self.normalize_url(raw_url, "https://www.amazon.in")

                    deal_elem = item.select_one("span.a-price span.a-offscreen") or item.select_one("span.a-price-whole")
                    original_elem = item.select_one("span.a-text-price span.a-offscreen") or item.select_one("span.a-price.a-text-price span")

                    deal_price = self.extract_price(deal_elem.get_text(" ", strip=True) if deal_elem else "")
                    original_price = self.extract_price(original_elem.get_text(" ", strip=True) if original_elem else "")

                    if deal_price <= 0:
                        continue

                    if original_price <= 0:
                        original_price = round(deal_price * 1.2, 2)

                    discount = self.calculate_discount(original_price, deal_price)
                    if discount < config.MIN_DISCOUNT:
                        continue

                    image_url = self.extract_image_url(item, "https://www.amazon.in")

                    deals.append(
                        {
                            "product_name": product_name,
                            "deal_price": int(deal_price),
                            "original_price": int(original_price),
                            "discount": discount,
                            "url": product_url,
                            "site": self.site_name,
                            "image_url": image_url,
                        }
                    )
                except Exception as e:
                    print(f"Error parsing Amazon deal: {e}")

        return deals[:60]
