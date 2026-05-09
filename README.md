# Telegram Proxy Checker Bot (Async, Python 3.12+)

Production-oriented aiogram 3 bot for collecting huge proxy lists, validating connectivity, checking risk through proxycheck.io, and exporting clean TXT files by category.

## Features
- Async architecture (aiogram + aiohttp + asyncio)
- Batch collection mode (multiple texts/files before checking)
- Proxy parsing/normalization + de-duplication
- High-concurrency checking with progress updates
- Fraud filtering (risk < 20)
- 24-hour downloadable storage via SQLite
- Docker + VPS ready

## Run
1. Copy `.env.example` to `.env` and fill values.
2. Install dependencies: `pip install -r requirements.txt`
3. Start: `./start.sh`

## Docker
`docker build -t proxy-bot . && docker run --env-file .env proxy-bot`

## VPS Deployment
- Use Ubuntu 22.04+, Python 3.12
- Create venv and install requirements
- Run with systemd (recommended)
- Keep `data/` persistent for 24h result storage

## Notes
- Supports HTTP/HTTPS directly; SOCKS may depend on runtime/network and endpoint behavior.
- Add admin/user plan modules later using modular `routers/services/utils/db` layout.
