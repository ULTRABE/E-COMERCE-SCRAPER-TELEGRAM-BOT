from typing import Dict, List

import config

from .base_scraper import BaseScraper


class FlipkartScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Flipkart"
        self.deal_urls = [
            "https://www.flipkart.com/offers-store",
            "https://www.flipkart.com/search?q=deals+of+the+day",
        ]

    def scrape(self) -> List[Dict]:
        deals = []

        for url in self.deal_urls:
            soup = self.get_page(url)
            if not soup:
                continue

            deal_items = soup.select("a._1fQZEK, a.CGtC98, div._1AtVbE")
            for item in deal_items:
                try:
                    link_elem = item if item.name == "a" else item.select_one("a[href]")
                    if not link_elem:
                        continue

                    product_url = self.normalize_url(link_elem.get("href", ""), "https://www.flipkart.com")

                    title_elem = (
                        item.select_one("div._4rR01T")
                        or item.select_one("div.KzDlHZ")
                        or item.select_one("div.s1Q9rs")
                        or item.select_one("img[alt]")
                    )
                    product_name = (
                        title_elem.get_text(" ", strip=True)
                        if title_elem and hasattr(title_elem, "get_text")
                        else title_elem.get("alt", "")
                        if title_elem
                        else ""
                    )
                    if len(product_name) < 8:
                        continue

                    price_elem = item.select_one("div._30jeq3") or item.select_one("div.Nx9bqj")
                    original_elem = item.select_one("div._3I9_wc") or item.select_one("div.yRaY8j")
                    discount_elem = item.select_one("div._3Ay6sb") or item.select_one("div.UkUFwK")

                    deal_price = self.extract_price(price_elem.get_text(strip=True) if price_elem else "")
                    if deal_price <= 0:
                        continue

                    original_price = self.extract_price(original_elem.get_text(strip=True) if original_elem else "")
                    if original_price <= 0:
                        original_price = round(deal_price * 1.2, 2)

                    discount = 0
                    if discount_elem:
                        discount = int("".join(filter(str.isdigit, discount_elem.get_text(" ", strip=True))) or 0)
                    if discount <= 0:
                        discount = self.calculate_discount(original_price, deal_price)

                    if discount < config.MIN_DISCOUNT:
                        continue

                    image_url = self.extract_image_url(item, "https://www.flipkart.com")

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
                    print(f"Error parsing Flipkart deal: {e}")

        return deals[:30]
