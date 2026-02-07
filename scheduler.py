import asyncio
from typing import List

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

    async def scrape_and_send_deals(self):
        if self.is_running:
            print("Previous scraping still in progress, skipping...")
            return

        self.is_running = True
        print("Starting deal scraping...")

        try:
            all_deals = []

            for scraper_class in ALL_SCRAPERS:
                try:
                    scraper = scraper_class()
                    scraper_name = scraper.site_name
                    proxies = self.proxy_manager.get_proxies_for_scraper(scraper_name, 5)
                    scraper.set_proxies(proxies)
                    print(f"Scraping {scraper_name}...")
                    deals = scraper.scrape()
                    all_deals.extend(deals)
                    print(f"Found {len(deals)} deals from {scraper_name}")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Error in scraper {scraper_class.__name__}: {e}")

            print(f"Total deals scraped: {len(all_deals)}")

            processed_deals = self.deal_processor.process_deals(all_deals)
            print(f"Unique/new deals after processing: {len(processed_deals)}")

            if not processed_deals:
                print("No new live deals to send")
                return

            authorized_chats = self.db.get_authorized_chats()
            print(f"Sending to {len(authorized_chats)} authorized chats")

            for chat_id in authorized_chats:
                sent_count = 0
                for deal in processed_deals:
                    if not self.keyword_manager.matches_keywords(chat_id, deal["product_name"]):
                        continue

                    message = MessageFormatter.format_deal(deal)
                    image_url = deal.get("image_url", "")
                    can_send_photo = False

                    if image_url:
                        can_send_photo = not any(k in image_url.lower() for k in ["40x40", "60x60", "80x80", "thumb", "thumbnail"])

                    try:
                        if can_send_photo:
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
                        print(f"Error sending deal message: {msg_err}")
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
                            pass

                    await asyncio.sleep(0.8)

                print(f"Sent {sent_count} deals to chat {chat_id}")

            self.db.cleanup_old_deals(3)

        except Exception as e:
            print(f"Error in scrape_and_send_deals: {e}")
        finally:
            self.is_running = False
            print("Scraping complete")

    def start(self):
        self.scheduler.add_job(
            self.scrape_and_send_deals,
            trigger=IntervalTrigger(minutes=config.SCRAPE_INTERVAL),
            id="deal_scraper",
            name="Scrape and send deals",
            replace_existing=True,
        )

        self.scheduler.start()
        print(f"Scheduler started - scraping every {config.SCRAPE_INTERVAL} minutes")

    def stop(self):
        self.scheduler.shutdown()
        print("Scheduler stopped")
