import asyncio
import logging
import uuid
from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery, BufferedInputFile

from app.config import settings
from app.routers.bot import router, sessions
from app.services.proxy_checker import ProxyChecker
from app.db.sqlite import DB
from app.middlewares.auth import OwnerOnlyMiddleware

logging.basicConfig(level=logging.INFO)

async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required")
    db = DB(settings.db_path)
    await db.init()
    bot = Bot(settings.bot_token, parse_mode="HTML")
    dp = Dispatcher()
    dp.message.middleware(OwnerOnlyMiddleware())
    dp.callback_query.middleware(OwnerOnlyMiddleware())
    dp.include_router(router)

    @dp.callback_query(F.data == "cancel")
    async def cancel(c: CallbackQuery):
        sessions.pop(c.from_user.id, None)
        await c.message.edit_text("❌ Cancelled.")
        await c.answer()

    @dp.callback_query(F.data == "start")
    async def run_check(c: CallbackQuery):
        s = sessions.get(c.from_user.id)
        if not s or not s.get("parsed"):
            await c.answer("No proxies collected", show_alert=True)
            return
        checker = ProxyChecker(settings.proxycheck_api_key, settings.max_concurrency, settings.connect_timeout, settings.total_timeout)
        msg = c.message

        async def progress(done, total, alive, filtered):
            bar = "━" * 14
            await msg.edit_text(f"{bar}\nChecked: {done:,}/{total:,}\nAlive: {alive:,}\nFiltered: {filtered:,}\n{bar}")

        res = await checker.check_batch(s["parsed"], progress)
        sid = str(uuid.uuid4())
        await db.save_results(c.from_user.id, sid, res)

        from aiogram.utils.keyboard import InlineKeyboardBuilder
        kb = InlineKeyboardBuilder()
        for cat, items in res.items():
            kb.button(text=f"📄 Download {cat} ({len(items)})", callback_data=f"dl:{sid}:{cat}")
        kb.adjust(1)
        await msg.edit_text("✅ Done. Download filtered proxies:", reply_markup=kb.as_markup())
        await c.answer()

    @dp.callback_query(F.data.startswith("dl:"))
    async def dl(c: CallbackQuery):
        _, sid, cat = c.data.split(":", 2)
        rows = await db.get_category(c.from_user.id, sid, cat, settings.result_ttl_hours)
        if not rows:
            await c.answer("Expired or empty", show_alert=True)
            return
        payload = ("\n".join(rows)).encode()
        file = BufferedInputFile(payload, filename=f"{cat.lower().replace('/', '_')}.txt")
        await c.message.answer_document(file)
        await c.answer("Sent")

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except Exception:
        pass
    asyncio.run(main())
