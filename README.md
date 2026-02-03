# Indian E-commerce Deal Bot 🛍️

A fully automated Telegram bot that scrapes deals from 12+ major Indian e-commerce sites and sends them to authorized groups/channels. Features owner-only authorization, keyword filtering, premium emoji support, welcome messages, and automatic deal updates every 20 minutes.

## Features

- 🔐 **Owner-Only Authorization**: Bot only works in groups after owner authorization
- 🤖 **Auto-Scraping**: Automatically scrapes deals every 20 minutes
- 🎯 **Keyword Filtering**: Filter deals by keywords per group
- 🚫 **Duplicate Prevention**: Smart hash-based duplicate detection
- 💎 **High-Quality Deals**: Only sends deals with 30%+ discount
- 📊 **Statistics Tracking**: Monitor bot performance
- 🛒 **12+ E-commerce Sites**: Amazon, Flipkart, Myntra, AJIO, Snapdeal, ShopClues, Croma, Vijay Sales, Meesho, Tata CLIQ, Nykaa, Lenskart
- 👋 **Welcome Messages**: Automatic welcome messages for new members with customizable templates
- ✨ **Premium Emoji Support**: Easy-to-customize emoji templates for premium emoji packs

## Setup Instructions

### 1. Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the `BOT_TOKEN` provided

### 2. Get Your Telegram ID

1. Search for `@userinfobot` on Telegram
2. Send `/start` to get your numeric user ID
3. Copy your `OWNER_ID` (e.g., 123456789)

### 3. Environment Variables

Create a `.env` file or set these environment variables:

```env
BOT_TOKEN=your_bot_token_here
OWNER_ID=your_numeric_telegram_id
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Bot

```bash
python bot.py
```

## Deployment on Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables:
   - `BOT_TOKEN`: Your bot token from BotFather
   - `OWNER_ID`: Your Telegram numeric ID
4. Railway will automatically detect the `Procfile` and deploy

## Usage

### Authorization Flow

1. Add bot to your group/channel
2. Bot sends: "🔒 This bot is not authorized in this group. Ask the bot owner to send /auth here."
3. Owner sends `/auth` command
4. Bot verifies owner and authorizes the group
5. Bot starts sending deals automatically

### Commands

- `/start` - Bot information and welcome message
- `/help` - Detailed help and usage instructions
- `/auth` - **(Owner Only)** Authorize bot in current group/channel
- `/only <keywords>` - Filter deals by keywords (e.g., `/only shoes iPhone`)
- `/only clear` - Remove all keyword filters
- `/stats` - Show bot statistics
- `/welcome <message>` - **(Owner Only)** Set custom welcome message with placeholders
- `/welcome default` - Reset to default welcome message

### Examples

**Filter by keywords:**
```
/only smartphone laptop
```
Bot will only send deals containing "smartphone" or "laptop"

**Clear filters:**
```
/only clear
```
Bot will send all deals

**Check statistics:**
```
/stats
```
Shows total deals sent, authorized chats, etc.

## How It Works

### 1. Scraping

- Runs every 20 minutes using APScheduler
- Scrapes 8+ major Indian e-commerce sites
- Extracts: product name, deal price, original price, discount, URL
- Only selects deals with 30%+ discount

### 2. Processing

- Generates unique hash for each deal (site + product + price)
- Filters out duplicate deals
- Ranks deals by discount percentage and price
- Stores deal history in SQLite database

### 3. Sending

- Only sends to authorized chats
- Applies per-group keyword filters
- Beautiful monospace formatting with quotes
- Rate-limited to prevent spam

### 4. Message Format

**Deal Message (with premium emoji support):**
```
🔥 HOT DEAL 🔥
━━━━━━━━━━━━━━━━━━
📦 Product Name
💰 Deal: ₹2,999
💵 MRP: ₹5,999
📉 Save: ₹3,000 (50% OFF)
🔗 https://example.com/deal
━━━━━━━━━━━━━━━━━━
🛒 Buy Now! 🚀
```

**Welcome Message:**
```
🎉 WELCOME! 🎉
━━━━━━━━━━━━━━━━━━
Hello @username! 👋
Welcome to Group Name! 🎊

🔥 Get best deals from:
• Amazon, Flipkart, Myntra, AJIO
• Snapdeal, ShopClues, Croma, Vijay Sales
• Meesho, Tata CLIQ, Nykaa, Lenskart

