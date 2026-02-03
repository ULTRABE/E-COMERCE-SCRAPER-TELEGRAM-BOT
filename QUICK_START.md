# 🚀 Quick Start - Indian E-commerce Deal Bot

Get your deal bot running in 5 minutes!

## Prerequisites

- Python 3.11+
- Telegram account

## 1. Get Bot Token (2 minutes)

1. Open Telegram, search **@BotFather**
2. Send `/newbot`
3. Name your bot: `My Deals Bot`
4. Username: `my_deals_bot` (must end with 'bot')
5. **Copy the token** (looks like: `1234567890:ABCdef...`)

## 2. Get Your Telegram ID (1 minute)

1. Search **@userinfobot** on Telegram
2. Send `/start`
3. **Copy your ID** (numbers like: `123456789`)

## 3. Setup & Run (2 minutes)

```bash
# Clone/download the code
cd path/to/indian-deal-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN="your_bot_token_here"
export OWNER_ID="your_numeric_id_here"

# Run the bot
python bot.py
```

You should see:
```
Starting Indian E-commerce Deal Bot...
Bot started successfully!
Scraping interval: 20 minutes
```

## 4. Authorize a Group (30 seconds)

1. Create a Telegram group
2. Add your bot to the group
3. Bot says: "🔒 This bot is not authorized..."
4. **You** send: `/auth`
5. Bot says: "✅ Bot authorized!"

## 5. Done! 🎉

Your bot will now:
- Auto-scrape 8+ e-commerce sites every 20 minutes
- Send hot deals (30%+ discount) to your group
- Filter duplicates automatically

## Optional: Add Filters

```
/only smartphone laptop         # Only get tech deals
/only shoes bags                # Only get fashion deals  
/only clear                     # Get all deals
```

## Deploy to Railway (Cloud)

1. Push code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Create new project from your repo
4. Add variables:
   - `BOT_TOKEN` = your token
   - `OWNER_ID` = your ID
5. Deploy!

Your bot runs 24/7 in the cloud!

## Commands

| Command | What it does |
|---------|-------------|
| `/start` | Show info |
| `/help` | Get help |
| `/auth` | Authorize group (owner only) |
| `/only <keywords>` | Filter deals |
| `/stats` | Show statistics |

## Need Help?

- **README.md** - Full documentation
- **USAGE.md** - Detailed guide
- **PROJECT_SUMMARY.md** - Technical overview

---

**That's it! Your deal bot is ready!** 🛍️
