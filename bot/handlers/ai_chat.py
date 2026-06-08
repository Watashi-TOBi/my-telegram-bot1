import logging
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType, ChatAction

from config import AI_API_KEY

logger = logging.getLogger(__name__)

_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash-lite:generateContent"
)

_SYSTEM_PROMPT = """
You are a chill, witty person chatting on Telegram — not an AI assistant.

Rules you must follow without exception:
- Never say you're an AI, a bot, a language model, or anything like that. If someone asks, deflect casually ("lol why would I be a bot") or change the subject.
- Talk like a real person texting a friend: short sentences, casual grammar, occasional slang. No bullet points, no numbered lists, no headers.
- Don't be overly positive or use filler phrases like "Certainly!", "Of course!", "Great question!", "Absolutely!" — real people don't talk like that.
- Match the user's energy. If they're funny, be funny back. If they're serious, tone it down. If they use their language or slang, mirror it naturally.
- Keep replies concise — most should be 1-3 sentences. Don't dump a wall of text unless you really need to.
- Swear occasionally if the vibe calls for it, but don't overdo it.
- Have opinions. Take sides. Be a little opinionated rather than always sitting on the fence.
- If you don't know something, say so like a human would ("honestly no clue", "no idea tbh") — not "I don't have access to real-time information".
- Never use emojis excessively. One at most per message, and only when it genuinely fits.
"""


async def _ask_gemini(user_text: str) -> str:
    import asyncio
    payload = {
        "system_instruction": {
            "parts": [{"text": _SYSTEM_PROMPT.strip()}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_text}]}
        ],
    }
    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(2):
            resp = await client.post(
                _GEMINI_URL,
                params={"key": AI_API_KEY},
                json=payload,
            )
            if resp.status_code == 429 and attempt == 0:
                logger.warning("Gemini 429 — retrying in 5s")
                await asyncio.sleep(5)
                continue
            if not resp.is_success:
                logger.error("Gemini HTTP %s: %s", resp.status_code, resp.text[:300])
                resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    raise RuntimeError("Gemini unavailable after retry")


def _should_respond(update: Update, bot_username: str, bot_id: int) -> tuple[bool, str]:
    if not update.message:
        return False, ""

    text = (update.message.text or update.message.caption or "").strip()
    chat_type = update.effective_chat.type

    # Always reply in private chat
    if chat_type == ChatType.PRIVATE:
        return True, text

    # Reply when @mentioned in a group
    mention = f"@{bot_username}"
    if mention.lower() in text.lower():
        clean = text.replace(mention, "").replace(mention.lower(), "").strip()
        return True, clean or text

    # Reply when someone replies to one of the bot's messages
    reply = update.message.reply_to_message
    if reply and reply.from_user and reply.from_user.id == bot_id:
        return True, text

    return False, ""


async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot_username = context.bot.username
    bot_id       = context.bot.id

    should_respond, user_text = _should_respond(update, bot_username, bot_id)

    if not should_respond:
        return

    if not user_text:
        await update.message.reply_text("wassup")
        return

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    try:
        reply = await _ask_gemini(user_text)
        if not reply:
            raise ValueError("Empty response from Gemini")
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error("Gemini error: %s", e, exc_info=True)
        await update.message.reply_text("ugh, something broke on my end. try again")
