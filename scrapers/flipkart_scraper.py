from typing import Dict, List

from .base_scraper import BaseScraper


class FlipkartScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Flipkart"
        self.update_logger()
        self.base_url = "https://www.flipkart.com"
        self.deal_urls = [
            f"{self.base_url}/offers-store",
            f"{self.base_url}/offers",
            f"{self.base_url}/offers-list",
            self.base_url,
        ]
        self.card_selectors = [
            "a._1fQZEK",
            "a._2rpwqI",
            "div._2kHMtA a",
            "div[data-id] a",
            "div._1AtVbE a",
        ]
        self.title_selectors = [
            "div._4rR01T",
            "div._2WkVRV",
            "a._2rpwqI",
            "div._3wU53n",
            "div._2B099V",
        ]
        self.price_selectors = ["div._30jeq3", "div._1_WHN1", "div._1vC4OE"]
        self.original_selectors = ["div._3I9_wc", "div._2p6lqe", "div._1s8dld"]
        self.discount_selectors = ["div._3Ay6sb", "span._3Ay6sb", "div._3LV0nZ"]
        self.url_selectors = ["a._1fQZEK", "a._2rpwqI", "a"]

    def scrape(self) -> List[Dict]:
        deals: List[Dict] = []
        soup, used_url = self.get_page_from_urls(self.deal_urls)
        if not soup:
            self.logger.error("%s: unable to fetch any deal page", self.site_name)
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
