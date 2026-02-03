# Deployment Guide - Telegram Deal Bot

## Quick Start

### 1. Environment Setup
Create a `.env` file in the project root:
```bash
BOT_TOKEN=your_bot_token_from_@BotFather
OWNER_ID=your_telegram_user_id_from_@userinfobot
CHANNEL_URL=https://t.me/yourchannel
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Bot
```bash
python bot.py
```

## Configuration

### Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the token provided
4. Paste it as `BOT_TOKEN` in `.env`

### Owner ID
1. Open Telegram and search for `@userinfobot`
2. Send `/start`
3. Copy your user ID
4. Paste it as `OWNER_ID` in `.env`

### Channel URL
1. Create a Telegram channel
2. Get the invite link or public link
3. Paste it as `CHANNEL_URL` in `.env`

## Features

### Scraping Interval
- **Current**: 3 minutes
- **Location**: `config.py` → `SCRAPE_INTERVAL`
- To change: Edit the value in `config.py`

### Proxies
- **Count**: 50 proxies configured
- **Distribution**: 5 proxies per scraper
- **Location**: `proxy_manager.py`
- **Rotation**: Automatic round-robin
- **Format**: `username:password:host:port`

### Owner Commands
Only the user with OWNER_ID can use:
- `/auth` - Authorize current group/channel
- `/addchannel <chat_id>` - Authorize by chat ID
- `/only <keywords>` - Set keyword filters
- `/stats` - View statistics
- `/welcome <message>` - Set custom welcome

### Public Commands
Anyone can use:
- `/start` - Show welcome message
- `/help` - Show help

Non-owners will see a "🚀 JOIN CHANNEL" button.

## Adding the Bot to Groups/Channels

### Method 1: Direct Authorization (Groups)
1. Add the bot to your group
2. As owner, send `/auth` in the group
3. Bot will confirm authorization

### Method 2: Channel Authorization (Channels)
1. Add the bot to your channel as admin
2. Get the channel ID (use @username_to_id_bot or similar)
3. As owner, send `/addchannel -1001234567890` (replace with your channel ID)
4. Bot will confirm authorization

## Monitoring

### Statistics
Send `/stats` (as owner) to see:
- Total deals sent
- Authorized chats
- Scrape interval
- Sites monitored

### Logs
The bot prints to console:
- Scraping status
- Deals found per site
- Sending status
- Errors and warnings

## Troubleshooting

### Bot Not Responding
- Check BOT_TOKEN is correct
- Ensure bot is running
- Check internet connection

### No Deals Being Sent
- Verify scraping is running (check console)
- Check if chat is authorized
- Verify keyword filters aren't too restrictive

### Proxy Errors
- Proxies may fail occasionally
- Bot automatically retries with different proxies
- Check console for specific proxy errors

### Image Sending Fails
- Bot automatically falls back to text-only
- Some products may not have images
- Check console for specific errors

## Production Deployment

### Using systemd (Linux)
Create `/etc/systemd/system/dealbot.service`:
```ini
[Unit]
Description=Telegram Deal Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 /path/to/bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable dealbot
sudo systemctl start dealbot
sudo systemctl status dealbot
```

### Using Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

Build and run:
```bash
docker build -t dealbot .
docker run -d --name dealbot --env-file .env dealbot
```

### Using Heroku
Create `Procfile` (already exists):
```
worker: python bot.py
```

Deploy:
```bash
heroku create your-app-name
heroku config:set BOT_TOKEN=your_token
heroku config:set OWNER_ID=your_id
heroku config:set CHANNEL_URL=your_url
git push heroku main
heroku ps:scale worker=1
```

## Maintenance

### Updating Proxies
Edit `proxy_manager.py` → `PROXIES` list

### Adding New Scrapers
1. Create new file in `scrapers/` directory
2. Extend `BaseScraper` class
3. Implement `scrape()` method
4. Add image extraction with `self.extract_image_url()`
5. Add to `scrapers/__init__.py` → `ALL_SCRAPERS`

### Changing Scraping Interval
Edit `config.py` → `SCRAPE_INTERVAL` (in minutes)

### Customizing Messages
Edit `message_formatter.py` for deal formatting
Edit emojis in `MessageFormatter` class

## Security

### Environment Variables
- Never commit `.env` file
- Keep BOT_TOKEN secret
- Don't share OWNER_ID publicly

### Owner Restrictions
- Only OWNER_ID can authorize chats
- Only OWNER_ID can manage filters
- Only OWNER_ID can view stats

### Database
- `bot_data.db` stores authorized chats, keywords, stats
- Backup regularly if running in production

## Support

For issues or questions:
1. Check console logs
2. Verify configuration
3. Test with `/start` command
4. Review IMPLEMENTATION_SUMMARY.md

## Version Info

- **Python**: 3.11+
- **Scraping Interval**: 3 minutes
- **Proxies**: 50 configured
- **Scrapers**: 12 sites
- **Environment Variables**: 3 required