Enjoy saving money! 💰✨
━━━━━━━━━━━━━━━━━━
```

## Technical Architecture

### Files Structure

```
.
├── bot.py                    # Main bot with command handlers
├── config.py                 # Configuration and environment variables
├── database.py               # SQLite database operations
├── auth_manager.py           # Authorization logic
├── keyword_manager.py        # Keyword filtering
├── welcome_manager.py        # Welcome message handling
├── message_formatter.py      # Deal message formatting with premium emoji support
├── deal_processor.py         # Deal processing and ranking
├── scheduler.py              # APScheduler integration
├── requirements.txt          # Python dependencies
├── Procfile                  # Railway deployment
├── .gitignore               # Git ignore rules
└── scrapers/                # Scraper modules
    ├── __init__.py
    ├── base_scraper.py
    ├── amazon_scraper.py
    ├── flipkart_scraper.py
    ├── myntra_scraper.py
    ├── ajio_scraper.py
    ├── snapdeal_scraper.py
    ├── shopclues_scraper.py
    ├── croma_scraper.py
    ├── vijaysales_scraper.py
    ├── meesho_scraper.py
    ├── tata_cliq_scraper.py
    ├── nykaa_scraper.py
    └── lenskart_scraper.py
```

### Database Schema

**authorized_chats**: Stores authorized groups/channels
- chat_id (PRIMARY KEY)
- chat_title
- authorized_at
- authorized_by

**keyword_filters**: Stores per-group keyword filters
- chat_id (PRIMARY KEY)
- keywords (JSON)

**deal_history**: Prevents duplicate deals
- id (PRIMARY KEY)
- deal_hash (UNIQUE)
- product_name
- site
- posted_at

**statistics**: Tracks bot metrics
- key (PRIMARY KEY)
- value

## Configuration

Edit `config.py` to customize:

```python
SCRAPE_INTERVAL = 20  # Minutes between scrapes
DATABASE_PATH = "bot_data.db"  # SQLite database path
USER_AGENT = "..."  # User agent for scraping
```

## Error Handling

- Scraper failures don't crash the bot
- Each scraper runs independently
- Database connection errors are handled gracefully
- Rate limiting prevents API throttling
- Old deals are cleaned up automatically (7 days)

## Security

- Only owner can authorize bot (verified by OWNER_ID)
- Bot only works in authorized chats
- No user data is collected
- All data stored locally in SQLite

## Troubleshooting

**Bot not responding:**
- Check if BOT_TOKEN is correct
- Verify bot is running (`python bot.py`)
- Check logs for errors

**Not receiving deals:**
- Ensure chat is authorized (`/auth`)
- Check keyword filters (`/only`)
- Verify scraping interval in logs

**Duplicate deals:**
- Deals are deduplicated by hash
- Old deals cleaned up after 7 days
- Check database integrity

## Contributing

Feel free to add more scrapers or improve existing ones! Follow the `BaseScraper` pattern in `scrapers/base_scraper.py`.

## License

MIT License - Feel free to use and modify!

## Premium Emoji Customization Guide

The bot uses standard Unicode emojis by default, but you can easily replace them with premium emojis from your packs after deployment.

### How to Customize Emojis

1. **Edit `message_formatter.py`**: Replace the emoji constants at the top of the file
2. **Available emoji categories**:
   - `EMOJI_DEAL` - For deal announcements (AnimatedAsianEmoji pack)
   - `EMOJI_MONEY`, `EMOJI_SPARKLE`, `EMOJI_PARTY` - For special messages (RestrictedEmoji pack)
   - `EMOJI_CART`, `EMOJI_LINK`, `EMOJI_ROCKET` - For action buttons (RetroFontEmoji pack)
   - `EMOJI_TAG`, `EMOJI_FIRE`, `EMOJI_DISCOUNT` - For deal details (NewsEmoji pack)

3. **Example customization**:
```python
# Replace standard emojis with premium ones
EMOJI_DEAL = "🔥"  # Replace with your premium fire emoji
EMOJI_MONEY = "💰"  # Replace with your premium money emoji
EMOJI_PARTY = "🎉"  # Replace with your premium party emoji
```

4. **Welcome message emojis**: Edit the `format_welcome_message` method in `message_formatter.py`

### Premium Emoji Packs Recommendation

- **AnimatedAsianEmoji** - Best for deal announcements
- **RestrictedEmoji** - For special messages and highlights
- **RetroFontEmoji** - For welcome messages and buttons
- **NewsEmoji** - For deal updates and statistics

### Easy Customization Tips

- All emoji templates are clearly marked in the code
- Use the same emoji style throughout for consistency
- Test emojis in a private chat before deploying
- Backup original emojis before making changes

## Support

For issues or questions, contact the bot owner through Telegram.

---

Made with ❤️ for Indian shoppers
