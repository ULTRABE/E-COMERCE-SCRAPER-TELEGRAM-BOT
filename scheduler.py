from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot
from telegram.constants import ParseMode
from typing import List
import asyncio
import config
from scrapers import ALL_SCRAPERS
from deal_processor import DealProcessor
from message_formatter import MessageFormatter
from keyword_manager import KeywordManager
from database import Database

class DealScheduler:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.deal_processor = DealProcessor(db)
        self.keyword_manager = KeywordManager(db)
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
                    print(f"Scraping {scraper.site_name}...")
                    deals = scraper.scrape()
                    all_deals.extend(deals)
                    print(f"Found {len(deals)} deals from {scraper.site_name}")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"Error in scraper {scraper_class.__name__}: {e}")
                    continue
            
            print(f"Total deals scraped: {len(all_deals)}")
            
            processed_deals = self.deal_processor.process_deals(all_deals)
            print(f"Unique deals after processing: {len(processed_deals)}")
            
            if not processed_deals:
                print("No new deals to send")
                self.is_running = False
                return
            
            authorized_chats = self.db.get_authorized_chats()
            print(f"Sending to {len(authorized_chats)} authorized chats")
            
            for chat_id in authorized_chats:
                try:
                    sent_count = 0
                    for deal in processed_deals:
                        if self.keyword_manager.matches_keywords(chat_id, deal['product_name']):
                            message = MessageFormatter.format_deal(deal)
                            
                            await self.bot.send_message(
                                chat_id=chat_id,
                                text=message,
                                parse_mode=ParseMode.MARKDOWN,
                                disable_web_page_preview=False
                            )
                            sent_count += 1
                            self.db.increment_stat('deals_sent')
                            await asyncio.sleep(1)
                    
                    print(f"Sent {sent_count} deals to chat {chat_id}")
                except Exception as e:
                    print(f"Error sending to chat {chat_id}: {e}")
                    continue
            
            self.db.cleanup_old_deals(7)
            
        except Exception as e:
            print(f"Error in scrape_and_send_deals: {e}")
        finally:
            self.is_running = False
            print("Scraping complete")
    
    def start(self):
        self.scheduler.add_job(
            self.scrape_and_send_deals,
            trigger=IntervalTrigger(minutes=config.SCRAPE_INTERVAL),
            id='deal_scraper',
            name='Scrape and send deals',
            replace_existing=True
        )
        
        self.scheduler.start()
        print(f"Scheduler started - scraping every {config.SCRAPE_INTERVAL} minutes")
    
    def stop(self):
        self.scheduler.shutdown()
        print("Scheduler stopped")
