import io
import logging
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InputFile, InputSticker
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

_FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_CARD_BG  = (28, 28, 36, 220)   # dark, slightly transparent
_ACCENT   = (130, 80, 220, 255)
_NAME_CLR = (200, 160, 255, 255)
_TEXT_CLR = (230, 230, 230, 255)
_DIM_CLR  = (90, 90, 110, 180)


def _strip_emoji(text: str) -> str:
    return re.sub(
        r"[\U00010000-\U0010ffff"
        r"\U0001F600-\U0001F64F"
        r"\U0001F300-\U0001F5FF"
        r"\U0001F680-\U0001F6FF"
        r"\U0001F1E0-\U0001F1FF"
        r"\u2600-\u26FF\u2700-\u27BF]+",
        "",
        text,
        flags=re.UNICODE,
    ).strip()


def _make_quote_sticker(sender_name: str, text: str) -> io.BytesIO:
    W, H = 512, 512

    try:
        fn = ImageFont.truetype(_FONT_BOLD, 28)
        ft = ImageFont.truetype(_FONT_REG,  24)
        fq = ImageFont.truetype(_FONT_BOLD, 80)
    except Exception:
        fn = ft = fq = ImageFont.load_default()

    # Fully transparent canvas — Telegram MUST treat RGBA WebP as sticker
    img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded card with semi-transparent dark background
    pad = 16
    draw.rounded_rectangle(
        [pad, pad, W - pad, H - pad],
        radius=24,
        fill=_CARD_BG,
    )

    # Left accent bar (inside card)
    bar_x = pad + 14
    draw.rectangle([bar_x, pad + 14, bar_x + 6, H - pad - 14], fill=_ACCENT)

    # Opening quote decoration
    q_x = W - pad - 90
    draw.text((q_x, pad - 4), "\u201c", font=fq, fill=(80, 55, 140, 160))

    # Sender name
    name_clean = _strip_emoji(sender_name) or sender_name
    name_x = bar_x + 16
    draw.text((name_x, pad + 16), name_clean, font=fn, fill=_NAME_CLR)

    # Divider line
    div_y = pad + 58
    draw.line([name_x, div_y, W - pad - 20, div_y], fill=(70, 60, 100, 200), width=1)

    # Message body (wrapped)
    body    = _strip_emoji(text) or text
    wrapped = textwrap.fill(body, width=26)
    draw.multiline_text((name_x, div_y + 12), wrapped, font=ft, fill=_TEXT_CLR, spacing=8)

    # Closing quote
    draw.text((W - pad - 72, H - pad - 90), "\u201d", font=fq, fill=(80, 55, 140, 160))

    buf = io.BytesIO()
    img.save(buf, format="WEBP", lossless=True)
    buf.seek(0)
    return buf


async def quote_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg.reply_to_message:
        await msg.reply_text("💬 Reply to a text message to turn it into a quote sticker!")
        return

    replied = msg.reply_to_message
    text = replied.text or replied.caption
    if not text:
        await msg.reply_text("❌ That message has no text to quote.")
        return

    sender      = replied.from_user
    sender_name = sender.full_name if sender else "Unknown"

    loading = await msg.reply_text("✨ Creating quote sticker...")
    try:
        sticker_buf = _make_quote_sticker(sender_name, text)
        await loading.delete()
        await context.bot.send_sticker(
            chat_id=msg.chat_id,
            sticker=InputFile(sticker_buf, filename="sticker.webp"),
            reply_to_message_id=msg.message_id,
        )
    except Exception as e:
        logger.error("Quote sticker error: %s", e, exc_info=True)
        try:
            await loading.edit_text(f"❌ Failed to create sticker: {e}")
        except Exception:
            pass


# ── Kang ─────────────────────────────────────────────────────────────────────

def _sticker_format(sticker) -> str:
    if sticker.is_animated:
        return "animated"
    if sticker.is_video:
        return "video"
    return "static"


async def kang_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg  = update.message
    user = msg.from_user
    bot  = context.bot

    if not msg.reply_to_message or not msg.reply_to_message.sticker:
        await msg.reply_text("🎨 Reply to a sticker to kang (steal) it into your pack!")
        return

    sticker = msg.reply_to_message.sticker
    fmt     = _sticker_format(sticker)

    raw_name = f"k{user.id}_by_{bot.username}"
    set_name  = raw_name[:64]
    set_title = f"{user.first_name}'s Stash"

    emoji_list = [sticker.emoji] if sticker.emoji else ["🎭"]

    sf   = await sticker.get_file()
    data = bytes(await sf.download_as_bytearray())

    input_s = InputSticker(sticker=data, emoji_list=emoji_list, format=fmt)
    status  = await msg.reply_text("🔄 Kanging sticker...")

    async def _send_success(created: bool) -> None:
        label    = "New pack created" if created else "Added to your pack"
        pack_url = f"https://t.me/addstickers/{set_name}"
        try:
            ss = await bot.get_sticker_set(set_name)
            await msg.reply_sticker(ss.stickers[-1].file_id)
        except Exception:
            pass
        await status.edit_text(
            f"✅ {label}!\n"
            f'📦 <a href="{pack_url}">Open sticker pack</a>',
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    try:
        await bot.add_sticker_to_set(user_id=user.id, name=set_name, sticker=input_s)
        await _send_success(created=False)
        return
    except Exception as e:
        logger.info("add_sticker_to_set failed (%s) — trying create", e)

    try:
        await bot.create_new_sticker_set(
            user_id=user.id,
            name=set_name,
            title=set_title,
            stickers=[input_s],
        )
        await _send_success(created=True)
    except Exception as e2:
        err = str(e2)
        logger.error("create_new_sticker_set failed: %s", err)
        if any(x in err for x in ("PEER_ID_INVALID", "Forbidden", "bot was blocked",
                                   "chat not found", "have no access")):
            await status.edit_text(
                f"⚠️ You need to start me in DM first so I can create your sticker pack!\n"
                f"👉 <a href='https://t.me/{bot.username}?start=kang'>Tap here to open DM</a>",
                parse_mode="HTML",
            )
        else:
            await status.edit_text(f"❌ Could not kang: {err}")
