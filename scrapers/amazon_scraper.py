from typing import Dict, List

from .base_scraper import BaseScraper


class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Amazon India"
        self.update_logger()
        self.base_url = "https://www.amazon.in"
        self.deal_urls = [
            f"{self.base_url}/deals",
            f"{self.base_url}/gp/goldbox",
            f"{self.base_url}/b?node=1968024031",
        ]
        self.card_selectors = [
            "div[data-deal-id]",
            "div[data-asin]",
            "div.a-section[data-asin]",
            "div.s-result-item",
        ]
        self.title_selectors = [
            "a[aria-label]",
            "span.a-truncate-full",
            "span.a-size-base-plus",
            "span.a-size-medium",
        ]
        self.price_selectors = [
            "span.a-price > span.a-offscreen",
            "span.a-price-whole",
            "span.a-color-price",
        ]
        self.original_selectors = ["span.a-text-price", "span.a-price.a-text-price"]
        self.discount_selectors = ["span.savingsPercentage", "span.a-color-secondary"]
        self.url_selectors = ["a.a-link-normal", "a.a-link-normal.s-no-outline", "a"]

    def scrape(self) -> List[Dict]:
        deals: List[Dict] = []
        soup, used_url = self.get_page_from_urls(self.deal_urls)
        if not soup:
            self.logger.error("%s: unable to fetch any deal page", self.site_name)
            return deals

        if "captcha" in soup.get_text(" ").lower():
            self.logger.warning("%s: captcha detected on %s", self.site_name, used_url)
            return deals

        cards = self.select_all(soup, self.card_selectors)
        self.logger.info("%s: found %s cards from %s", self.site_name, len(cards), used_url)

        for card in cards[:40]:
            deal = self.build_deal(
                card,
                self.base_url,
                self.title_selectors,
                self.price_selectors,
                self.url_selectors,
                self.original_selectors,
                self.discount_selectors,
            )
            if deal:
                deals.append(deal)

        self.logger.info("%s: parsed %s deals", self.site_name, len(deals))
        return deals[:15]
