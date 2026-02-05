import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot
from telegram.constants import ParseMode

import config
from database import Database
from deal_processor import DealProcessor
from keyword_manager import KeywordManager
from message_formatter import MessageFormatter
from proxy_manager import ProxyManager
from scrapers import ALL_SCRAPERS


class DealScheduler:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.deal_processor = DealProcessor(db)
        self.keyword_manager = KeywordManager(db)
        self.proxy_manager = ProxyManager()
        self.is_running = False
        self.logger = logging.getLogger(self.__class__.__name__)

    async def scrape_and_send_deals(self):
        if self.is_running:
            self.logger.warning("Previous scraping still in progress, skipping...")
            return

        self.is_running = True
        self.logger.info("Starting deal scraping...")

        try:
            all_deals = []
            scrape_summary = {}

            for scraper_class in ALL_SCRAPERS:
                scraper = None
                try:
                    scraper = scraper_class()
                    scraper_name = scraper.site_name
                    scraper.set_proxy_manager(self.proxy_manager)
                    proxies = self.proxy_manager.get_proxies_for_scraper(scraper_name, 5)
                    scraper.set_proxies(proxies)
                    self.logger.info(
                        "Scraping %s with %s proxies",
                        scraper_name,
                        len(proxies),
                    )
                    deals = scraper.scrape()
                    all_deals.extend(deals)
                    scrape_summary[scraper_name] = len(deals)
                    self.logger.info("Found %s deals from %s", len(deals), scraper_name)
                    await asyncio.sleep(2)
                except Exception as exc:
                    scraper_name = scraper.site_name if scraper else scraper_class.__name__
                    scrape_summary[scraper_name] = 0
                    self.logger.exception("Error in scraper %s: %s", scraper_name, exc)
                    continue

            self.logger.info("Scrape summary: %s", scrape_summary)
            self.logger.info("Total deals scraped: %s", len(all_deals))

            processed_deals = self.deal_processor.process_deals(all_deals)
            self.logger.info("Unique deals after processing: %s", len(processed_deals))

            if not processed_deals:
                self.logger.warning("No new deals to send")
                return

            authorized_chats = self.db.get_authorized_chats()
            self.logger.info("Sending to %s authorized chats", len(authorized_chats))

            for chat_id in authorized_chats:
                try:
                    sent_count = 0
                    for deal in processed_deals:
                        if self.keyword_manager.matches_keywords(chat_id, deal["product_name"]):
                            message = MessageFormatter.format_deal(deal)
                            image_url = deal.get("image_url", "")

                            try:
                                if image_url:
                                    await self.bot.send_photo(
                                        chat_id=chat_id,
                                        photo=image_url,
                                        caption=message,
                                        parse_mode=ParseMode.MARKDOWN,
                                    )
                                else:
                                    await self.bot.send_message(
                                        chat_id=chat_id,
                                        text=message,
                                        parse_mode=ParseMode.MARKDOWN,
                                        disable_web_page_preview=False,
                                    )
                                sent_count += 1
                                self.db.increment_stat("deals_sent")
                            except Exception as msg_err:
                                self.logger.warning("Error sending deal message: %s", msg_err)
                                try:
                                    await self.bot.send_message(
                                        chat_id=chat_id,
                                        text=message,
                                        parse_mode=ParseMode.MARKDOWN,
                                        disable_web_page_preview=False,
                                    )
                                    sent_count += 1
                                    self.db.increment_stat("deals_sent")
                                except Exception:
                                    self.logger.exception("Failed to send fallback message")

                            await asyncio.sleep(1)

                    self.logger.info("Sent %s deals to chat %s", sent_count, chat_id)
                except Exception as exc:
                    self.logger.exception("Error sending to chat %s: %s", chat_id, exc)
                    continue

            self.db.cleanup_old_deals(7)
        except Exception as exc:
            self.logger.exception("Error in scrape_and_send_deals: %s", exc)
        finally:
            self.is_running = False
            self.logger.info("Scraping complete")

    def start(self):
        self.scheduler.add_job(
            self.scrape_and_send_deals,
            trigger=IntervalTrigger(minutes=config.SCRAPE_INTERVAL),
            id="deal_scraper",
            name="Scrape and send deals",
            replace_existing=True,
        )

        self.scheduler.start()
        self.logger.info("Scheduler started - scraping every %s minutes", config.SCRAPE_INTERVAL)

    def stop(self):
        self.scheduler.shutdown()
        self.logger.info("Scheduler stopped")
