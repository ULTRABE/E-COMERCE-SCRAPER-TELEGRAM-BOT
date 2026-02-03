# Quick Start Guide

## Step 1: Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "Indian Deals Bot")
4. Choose a username (must end with 'bot', e.g., "indian_deals_bot")
5. Copy the **BOT_TOKEN** that BotFather provides

Example token: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

## Step 2: Get Your Telegram ID

1. Search for **@userinfobot** on Telegram
2. Send `/start` to the bot
3. Copy your **numeric ID** (e.g., 123456789)

This is your **OWNER_ID**.

## Step 3: Set Environment Variables

### Option A: Using .env file (Local Development)

Create a `.env` file:

```bash
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OWNER_ID=123456789
```

### Option B: Export in Terminal

```bash
export BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export OWNER_ID="123456789"
```

### Option C: Railway Deployment

In your Railway project:
1. Go to Variables tab
2. Add `BOT_TOKEN` = your token
3. Add `OWNER_ID` = your ID

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Run the Bot

```bash
python bot.py
```

You should see:
```
Starting Indian E-commerce Deal Bot...
Bot started successfully!
Scraping interval: 20 minutes
Owner ID: 123456789
```

## Step 6: Authorize Your Group/Channel

### For Private Groups:
1. Create a Telegram group
2. Add your bot to the group (make it admin if it's a channel)
3. Bot will send: "🔒 This bot is not authorized..."
4. **You (the owner)** send `/auth` in the group
5. Bot responds: "✅ Bot authorized! I'll start sending deals now."

### For Channels:
1. Create a Telegram channel
2. Add your bot as an administrator
3. In the channel's "Discussion Group" or send a message mentioning the bot
4. Send `/auth` command
5. Bot is now authorized

## Step 7: Configure Filters (Optional)

Filter deals by keywords:

```
/only smartphone laptop headphones
```

Now you'll only receive deals matching those keywords.

Clear filters:

```
/only clear
```

## Common Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show welcome message | `/start` |
| `/help` | Get help | `/help` |
| `/auth` | Authorize bot (owner only) | `/auth` |
| `/only <keywords>` | Filter by keywords | `/only shoes bags` |
| `/only clear` | Remove filters | `/only clear` |
| `/stats` | Show statistics | `/stats` |

## How Deals Are Sent

### Message Format:

```
🎯 Samsung Galaxy M32 (128GB, Black)

💰 Deal Price: ₹12,999
💸 Real Price: ₹18,999
🔥 Discount: 31% OFF

🛒 Site: Amazon India

🔗 Buy Now
```

### Frequency:
- Bot scrapes every **20 minutes**
- Only sends **new deals** (no duplicates)
- Minimum **30% discount** filter

### Sites Covered:
1. Amazon India
2. Flipkart
3. Myntra
4. AJIO
5. Snapdeal
6. ShopClues
7. Croma
8. Vijay Sales

## Troubleshooting

### Bot Not Starting

**Error:** "BOT_TOKEN not found"
- Solution: Make sure you set the BOT_TOKEN environment variable

**Error:** "OWNER_ID not found"
- Solution: Set your OWNER_ID environment variable

### Bot Not Responding

1. Check if bot is running: Look for "Bot started successfully!" message
2. Verify bot token is correct
3. Make sure bot is not blocked by Telegram

### Not Receiving Deals

1. **Check authorization:** Send `/auth` in the group (as owner)
2. **Check filters:** Send `/only` to see current filters
3. **Wait for scraping:** Deals are sent every 20 minutes
4. **Check logs:** Look for "Scraping complete" messages

### Authorization Failed

**Error:** "Only the bot owner can authorize"
- Solution: Make sure you're using the Telegram account with the OWNER_ID
- Verify OWNER_ID matches your Telegram numeric ID from @userinfobot

### No Deals Being Found

This is normal! Real deals depend on:
- Current promotions on e-commerce sites
- Site structure changes (scrapers may need updates)
- Network connectivity

## Advanced Configuration

### Change Scraping Interval

Edit `config.py`:

```python
SCRAPE_INTERVAL = 30  # Change from 20 to 30 minutes
```

### Add More Scrapers

Create a new scraper in `scrapers/` directory following the `BaseScraper` pattern.

### Database Location

Change in `config.py`:

```python
DATABASE_PATH = "/path/to/your/bot_data.db"
```

## Deployment Options

### 1. Railway (Recommended)

1. Fork/push code to GitHub
2. Create Railway account
3. Create new project from GitHub repo
4. Add environment variables
5. Deploy automatically

### 2. Heroku

1. Create `Procfile` (already included)
2. Push to Heroku Git
3. Set config vars for BOT_TOKEN and OWNER_ID
4. Scale worker dyno: `heroku ps:scale worker=1`

### 3. VPS (DigitalOcean, AWS, etc.)

```bash
git clone <your-repo>
cd <repo-name>
pip install -r requirements.txt
export BOT_TOKEN="your_token"
export OWNER_ID="your_id"
nohup python bot.py > bot.log 2>&1 &
```

### 4. Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

Build and run:
```bash
docker build -t deals-bot .
docker run -e BOT_TOKEN="..." -e OWNER_ID="..." deals-bot
```

## Security Notes

- **Never commit** `.env` file to Git (already in .gitignore)
- **Keep your BOT_TOKEN secret** - anyone with it can control your bot
- **Verify OWNER_ID** - only this user can authorize groups
- **Database backup** - periodically backup `bot_data.db`

## Monitoring

Check bot status:
- Use `/stats` command in authorized groups
- Check logs for "Scraping complete" messages
- Monitor database file size
- Watch for error messages in logs

## Support

If you encounter issues:
1. Check this guide
2. Review README.md
3. Check bot logs for error messages
4. Verify environment variables are set correctly

---

Happy deal hunting! 🎉
