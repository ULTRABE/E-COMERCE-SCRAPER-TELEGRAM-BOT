import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
import config

class Database:
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_chats (
                chat_id INTEGER PRIMARY KEY,
                chat_title TEXT,
                authorized_at TEXT,
                authorized_by INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword_filters (
                chat_id INTEGER PRIMARY KEY,
                keywords TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_hash TEXT UNIQUE,
                product_name TEXT,
                site TEXT,
                posted_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                key TEXT PRIMARY KEY,
                value INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS welcome_messages (
                chat_id INTEGER PRIMARY KEY,
                message TEXT
            )
        ''')

        conn.commit()
        conn.close()
    
    def authorize_chat(self, chat_id: int, chat_title: str, authorized_by: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO authorized_chats VALUES (?, ?, ?, ?)',
            (chat_id, chat_title, datetime.now().isoformat(), authorized_by)
        )
        conn.commit()
        conn.close()
    
    def is_chat_authorized(self, chat_id: int) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM authorized_chats WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_authorized_chats(self) -> List[int]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM authorized_chats')
        chats = [row[0] for row in cursor.fetchall()]
        conn.close()
        return chats
    
    def set_keywords(self, chat_id: int, keywords: List[str]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO keyword_filters VALUES (?, ?)',
            (chat_id, json.dumps(keywords))
        )
        conn.commit()
        conn.close()
    
    def get_keywords(self, chat_id: int) -> Optional[List[str]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT keywords FROM keyword_filters WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return json.loads(result[0])
        return None
    
    def clear_keywords(self, chat_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM keyword_filters WHERE chat_id = ?', (chat_id,))
        conn.commit()
        conn.close()
    
    def set_welcome_message(self, chat_id: int, message: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO welcome_messages VALUES (?, ?)',
            (chat_id, message)
        )
        conn.commit()
        conn.close()
    
    def get_welcome_message(self, chat_id: int) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT message FROM welcome_messages WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def clear_welcome_message(self, chat_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM welcome_messages WHERE chat_id = ?', (chat_id,))
        conn.commit()
        conn.close()
    
    def is_duplicate_deal(self, deal_hash: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT deal_hash FROM deal_history WHERE deal_hash = ?', (deal_hash,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def add_deal(self, deal_hash: str, product_name: str, site: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO deal_history (deal_hash, product_name, site, posted_at) VALUES (?, ?, ?, ?)',
                (deal_hash, product_name, site, datetime.now().isoformat())
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
    
    def increment_stat(self, key: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO statistics (key, value) VALUES (?, 1) ON CONFLICT(key) DO UPDATE SET value = value + 1',
            (key,)
        )
        conn.commit()
        conn.close()
    
    def get_stat(self, key: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM statistics WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def cleanup_old_deals(self, days: int = 7):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cutoff = datetime.now().timestamp() - (days * 86400)
        cursor.execute(
            'DELETE FROM deal_history WHERE datetime(posted_at) < datetime(?, "unixepoch")',
            (cutoff,)
        )
        conn.commit()
        conn.close()
