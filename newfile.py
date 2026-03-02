import asyncio
import random
from datetime import datetime, time, timedelta
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction, ParseMode

# --- НАЛАШТУВАННЯ ---
API_ID = 33949991
API_HASH = "1b75c81111e993ec9ecd7035e7f572a8"
BOT_TOKEN = "8521570475:AAFt3MbZIoU_qvwFRaQnRbcuCUs7TobXgXU"

# ТВІЙ STRING SESSION (ВЖЕ ТУТ)
STRING_SESSION = "AgIGCScAKkLcFE9QvCZ7CJeqkoqFzSRvgBZ0htSUCEVvHcjApfAIbFXCnJ_DhhHKCfY57a0h4FmkmuVVfYBxgBveq-Xp6YwjJPjL0oPg5hhHnczcs8W33mFOxl8H8ZQIQwrflfgzO608ZpyC_LfUbh8msSOSpud_MkDME8Y2cdzKStlOIfgLboz-rYHr4zf5EsOSKvsUiwT21H-OoDS0YEMcH3xASjQIFLoz0P8vh7N6O6x6wpHJ8FAxdQ9bTakS-Lp4NHk9jLwCp9PWIl_-0zRttWVYpNC-kTG23_OvSEXKk4bHhb6Ofb2gUHLXniDYWybFqeZAGeCpNswFPkKXIDxdVOQmMAAAAABXsl0xAA"

TARGET_IDS = [839209146, 59991523, 2025257353]
REPLY_VARIANTS = ["Го", "я", "в лс", "Я проведу", "Го я", "Пиши"]
EMOJIS = ["✅", "🖐", "👍", "🔥", ""]

# Нічний режим (00:00 - 07:00)
NIGHT_START = time(0, 0)
NIGHT_END = time(7, 0)
COOLDOWN_MIN = 5

# Клієнти
bot = Client("manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("my_account", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

state = {"active": False, "total": 0, "my_id": None, "cooldowns": {}}

def get_main_menu():
    st = "🟢 АКТИВНИЙ" if state["active"] else "🔴 ВИМКНЕНИЙ"
    text = (f"<b>🚀 ULTRA CLOUD v4.0</b>\n"
            f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"<b>Статус:</b> {st}\n"
            f"<b>Успішно:</b> <code>{state['total']}</code>\n"
            f"<b>Цілей:</b> <code>{len(TARGET_IDS)}</code>")
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ УВІМКНУТИ", callback_data="p_on"),
        InlineKeyboardButton("❌ ВИМКНУТИ", callback_data="p_off")
    ]])
    return text, kb

@bot.on_callback_query()
async def cb(c, q):
    if q.data == "p_on": state["active"] = True
    elif q.data == "p_off": state["active"] = False
    t, k = get_main_menu()
    await q.edit_message_text(t, reply_markup=k)

@user.on_message(filters.me & filters.text)
async def user_cmds(c, m):
    if m.text.lower() == ".сделка старт":
        state["active"] = True
        await m.edit("🚀 <b>Запущено в хмарі</b>"); await asyncio.sleep(2); await m.delete()
    elif m.text.lower() == ".сделка стоп":
        state["active"] = False
        await m.edit("😴 <b>Зупинено</b>"); await asyncio.sleep(2); await m.delete()

@user.on_message(filters.text & ~filters.me & ~filters.bot)
async def hunter(c, m):
    if not state["active"] or not m.from_user or m.from_user.id not in TARGET_IDS: return
    now = datetime.now()
    if NIGHT_START <= now.time() <= NIGHT_END: return
    uid = m.from_user.id
    if uid in state["cooldowns"] and now < state["cooldowns"][uid]: return
    
    txt = (m.text or "").lower()
    if "#сделка" in txt:
        if any(x in txt for x in ["руб", "₽", "rub"]) or not txt.replace("#сделка", "").strip(): return
        try:
            await asyncio.sleep(random.uniform(2, 5))
            await c.send_chat_action(m.chat.id, ChatAction.TYPING)
            await asyncio.sleep(random.uniform(1, 2))
            ans = f"{random.choice(REPLY_VARIANTS)} {random.choice(EMOJIS)}".strip()
            await m.reply(ans)
            state["total"] += 1
            state["cooldowns"][uid] = now + timedelta(minutes=COOLDOWN_MIN)
            if state["my_id"]:
                await bot.send_message(state["my_id"], f"🎯 <b>ПЕРЕХОПЛЕНО!</b>\nВід: <code>{uid}</code>\n<a href='{m.link}'>Перейти</a>")
        except: pass

async def start():
    print("⏳ Запуск хмарного сервера...")
    await bot.start(); await user.start()
    me = await user.get_me(); state["my_id"] = me.id
    print("✅ СИСТЕМА ПРАЦЮЄ 24/7"); await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start())
