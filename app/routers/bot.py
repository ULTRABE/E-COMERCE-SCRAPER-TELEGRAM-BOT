import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.utils.proxy_parser import parse_many
from app.config import settings

router = Router()
sessions: dict[int, dict] = {}

def _owner_only(uid: int) -> bool:
    return uid == settings.owner_id

def kb_main():
    b = InlineKeyboardBuilder(); b.button(text="📡 Send Proxies", callback_data="send")
    return b.as_markup()

def kb_collect():
    b = InlineKeyboardBuilder()
    b.button(text="➕ Add More", callback_data="send")
    b.button(text="✅ Start Checking", callback_data="start")
    b.button(text="❌ Cancel", callback_data="cancel")
    b.adjust(1)
    return b.as_markup()

@router.message(F.text == "/start")
async def start(m: Message):
    if not _owner_only(m.from_user.id):
        await m.answer("⛔ Access denied.")
        return
    await m.answer("✨ <b>Premium Proxy Checker</b>\n🚀 High-speed async validation.", reply_markup=kb_main())

@router.callback_query(F.data == "send")
async def send_mode(c: CallbackQuery):
    if not _owner_only(c.from_user.id):
        await c.answer("Access denied", show_alert=True)
        return
    sessions.setdefault(c.from_user.id, {"collect": True, "lines": [], "last": 0.0})["collect"] = True
    await c.message.edit_text("📥 Send plain text proxies or TXT files.\nYou can upload multiple times.", reply_markup=kb_collect())
    await c.answer()

@router.message(F.document | F.text)
async def collect(m: Message):
    if not _owner_only(m.from_user.id):
        return
    s = sessions.get(m.from_user.id)
    if not s or not s.get("collect"):
        return
    if time.time() - s.get("last", 0) < settings.user_cooldown_seconds:
        return
    s["last"] = time.time()

    if m.document:
        if not m.document.file_name.lower().endswith(".txt"):
            await m.answer("⚠️ Only TXT files are accepted.")
            return
        if m.document.file_size and m.document.file_size > 15 * 1024 * 1024:
            await m.answer("⚠️ File too large (max 15MB).")
            return
        f = await m.bot.get_file(m.document.file_id)
        data = await m.bot.download_file(f.file_path)
        s["lines"].extend(data.read().decode(errors="ignore").splitlines())
    elif m.text:
        s["lines"].extend(m.text.splitlines())

    parsed = parse_many(s["lines"])
    s["parsed"] = list(parsed)
    await m.answer(f"📊 Collected: <b>{len(parsed):,}</b> unique proxies", reply_markup=kb_collect())
