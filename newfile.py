import asyncio
import os
from datetime import datetime
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageNotModified, FloodWait, PeerIdInvalid, InternalServerError

# --- КОНФІГУРАЦІЯ ---
API_ID = 33949991
API_HASH = "1b75c81111e993ec9ecd7035e7f572a8"
BOT_TOKEN = "8521570475:AAFt3MbZIoU_qvwFRaQnRbcuCUs7TobXgXU"

bot = Client("manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("my_account", api_id=API_ID, api_hash=API_HASH, device_model="Samsung S24 Ultra")

state = {
    "is_active": False, 
    "reply_text": "Го я пиши в лс [Если сделка руб не смогу]!",
    "counter": 0,
    "last_date": datetime.now().date(),
    "my_id": None,
    "blocked_users": set()  # Список ID заблокованих юзерів
}

# --- МЕНЮ ---
def get_status_text():
    if datetime.now().date() > state["last_date"]:
        state["counter"] = 0
        state["last_date"] = datetime.now().date()

    e = ["5357069174512303778", "5258152182150077732" if state["is_active"] else "5258011861273551368", "5257969839313526622", "5431343731238258313", "5210943560647115841"]
    st = "<b>АКТИВНИЙ</b>" if state["is_active"] else "<i>СПИТЬ</i>"
    
    return (
        f"<tg-emoji emoji-id='{e[0]}'>✔️</tg-emoji> <b>СТАТУС:</b> {st} <tg-emoji emoji-id='{e[1]}'>⚡️</tg-emoji>\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"<tg-emoji emoji-id='{e[3]}'>📊</tg-emoji> <b>Угод сьогодні:</b> <code>{state['counter']}</code>\n"
        f"<tg-emoji emoji-id='{e[4]}'>🚫</tg-emoji> <b>В блоці:</b> <code>{len(state['blocked_users'])}</code>\n"
        f"<tg-emoji emoji-id='{e[2]}'>📁</tg-emoji> <b>Текст:</b> {state['reply_text']}\n\n"
        f"<b>Команди:</b>\n"
        f"• <code>.блок @юзер</code> | <code>.разблок @юзер</code>\n"
        f"• <code>.сделка</code> | <code>.сделка старт/стоп</code>"
    )

# --- ОБРОБКА БОТА (START) ---
@bot.on_message(filters.command("start") & filters.private)
async def start_bot(c, m):
    await m.reply(get_status_text(), parse_mode=ParseMode.HTML)

# --- ОБРОБКА ЮЗЕРБОТА (КЕРУВАННЯ) ---
@user.on_message(filters.me & filters.text)
async def commands(c, m):
    global state
    txt = m.text.lower()
    
    # Команда БЛОКУВАННЯ
    if txt.startswith(".блок"):
        target = None
        if m.reply_to_message:
            target = m.reply_to_message.from_user
        elif len(m.text.split()) > 1:
            try: target = await c.get_users(m.text.split()[1])
            except: pass
        
        if target:
            state["blocked_users"].add(target.id)
            await m.edit_text(f"🚫 <b>Користувач {target.first_name} доданий в ігнор.</b>")
        else:
            await m.edit_text("❌ <b>Не вдалося знайти користувача.</b>")

    # Команда РОЗБЛОКУВАННЯ
    elif txt.startswith(".разблок"):
        target = None
        if m.reply_to_message:
            target = m.reply_to_message.from_user
        elif len(m.text.split()) > 1:
            try: target = await c.get_users(m.text.split()[1])
            except: pass
        
        if target and target.id in state["blocked_users"]:
            state["blocked_users"].remove(target.id)
            await m.edit_text(f"✅ <b>Користувач {target.first_name} видалений з ігнору.</b>")
        else:
            await m.edit_text("❌ <b>Користувача немає в списку.</b>")

    elif txt == ".сделка":
        await m.edit_text(get_status_text(), parse_mode=ParseMode.HTML)

    elif ".сделка старт" in txt:
        state["is_active"] = True
        parts = m.text.split(".сделка старт")
        if len(parts) > 1 and parts[1].strip(): state["reply_text"] = parts[1].strip()
        await m.edit_text(get_status_text(), parse_mode=ParseMode.HTML)

    elif ".сделка стоп" in txt:
        state["is_active"] = False
        await m.edit_text(get_status_text(), parse_mode=ParseMode.HTML)

# --- ЛОВЕЦЬ ---
@user.on_message(filters.text & ~filters.me & ~filters.bot)
async def hunt(c, m):
    if not state["is_active"] or not m.from_user:
        return

    # ПЕРЕВІРКА НА БЛОК
    if m.from_user.id in state["blocked_users"]:
        return

    msg_text = (m.text or "").lower()
    if "#сделка" in msg_text:
        if any(word in msg_text for word in ["руб", "рублей", "рубли", "₽"]):
            return

        try:
            await m.reply(state["reply_text"])
            state["counter"] += 1
            if state["my_id"]:
                try:
                    await bot.send_message(
                        state["my_id"],
                        f"🚀 <b>НОВА УГОДА!</b>\n📍 <b>Чат:</b> {m.chat.title or 'ЛС'}\n👤 <b>Юзер:</b> {m.from_user.first_name}\n🔗 <a href='{m.link}'>ПЕРЕЙТИ</a>",
                        parse_mode=ParseMode.HTML, disable_web_page_preview=True
                    )
                except: pass
        except Exception: pass

# --- ЗАПУСК ---
async def start_all():
    await bot.start()
    await user.start()
    me = await user.get_me()
    state["my_id"] = me.id
    print(f"✅ Система онлайн! ID: {me.id}")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_all())
