from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from ..data_store import DataStore


karma_router = Router()


@karma_router.message(~F.text.startswith("/"))
async def handle_karma(message: Message, store: DataStore):
    if not message.reply_to_message:
        return
    target_user = message.reply_to_message.from_user
    text = (message.text or "").strip()
    if not text:
        return
    if text.isdigit() or (text.startswith("+") and text[1:].isdigit()):
        value = int(text.replace("+", ""))
        new_karma = store.add_karma(target_user.id, value)
    elif text.startswith("-") and text[1:].isdigit():
        value = int(text)
        new_karma = store.add_karma(target_user.id, value)
    else:
        return
    store.set_karma(target_user.id, new_karma)
    await message.reply(
        f"⚖️ Карма користувача {target_user.full_name}: <b>{new_karma}</b>\n"
        f"(Максимум: 1000 | Мінімум: -1000)"
    )


@karma_router.callback_query(F.data == "my_punishments")
async def show_punishments(callback: CallbackQuery, store: DataStore):
    user_id = callback.from_user.id
    punishments = store.get_history(user_id)
    if punishments:
        text = "<b>👮 Ваші покарання:</b>\n\n"
        for p in punishments:
            text += (
                f"⛔ <b>Тип:</b> {p.type}\n"
                f"📌 <b>Причина:</b> {p.reason}\n"
                f"⏰ <b>Дата:</b> {p.date}\n"
                f"📅 <b>До:</b> {p.until or '—'}\n\n"
            )
    else:
        text = "<b>✅ У вас немає покарань!</b>"
    await callback.message.answer(text)
    await callback.answer()

