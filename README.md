# Telegram Proxy Checker Bot

Async production-focused proxy checker bot (aiogram 3 + aiohttp + sqlite).

## Setup
1. `cp .env.example .env`
2. Fill `.env` with your real values (keep it private).
3. `pip install -r requirements.txt`
4. `./start.sh`

## Security
- `.env` is ignored by git.
- Owner-only access is enforced by `OWNER_ID`.
- TXT-only uploads and file size limits are enforced.

## Deploy (VPS)
- Python 3.12+
- Run behind systemd or Docker
- Persist `data/` directory for 24-hour downloads

## Docker
`docker build -t proxy-bot .`
`docker run --env-file .env -v $(pwd)/data:/app/data proxy-bot`
