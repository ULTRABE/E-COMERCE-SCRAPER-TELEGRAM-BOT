from typing import Dict, List

import config

from .base_scraper import BaseScraper


class JioMartScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "JioMart"
        self.deal_urls = [
            "https://www.jiomart.com/c/groceries/2",
            "https://www.jiomart.com/c/electronics/4",
            "https://www.jiomart.com/c/fashion/3",
        ]

    def scrape(self) -> List[Dict]:
        deals = []

        for url in self.deal_urls:
            soup = self.get_page(url)
            if not soup:
                continue

            cards = soup.select("li.plp-card-container, div.product-card")
            for card in cards:
                try:
                    title_elem = card.select_one(".plp-card-details-name") or card.select_one("a[title]")
                    product_name = title_elem.get_text(" ", strip=True) if title_elem else ""
                    if not product_name:
                        title_attr = title_elem.get("title", "") if title_elem else ""
                        product_name = title_attr.strip()
                    if len(product_name) < 3:
                        continue

                    link_elem = card.select_one("a[href]")
                    product_url = self.normalize_url(link_elem.get("href", "") if link_elem else "", "https://www.jiomart.com")

                    deal_elem = card.select_one(".jm-heading-xxs") or card.select_one("span.jm-body-xs")
                    original_elem = card.select_one(".original-price") or card.select_one("span.line-through")
                    discount_elem = card.select_one(".discount")

                    deal_price = self.extract_price(deal_elem.get_text(" ", strip=True) if deal_elem else "")
                    if deal_price <= 0:
                        continue

                    original_price = self.extract_price(original_elem.get_text(" ", strip=True) if original_elem else "")
                    if original_price <= 0:
                        original_price = round(deal_price * 1.15, 2)

                    discount = 0
                    if discount_elem:
                        discount = int("".join(filter(str.isdigit, discount_elem.get_text(" ", strip=True))) or 0)
                    if discount <= 0:
                        discount = self.calculate_discount(original_price, deal_price)

                    if discount < config.MIN_DISCOUNT:
                        continue

                    image_url = self.extract_image_url(card, "https://www.jiomart.com")

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
                    print(f"Error parsing JioMart deal: {e}")

        return deals[:30]
