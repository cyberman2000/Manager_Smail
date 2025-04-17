import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler
)
import sqlite3
import requests
from functools import wraps
from cachetools import TTLCache
from datetime import timedelta

# تنظیمات اولیه
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات دیتابیس
DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///smart_bot_db.sqlite')

def get_db_connection():
    if DB_URL.startswith('postgres'):
        import psycopg2
        conn = psycopg2.connect(DB_URL, sslmode='require')
    else:
        conn = sqlite3.connect('smart_bot_db.sqlite')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if DB_URL.startswith('postgres'):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            is_whitelisted BOOLEAN DEFAULT FALSE,
            coin_balance INTEGER DEFAULT 0,
            region TEXT DEFAULT 'BR'
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS website_credentials (
            email TEXT PRIMARY KEY,
            api_key TEXT,
            auth_token TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount INTEGER,
            item_code TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        ''')
    else:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            is_whitelisted BOOLEAN DEFAULT FALSE,
            coin_balance INTEGER DEFAULT 0,
            region TEXT DEFAULT 'BR'
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS website_credentials (
            email TEXT PRIMARY KEY,
            api_key TEXT,
            auth_token TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            item_code TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id))
        ''')
    
    conn.commit()
    conn.close()

# بقیه کدها مانند قبل (کلاس SmartManagerBot و توابع کمکی)
# ... [کدهای قبلی را اینجا قرار دهید] ...

def start_webhook():
    """شروع ربات با وب هوک برای Render.com"""
    bot_token = os.environ.get('7132343540:AAEl20NBB6i4n8dGa4bzdWfBJmgMcXtIpCc')
    if not bot_token:
        raise ValueError("توکن ربات تنظیم نشده است!")
    
    port = int(os.environ.get('PORT', 5000))
    app_name = os.environ.get('RENDER_APP_NAME')
    
    if not app_name:
        raise ValueError("نام برنامه در Render تنظیم نشده است!")
    
    webhook_url = f'https://{app_name}.onrender.com/{bot_token}'
    
    bot = SmartManagerBot(bot_token)
    updater = bot.updater
    
    # تنظیم وب هوک
    updater.start_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=bot_token,
        webhook_url=webhook_url
    )
    
    logger.info(f"ربات شروع به کار کرد. وب هوک: {webhook_url}")
    updater.idle()

if __name__ == '__main__':
    init_db()
    if os.environ.get('RENDER'):
        start_webhook()
    else:
        # حالت توسعه محلی
        bot = SmartManagerBot(os.environ.get('7132343540:AAEl20NBB6i4n8dGa4bzdWfBJmgMcXtIpCc', '7132343540:AAEl20NBB6i4n8dGa4bzdWfBJmgMcXtIpCc'))
        bot.run()